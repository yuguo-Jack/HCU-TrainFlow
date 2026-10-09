"""Private, evidence-bound training experience Wiki, replayable from milestones."""
import contextlib
import json
import math
from pathlib import Path
import sqlite3
from urllib.parse import urlsplit

from .core import FlowError, atomic_write, digest, fingerprint, safe_id, utc, write_json, read_json
from .wiki import terms


def schema(store):
    with store.db() as db:
        db.executescript('''
        CREATE TABLE IF NOT EXISTS experiences(id TEXT PRIMARY KEY,task TEXT,context TEXT,model TEXT,environment TEXT,
          kind TEXT,outcome TEXT,artifact TEXT,created TEXT);
        CREATE VIRTUAL TABLE IF NOT EXISTS experience_fts USING fts5(id UNINDEXED,body);
        CREATE TABLE IF NOT EXISTS experience_events(event TEXT PRIMARY KEY,experience TEXT);
        ''')


def label(value):
    return value if isinstance(value,str) else json.dumps(value,ensure_ascii=False,sort_keys=True)


def save(store, document, event=None):
    schema(store)
    ident=fingerprint(document)
    if fingerprint(document['context_spec'])!=document['context']:
        raise FlowError('Experience context fingerprint mismatch')
    raw=json.dumps(document,ensure_ascii=False,sort_keys=True,allow_nan=False).encode()
    sha=store.put(raw) # Always private; public visibility is never inferred from a result.
    write_json(store.root/'experience/records'/f'{ident}.json',document)
    context=document['context_spec']
    model=label(context.get('model','unknown'))
    environment=label(context.get('environment','unknown'))
    with store.db() as db:
        db.execute('BEGIN IMMEDIATE')
        exists=db.execute('SELECT id FROM experiences WHERE id=?',(ident,)).fetchone()
        if not exists:
            db.execute('INSERT INTO experiences VALUES(?,?,?,?,?,?,?,?,?)',
                       (ident,document['task'],document['context'],model,environment,document['kind'],document['outcome'],sha,document['created_at']))
            db.execute('INSERT INTO experience_fts(id,body) VALUES(?,?)',(ident,' '.join(terms(raw.decode()))))
        if event:db.execute('INSERT OR IGNORE INTO experience_events VALUES(?,?)',(event,ident))
    body='# '+document['summary']+'\n\n'
    body+=f'Private training experience · {document["kind"]} · {document["outcome"]}\n\n'
    body+='## Environment, model and source identity\n\n```json\n'+json.dumps(context,indent=2,ensure_ascii=False)+'\n```\n\n'
    body+='## Observation and interpretation\n\n'+document.get('interpretation','Automatic milestone capture; evidence still requires interpretation.')+'\n\n'
    body+='## Measurements and numerical validation\n\n```json\n'+json.dumps({'metrics':document.get('metrics',[]),'loss':document.get('loss',{'status':'not-recorded'})},indent=2,ensure_ascii=False)+'\n```\n\n'
    body+='## Evidence\n\n'+'\n'.join(f'- [{e}](../../objects/{e[:2]}/{e})' for e in document['evidence'])+'\n\n'
    body+='## Complete record\n\n'+f'[Immutable record](../../objects/{sha[:2]}/{sha})\n\n'
    body+='Cross-environment retrieval is a reference, not proof of portability. Revalidate on the actual model, data, precision and topology. Missing loss data is not a pass.\n'
    page=store.root/'experience/pages'/f'{ident}.md'
    atomic_write(page,body)
    with store.db() as db:
        rows=db.execute('SELECT id,task,model,environment,kind,outcome,created FROM experiences ORDER BY created DESC').fetchall()
    index='# Private training experience Wiki\n\nReports, interpreted milestones and Cookbook delivery records are separate evidence types.\n\n'
    index+='\n'.join(f'- [{r["task"]} / {r["kind"]} / {r["outcome"]}](pages/{r["id"]}.md) · model `{r["model"]}` · environment `{r["environment"]}`' for r in rows)+'\n'
    atomic_write(store.root/'experience/INDEX.md',index)
    return {'id':ident,'artifact':sha,'page':str(page),'visibility':'private','status':'recorded'}


def sync(store, tid=None):
    """Replay all eligible milestones, preserving their original context and evidence."""
    schema(store)
    recorded=[]; skipped=[]
    with store.db() as db:
        events=[dict(r) for r in db.execute("SELECT * FROM events WHERE kind IN ('report-recorded','flow-advanced') ORDER BY seq")]
    for event in events:
        if tid and event['task']!=tid:continue
        with store.db() as db:
            prior=db.execute('SELECT experience FROM experience_events WHERE event=?',(event['event_id'],)).fetchone()
        if prior and (store.root/'experience/pages'/f'{prior[0]}.md').exists():continue
        value=json.loads(event['payload'])
        spec=value.get('context_spec')
        if not spec:
            skipped.append({'event':event['event_id'],'reason':'Historical event lacks context snapshot; do not relabel it with current environment.'})
            continue
        evidence=value.get('evidence') or ([value['artifact']] if value.get('artifact') else [])
        if not evidence:continue
        for sha in evidence:store.artifact(sha)
        document={'schema_version':1,'task':event['task'],'milestone':event['event_id'],
                  'context':fingerprint(spec),'context_spec':spec,'kind':value.get('kind','workflow-milestone'),
                  'summary':f'{event["task"]}: {value.get("kind",value.get("target","milestone"))}',
                  'outcome':value.get('status','observed'),'evidence':evidence,'created_at':event['created'],
                  'loss':{'status':'not-recorded'},'metrics':[], 'automatic':True}
        # Retain report payload, but do not turn an arbitrary PASS into stage loss validation.
        if value.get('artifact'):
            report=json.loads(store.artifact(value['artifact']))
            document['report']=report
            if value.get('kind')=='stage-quality':
                document['loss']={'status':report['status'],'report':value['artifact'],'scope':'stage-quality'}
        recorded.append(save(store,document,event['event_id']))
    return {'status':'complete','records':len(recorded),'skipped':skipped,'visibility':'private'}


def rebuild(store):
    schema(store)
    documents=[]
    for path in (store.root/'experience/records').glob('*.json'):
        record=read_json(path)
        if fingerprint(record)!=path.stem:raise FlowError('Experience record changed: '+path.name)
        for sha in record['evidence']:store.artifact(sha)
        documents.append(record)
    # Validate everything before replacing the rebuildable index.
    with store.db() as db:
        db.execute('DELETE FROM experience_fts');db.execute('DELETE FROM experiences')
    for record in documents:save(store,record)
    return {'status':'complete','records':len(documents),'visibility':'private'}


def record(store, tid, value):
    task=store.task(tid)
    required={'milestone','kind','summary','outcome','evidence'}
    if not required<=set(value):raise FlowError('Experience needs milestone/kind/summary/outcome/evidence')
    if value.get('context')!=task['context']:raise FlowError('Experience context differs from current task')
    safe_id(value['milestone'])
    if not isinstance(value['summary'],str) or not value['summary'].strip():raise FlowError('Experience requires a summary')
    if value['outcome'] not in {'observed','accepted','rejected','incomplete'}:raise FlowError('Invalid experience outcome')
    if value['kind'] not in {'environment','baseline','performance','numerical','diagnosis','scale','optimization','cookbook','completion'}:
        raise FlowError('Invalid experience kind')
    if not isinstance(value['evidence'],list) or not value['evidence']:raise FlowError('Experience needs retained evidence')
    for sha in value['evidence']:store.artifact(sha)
    metrics=value.get('metrics',[])
    if not isinstance(metrics,list):raise FlowError('Metrics must be a list')
    for metric in metrics:
        if not all(metric.get(k) for k in ('name','unit','scope','aggregation','evidence','measurement_window')):
            raise FlowError('Metric requires name/unit/scope/aggregation/window/evidence')
        number=metric.get('value')
        if isinstance(number,bool) or not isinstance(number,(int,float)) or not math.isfinite(number):raise FlowError('Metric must be finite')
        if metric['evidence'] not in value['evidence']:raise FlowError('Metric evidence must be retained in record')
    loss=value.get('loss',{'status':'not-run'})
    if loss.get('status') not in {'not-run','pass','fail','incomplete'}:raise FlowError('Invalid loss state')
    if loss['status']!='not-run':
        report_id=loss.get('report')
        if report_id not in value['evidence']:raise FlowError('Loss requires retained report evidence')
        report=json.loads(store.artifact(report_id))
        if report.get('context')!=task['context'] or report.get('status')!=loss['status']:
            raise FlowError('Loss report context/status mismatch')
        if loss['status']=='pass' and (not isinstance(report.get('executed'),int) or isinstance(report.get('executed'),bool)
                                      or report['executed']<=0 or report.get('failures') or report.get('required_missing') or report.get('skipped_required')):
            raise FlowError('Loss pass requires executed validation and required coverage')
        if loss.get('scope') not in {'operator','short-run','stage'}:raise FlowError('Record numerical validation scope')
    baseline=value.get('baseline')
    if baseline:
        prior=get(store,baseline)['record']
        comparison=value.get('comparison') or {}
        if not comparison.get('controlled_variables') or not comparison.get('changed_variables') or not comparison.get('limitations'):
            raise FlowError('Baseline comparison requires controlled/changed variables and limitations')
        if prior['context']!=task['context'] and not comparison.get('context_difference'):
            raise FlowError('Cross-context comparison must explain environment/model/source differences')
    if value['kind']=='cookbook':
        delivery=value.get('delivery',{})
        if delivery.get('status') not in {'draft','submitted','merged','rejected','superseded'}:
            raise FlowError('Cookbook delivery status required')
        if not delivery.get('experience_ids'):raise FlowError('Cookbook must link the underlying experience records')
        for ident in delivery['experience_ids']:get(store,ident)
        if delivery['status'] in {'submitted','merged'}:
            url=urlsplit(delivery.get('url',''))
            if url.scheme not in {'http','https'} or not url.netloc or url.username:raise FlowError('Submitted cookbook needs canonical PR URL')
        if delivery.get('public') and not delivery.get('redaction_review'):
            raise FlowError('Public cookbook needs an explicit redaction review; record does not publish data')
    document={**value,'schema_version':1,'task':tid,'context_spec':task['spec']['context'],
              'loss':loss,'metrics':metrics,'created_at':utc(),'automatic':False}
    schema(store)
    event='manual:'+fingerprint([tid,value])
    with store.db() as db:prior=db.execute('SELECT experience FROM experience_events WHERE event=?',(event,)).fetchone()
    if prior:
        old=get(store,prior[0])
        return save(store,old['record'],event)
    return save(store,document,event)


def get(store, ident):
    schema(store)
    with store.db() as db:row=db.execute('SELECT * FROM experiences WHERE id=?',(ident,)).fetchone()
    if not row:raise FlowError('Unknown experience ID')
    result=dict(row);result['record']=json.loads(store.artifact(row['artifact']))
    return result


def search(store, query, limit=10, model=None, environment=None, kind=None, context=None):
    schema(store)
    if not 1<=limit<=100:raise FlowError('limit must be 1..100')
    tokens=terms(query)
    if not tokens:return {'results':[],'visibility':'private'}
    expression=' OR '.join('"'+t.replace('"','""')+'"' for t in tokens[:50])
    conditions=['experience_fts MATCH ?'];args=[expression]
    for name,value in [('model',model),('environment',environment),('kind',kind)]:
        if value:conditions.append('e.'+name+'=?');args.append(value)
    with store.db() as db:
        rows=db.execute('SELECT e.*,bm25(experience_fts) score FROM experience_fts JOIN experiences e ON experience_fts.id=e.id WHERE '+' AND '.join(conditions)+' ORDER BY score LIMIT ?',args+[limit]).fetchall()
    results=[]
    for row in rows:
        record=json.loads(store.artifact(row['artifact']))
        results.append({**dict(row),'summary':record['summary'],'loss':record.get('loss'),'metrics':record.get('metrics',[]),
                        'context_match':None if context is None else row['context']==context,
                        'reuse':'candidate-reference; validate in target environment',
                        'page':str(store.root/'experience/pages'/f'{row["id"]}.md')})
    return {'results':results,'visibility':'private','instruction':'Compare model/data/precision/parallelism/topology and measurement windows. Rejected attempts are useful negative evidence, not recommended configurations.'}


def compare(store, left, right):
    a=get(store,left)['record'];b=get(store,right)['record']
    diffs={k:{'left':a['context_spec'].get(k),'right':b['context_spec'].get(k)} for k in a['context_spec'].keys()|b['context_spec'].keys()
           if a['context_spec'].get(k)!=b['context_spec'].get(k)}
    return {'left':left,'right':right,'context_differences':diffs,'metrics':{'left':a.get('metrics',[]),'right':b.get('metrics',[])},
            'loss':{'left':a.get('loss'),'right':b.get('loss')},
            'automatic_speedup':None,'instruction':'Review measurement scope, units, windows and controlled variables before computing a comparable speedup.'}
