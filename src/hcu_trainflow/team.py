"""Dependency-aware work reservations and durable peer exchange, independent of model runtime.

Owner/session labels are attribution, not OS authentication. The controller launches
actual Agents after claiming work; accepted results, not delivery receipts, unlock dependents.
"""
import json
from pathlib import PurePosixPath

from .core import FlowError, context_epoch, safe_id, utc


def goal(db, tid):
    row = db.execute('SELECT goal FROM flows WHERE task=?', (tid,)).fetchone()
    return row['goal'] if row else None


def records(db, tid):
    return {r['id']: {**dict(r), 'spec': json.loads(r['payload'])}
            for r in db.execute('SELECT * FROM assignments WHERE task=? ORDER BY id', (tid,))}


def get(db, aid):
    row = db.execute('SELECT * FROM assignments WHERE id=?', (aid,)).fetchone()
    if not row:
        raise FlowError('Unknown assignment')
    return {**dict(row), 'spec': json.loads(row['payload'])}


def stale(db, row):
    task = db.execute('SELECT context FROM tasks WHERE id=?', (row['task'],)).fetchone()
    registered = db.execute("SELECT COALESCE(MAX(seq),0) FROM events WHERE task=? AND kind='assignment-registered' AND json_extract(payload,'$.id')=?", (row['task'], row['id'])).fetchone()[0]
    return (row['spec']['context'] != task['context'] or row['spec'].get('flow_goal') != goal(db, row['task'])
            or context_epoch(db, row['task']) > registered)


def proof(store, values):
    if not isinstance(values, list) or not values:
        raise FlowError('Retained evidence is required')
    for sha in values:
        store.artifact(sha)


def json_object(store, sha):
    value = json.loads(store.artifact(sha))
    if not isinstance(value, dict):
        raise FlowError('Expected retained JSON report')
    return value


def normalize(spec, task, flow_goal):
    required = {'id','owner','goal','scope','allowed_paths','acceptance','budget','context'}
    optional = {'depends_on','peers','mode','checkout','resources','resource_scope','required'}
    if not isinstance(spec, dict) or required - spec.keys() or set(spec) - required - optional:
        raise FlowError('Assignment requires bounded work and known contract fields')
    for key in ('id','owner'):
        safe_id(spec[key])
    if spec['id'] == 'controller' or spec['owner'] == 'controller':
        raise FlowError('controller is reserved for the coordinating endpoint')
    for key in ('goal','scope','acceptance'):
        if not isinstance(spec[key], str) or not spec[key].strip():
            raise FlowError('Assignment goal, scope and acceptance must be explicit')
    if spec['context'] != task['context']:
        raise FlowError('Assignment context is stale')
    if not isinstance(spec['budget'], dict) or not spec['budget'] or set(spec['budget'])-{'max_operations','max_seconds'} or any(type(v) not in (int,float) or not 0 < v < float('inf') for v in spec['budget'].values()):
        raise FlowError('Assignment budget requires positive finite limits')
    result = {'depends_on':[], 'peers':[], 'mode':'write', 'checkout':'task', 'resources':[],
              'resource_scope':'assignment', 'required':True, **spec, 'flow_goal':flow_goal}
    if result['mode'] not in {'read','write','experiment','review'} or type(result['required']) is not bool:
        raise FlowError('Invalid assignment mode/required flag')
    if not result['required'] and result['mode'] not in {'read','review'}:
        raise FlowError('Mutating/experimental work must participate in integration acceptance')
    if result['resource_scope'] not in {'assignment','operation'}:
        raise FlowError('resource_scope must be assignment or operation')
    safe_id(result['checkout'])
    for field in ('depends_on','peers','resources','allowed_paths'):
        if not isinstance(result[field], list) or any(not isinstance(v,str) or not v.strip() for v in result[field]) or len(set(result[field])) != len(result[field]):
            raise FlowError('Assignment lists must contain unique nonempty strings')
    if not result['allowed_paths']:
        raise FlowError('Declare read/write path scope, using . for the complete checkout')
    paths=[]
    for raw in result['allowed_paths']:
        path=PurePosixPath(raw.replace('\\','/'))
        if path.is_absolute() or '..' in path.parts or ':' in raw or any(c in raw for c in '*?['):
            raise FlowError('Use checkout-relative literal paths, not globs or escaping paths')
        paths.append(path.as_posix())
    result['allowed_paths']=paths
    for field in ('depends_on','peers'):
        for aid in result[field]:
            safe_id(aid)
            if aid == result['id']:
                raise FlowError('An assignment cannot depend on or message itself')
    return result


def plan(store, tid, value):
    task=store.task(tid)
    if task['state'] in {'completed','cancelled'}:
        raise FlowError('Cannot plan work on a terminal task')
    if not isinstance(value,dict) or set(value) != {'rationale','max_parallel','assignments'} or not isinstance(value['rationale'],str) or not value['rationale'].strip():
        raise FlowError('Team plan requires rationale, max_parallel and assignments')
    if type(value['max_parallel']) is not int or not 1 <= value['max_parallel'] <= 64 or not isinstance(value['assignments'],list) or not value['assignments']:
        raise FlowError('Declare a bounded team and nonempty work list')
    with store.db() as db:
        fg=goal(db,tid)
    normalized=[normalize(s,task,fg) for s in value['assignments']]
    ids=[s['id'] for s in normalized]
    if len(set(ids)) != len(ids):
        raise FlowError('Duplicate assignment ID')
    sha=store.put(json.dumps({**value,'assignments':normalized},ensure_ascii=False).encode())
    with store.db() as db:
        db.execute('BEGIN IMMEDIATE')
        current=db.execute('SELECT context,state FROM tasks WHERE id=?',(tid,)).fetchone()
        if current['state'] in {'completed','cancelled'} or current['context'] != task['context'] or context_epoch(db,tid) != task['context_epoch'] or goal(db,tid) != fg:
            raise FlowError('Context changed during planning')
        old=records(db,tid)
        for spec in normalized:
            if db.execute('SELECT 1 FROM assignments WHERE id=?',(spec['id'],)).fetchone():
                raise FlowError('Assignment IDs are immutable; add a new ID for revised work')
        specs={**{k:r['spec'] for k,r in old.items()}, **{s['id']:s for s in normalized}}
        for spec in normalized:
            for dep in spec['depends_on'] + spec['peers']:
                if dep not in specs or specs[dep]['context'] != task['context'] or specs[dep].get('flow_goal') != fg or dep in old and stale(db,old[dep]):
                    raise FlowError('Dependency/peer must be registered in the same current task/goal')
        visited=set(); visiting=set()
        def visit(aid):
            if aid in visiting: raise FlowError('Cyclic assignment dependency')
            if aid in visited: return
            visiting.add(aid)
            for dep in specs[aid].get('depends_on',[]): visit(dep)
            visiting.remove(aid);visited.add(aid)
        for aid in ids: visit(aid)
        for spec in normalized:
            db.execute("INSERT INTO assignments VALUES(?,?,?,'pending')",(spec['id'],tid,json.dumps(spec)))
            store.event(db,tid,'assignment-registered',{'id':spec['id'],'context':task['context']})
        if any(s['required'] for s in normalized):
            db.execute("UPDATE flow_rounds SET status='superseded' WHERE task=? AND status IN ('submitted','accepted')", (tid,))
        db.execute('INSERT OR REPLACE INTO team_plans VALUES(?,?,?)',(tid,sha,value['max_parallel']))
        store.event(db,tid,'team-planned',{'plan':sha,'context':task['context'],'assignments':ids})
    return schedule(store,tid)


def conflict(left, right, *, shared_checkout=True):
    if set(left['resources']) & set(right['resources']) and (
            left.get('resource_scope','assignment')=='assignment' or right.get('resource_scope','assignment')=='assignment'):
        return 'shared-resource'
    # Readers of a mutable checkout also conflict with a writer. Give readers an
    # immutable snapshot with another checkout ID to safely run beside writes.
    writes=lambda s:s['mode'] in {'write','experiment'}
    if shared_checkout and left['checkout'] == right['checkout'] and (writes(left) or writes(right)):
        for a in left['allowed_paths']:
            for b in right['allowed_paths']:
                if a == '.' or b == '.' or a.casefold() == b.casefold() or a.casefold().startswith(b.casefold()+'/') or b.casefold().startswith(a.casefold()+'/'):
                    return 'shared-checkout-path'
    return None


def active_reservations(db):
    return [{**dict(row), 'spec': json.loads(row['payload'])}
            for row in db.execute("SELECT * FROM assignments WHERE status='claimed'")]


def reservation_conflict(left, right):
    # The default checkout is local to its task; explicitly named checkouts and
    # hardware resources identify shared scopes throughout the workspace.
    shared = left['task'] == right['task'] or all(row['spec']['checkout'] != 'task' for row in (left, right))
    return conflict(left['spec'], right['spec'], shared_checkout=shared)


def message_blockers(db, tid, endpoint):
    reasons=[]
    context=db.execute('SELECT context FROM tasks WHERE id=?',(tid,)).fetchone()['context']
    fg=goal(db,tid)
    for row in db.execute("SELECT * FROM agent_messages WHERE task=? AND status!='handled'",(tid,)):
        message=json.loads(row['payload'])
        if message['context']!=context or message.get('flow_goal')!=fg:continue
        if message['blocking'] and (message['recipient'] == endpoint or message['kind'] == 'question' and message['sender'] == endpoint):
            reasons.append('message:'+row['id'])
    return reasons


def dependency_blockers(db, row, visited=None):
    """An accepted intermediate result cannot hide invalidated upstream inputs."""
    visited=set() if visited is None else visited
    reasons=[]
    for dep in row['spec'].get('depends_on',[]):
        if dep in visited: continue
        visited.add(dep)
        parent=get(db,dep)
        if parent['status'] != 'accepted': reasons.append('dependency-not-accepted:'+dep)
        if stale(db,parent): reasons.append('dependency-stale:'+dep)
        if message_blockers(db,row['task'],dep):reasons.append('dependency-has-peer-blocker:'+dep)
        reasons += dependency_blockers(db,parent,visited)
    return reasons


def readiness(db,row,all_rows):
    reasons=dependency_blockers(db,row)
    if stale(db,row): reasons.append('stale-context-or-goal')
    # Incoming questions must not prevent their recipient from running to answer.
    # A voluntarily yielded worker can resume after its blocking exchange resolves.
    if row['status']=='waiting':reasons += message_blockers(db,row['task'],row['id'])
    return reasons


def schedule(store, tid):
    store.task(tid)
    with store.db() as db:
        rows=records(db,tid)
        cfg=db.execute('SELECT max_parallel FROM team_plans WHERE task=?',(tid,)).fetchone()
        limit=cfg['max_parallel'] if cfg else 1
        occupied_rows=active_reservations(db)
        active=[r for r in occupied_rows if r['task']==tid]
        selected=[];waiting={};returned=[]
        for aid,row in rows.items():
            if row['status']=='returned' and not stale(db,row): returned.append(aid)
            if row['status'] not in {'pending','needs-revision','waiting'}: continue
            reasons=readiness(db,row,rows)
            if len(active)+len(selected)>=limit: reasons.append('parallel-slot-limit')
            for occupied in occupied_rows+selected:
                why=reservation_conflict(row,occupied)
                if why: reasons.append(why+':'+occupied['id'])
                if row['task']==occupied['task'] and row['spec']['owner']==occupied['spec']['owner']: reasons.append('owner-busy:'+occupied['id'])
            if reasons: waiting[aid]=reasons
            else:selected.append(row)
        items=[]
        for row in rows.values():
            run=db.execute('SELECT * FROM assignment_runs WHERE assignment=?',(row['id'],)).fetchone()
            items.append({'id':row['id'],'owner':row['spec']['owner'],'status':row['status'],
                'goal':row['spec']['goal'],'depends_on':row['spec'].get('depends_on',[]),
                'resources':row['spec'].get('resources',[]),'resource_scope':row['spec'].get('resource_scope','assignment'),
                'stale':stale(db,row),
                'run':dict(run) if run else None})
        return {'task':tid,'max_parallel':limit,'dispatchable':[r['id'] for r in selected],
                'active':[r['id'] for r in active],'awaiting_acceptance':returned,'waiting':waiting,'assignments':items,
                'replan_required':[{'assignment':r['id'],'action':'flow-replan',
                    'reason':'Required work was cancelled. Replan the flow with an explicit replacement reason, then register current assignments; adding a new assignment alone does not replace the cancelled obligation.'}
                    for r in rows.values() if r['status']=='cancelled' and r['spec'].get('required',True) and not stale(db,r)],
                'dispatch':'Claim, launch through the installed harness, then bind the actual session ID'}


def claimed(db,aid,owner,token):
    row=get(db,aid)
    run=db.execute('SELECT * FROM assignment_runs WHERE assignment=?',(aid,)).fetchone()
    if row['status']!='claimed' or row['spec']['owner']!=owner or not run or run['token']!=token:
        raise FlowError('Assignment is not claimed by this owner/token')
    if stale(db,row):raise FlowError('Assignment context/goal is stale')
    validate_inputs(db,row,run)
    return row,dict(run)


def validate_inputs(db,row,run):
    if dependency_blockers(db,row):
        raise FlowError('Accepted dependency evidence changed')
    for dep,sha in json.loads(run['inputs']).items():
        parent=get(db,dep)
        parent_run=db.execute('SELECT report FROM assignment_runs WHERE assignment=?',(dep,)).fetchone()
        if parent['status']!='accepted' or not parent_run or parent_run['report']!=sha or message_blockers(db,row['task'],dep):
            raise FlowError('Accepted dependency evidence changed')


def claim(store,aid,owner):
    with store.db() as db:tid=get(db,aid)['task']
    from .flow import guard_execution
    guard_execution(store,tid,allow_parallel=True)
    with store.db() as db:
        db.execute('BEGIN IMMEDIATE')
        row=get(db,aid)
        task=db.execute('SELECT * FROM tasks WHERE id=?',(row['task'],)).fetchone()
        if task['state'] in {'paused','blocked','failed','completed','cancelled'}:raise FlowError('Task is not active')
        if row['spec']['owner']!=owner or row['status'] not in {'pending','needs-revision','waiting'}:raise FlowError('Assignment cannot be claimed')
        all_rows=records(db,row['task']);reasons=readiness(db,row,all_rows)
        occupied_rows=active_reservations(db)
        active=[r for r in occupied_rows if r['task']==row['task']]
        limit=db.execute('SELECT max_parallel FROM team_plans WHERE task=?',(row['task'],)).fetchone()
        if len(active)>=(limit['max_parallel'] if limit else 1):reasons.append('parallel-slot-limit')
        for other in occupied_rows:
            why=reservation_conflict(row,other)
            if why or other['task']==row['task'] and other['spec']['owner']==owner:reasons.append(why or 'owner-busy')
        if reasons:raise FlowError('Claim blocked: '+', '.join(reasons))
        old=db.execute('SELECT token FROM assignment_runs WHERE assignment=?',(aid,)).fetchone()
        token=old['token']+1 if old else 1
        inputs={dep:db.execute('SELECT report FROM assignment_runs WHERE assignment=?',(dep,)).fetchone()['report'] for dep in row['spec']['depends_on']}
        db.execute('INSERT OR REPLACE INTO assignment_runs VALUES(?,?,NULL,?,NULL,?,NULL)',(aid,token,json.dumps(inputs),utc()))
        db.execute("UPDATE assignments SET status='claimed' WHERE id=?",(aid,))
        payload={'id':aid,'owner':owner,'token':token,'inputs':inputs,'spec':row['spec'],'context':row['spec']['context']}
        store.event(db,row['task'],'assignment-ready',payload,channel='agent')
    return {**payload,'status':'claimed','launched':False}


def bind(store,aid,owner,token,session):
    if not isinstance(session,str) or not session.strip():raise FlowError('Actual runtime session ID is required')
    with store.db() as db:
        db.execute('BEGIN IMMEDIATE');row,run=claimed(db,aid,owner,token)
        if run['session'] and run['session']!=session:raise FlowError('Claim already bound to another session')
        if db.execute("SELECT 1 FROM assignment_runs r JOIN assignments a ON r.assignment=a.id WHERE r.session=? AND a.status='claimed' AND a.id!=?",(session,aid)).fetchone():raise FlowError('Runtime session already bound to another active assignment')
        db.execute('UPDATE assignment_runs SET session=?,updated=? WHERE assignment=?',(session,utc(),aid))
        store.event(db,row['task'],'assignment-session-bound',{'id':aid,'session':session,'token':token})
    return {'id':aid,'session':session,'token':token}


def finish(store,aid,owner,report_id,token):
    value=json_object(store,report_id)
    proof(store,value.get('evidence'))
    if not isinstance(value.get('summary'),str) or not value['summary'].strip():raise FlowError('Return needs a substantive summary')
    with store.db() as db:
        db.execute('BEGIN IMMEDIATE');row,run=claimed(db,aid,owner,token)
        if value.get('context')!=row['spec']['context'] or value.get('inputs')!=json.loads(run['inputs']):raise FlowError('Return must bind current context and exact accepted input hashes')
        if message_blockers(db,row['task'],aid):raise FlowError('Unresolved peer question/blocker')
        if db.execute("SELECT 1 FROM assignment_operations a JOIN operations o ON a.operation=o.id WHERE a.assignment=? AND o.status IN ('started','unknown')",(aid,)).fetchone():raise FlowError('Reconcile or finish assignment executions before return')
        db.execute('UPDATE assignment_runs SET report=?,updated=? WHERE assignment=?',(report_id,utc(),aid))
        db.execute("UPDATE assignments SET status='returned' WHERE id=?",(aid,))
        store.event(db,row['task'],'assignment-returned',{'id':aid,'context':row['spec']['context'],'report':report_id,'acceptance':'controller-review-required'},channel='agent')
    return {'id':aid,'status':'returned','report':report_id}


def review(store,aid,value):
    if set(value)!={'report','reviewer','verdict','note','evidence'} or value['verdict'] not in {'accept','revise'} or not isinstance(value['note'],str) or not value['note'].strip():raise FlowError('Result review needs report, reviewer, verdict, note and evidence')
    proof(store,value['evidence']);safe_id(value['reviewer'])
    sha=store.put(json.dumps(value,ensure_ascii=False).encode())
    with store.db() as db:
        db.execute('BEGIN IMMEDIATE');row=get(db,aid)
        run=db.execute('SELECT * FROM assignment_runs WHERE assignment=?',(aid,)).fetchone()
        if row['status']!='returned' or stale(db,row) or not run or run['report']!=value['report']:raise FlowError('No matching current returned result')
        if value['verdict']=='accept':validate_inputs(db,row,run)
        if row['spec']['owner']==value['reviewer']:raise FlowError('Owner cannot accept their own result')
        if message_blockers(db,row['task'],aid):raise FlowError('Resolve peer blockers before accepting result')
        state='accepted' if value['verdict']=='accept' else 'needs-revision'
        db.execute('UPDATE assignments SET status=? WHERE id=?',(state,aid))
        db.execute('UPDATE assignment_runs SET note=?,updated=? WHERE assignment=?',(sha,utc(),aid))
        store.event(db,row['task'],'assignment-reviewed',{'id':aid,'status':state,'review':sha,'context':row['spec']['context']},channel='agent')
    return {'id':aid,'status':state,'review':sha}


def cancel(store,aid,value):
    if set(value)!={'stopped','note','evidence'} or value['stopped'] is not True or not isinstance(value['note'],str) or not value['note'].strip():raise FlowError('Cancellation requires verified stopped state and explanation')
    proof(store,value['evidence'])
    with store.db() as db:
        db.execute('BEGIN IMMEDIATE');row=get(db,aid)
        if row['status'] in {'accepted','cancelled'}:raise FlowError('Result is already terminal')
        if db.execute("SELECT 1 FROM assignment_operations a JOIN operations o ON a.operation=o.id WHERE a.assignment=? AND o.status IN ('started','unknown')",(aid,)).fetchone():raise FlowError('Reconcile running/unknown operations before releasing work scope')
        db.execute("UPDATE assignments SET status='cancelled' WHERE id=?",(aid,))
        store.event(db,row['task'],'assignment-cancelled',{'id':aid,**value})
    return {'id':aid,'status':'cancelled','note':'Required work remains incomplete; explicitly replan its replacement'}


def yield_assignment(store,aid,owner,token,value):
    if set(value)!={'quiescent','note','evidence'} or value['quiescent'] is not True or not isinstance(value['note'],str) or not value['note'].strip():raise FlowError('Yield requires verified quiescent work scope and an explanation')
    proof(store,value['evidence'])
    with store.db() as db:
        db.execute('BEGIN IMMEDIATE');row,run=claimed(db,aid,owner,token)
        if db.execute("SELECT 1 FROM assignment_operations a JOIN operations o ON a.operation=o.id WHERE a.assignment=? AND o.status IN ('started','unknown')",(aid,)).fetchone():raise FlowError('Finish/reconcile executions before yielding resources')
        db.execute("UPDATE assignments SET status='waiting' WHERE id=?",(aid,))
        store.event(db,row['task'],'assignment-yielded',{'id':aid,'token':token,**value})
    return {'id':aid,'status':'waiting','scope_released':True,'note':'No more mutations until reclaimed with a new token'}


def endpoint(db,tid,aid,owner=None):
    if aid=='controller':
        if owner is not None and owner!='controller':raise FlowError('Controller endpoint owner mismatch')
        return None
    row=get(db,aid)
    if row['task']!=tid or stale(db,row) or row['status']=='cancelled':raise FlowError('Peer endpoint is unavailable/stale')
    if owner is not None and owner!=row['spec']['owner']:raise FlowError('Message endpoint owner mismatch')
    return row


def send(store,tid,value):
    required={'id','sender','recipient','owner','kind','body','context','evidence'}
    if required-value.keys() or set(value)-required-{'reply_to','blocking'}:raise FlowError('Invalid agent message fields')
    safe_id(value['id'])
    if value['kind'] not in {'question','answer','finding','blocker','handoff'} or not isinstance(value['body'],str) or not value['body'].strip():raise FlowError('Message needs kind and substantive body')
    if value['sender']==value['recipient']:raise FlowError('Choose another recipient')
    if not isinstance(value['evidence'],list):raise FlowError('Evidence must be an artifact list')
    for sha in value['evidence']:store.artifact(sha)
    message={'blocking':value['kind']=='blocker','reply_to':None,**value}
    if type(message['blocking']) is not bool or value['kind']=='blocker' and not message['blocking']:raise FlowError('Blocker must be marked blocking')
    with store.db() as db:
        db.execute('BEGIN IMMEDIATE')
        task=db.execute('SELECT context,state FROM tasks WHERE id=?',(tid,)).fetchone()
        if not task or task['context']!=message['context'] or task['state'] in {'completed','cancelled'}:raise FlowError('Message task/context is unavailable')
        left=endpoint(db,tid,message['sender'],message['owner']);right=endpoint(db,tid,message['recipient'])
        if left and right:
            links=left['spec'].get('peers',[])+left['spec'].get('depends_on',[])
            back=right['spec'].get('peers',[])+right['spec'].get('depends_on',[])
            if right['id'] not in links and left['id'] not in back:raise FlowError('Declare a dependency or peer relationship before direct exchange')
            if message['kind']=='question' and message['blocking']:
                all_rows=records(db,tid)
                def depends(aid,ancestor):
                    return ancestor in all_rows[aid]['spec'].get('depends_on',[]) or any(depends(p,ancestor) for p in all_rows[aid]['spec'].get('depends_on',[]))
                if depends(right['id'],left['id']):raise FlowError('Blocking question waits on its own dependent; ask the controller or split an interface task')
        message['flow_goal']=goal(db,tid)
        prior=db.execute('SELECT payload FROM agent_messages WHERE id=?',(message['id'],)).fetchone()
        if prior:
            if json.loads(prior['payload'])!=message:raise FlowError('Message ID collision')
            return {'id':message['id'],'status':'already-recorded'}
        if message['kind']=='answer':
            parent=db.execute('SELECT * FROM agent_messages WHERE id=? AND task=?',(message['reply_to'],tid)).fetchone()
            if not parent:raise FlowError('Answer needs an existing question')
            question=json.loads(parent['payload'])
            if question['kind']!='question' or question['sender']!=message['recipient'] or question['recipient']!=message['sender'] or question.get('flow_goal')!=message['flow_goal'] or parent['status']=='handled':raise FlowError('Answer must return to the current question author')
        elif message['reply_to'] is not None:raise FlowError('Only answers use reply_to')
        db.execute("INSERT INTO agent_messages VALUES(?,?,?,'pending',?,NULL)",(message['id'],tid,json.dumps(message),utc()))
        if message['blocking']:
            db.execute("UPDATE flow_rounds SET status='superseded' WHERE task=? AND status IN ('submitted','accepted')", (tid,))
        store.event(db,tid,'agent-message',{'message':message['id'],'recipient':message['recipient'],'context':message['context']},channel='agent')
    return {'id':message['id'],'status':'pending','delivery':'Recipient must read and acknowledge; no Agent launch is implied'}


def messages(store,tid,recipient=None):
    context=store.task(tid)['context']
    with store.db() as db:
        values=[{**dict(r),'message':json.loads(r['payload'])} for r in db.execute('SELECT * FROM agent_messages WHERE task=? ORDER BY created,id',(tid,))]
        for row in values:
            row.pop('payload')
            row['stale']=row['message']['context']!=context or row['message'].get('flow_goal')!=goal(db,tid)
    return [v for v in values if recipient is None or v['message']['recipient']==recipient]


def acknowledge(store,mid,owner,value):
    if set(value)!={'decision','note','evidence'} or value['decision'] not in {'seen','handled'} or not isinstance(value['note'],str) or not value['note'].strip():raise FlowError('Message receipt requires decision, explanation and evidence')
    if not isinstance(value['evidence'],list):raise FlowError('Receipt evidence must be a list')
    for sha in value['evidence']:store.artifact(sha)
    with store.db() as db:
        db.execute('BEGIN IMMEDIATE');row=db.execute('SELECT * FROM agent_messages WHERE id=?',(mid,)).fetchone()
        if not row:raise FlowError('Unknown message')
        m=json.loads(row['payload']);endpoint(db,row['task'],m['recipient'],owner)
        current=db.execute('SELECT context FROM tasks WHERE id=?',(row['task'],)).fetchone()['context']
        if m.get('flow_goal')!=goal(db,row['task']) or m['context']!=current:raise FlowError('Message context/goal is stale')
        if row['status']=='handled':raise FlowError('Message already handled')
        if value['decision']=='handled' and m['kind']=='question':raise FlowError('Answer the question; its author acknowledges the answer')
        if value['decision']=='handled' and m['blocking'] and not value['evidence']:raise FlowError('Resolving a blocker requires evidence')
        db.execute('UPDATE agent_messages SET status=?,receipt=? WHERE id=?',(value['decision'],json.dumps({'owner':owner,**value}),mid))
        if value['decision']=='handled' and m['kind']=='answer':
            parent=db.execute('SELECT status,payload FROM agent_messages WHERE id=?',(m['reply_to'],)).fetchone()
            if parent['status']=='handled':raise FlowError('Question already resolved by another acknowledged answer')
            if json.loads(parent['payload'])['blocking'] and not value['evidence']:
                raise FlowError('Resolving a blocking question requires evidence')
            db.execute("UPDATE agent_messages SET status='handled',receipt=? WHERE id=?",(json.dumps({'answered_by':mid,'confirmed_by':owner,**value}),m['reply_to']))
        store.event(db,row['task'],'agent-message-acknowledged',{'message':mid,'owner':owner,**value})
    return {'id':mid,'status':value['decision']}


def completion_blockers(db,tid):
    reasons=message_blockers(db,tid,'controller')
    for row in records(db,tid).values():
        if stale(db,row):
            if row['status']=='claimed':reasons.append('stale-running-assignment:'+row['id'])
            continue
        if row['spec'].get('required',True) and row['status']!='accepted':reasons.append('assignment-not-accepted:'+row['id'])
        if row['status']=='claimed':reasons.append('assignment-still-running:'+row['id'])
        reasons+=message_blockers(db,tid,row['id'])
    return list(dict.fromkeys(reasons))


def check_execution(db,tid,aid,owner,token,resource):
    row,run=claimed(db,aid,owner,token)
    if row['task']!=tid or resource not in row['spec']['resources']:raise FlowError('Execution must use a resource reserved by this assignment')
    # Owners may execute bounded diagnostic/corrective work to resolve a message.
    # The unresolved exchange blocks result acceptance and integration instead.
    return row


def active_operation(db,oid,tid):
    link=db.execute('SELECT * FROM assignment_operations WHERE operation=?',(oid,)).fetchone()
    if not link:return False
    row=get(db,link['assignment'])
    run=db.execute('SELECT token FROM assignment_runs WHERE assignment=?',(row['id'],)).fetchone()
    return row['task']==tid and row['status']=='claimed' and not stale(db,row) and run and run['token']==link['token']
