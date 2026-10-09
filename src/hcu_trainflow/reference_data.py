"""Private scoped reference facts and measurements, never environment PASS."""
import json
import math
from datetime import datetime, timezone
from urllib.parse import urlsplit

from .core import FlowError, atomic_write, fingerprint, read_json, safe_id, utc

CATEGORIES = {'hardware', 'environment', 'performance'}
BASES = {'documented', 'nominal', 'historical-measurement', 'site-measurement'}
DIMENSIONS = {'hardware', 'software', 'topology', 'workload', 'environment'}
UNKNOWN = {'unknown', 'any', '*', 'unspecified', 'latest', 'unversioned'}


def _text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise FlowError(field + ' must be a nonempty string')


def _moment(value):
    _text(value, 'timestamp')
    try:
        result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError as exc:
        raise FlowError('Use an ISO timestamp with an explicit timezone') from exc
    if result.tzinfo is None:
        raise FlowError('Timestamp timezone is required')
    return result.astimezone(timezone.utc)


def _finite(value):
    try:
        return not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(value)
    except OverflowError:
        return False


def _scope(value):
    if not isinstance(value, dict) or set(value)-DIMENSIONS:
        raise FlowError('Scope supports hardware/software/topology/workload/environment dimensions')
    def walk(item):
        if isinstance(item, dict):
            if not item or any(not isinstance(k, str) or not k for k in item):
                raise FlowError('Scope objects need named fields; omit independent dimensions')
            for child in item.values(): walk(child)
        elif isinstance(item, list):
            if not item: raise FlowError('Scope lists cannot be empty')
            for child in item: walk(child)
        elif item is None or isinstance(item, str) and (not item.strip() or item.strip().lower() in UNKNOWN):
            raise FlowError('Unknown/wildcard scope is not a reusable applicability contract')
        elif not isinstance(item, (str, bool)) and not _finite(item):
            raise FlowError('Scope must contain finite JSON values')
    for dimension in value.values():
        if not isinstance(dimension, dict): raise FlowError('Each scope dimension must be an object')
        walk(dimension)


def _validate(store, value, *, now=None, verified=None):
    verified = set() if verified is None else verified
    required = {'schema_version','key','title','category','basis','scope','value','unit','statistic',
                'method','reviewed_at','reviewer','sources','evidence','freshness','limitations'}
    optional = {'observed_at','supersedes','experience_ids'}
    if not isinstance(value, dict) or not required <= value.keys() or set(value)-(required|optional):
        raise FlowError('Reference needs the documented fields and no unknown fields')
    if type(value['schema_version']) is not int or value['schema_version'] != 1:
        raise FlowError('Unsupported reference schema')
    safe_id(value['key'])
    for name in ('title','category','basis','unit','statistic','reviewer','limitations'): _text(value[name], name)
    if value['category'] not in CATEGORIES or value['basis'] not in BASES:
        raise FlowError('Unknown reference category/basis')
    measured = value['basis'] in {'historical-measurement','site-measurement'}
    if value['category']=='performance' or value['basis']=='nominal':
        if not _finite(value['value']) or value['value'] < 0:
            raise FlowError('Performance/nominal values must be finite nonnegative numbers, not bool')
    elif not isinstance(value['value'], (str, bool)) and not _finite(value['value']):
        raise FlowError('Reference value must be a finite scalar fact')
    if isinstance(value['value'], str): _text(value['value'], 'value')
    if value['basis']=='nominal' and (value['category']!='hardware' or value['statistic']!='nominal'):
        raise FlowError('Nominal peaks are hardware references with statistic=nominal')
    if value['category']=='performance' and not measured:
        raise FlowError('Performance records require historical or site measurements; keep nominal peaks separate')
    if value['basis']=='documented' and value['statistic']!='documented':
        raise FlowError('Documented facts require statistic=documented')
    if measured and value['statistic'] not in {'single','mean','median','min','max','p50','p90','p95','p99'}:
        raise FlowError('Measurement requires an explicit supported statistic')
    _scope(value['scope'])
    hardware = value['scope'].get('hardware', {})
    _text(hardware.get('architecture'), 'scope.hardware.architecture')
    if value['basis']=='nominal':
        _text(hardware.get('product'), 'scope.hardware.product for nominal product specifications')
    if value['category']=='performance':
        if any(not value['scope'].get(k) for k in ('software','topology','workload')):
            raise FlowError('Performance scope needs software, topology and workload')
        if not all(k in value['scope']['workload'] for k in ('shape','dtype')):
            raise FlowError('Performance workload needs exact shape and dtype')
    if value['basis']=='site-measurement' or value['category']=='environment':
        if not value['scope'].get('environment') or not value['scope'].get('software'):
            raise FlowError('Site/environment references need environment and software identity')
    method = value['method']
    if not isinstance(method, dict) or set(method) != {'id','revision','description'}:
        raise FlowError('Method requires id, fixed revision and description')
    for key in method: _text(method[key], 'method.'+key)
    if method['revision'].strip().lower() in UNKNOWN|{'main','master','head'}:
        raise FlowError('Pin the method revision, not its moving branch')
    reviewed = _moment(value['reviewed_at'])
    if reviewed > (now or datetime.now(timezone.utc)):
        raise FlowError('Reviewed time cannot be in the future')
    observed = _moment(value['observed_at']) if 'observed_at' in value else None
    if observed and observed > reviewed:
        raise FlowError('Observed time must not follow review time')
    freshness = value['freshness']
    if not isinstance(freshness, dict): raise FlowError('Reference requires a freshness policy')
    if freshness.get('mode')=='source-revision':
        if set(freshness)!={'mode'} or value['category']!='hardware' or measured:
            raise FlowError('Only stable documented/nominal hardware facts may use revision freshness')
    elif freshness.get('mode')=='age':
        if set(freshness)!={'mode','max_age_seconds','update_due'} or not _finite(freshness['max_age_seconds']) or freshness['max_age_seconds']<=0:
            raise FlowError('Age freshness requires positive max_age_seconds and update_due')
        _moment(freshness['update_due'])
        if observed is None:
            raise FlowError('Age freshness must be anchored to observed_at, not a later reread')
    else:
        raise FlowError('Use source-revision or age freshness')
    evidence = value['evidence']
    if not isinstance(evidence, list) or not evidence or any(not isinstance(x,str) for x in evidence):
        raise FlowError('Reference needs retained evidence artifacts')
    for sha in evidence:
        if sha not in verified:
            store.artifact(sha); verified.add(sha)
    if not isinstance(value['sources'], list) or not value['sources']:
        raise FlowError('Reference needs original sources with fixed provenance')
    seen = set()
    for source in value['sources']:
        if not isinstance(source, dict) or set(source)!={'id','uri','revision','retrieved_at','evidence'}:
            raise FlowError('Source requires id/uri/revision/retrieved_at/evidence')
        safe_id(source['id'])
        if source['id'] in seen: raise FlowError('Source IDs must be unique')
        seen.add(source['id'])
        for key in ('uri','revision'): _text(source[key], 'source.'+key)
        if source['revision'].strip().lower() in UNKNOWN|{'main','master','head'}:
            raise FlowError('Source revision must be fixed; retain content hash for a latest URL')
        uri = urlsplit(source['uri'])
        if any(c.isspace() for c in source['uri']) or uri.scheme not in {'http','https','file','artifact'} or uri.username or uri.password or uri.scheme in {'http','https'} and not uri.netloc:
            raise FlowError('Use an original source URI without embedded credentials')
        if _moment(source['retrieved_at']) > reviewed:
            raise FlowError('Source retrieval must not follow review time')
        if not isinstance(source['evidence'], list) or not source['evidence'] or any(x not in evidence for x in source['evidence']):
            raise FlowError('Each source must reference evidence retained in this record')
    for name in ('supersedes','experience_ids'):
        if not isinstance(value.get(name, []), list) or any(not isinstance(x,str) for x in value.get(name, [])):
            raise FlowError(name + ' must be a list of fixed IDs')
    for ident in value.get('experience_ids', []):
        with store.db() as db:
            exists = db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='experiences'").fetchone()
            linked = db.execute('SELECT artifact FROM experiences WHERE id=?', (ident,)).fetchone() if exists else None
        if not linked: raise FlowError('Unknown linked experience ID')
        if linked['artifact'] not in verified:
            store.artifact(linked['artifact']); verified.add(linked['artifact'])
    return value


def _root(store):
    return store.root/'experience'/'references'


def _records(store):
    records, verified = {}, set()
    for path in sorted((_root(store)/'records').glob('*.json')):
        value = read_json(path)
        ident = fingerprint(value)
        if path.stem != ident or fingerprint(json.loads(store.artifact(ident))) != ident:
            raise FlowError('Reference record/artifact changed: '+path.name)
        _validate(store, value, verified=verified)
        records[ident] = value
    for ident, value in records.items():
        for prior in value.get('supersedes', []):
            if prior not in records or prior==ident:
                raise FlowError('Superseded reference is missing or self-referential')
            if _family(records[prior]) != _family(value):
                raise FlowError('Supersession must preserve exact key/basis/scope/unit/statistic/method; different scopes coexist')
    return records


def _family(value):
    return fingerprint({k:value[k] for k in ('key','category','basis','scope','unit','statistic')} |
                       {'method':{k:value['method'][k] for k in ('id','revision')}})


def _publish(store, records):
    root = _root(store)
    replaced = {sha for r in records.values() for sha in r.get('supersedes',[])}
    lines = ['# 私有硬件、环境与性能参考', '',
             '这些是带适用条件的参考值，不是当前环境通过证明；标称峰值、历史测量、现场测量分别保存。', '',
             '先用 reference-query 检查目标条件、来源版本和时效。页面为派生视图，records 和 objects 是长期原件。', '']
    for ident, value in sorted(records.items(), key=lambda item:(item[1]['key'],item[1]['reviewed_at']), reverse=True):
        body = '# '+value['title']+'\n\n'
        body += f"私有参考 · {value['category']} / {value['basis']} · {'已被替代' if ident in replaced else '保留中'}\n\n"
        body += f"值：`{value['value']}` · 单位：`{value['unit']}` · 统计：`{value['statistic']}`\n\n"
        body += '适用状态需要对目标条件实时查询，不由页面生成时间决定。\n\n'
        body += '## 适用条件与方法\n\n```json\n'+json.dumps({'scope':value['scope'],'method':value['method'],'observed_at':value.get('observed_at'),'reviewed_at':value['reviewed_at'],'freshness':value['freshness']},ensure_ascii=False,indent=2)+'\n```\n\n'
        body += '## 来源与边界\n\n'+value['limitations']+'\n\n'
        for source in value['sources']:
            body += '- ['+source['id']+'](<'+source['uri'].replace('>','%3E')+'>) · 固定版本 `'+source['revision']+'`\n'
        body += '\n'+ '\n'.join(f'- [原始证据 {sha[:12]}](../../../objects/{sha[:2]}/{sha})' for sha in value['evidence'])+'\n\n'
        body += f'[完整固定记录](../../../objects/{ident[:2]}/{ident})\n'
        atomic_write(root/'pages'/f'{ident}.md', body)
        lines.append(f"- [{value['key']} / {value['basis']} / {value['value']} {value['unit']}](pages/{ident}.md) · {'已替代' if ident in replaced else '保留'} · review {value['reviewed_at']}")
    atomic_write(root/'INDEX.md', '\n'.join(lines)+'\n')
    atomic_write(root/'README.md', '# 私有参考数据\n\n原始证据与不可变记录存放于 workspace/objects；records 为可移植记录，pages/INDEX 为可重建视图。备份整个私有 Store，不只复制索引。复用前运行 reference-query，缺项、过期、冲突和不同适用范围均需查证；不自动查询远端或更新 HCU-Knowledge。记录/检索/重建不会通过训练或健康门槛。\n')


def record(store, value):
    _validate(store, value)
    ident = fingerprint(value)
    # Same canonical input retries have the same immutable ID; no hidden now().
    artifact = store.put(json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False).encode())
    assert artifact == ident
    with store.db() as db:
        db.execute('BEGIN IMMEDIATE')
        records = _records(store)
        for prior in value.get('supersedes', []):
            if prior not in records or _family(records[prior]) != _family(value):
                raise FlowError('Supersedes must name an existing record with the same precise reference family')
            if _moment(value['reviewed_at']) < _moment(records[prior]['reviewed_at']):
                raise FlowError('A superseding review cannot be older than the replaced review')
        atomic_write(_root(store)/'records'/f'{ident}.json', json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2)+'\n')
        records[ident] = value
        store.event(db, None, 'reference-recorded', {'reference':ident,'basis':value['basis'],'key':value['key']}, event_id='reference:'+ident)
        _publish(store, records)
    return {'id':ident,'artifact':ident,'page':str(_root(store)/'pages'/f'{ident}.md'),'visibility':'private','status':'recorded'}


def rebuild(store):
    with store.db() as db:
        db.execute('BEGIN IMMEDIATE')
        records = _records(store)
        _publish(store, records)
    return {'status':'complete','records':len(records),'index':str(_root(store)/'INDEX.md'),'visibility':'private'}


def _match(required, actual, prefix, missing, mismatch):
    for key, value in required.items():
        name = prefix+'.'+key if prefix else key
        if key not in actual:
            missing.append(name)
        elif isinstance(value, dict):
            if not isinstance(actual[key],dict): mismatch.append(name)
            else: _match(value,actual[key],name,missing,mismatch)
        elif fingerprint(value) != fingerprint(actual[key]):
            mismatch.append(name)


def query(store, request, *, now=None):
    allowed = {'key','category','basis','scope','unit','statistic','method','source_revisions'}
    if not isinstance(request,dict) or not {'key','scope'}<=request.keys() or set(request)-allowed:
        raise FlowError('Query needs exact key and target scope; no natural-language inferred matching')
    safe_id(request['key']); _scope(request['scope'])
    for name in ('category','basis','unit','statistic'):
        if name in request: _text(request[name], name)
    if request.get('category') is not None and request['category'] not in CATEGORIES or request.get('basis') is not None and request['basis'] not in BASES:
        raise FlowError('Unknown query category/basis')
    revisions = request.get('source_revisions',{})
    if not isinstance(revisions,dict) or any(not isinstance(v,str) or not v for v in revisions.values()):
        raise FlowError('source_revisions must map source IDs to fixed revisions')
    if 'method' in request and (not isinstance(request['method'],dict) or set(request['method'])!={'id','revision'}):
        raise FlowError('Requested method must identify id and revision')
    records = _records(store)
    replaced = {sha for value in records.values() for sha in value.get('supersedes',[])}
    current = now or datetime.now(timezone.utc)
    results = []
    for ident, value in records.items():
        if value['key']!=request['key']: continue
        missing, mismatch, stale = [], [], []
        _match(value['scope'],request['scope'],'scope',missing,mismatch)
        for field in ('category','basis','unit','statistic'):
            if field in request and fingerprint(request[field])!=fingerprint(value[field]): mismatch.append(field)
        protocol = {k:value['method'][k] for k in ('id','revision')}
        if 'method' in request and fingerprint(request['method'])!=fingerprint(protocol): mismatch.append('method')
        if value['category']=='performance':
            missing += [field for field in ('unit','statistic','method') if field not in request]
        for source in value['sources']:
            if source['id'] in revisions and revisions[source['id']]!=source['revision']:
                stale.append('source-revision-changed:'+source['id'])
        freshness = value['freshness']
        due = None
        if freshness['mode']=='age':
            age = (current-_moment(value['observed_at'])).total_seconds()
            due = min(_moment(freshness['update_due']).timestamp(), _moment(value['observed_at']).timestamp()+freshness['max_age_seconds'])
            if current.timestamp()>=due: stale.append('measurement-age-or-update-due')
            if age<0: stale.append('observation-clock-in-future')
        if _moment(value['reviewed_at'])>current: stale.append('review-clock-in-future')
        if ident in replaced: stale.append('superseded')
        status = 'mismatched' if mismatch else 'missing' if missing else 'stale' if stale else 'compatible'
        results.append({'id':ident,'status':status,'missing':missing,'mismatched':mismatch,'stale':stale,
                        'effective_update_due':datetime.fromtimestamp(due,timezone.utc).isoformat() if due is not None else None,
                        'record':value,'page':str(_root(store)/'pages'/f'{ident}.md'),
                        'source_currentness':'fixed-source only; no online refresh performed','conflicts':[]})
    # Never silently choose between active, same-contract contradictory values.
    active = [r for r in results if r['status']=='compatible']
    for row in active:
        row['conflicts'] = [other['id'] for other in active if other['id']!=row['id'] and _family(other['record'])==_family(row['record']) and fingerprint(other['record']['value'])!=fingerprint(row['record']['value'])]
    usable = [r['id'] for r in active if not r['conflicts']]
    status = 'compatible' if active else 'stale' if any(r['status']=='stale' for r in results) else 'missing' if not results or any(r['status']=='missing' for r in results) else 'mismatched'
    action = ('reuse-fixed-reference' if usable else 'review-conflicting-evidence' if active else
              'refresh-source-or-measurement' if status=='stale' else
              'acquire-for-target-scope' if status=='mismatched' else 'complete-target-conditions-or-acquire')
    return {'status':status,'results':results,'reusable_ids':usable,'selection_status':'conflict' if active and not usable else 'available' if usable else 'unavailable',
            'refresh_recommended':not bool(usable),'next_action':action,
            'visibility':'private','environment_pass':False,
            'instruction':'Compatible means reference applicability only. Preserve basis/units/statistic/protocol; inspect conflicts, original evidence and limitations. Recheck missing/stale/changed scope; never treat historical/nominal values as current environment acceptance.'}
