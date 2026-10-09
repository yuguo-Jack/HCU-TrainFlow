"""Synthetic protocol fixtures; numbers are not HCU hardware specifications."""
import copy
import json
import shutil
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

import pytest

from hcu_trainflow import reference_data as refs
from hcu_trainflow.core import FlowError, Store, fingerprint, write_json
from hcu_trainflow.delivery import export_public

TIME = datetime(2020, 1, 1, tzinfo=timezone.utc)


@pytest.fixture
def store(tmp_path):
    return Store(tmp_path/'private')


def measured(store, **changes):
    proof = store.put(b'Synthetic reference fixture; not an actual hardware measurement')
    return {'schema_version':1,'key':'fixture-memory-copy','title':'Synthetic memory copy fixture',
            'category':'performance','basis':'site-measurement',
            'scope':{'hardware':{'architecture':'gfx-fixture'},'software':{'build':'fixture-runtime-sha'},
                     'topology':{'nodes':1,'devices':1},'workload':{'shape':[1024], 'dtype':'fp32'},
                     'environment':{'id':'fixture-site'}},
            'value':10.0,'unit':'GB/s','statistic':'median',
            'method':{'id':'copy-fixture','revision':'fixture-v1','description':'Synthetic timing protocol, one device, fixed byte definition'},
            'observed_at':TIME.isoformat(),'reviewed_at':(TIME+timedelta(seconds=1)).isoformat(),
            'reviewer':'fixture-reviewer','sources':[{'id':'fixture-source','uri':'https://example.invalid/reference',
               'revision':'fixture-report-sha','retrieved_at':TIME.isoformat(),'evidence':[proof]}],
            'evidence':[proof],'freshness':{'mode':'age','max_age_seconds':100,'update_due':(TIME+timedelta(seconds=80)).isoformat()},
            'limitations':'Synthetic unit-test fixture only; no acceptance claim.', **changes}


def nominal(store):
    value = measured(store)
    value.update(category='hardware',basis='nominal',statistic='nominal',scope={'hardware':{'architecture':'gfx-fixture','product':'synthetic-product'}},
                 freshness={'mode':'source-revision'})
    value.pop('observed_at')
    return value


def target(value, **changes):
    return {'key':value['key'],'scope':copy.deepcopy(value['scope']), 'unit':value['unit'],
            'statistic':value['statistic'],'method':{k:value['method'][k] for k in ('id','revision')}, **changes}


def test_exact_scope_reuse_preserves_original_provenance_and_units(store):
    value=measured(store); ident=refs.record(store,value)['id']
    result=refs.query(store,target(value),now=TIME+timedelta(seconds=5))
    assert result['status']=='compatible' and result['reusable_ids']==[ident]
    assert result['environment_pass'] is False
    assert result['results'][0]['record']==value
    assert result['results'][0]['source_currentness'].startswith('fixed-source')
    assert refs.record(Store(store.root),value)['id']==ident
    assert len([e for e in store.events() if e['kind']=='reference-recorded'])==1


def test_age_is_anchored_to_observation_and_due_boundary_is_stale(store):
    value=measured(store,reviewed_at=(TIME+timedelta(seconds=70)).isoformat())
    refs.record(store,value)
    assert refs.query(store,target(value),now=TIME+timedelta(seconds=79))['status']=='compatible'
    result=refs.query(store,target(value),now=TIME+timedelta(seconds=80))
    assert result['status']=='stale' and result['refresh_recommended'] and not result['reusable_ids']
    value['reviewed_at']=(TIME+timedelta(seconds=110)).isoformat()
    value['freshness']['update_due']=(TIME+timedelta(days=10)).isoformat()
    changed=refs.record(store,value)['id']
    result=refs.query(store,target(value),now=TIME+timedelta(seconds=111))
    assert next(x for x in result['results'] if x['id']==changed)['status']=='stale'


def test_stable_revision_fact_needs_no_arbitrary_expiry_but_revision_change_refreshes(store):
    value=nominal(store); ident=refs.record(store,value)['id']
    request={'key':value['key'],'scope':value['scope']}
    result=refs.query(store,request,now=TIME+timedelta(days=1000))
    assert result['reusable_ids']==[ident] and result['results'][0]['effective_update_due'] is None
    request['source_revisions']={'fixture-source':'new-known-report-sha'}
    assert refs.query(store,request,now=TIME+timedelta(days=1000))['status']=='stale'


@pytest.mark.parametrize('change,expected', [
    ({'scope':{'hardware':{'architecture':'different-gfx'}}},'mismatched'),
    ({'scope':{'hardware':{'architecture':'gfx-fixture'}}},'missing'),
    ({'unit':'GiB/s'},'mismatched'),
    ({'statistic':'p95'},'mismatched'),
    ({'method':{'id':'copy-fixture','revision':'different'}},'mismatched')])
def test_scope_unit_statistic_and_protocol_are_not_fuzzy_inferred(store,change,expected):
    value=measured(store); refs.record(store,value)
    result=refs.query(store,target(value,**change),now=TIME+timedelta(seconds=5))
    assert result['status']==expected and not result['reusable_ids']
    assert result['refresh_recommended']


def test_missing_method_and_bool_integer_identity_do_not_match(store):
    value=measured(store); refs.record(store,value)
    request=target(value); request.pop('method')
    result=refs.query(store,request,now=TIME+timedelta(seconds=5))
    assert result['status']=='missing' and 'method' in result['results'][0]['missing']
    request=target(value); request['scope']['topology']['nodes']=True
    assert refs.query(store,request,now=TIME+timedelta(seconds=5))['status']=='mismatched'


def test_nominal_historical_and_site_values_do_not_merge(store):
    site=measured(store)
    historical={**copy.deepcopy(site),'basis':'historical-measurement'}
    historical['scope'].pop('environment')
    ids={row['basis']:refs.record(store,row)['id'] for row in [nominal(store),site,historical]}
    result=refs.query(store,target(site,basis='site-measurement'),now=TIME+timedelta(seconds=5))
    assert result['reusable_ids']==[ids['site-measurement']]
    assert len(result['results'])==3 and len({r['record']['basis'] for r in result['results']})==3


def test_conflicts_retained_until_explicit_same_family_supersession(store):
    value=measured(store); first=refs.record(store,value)['id']
    second=refs.record(store,{**value,'value':20.0})['id']
    result=refs.query(store,target(value),now=TIME+timedelta(seconds=5))
    assert result['selection_status']=='conflict' and result['reusable_ids']==[]
    assert all(r['conflicts'] for r in result['results'])
    third=refs.record(store,{**value,'value':15.0,'supersedes':[first,second]})['id']
    result=refs.query(store,target(value),now=TIME+timedelta(seconds=5))
    assert result['reusable_ids']==[third]
    assert result['refresh_recommended'] is False
    assert len(result['results'])==3
    assert all('superseded' in r['stale'] for r in result['results'] if r['id']!=third)


def test_different_architecture_cannot_supersede_old_scope(store):
    value=measured(store); first=refs.record(store,value)['id']
    changed=copy.deepcopy(value); changed['scope']['hardware']['architecture']='new-gfx'
    changed['supersedes']=[first]
    with pytest.raises(FlowError,match='Supersedes'):
        refs.record(store,changed)
    assert refs.rebuild(store)['records']==1


@pytest.mark.parametrize('value',[True,float('nan'),float('inf'),-1,10**400])
def test_invalid_numeric_performance_is_not_reference_evidence(store,value):
    with pytest.raises(FlowError,match='finite nonnegative'):
        refs.record(store,measured(store,value=value))


def test_measurements_require_shape_software_freshness_and_original_sources(store):
    initial=measured(store)
    mutations=[lambda v:v['scope'].pop('software'),lambda v:v['scope']['workload'].pop('shape'),
               lambda v:v.update(freshness={'mode':'source-revision'}),
               lambda v:v['sources'][0].update(evidence=[]),lambda v:v['sources'][0].update(revision='main'),
               lambda v:v['sources'][0].update(uri='https://secret:password@example.invalid/file'),
               lambda v:v['scope']['hardware'].update(architecture='unknown'),
               lambda v:v.update(reviewed_at=(datetime.now(timezone.utc)+timedelta(days=1)).isoformat())]
    for mutation in mutations:
        value=copy.deepcopy(initial); mutation(value)
        with pytest.raises(FlowError): refs.record(store,value)


def test_portable_records_rebuild_pages_and_detect_tamper_before_replacing_index(store,tmp_path):
    value=measured(store); ident=refs.record(store,value)['id']
    destination=tmp_path/'restored'; shutil.copytree(store.root,destination)
    restored=Store(destination)
    page=destination/'experience/references/pages'/f'{ident}.md'; page.unlink()
    assert refs.rebuild(restored)['records']==1 and page.exists()
    assert refs.query(restored,target(value),now=TIME+timedelta(seconds=5))['reusable_ids']==[ident]
    path=destination/'experience/references/records'/f'{ident}.json'
    bad=copy.deepcopy(value); bad['value']=999; write_json(path,bad)
    index=destination/'experience/references/INDEX.md'; previous=index.read_bytes()
    with pytest.raises(FlowError,match='changed'): refs.rebuild(restored)
    assert index.read_bytes()==previous


def test_missing_source_evidence_rejects_query(store):
    value=measured(store); refs.record(store,value)
    sha=value['evidence'][0]
    (store.root/'objects'/sha[:2]/sha).unlink()
    with pytest.raises((FlowError,FileNotFoundError)):
        refs.query(store,target(value))


def test_concurrent_records_and_interrupted_publication_are_recoverable(store,monkeypatch):
    value=nominal(store)
    with ThreadPoolExecutor(max_workers=3) as pool:
        ids=list(pool.map(lambda _:refs.record(store,value)['id'],range(6)))
    assert len(set(ids))==1 and refs.rebuild(store)['records']==1
    original=refs._publish
    def fail(*args): raise OSError('synthetic derived-page failure')
    monkeypatch.setattr(refs,'_publish',fail)
    second={**value,'key':'other-fixture'}
    with pytest.raises(OSError): refs.record(store,second)
    monkeypatch.setattr(refs,'_publish',original)
    assert refs.rebuild(Store(store.root))['records']==2
    assert refs.record(store,second)['id']==fingerprint(second)


def test_experience_link_uses_existing_artifacts_without_nested_write_deadlock(store):
    from hcu_trainflow import experience
    task=store.create({'schema_version':1,'task_id':'t','mode':'analyze','objective':'Synthetic fixture','context':{'source':'fixture'}})
    value=measured(store)
    prior=experience.record(store,'t',{'context':task['context'],'milestone':'fixture','kind':'baseline',
        'summary':'Synthetic observation','outcome':'observed','evidence':value['evidence']})
    value['experience_ids']=[prior['id']]
    assert refs.record(store,value)['status']=='recorded'
    assert refs.rebuild(store)['records']==1


def test_reference_pages_remain_inside_existing_private_export_boundary(store,tmp_path):
    value=nominal(store); ident=refs.record(store,value)['id']
    relative=f'experience/references/pages/{ident}.md'
    from hcu_trainflow.core import digest
    manifest={'reviewed_by':'fixture-reviewer','files':[{'path':relative,'sha256':digest((store.root/relative).read_bytes())}]}
    with pytest.raises(FlowError,match='Private'):
        export_public(store.root,tmp_path/'public',manifest)


def test_three_cli_commands_are_sufficient(store,tmp_path,capsys):
    from hcu_trainflow.cli import main
    value=nominal(store); source=tmp_path/'record.json'; write_json(source,value)
    request=tmp_path/'query.json'; write_json(request,{'key':value['key'],'scope':value['scope']})
    args=['--workspace',str(store.root)]
    assert main(args+['reference-record',str(source)])==0
    ident=json.loads(capsys.readouterr().out)['id']
    assert main(args+['reference-query',str(request)])==0
    assert json.loads(capsys.readouterr().out)['reusable_ids']==[ident]
    assert main(args+['reference-index'])==0
    assert json.loads(capsys.readouterr().out)['records']==1


def test_environment_identity_and_missing_reference_never_silently_match(store):
    request={'key':'environment-image','scope':{'hardware':{'architecture':'gfx-fixture'}}}
    missing=refs.query(store,request,now=TIME)
    assert missing['status']=='missing' and missing['refresh_recommended']
    value=measured(store,key='environment-image',category='environment',basis='documented',
                   statistic='documented',value='fixture-content-digest',unit='image-digest')
    ident=refs.record(store,value)['id']
    result=refs.query(store,target(value),now=TIME+timedelta(seconds=5))
    assert result['reusable_ids']==[ident]
    changed=target(value); changed['scope']['software']['build']='same-tag-but-different-image-content'
    assert refs.query(store,changed,now=TIME+timedelta(seconds=5))['status']=='mismatched'
    assert refs.query(store,target(value),now=TIME+timedelta(days=100))['status']=='stale'


def test_shared_large_source_is_verified_once_per_query_without_persistent_trust_cache(store,monkeypatch):
    first=nominal(store)
    refs.record(store,first); refs.record(store,{**first,'key':'another-key'})
    original=store.artifact
    calls=[]
    def counted(sha):
        calls.append(sha)
        return original(sha)
    monkeypatch.setattr(store,'artifact',counted)
    request={'key':first['key'],'scope':first['scope']}
    refs.query(store,request)
    assert calls.count(first['evidence'][0])==1
    refs.query(store,request)
    assert calls.count(first['evidence'][0])==2
