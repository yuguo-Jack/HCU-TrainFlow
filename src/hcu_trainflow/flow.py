"""Persistent implement/review/correct decisions around the training evidence gates.

The Agent executes the decisions. This module never silently launches a model,
claims to authenticate reviewer identity, or treats a code review as a GPU test.
"""
import json
import time
from .core import FlowError, GATES, atomic_write, child, safe_id, utc

DEFAULTS = {'max_rounds': 20, 'max_stalled_rounds': 3, 'full_review_every': 4,
            'max_review_failures': 3, 'poll_seconds': 300}
DELIVERABLES = {'environment': 'environment', 'adapt': 'baseline', 'analyze': 'analysis',
                'optimize': 'stage-quality', 'diagnose': 'diagnosis', 'operate': 'operations'}
NEXT = {'prepared': 'environment_checked', 'environment_checked': 'baseline_validated',
        'baseline_validated': 'profiling', 'profiling': 'optimizing', 'optimizing': 'scale_ready',
        'scale_ready': 'training', 'training': 'completed'}
STAGES = {'prepared': 'adapt', 'environment_checked': 'adapt', 'baseline_validated': 'optimize',
          'profiling': 'optimize', 'optimizing': 'optimize', 'scale_ready': 'fault-tolerance',
          'training': 'fault-tolerance'}


def artifact_json(store, value):
    document = json.loads(store.artifact(value))
    if not isinstance(document, dict):
        raise FlowError('Expected a retained JSON object')
    return document


def retain(store, value):
    return store.put(json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False).encode())


def get_flow(db, tid):
    row = db.execute('SELECT * FROM flows WHERE task=?', (tid,)).fetchone()
    return {**dict(row), 'plan': json.loads(row['plan'])} if row else None


def board_paths(store, tid):
    directory = child(store.root, 'collaboration/' + safe_id(tid))
    return directory, child(directory, 'BOARD.md'), child(directory, 'GUIDANCE.md')


def start(store, tid, plan, reason=None):
    task = store.task(tid)
    if task['state'] in {'completed', 'cancelled'}:
        raise FlowError('Create a new task for a new objective')
    if set(plan) - (set(DEFAULTS) | {'acceptance'}):
        raise FlowError('Unknown flow-plan fields')
    plan = {**DEFAULTS, **plan}
    for key in DEFAULTS:
        if type(plan[key]) is not int or plan[key] <= 0:
            raise FlowError('Flow limits must be positive integers')
    if not 1 <= plan['poll_seconds'] <= 3600:
        raise FlowError('Guidance polling interval must be 1..3600 seconds')
    acceptance = plan.get('acceptance')
    if not isinstance(acceptance, dict) or not acceptance or any(not isinstance(v, str) or not v.strip() for v in acceptance.values()):
        raise FlowError('Plan requires named, concrete acceptance criteria')
    for key in acceptance:
        safe_id(key)
    goal_record = {'objective': task['spec']['objective'], 'context': task['context'], 'plan': plan}
    if reason is not None:
        if not reason.strip():
            raise FlowError('Replanning requires a concrete reason')
        goal_record.update(revision_reason=reason, replanned_at=utc())
    goal = retain(store, goal_record)
    with store.db() as db:
        db.execute('BEGIN IMMEDIATE')
        old = get_flow(db, tid)
        if old and old['goal'] != goal and not reason:
            raise FlowError('Plan/context changed; use flow-replan with a concrete reason')
        if old and old['goal'] == goal:
            return {'task': tid, 'goal': goal, 'status': 'unchanged'}
        db.execute('INSERT OR REPLACE INTO flows VALUES(?,?,?,?)', (tid, json.dumps(plan), goal, task['context']))
        db.execute("UPDATE flow_rounds SET status='superseded' WHERE task=? AND status IN ('submitted','accepted')", (tid,))
        store.event(db, tid, 'flow-replanned' if old else 'flow-started', {'goal': goal, 'reason': reason, 'context': task['context']})
    directory, board, guidance = board_paths(store, tid)
    if not guidance.exists():
        directory.mkdir(parents=True, exist_ok=True)
        # Never overwrite this file after creation; it belongs to the human.
        with guidance.open('x', encoding='utf8') as stream:
            stream.write('# Human guidance\n\nAdd comments, answers and priorities below. Refer to a question ID when replying.\n')
        sha = store.put(guidance.read_bytes())
        with store.db() as db:
            db.execute('INSERT OR IGNORE INTO flow_guidance VALUES(?,?,?,?,?,?)', (tid, sha, task['context'], 'template', '', utc()))
            db.execute('INSERT OR REPLACE INTO flow_guidance_cursor VALUES(?,?)', (tid, sha))
    if task['state'] == 'draft':
        store.transition(tid, 'prepared')
    render_board(store, tid)
    return {'task': tid, 'goal': goal, 'status': 'started', 'board': str(board), 'guidance': str(guidance)}


def sync_guidance(store, tid, *, force=False):
    with store.db() as db:
        flow = get_flow(db, tid)
        scan = db.execute('SELECT checked_at FROM flow_guidance_scans WHERE task=?', (tid,)).fetchone()
    if not flow:
        return {'new': 0}
    now = time.time()
    if not force and scan and 0 <= now - scan['checked_at'] < flow['plan']['poll_seconds']:
        return {'new': 0, 'scan': 'not-due'}
    _, _, path = board_paths(store, tid)
    if not path.is_file():
        raise FlowError('Human guidance file is missing; restore it rather than silently resetting the inbox')
    if path.stat().st_size > 1024 * 1024:
        raise FlowError('Guidance exceeds 1 MiB; retain large evidence separately')
    data = path.read_bytes()
    data.decode('utf-8-sig')
    sha = store.put(data)
    task = store.task(tid)
    with store.db() as db:
        db.execute('BEGIN IMMEDIATE')
        db.execute('INSERT OR REPLACE INTO flow_guidance_scans VALUES(?,?)', (tid, now))
        previous = db.execute('SELECT hash FROM flow_guidance_cursor WHERE task=?', (tid,)).fetchone()
        if previous and previous['hash'] == sha:
            return {'new': 0, 'guidance': sha}
        # A deliberate revert to earlier content is still a new human action.
        db.execute('INSERT OR REPLACE INTO flow_guidance VALUES(?,?,?,?,?,?)', (tid, sha, task['context'], 'pending', '', utc()))
        db.execute('INSERT OR REPLACE INTO flow_guidance_cursor VALUES(?,?)', (tid, sha))
        db.execute("UPDATE flow_rounds SET status='superseded' WHERE task=? AND status IN ('submitted','accepted')", (tid,))
        event = store.event(db, tid, 'human-guidance-received', {'guidance': sha, 'context': task['context']}, channel='agent')
    return {'new': 1, 'guidance': sha, 'event_id': event}


def acknowledge(store, tid, sha, decision, note):
    if decision not in {'applied', 'queued', 'needs-human', 'not-applicable'} or not note.strip():
        raise FlowError('Guidance needs a disposition and concrete response')
    with store.db() as db:
        db.execute('BEGIN IMMEDIATE')
        row = db.execute('SELECT * FROM flow_guidance WHERE task=? AND id=?', (tid, sha)).fetchone()
        if not row or row['status'] == 'template':
            raise FlowError('Unknown human guidance')
        db.execute('UPDATE flow_guidance SET status=?,note=? WHERE task=? AND id=?', (decision, note, tid, sha))
        store.event(db, tid, 'human-guidance-acknowledged', {'guidance': sha, 'decision': decision, 'note': note})
    return render_board(store, tid)


def question(store, tid, value):
    store.task(tid)
    if set(value) != {'id', 'title', 'body', 'blocking'} or type(value['blocking']) is not bool or any(not isinstance(value[k], str) or not value[k].strip() for k in ('title','body')):
        raise FlowError('Question requires id, title, body and boolean blocking')
    safe_id(value['id'])
    with store.db() as db:
        if not get_flow(db, tid):
            raise FlowError('Start the collaborative flow first')
        old = db.execute('SELECT payload FROM flow_questions WHERE task=? AND id=?', (tid, value['id'])).fetchone()
        if old and json.loads(old['payload']) != value:
            raise FlowError('Question ID already has different content')
        db.execute("INSERT OR IGNORE INTO flow_questions VALUES(?,?,?,'open',NULL)", (tid, value['id'], json.dumps(value)))
        if not old:
            store.event(db, tid, 'human-question-opened', value)
    return render_board(store, tid)


def close_question(store, tid, qid, guidance, note):
    if not note.strip():
        raise FlowError('Question resolution needs an explanation')
    with store.db() as db:
        db.execute('BEGIN IMMEDIATE')
        answer = db.execute('SELECT status FROM flow_guidance WHERE task=? AND id=?', (tid, guidance)).fetchone()
        if not answer or answer['status'] not in {'applied', 'not-applicable'}:
            raise FlowError('Resolve with reviewed human guidance, not an inferred answer')
        if not db.execute('SELECT 1 FROM flow_questions WHERE task=? AND id=?', (tid, qid)).fetchone():
            raise FlowError('Unknown question')
        resolution = {'guidance': guidance, 'note': note}
        db.execute("UPDATE flow_questions SET status='closed',resolution=? WHERE task=? AND id=?", (json.dumps(resolution), tid, qid))
        store.event(db, tid, 'human-question-resolved', {'id': qid, **resolution})
    return render_board(store, tid)


def blockers(db, tid, task, flow):
    reasons = []
    if flow['context'] != task['context']:
        reasons.append('context-changed: replan and revalidate')
    if db.execute("SELECT 1 FROM flow_guidance WHERE task=? AND status IN ('pending','needs-human')", (tid,)).fetchone():
        reasons.append('human-guidance-needs-response')
    if any(json.loads(x['payload'])['blocking'] for x in db.execute("SELECT payload FROM flow_questions WHERE task=? AND status='open'", (tid,))):
        reasons.append('blocking-human-question')
    return reasons


def target(task):
    return 'completed' if task['spec']['mode'] != 'full' else NEXT.get(task['state'])


def required_reports(task, destination):
    if destination == 'iterate':
        return []
    if task['spec']['mode'] != 'full':
        kinds = [DELIVERABLES[task['spec']['mode']]]
        if task['spec']['mode'] == 'optimize':
            kinds.append('performance')
        return kinds
    return GATES.get(destination, [])


def gate(store, db, task, candidate):
    """Reports are current and belong to this exact candidate; LLM verdict cannot waive them."""
    from .team import completion_blockers
    reasons = completion_blockers(db,task['id'])
    if candidate['target'] == 'completed' and db.execute("SELECT 1 FROM flow_guidance WHERE task=? AND status='queued'", (task['id'],)).fetchone():
        reasons.append('queued-human-guidance-needs-final-disposition')
    for kind in required_reports(task, candidate['target']):
        sha = candidate['reports'].get(kind)
        row = db.execute('SELECT * FROM reports WHERE task=? AND kind=? AND context=?', (task['id'], kind, task['context'])).fetchone()
        if not row or row['artifact'] != sha:
            reasons.append('missing-or-replaced-report:' + kind)
            continue
        body = artifact_json(store, sha)
        if body.get('candidate_snapshot') != candidate['snapshot']:
            reasons.append('snapshot-mismatch:' + kind)
        delivery_only = task['spec']['mode'] in {'environment', 'analyze', 'diagnose', 'operate'}
        accepted = {'pass', 'complete', 'fail', 'incomplete'} if delivery_only else {'pass', 'complete'} if kind == 'analysis' else {'pass'}
        if row['result'] not in accepted:
            reasons.append('report-not-passing:' + kind)
    experiment = candidate.get('experiment')
    if candidate['target'] == 'iterate' or (candidate['target'] == 'scale_ready' or task['spec']['mode'] == 'optimize'):
        if not experiment:
            reasons.append('missing-local-correctness-and-performance-experiment')
        else:
            from .quality import assess_iteration
            inputs = artifact_json(store, experiment)
            if inputs.get('context') != task['context'] or inputs.get('correctness', {}).get('candidate_snapshot') != candidate['snapshot']:
                reasons.append('experiment-context-or-snapshot-mismatch')
            else:
                for sha in inputs['correctness'].get('evidence', []):
                    store.artifact(sha)
                try:
                    assessment = assess_iteration(**inputs)
                except (ValueError, TypeError, KeyError):
                    assessment = {'status': 'invalid-experiment'}
                if assessment['status'] != 'iteration-kept':
                    reasons.append('iteration-not-kept')
    return reasons


def last_round(db, tid):
    return db.execute('SELECT * FROM flow_rounds WHERE task=? ORDER BY number DESC LIMIT 1', (tid,)).fetchone()


def next_step(store, tid):
    sync_guidance(store, tid)
    task = store.task(tid)
    with store.db() as db:
        flow = get_flow(db, tid)
        if not flow:
            raise FlowError('Start the collaborative flow first')
        result = {'task': tid, 'state': task['state'], 'context': task['context'], 'goal': flow['goal']}
        row = last_round(db, tid)
        if row and row['status'] == 'accepted':
            candidate = artifact_json(store, row['candidate'])
            # Includes a crash just after committing the terminal transition.
            if row['context'] == task['context'] and row['goal'] == flow['goal'] and task['state'] == candidate['target'] and task['revision'] == row['revision'] + 1:
                db.execute("UPDATE flow_rounds SET status='advanced' WHERE task=? AND number=?", (tid, row['number']))
                row = last_round(db, tid)
        if task['state'] in {'completed', 'cancelled'}:
            return {**result, 'action': task['state']}
        from .team import active_operation, completion_blockers, schedule
        uncertain = [r['id'] for r in db.execute("SELECT id,status FROM operations WHERE task=? AND status IN ('started','unknown')", (tid,))
                     if r['status']=='unknown' or not active_operation(db,r['id'],tid)]
        if uncertain:
            return {**result, 'action': 'reconcile', 'operations': uncertain}
        reasons = blockers(db, tid, task, flow)
        if task['state'] in {'paused', 'blocked', 'failed'}:
            reasons.append('task-' + task['state'])
        if reasons:
            return {**result, 'action': 'human', 'reasons': reasons}
        if row and row['status'] == 'blocked' and row['goal'] == flow['goal']:
            return {**result, 'action': 'human', 'reasons': ['review-blocked'], 'review': row['review']}
        if row and row['status'] in {'submitted', 'accepted'}:
            candidate = artifact_json(store, row['candidate'])
            # Reconcile a crash after the core transition committed but before advance recorded it.
            if row['status'] == 'accepted' and task['state'] == candidate['target'] and task['revision'] == row['revision'] + 1:
                db.execute("UPDATE flow_rounds SET status='advanced' WHERE task=? AND number=?", (tid, row['number']))
            elif row['context'] != task['context'] or row['goal'] != flow['goal'] or row['revision'] != task['revision']:
                return {**result, 'action': 'repair', 'reasons': ['stale-round'], 'round': row['number']}
            else:
                if row['failures'] >= flow['plan']['max_review_failures']:
                    return {**result, 'action': 'human', 'reasons': ['review-failures'], 'round': row['number']}
                problems = gate(store, db, task, candidate) if row['status'] == 'accepted' else []
                team_reasons = completion_blockers(db, tid)
                if team_reasons:
                    return {**result, 'action': 'coordinate', 'reasons': team_reasons, 'team': schedule(store, tid)}
                return {**result, 'action': 'repair' if problems else 'advance' if row['status'] == 'accepted' else 'review',
                        'round': row['number'], 'candidate': row['candidate'], 'review': row['review'], 'reasons': problems,
                        'full_alignment_required': row['number'] % flow['plan']['full_review_every'] == 0 or candidate['target'] in {'scale_ready', 'training', 'completed'}}
        rounds = db.execute('SELECT * FROM flow_rounds WHERE task=? AND goal=? ORDER BY number DESC', (tid, flow['goal'])).fetchall()
        stalled = 0
        for previous in rounds:
            if not previous['review']:
                break
            review = artifact_json(store, previous['review'])
            if review['progress'] == 'advanced':
                break
            stalled += 1
        if len(rounds) >= flow['plan']['max_rounds'] or stalled >= flow['plan']['max_stalled_rounds']:
            return {**result, 'action': 'human', 'reasons': ['round-budget-or-progress-plateau'], 'rounds': len(rounds), 'stalled': stalled}
        mode = task['spec']['mode']
        stage = STAGES.get(task['state'], 'adapt') if mode == 'full' else 'adapt' if mode in {'environment', 'adapt'} else 'optimize' if mode in {'analyze', 'optimize'} else 'fault-tolerance'
        action = 'repair' if row and row['status'] in {'revise', 'superseded'} else 'work'
        team_reasons=completion_blockers(db,tid)
        if team_reasons:
            return {**result,'action':'coordinate','reasons':team_reasons,'team':schedule(store,tid)}
        return {**result, 'action': action, 'skill': 'hcu-train-' + stage, 'target': target(task),
                'required_reports': required_reports(task, target(task)), 'last_review': row['review'] if row else None,
                'poll_seconds': flow['plan']['poll_seconds']}


def submit(store, tid, candidate):
    decision = next_step(store, tid)
    if decision['action'] not in {'work', 'repair'}:
        raise FlowError('Resolve the current flow decision before submitting another candidate')
    task = store.task(tid)
    fields = {'author', 'context', 'goal', 'snapshot', 'summary', 'reports', 'target', 'evidence'}
    if fields - candidate.keys() or set(candidate) - (fields | {'experiment'}):
        raise FlowError('Invalid candidate fields')
    if any(not isinstance(candidate[k], str) or not candidate[k].strip() for k in ('author','summary')) or not isinstance(candidate['reports'], dict):
        raise FlowError('Candidate needs author, substantive summary and reports')
    if candidate['context'] != task['context'] or candidate['goal'] != decision['goal']:
        raise FlowError('Candidate context/goal is stale')
    allowed = {target(task)}
    if task['state'] == 'optimizing' or task['spec']['mode'] == 'optimize':
        allowed.add('iterate')
    if candidate['target'] not in allowed:
        raise FlowError('Candidate cannot skip a workflow stage')
    if not isinstance(candidate['evidence'], list) or not candidate['evidence']:
        raise FlowError('Candidate needs retained evidence')
    for sha in [candidate['snapshot'], *candidate['evidence'], *candidate['reports'].values(), *([candidate['experiment']] if candidate.get('experiment') else [])]:
        store.artifact(sha)
    if candidate.get('experiment'):
        inputs = artifact_json(store, candidate['experiment'])
        required = {'context', 'correctness', 'baseline_times', 'candidate_times'}
        if required - inputs.keys() or set(inputs) - (required | {'max_regression'}) or not isinstance(inputs['correctness'], dict):
            raise FlowError('Experiment must follow the iteration-check input contract')
    sha = retain(store, candidate)
    with store.db() as db:
        db.execute('BEGIN IMMEDIATE')
        current = db.execute('SELECT context,revision FROM tasks WHERE id=?', (tid,)).fetchone()
        row = last_round(db, tid)
        if current['context'] != task['context'] or current['revision'] != task['revision'] or get_flow(db, tid)['goal'] != candidate['goal']:
            raise FlowError('Task changed while submitting')
        if row and row['status'] in {'submitted', 'accepted'} and decision.get('round') != row['number']:
            raise FlowError('Another controller submitted a round')
        number = row['number'] + 1 if row else 1
        if row and row['status'] in {'submitted', 'accepted'}:
            db.execute("UPDATE flow_rounds SET status='superseded' WHERE task=? AND number=?", (tid, row['number']))
        db.execute('INSERT INTO flow_rounds VALUES(?,?,?,?,?,?,NULL,?,0)', (tid, number, task['context'], task['revision'], candidate['goal'], sha, 'submitted'))
        store.event(db, tid, 'flow-review-requested', {'round': number, 'candidate': sha, 'context': task['context']}, channel='agent')
    render_board(store, tid)
    return {'round': number, 'candidate': sha, 'status': 'awaiting-review'}


def review_failure(store, tid, number, reason):
    if not reason.strip():
        raise FlowError('Record the actual review failure')
    with store.db() as db:
        row = last_round(db, tid)
        if not row or row['number'] != number or row['status'] != 'submitted':
            raise FlowError('No such pending review')
        db.execute('UPDATE flow_rounds SET failures=failures+1 WHERE task=? AND number=?', (tid, number))
        store.event(db, tid, 'flow-review-failed', {'round': number, 'reason': reason})
    render_board(store, tid)
    return {'status': 'review-failed', 'round': number}


def review(store, tid, value):
    """Invalid reviewer output is an attempt, never implicit acceptance."""
    decision = next_step(store, tid)
    if decision['action'] != 'review':
        raise FlowError('No current review request')
    try:
        return _review(store, tid, value, decision)
    except (ValueError, KeyError, TypeError, AttributeError) as exc:
        # Do not count an old result against a different concurrently submitted round.
        with store.db() as db:
            current = last_round(db, tid)
        if current and current['number'] == decision['round'] and current['status'] == 'submitted':
            review_failure(store, tid, decision['round'], str(exc))
        raise FlowError(str(exc)) from exc


def _review(store, tid, value, decision):
    fields = {'round', 'candidate', 'goal', 'context', 'reviewer', 'verdict', 'summary', 'findings', 'acceptance', 'progress', 'full_alignment', 'evidence'}
    if set(value) != fields:
        raise FlowError('Review must follow the complete structured contract; empty/partial output is not a pass')
    candidate = artifact_json(store, decision['candidate'])
    if any(value[k] != decision[k] for k in ('round', 'candidate', 'goal', 'context')):
        raise FlowError('Review refers to a different round/goal/context')
    if not value['reviewer'].strip() or value['reviewer'] == candidate['author'] or not value['summary'].strip():
        raise FlowError('Require a separate reviewer identity and a substantive review')
    if value['verdict'] not in {'accept', 'revise', 'blocked'} or value['progress'] not in {'advanced', 'stalled', 'regressed'}:
        raise FlowError('Invalid review verdict/progress')
    if type(value['full_alignment']) is not bool or decision['full_alignment_required'] and not value['full_alignment']:
        raise FlowError('This boundary requires review against the complete goal')
    with store.db() as db:
        criteria = get_flow(db, tid)['plan']['acceptance']
    if set(value['acceptance']) != set(criteria) or any(v not in {'met', 'pending'} for v in value['acceptance'].values()):
        raise FlowError('Review every named acceptance criterion without weakening the goal')
    if not isinstance(value['findings'], list) or any(not isinstance(f, dict) or f.get('severity') not in {'blocking', 'followup'} or not f.get('detail') for f in value['findings']):
        raise FlowError('Findings require severity and actionable details')
    if not isinstance(value['evidence'], list) or not value['evidence']:
        raise FlowError('Review needs evidence, not only a completion marker')
    for sha in value['evidence']:
        store.artifact(sha)
    if value['verdict'] == 'accept' and (any(f['severity'] == 'blocking' for f in value['findings']) or candidate['target'] == 'completed' and 'pending' in value['acceptance'].values()):
        raise FlowError('Blocking findings or unfinished final criteria prohibit acceptance')
    sha = retain(store, value)
    with store.db() as db:
        db.execute('BEGIN IMMEDIATE')
        row = last_round(db, tid)
        task = store.task(tid)
        if not row or row['candidate'] != decision['candidate'] or row['status'] != 'submitted' or row['revision'] != task['revision'] or get_flow(db, tid)['goal'] != value['goal']:
            raise FlowError('Review request changed while reviewing')
        status = 'accepted' if value['verdict'] == 'accept' else value['verdict']
        db.execute('UPDATE flow_rounds SET review=?,status=? WHERE task=? AND number=?', (sha, status, tid, row['number']))
        store.event(db, tid, 'flow-reviewed', {'round': row['number'], 'review': sha, 'verdict': value['verdict']})
    render_board(store, tid)
    return {'round': value['round'], 'status': status, 'review': sha}


def guard_transition(store, db, task, destination):
    flow = get_flow(db, task['id'])
    if not flow or destination in {'prepared', 'paused', 'blocked', 'failed', 'cancelled'}:
        return
    row = last_round(db, task['id'])
    reasons = blockers(db, task['id'], task, flow)
    if db.execute("SELECT 1 FROM operations WHERE task=? AND status IN ('started','unknown')", (task['id'],)).fetchone():
        reasons.append('reconcile-unresolved-execution')
    if not row or row['status'] != 'accepted' or row['context'] != task['context'] or row['goal'] != flow['goal'] or row['revision'] != task['revision']:
        reasons.append('current-independent-review-required')
    else:
        candidate = artifact_json(store, row['candidate'])
        if candidate['target'] != destination:
            reasons.append('review-target-mismatch')
        # A sqlite row from Store.transition has a JSON spec; keep the gate shared.
        task = {**task, 'spec': json.loads(task['spec']) if isinstance(task['spec'], str) else task['spec']}
        reasons += gate(store, db, task, candidate)
    if reasons:
        raise FlowError('Flow transition blocked: ' + ', '.join(reasons))


def advance(store, tid):
    decision = next_step(store, tid)
    if decision['action'] != 'advance':
        raise FlowError('Cannot advance: ' + decision['action'] + ' ' + ', '.join(decision.get('reasons', [])))
    candidate = artifact_json(store, decision['candidate'])
    if candidate['target'] != 'iterate':
        store.transition(tid, candidate['target'])
    with store.db() as db:
        db.execute('BEGIN IMMEDIATE')
        if candidate['target'] == 'iterate':
            task = dict(db.execute('SELECT * FROM tasks WHERE id=?', (tid,)).fetchone())
            guard_transition(store, db, task, 'iterate')
        changed = db.execute("UPDATE flow_rounds SET status='advanced' WHERE task=? AND number=? AND status='accepted'", (tid, decision['round'])).rowcount
        if changed:
            current = store.task(tid)
            store.event(db, tid, 'flow-advanced', {'round': decision['round'], 'target': candidate['target'],
                'context_spec':current['spec']['context'],'evidence':[decision['candidate']]})
    from .experience import sync
    try:
        knowledge=sync(store,tid)
    except (OSError,ValueError) as exc:
        knowledge={'status':'pending','reason':type(exc).__name__,'resume':'experience-sync '+tid}
    render_board(store, tid)
    return {**next_step(store, tid),'knowledge':knowledge}


def guard_execution(store, tid, *, allow_parallel=False):
    with store.db() as db:
        flow = get_flow(db, tid)
    if flow:
        decision = next_step(store, tid)
        task=store.task(tid)
        with store.db() as db: reasons=blockers(db,tid,task,flow)
        if reasons or decision['action'] in {'human','completed','cancelled'} or decision['action']=='reconcile' and not allow_parallel:
            raise FlowError('Resolve flow decision before more execution: ' + decision['action'] + ' ' + ', '.join(decision.get('reasons', [])))


def render_board(store, tid):
    task = store.task(tid)
    with store.db() as db:
        flow = get_flow(db, tid)
        if not flow:
            raise FlowError('Start the collaborative flow first')
        rounds = [dict(x) for x in db.execute('SELECT * FROM flow_rounds WHERE task=? ORDER BY number', (tid,))]
        guidance = [dict(x) for x in db.execute("SELECT * FROM flow_guidance WHERE task=? AND status!='template' ORDER BY created", (tid,))]
        questions = [dict(x) for x in db.execute('SELECT * FROM flow_questions WHERE task=?', (tid,))]
        reports = [dict(x) for x in db.execute('SELECT kind,result,artifact,created FROM reports WHERE task=? AND context=?', (tid, task['context']))]
        events = [dict(x) for x in db.execute('SELECT kind,payload,created FROM events WHERE task=? ORDER BY seq DESC LIMIT 12', (tid,))]
    directory, board, human = board_paths(store, tid)
    def link(sha):
        return f'[{sha[:12]}](../../objects/{sha[:2]}/{sha})'
    lines = ['# HCU-TrainFlow collaboration board', '', task['spec']['objective'], '',
             f"Updated: {utc()} · State: **{task['state']}** · Mode: {task['spec']['mode']}",
             f"Context: `{task['context']}` · Goal: {link(flow['goal'])}", '',
             'Write comments in [GUIDANCE.md](GUIDANCE.md). This board is generated; guidance is never overwritten.',
             'Local tests, source inspection and real HCU validation are separate evidence scopes.', '', '## Acceptance', '']
    lines += [f'- **{key}**: {text}' for key, text in flow['plan']['acceptance'].items()]
    lines += ['', '## Questions', '']
    for row in questions:
        q = json.loads(row['payload'])
        lines += [f"### {q['id']} · {row['status']} · {'blocking' if q['blocking'] else 'advisory'}", '', q['title'], '', q['body'], '']
        if row['resolution']:
            lines += ['Resolution: ' + json.loads(row['resolution'])['note'], '']
    lines += ['', '## Human guidance and responses', '']
    lines += [f"- {link(x['id'])} · **{x['status']}** · {x['note'] or 'Awaiting agent response'}" for x in guidance]
    lines += ['', '## Iteration and independent review', '']
    for row in rounds:
        c = artifact_json(store, row['candidate'])
        lines += [f"### Round {row['number']} · {row['status']} · target {c['target']}", '', c['summary'], '',
                  f"Candidate {link(row['candidate'])} · snapshot {link(c['snapshot'])} · review {link(row['review']) if row['review'] else 'pending'} · review failures: {row['failures']}", '']
        if row['review']:
            review = artifact_json(store, row['review'])
            lines += [review['summary'], ''] + [f"- {f['severity']}: {f['detail']}" for f in review['findings']]
    lines += ['', '## Current evidence', ''] + [f"- {r['kind']}: {r['result']} · {link(r['artifact'])}" for r in reports]
    lines += ['', '## Recent progress and incidents', ''] + [f"- {e['created']} · {e['kind']} · `{e['payload']}`" for e in reversed(events)]
    from .team import schedule, messages
    team=schedule(store,tid)
    lines += ['', '## Agent work and dependencies', '', f"Parallel slots: {team['max_parallel']} · Ready: {', '.join(team['dispatchable']) or 'none'}", '']
    for item in team['assignments']:
        lines += [f"- **{item['id']}** · {item['owner']} · {item['status']} · stale={item['stale']} · depends on {', '.join(item['depends_on']) or 'none'}: {item['goal']}"]
        run=item['run']
        if run:lines += [f"  - Session: {run['session'] or 'not bound'} · token {run['token']} · result {link(run['report']) if run['report'] else 'pending'}"]
    lines += ['', '## Agent questions and findings', '']
    for item in messages(store,tid):
        m=item['message']
        lines += [f"- **{item['id']}** · {m['sender']} → {m['recipient']} · {m['kind']} / {item['status']} · stale={item['stale']}: {m['body']}"]
    atomic_write(board, '\n'.join(lines) + '\n')
    return {'board': str(board), 'guidance': str(human), 'task': tid}
