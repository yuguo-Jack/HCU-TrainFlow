import copy
import hashlib
import json
from pathlib import Path

import pytest

from hcu_trainflow import capture_policy, official, wiki
from hcu_trainflow.core import FlowError, Store, read_json, write_json


A='a'*40
B='b'*40
ROOT='1'*40
CHILD='2'*40
OLD='c'*64
NEW='d'*64


def project(tmp_path, paths=None):
    root=tmp_path/'project'
    source={'id':'engine','repository':'org/engine','ref':'main','paths':paths or ['a.py'],
            'baseline_commit':A,'baseline_files':{'a.py':{'sha256':OLD}}}
    write_json(root/'knowledge/storage.json',{'profile':'discovery-first'})
    write_json(root/'knowledge/sources.json',[source])
    write_json(root/'knowledge/source-lock.json',{'files':[{'repo':'org/engine','commit':A,'ref':'main',
               'path':'a.py','sha256':OLD,'status':'collected'}]})
    return root


def api_at(commit):
    def api(repo,suffix,token=None):
        if suffix=='/commits/main':return {'sha':commit},''
        if not suffix:return {'private':False},''
        if suffix.startswith('/pulls?'):return [],''
        raise AssertionError('Unexpected source request: '+suffix)
    return api


def stage_for_apply(store,root,files=None,proofs=None):
    stage={'source':'engine','repository':'org/engine','ref':'main','commit':B,
           'files':files if files is not None else {'a.py':{'sha256':NEW}},'failures':[]}
    if proofs:stage['absence_proofs']=proofs
    write_json(store.root/'wiki/staging/apply1.json',stage)
    write_json(store.root/'wiki/reviews/apply1.json',{'page_hashes':{},'content_hashes':{},
               'decisions':{},'workflow_decisions':{}})
    write_json(store.root/'wiki/sources/engine.json',{'commit':B})


@pytest.mark.parametrize('change', ['repository', 'ref', 'paths', 'proof-repository'])
def test_lite_apply_rejects_stale_registration_and_foreign_absence_before_writes(tmp_path, change):
    root=project(tmp_path);store=Store(tmp_path/'private')
    if change=='proof-repository':
        proof={'kind':'fixed-complete-inventory-absence-v1','repository':'other/engine',
               'commit':B,'path':'a.py','complete':True,'inventory_artifact_sha256':'e'*64}
        stage_for_apply(store,root,files={},proofs={'a.py':proof})
    else:
        stage_for_apply(store,root)
        registry=read_json(root/'knowledge/sources.json')
        registry[0][change]={'repository':'other/engine','ref':'other','paths':['a.py','new.py']}[change]
        write_json(root/'knowledge/sources.json',registry)
    before={name:(root/'knowledge'/name).read_bytes() for name in ['sources.json','source-lock.json']}
    with pytest.raises(FlowError,match='registration changed|absence proof'):
        official.apply_refresh(store,root,'apply1')
    assert before=={name:(root/'knowledge'/name).read_bytes() for name in before}


def test_new_source_inherits_project_discovery_and_does_not_mirror(tmp_path,monkeypatch):
    root=project(tmp_path);store=Store(tmp_path/'private')
    monkeypatch.setattr(official,'api',api_at(A))
    for name in ['inventory','sync_documents','read_pr','retain_pr']:
        monkeypatch.setattr(official,name,lambda *args,**kwargs:pytest.fail('New lite sources must not use full capture'))
    monkeypatch.setattr(wiki,'refresh_source',lambda *args,**kwargs:pytest.fail('Complete applied baseline is unchanged'))
    result=official.update_source(store,root,'engine')
    assert result['status']=='unchanged' and result['stages']['prs']['status']=='discovered'
    assert result['stages']['prs']['captured']==0
    assert not (store.root/'wiki/pr-sync/engine.json').exists()
    assert capture_policy.is_discovery(read_json(root/'knowledge/sources.json')[0],root)
    assert not capture_policy.is_discovery({'capture_policy':{'changes':'full'}},root)
    assert not capture_policy.is_discovery({})


@pytest.mark.parametrize('policy',[None,'full',{'changes':None},{'changes':[]},{'changes':'unknown'},
                                   {'mode':[]},{'write_views':'yes'}])
def test_malformed_policy_fails_before_source_io(tmp_path,monkeypatch,policy):
    root=project(tmp_path);store=Store(tmp_path/'private')
    registry=read_json(root/'knowledge/sources.json');registry[0]['capture_policy']=policy
    write_json(root/'knowledge/sources.json',registry)
    monkeypatch.setattr(official,'api',lambda *args:pytest.fail('Malformed policy must fail before network'))
    with pytest.raises(FlowError,match='capture_policy'):
        official.update_source(store,root,'engine')


def test_native_apply_then_next_update_is_noop_with_history(tmp_path,monkeypatch):
    root=project(tmp_path);store=Store(tmp_path/'private')
    stage_for_apply(store,root)
    official.apply_refresh(store,root,'apply1')
    source=read_json(root/'knowledge/sources.json')[0]
    lock=read_json(root/'knowledge/source-lock.json')
    assert {row['commit'] for row in lock['files']}=={A,B}
    assert source['baseline_commit']==B and official._locked_source_commit(root,source)==B
    # Historical collected and partial observations cannot select a new baseline.
    lock['files'].append({'repo':'org/engine','commit':'e'*40,'ref':'main','path':'a.py','sha256':'f'*64,'status':'partial'})
    write_json(root/'knowledge/source-lock.json',lock)
    assert official._locked_source_commit(root,source)==B
    # Compatible old native-apply records did not have a status field.
    next(row for row in lock['files'] if row['commit']==B).pop('status')
    write_json(root/'knowledge/source-lock.json',lock)
    assert official._locked_source_commit(root,source)==B
    monkeypatch.setattr(official,'api',api_at(B))
    monkeypatch.setattr(wiki,'refresh_source',lambda *args,**kwargs:pytest.fail('Applied unchanged bytes must not download again'))
    result=official.update_source(store,root,'engine')
    assert result['status']=='unchanged' and result['stages']['catalog']['rebuilt'] is False
    assert result['stages']['content']['body_read'] is False
    incomplete=copy.deepcopy(source);incomplete['paths'].append('new.py')
    assert official._locked_source_commit(root,incomplete) is None
    wrong_hash=copy.deepcopy(source);wrong_hash['baseline_files']['a.py']['sha256']='0'*64
    assert official._locked_source_commit(root,wrong_hash) is None


def tree_provider(calls, *, truncated=False, present=False):
    def get(url,token=None):
        calls.append(url)
        if '/commits/' in url and '/git/commits/' not in url:
            return {'sha':B,'commit':{'tree':{'sha':ROOT}}},''
        if url.endswith('/git/trees/'+ROOT):
            return {'sha':ROOT,'truncated':False,'tree':[{'path':'old','type':'tree','mode':'040000','sha':CHILD}]},''
        if url.endswith('/git/trees/'+CHILD):
            return {'sha':CHILD,'truncated':truncated,'tree':([{'path':'gone.py','type':'blob','sha':'3'*40,'mode':'100644'}] if present else [])},''
        raise FlowError('No unexpected or recursive request: '+url)
    return get


def test_fixed_parent_tree_absence_is_cached_and_applied(tmp_path,monkeypatch):
    root=project(tmp_path,paths=['old/gone.py','old/also-gone.py']);store=Store(tmp_path/'private')
    calls=[]
    monkeypatch.setattr(wiki,'_get_json',tree_provider(calls))
    monkeypatch.setattr(wiki.urllib.request,'urlopen',lambda *args,**kwargs:(_ for _ in ()).throw(OSError('raw 404')))
    monkeypatch.setattr(official,'read_code',lambda *args,**kwargs:(_ for _ in ()).throw(FlowError('contents 404')))
    result=wiki.refresh_source(store,root,'engine',fixed_commit=B)
    assert not result['failures'] and result['files']=={}
    proofs=result['absence_proofs']
    assert set(proofs)=={'old/gone.py','old/also-gone.py'}
    assert all(wiki.valid_absence_proof(proof,B,name) for name,proof in proofs.items())
    invalid=copy.deepcopy(proofs['old/gone.py']);invalid['trees'][0]['path']='unrelated'
    assert not wiki.valid_absence_proof(invalid,B,'old/gone.py')
    invalid=copy.deepcopy(proofs['old/gone.py']);invalid['trees'].insert(0,None)
    assert not wiki.valid_absence_proof(invalid,B,'old/gone.py')
    assert sum('/git/trees/' in url for url in calls)==2
    assert not any('recursive' in url for url in calls)
    stage_for_apply(store,root,files={},proofs=proofs)
    official.apply_refresh(store,root,'apply1')
    source=read_json(root/'knowledge/sources.json')[0]
    lock=read_json(root/'knowledge/source-lock.json')
    assert source['baseline_absent_files']==proofs
    assert len(lock['absences'])==2 and lock['files'][0]['commit']==A
    assert official._locked_source_commit(root,source)==B
    lock['absences'][0]['status']='partial'
    write_json(root/'knowledge/source-lock.json',lock)
    assert official._locked_source_commit(root,source) is None


@pytest.mark.parametrize('commit,path',[(None,None),('short','gone.py'),(B,''),(B,'../gone.py'),
                                      (B,'/gone.py'),(B,'C:gone.py'),(B,'dir\\gone.py')])
def test_absence_proof_requires_fixed_commit_and_safe_relative_path(commit,path):
    proof={'kind':'fixed-complete-inventory-absence-v1','repository':'org/engine',
           'commit':commit,'path':path,'inventory_artifact_sha256':'f'*64,'complete':True}
    assert not wiki.valid_absence_proof(proof,commit,path)


@pytest.mark.parametrize('truncated,present',[(True,False),(False,True)])
def test_404_is_not_deletion_without_complete_absence_proof(tmp_path,monkeypatch,truncated,present):
    root=project(tmp_path,paths=['old/gone.py']);store=Store(tmp_path/'private')
    monkeypatch.setattr(wiki,'_get_json',tree_provider([],truncated=truncated,present=present))
    monkeypatch.setattr(wiki.urllib.request,'urlopen',lambda *args,**kwargs:(_ for _ in ()).throw(OSError('raw failed')))
    monkeypatch.setattr(official,'read_code',lambda *args,**kwargs:(_ for _ in ()).throw(FlowError('contents failed')))
    result=wiki.refresh_source(store,root,'engine',fixed_commit=B)
    assert result['status']=='partial' and result['failures']
    assert not result.get('absence_proofs')
    assert not (store.root/'wiki/sources/engine.json').exists()


def test_absence_proof_rejects_tree_from_a_different_commit(tmp_path,monkeypatch):
    store=Store(tmp_path/'private')
    monkeypatch.setattr(wiki,'_get_json',lambda *args:pytest.fail('Wrong provided commit must be rejected before requests'))
    with pytest.raises(FlowError,match='commit tree proof mismatch'):
        wiki.prove_git_path_absence(store,{'repository':'org/engine'},B,'gone.py',
                                   commit_info={'sha':A,'commit':{'tree':{'sha':ROOT}}})


def test_query_artifacts_deduplicate_time_but_preserve_query_scope(tmp_path,monkeypatch):
    store=Store(tmp_path/'private')
    ticks=iter(f'2026-11-05T01:00:{n:02d}Z' for n in range(30))
    monkeypatch.setattr(official,'utc',lambda:next(ticks))
    detail={'number':1,'title':'same','body':'same','updated_at':'2026-11-05T00:00:00Z','changed_files':0,
            'head':{'sha':A,'repo':{'full_name':'org/engine'}},'base':{'sha':B,'repo':{'full_name':'org/engine'}}}
    monkeypatch.setattr(wiki,'_get_json',lambda *args:(detail,''))
    one=official.read_pr(store,'org/engine',1,discussions=False,files=False)
    two=official.read_pr(store,'org/engine',1,discussions=False,files=False)
    assert one['artifact']==two['artifact'] and one['observed_at']!=two['observed_at']
    assert 'observed_at' not in json.loads(store.artifact(one['artifact']))
    monkeypatch.setattr(wiki,'_get_json',lambda *args:({'items':[],'total_count':0,'incomplete_results':False},''))
    one=official.search_prs(store,'overlap',['https://github.com/org/engine.git'])
    two=official.search_prs(store,'overlap',['org/engine'])
    assert one['artifact']==two['artifact'] and one['queried_at']!=two['queried_at']
    for kwargs in [{'state':'open'},{'branch':'dev'},{'page':2},{'limit':5}]:
        assert official.search_prs(store,'overlap',['org/engine'],**kwargs)['artifact']!=one['artifact']
    payload=json.loads(store.artifact(one['artifact']))
    assert payload['query_scope']=={'repositories':['org/engine'],'state':'all','branch':None,'page':1,'limit':10}


def test_catalog_refreshes_only_navigation_inputs(tmp_path):
    root=project(tmp_path);store=Store(tmp_path/'private')
    local=root/'knowledge/projects/engine/knowledgebase/local/topics/known.md'
    local.parent.mkdir(parents=True)
    local.write_text('---\nid: known\ntitle: First title\n---\n# Known\nBody\n',encoding='utf-8')
    assert official._maybe_catalog(store,root)['rebuilt']
    assert not official._maybe_catalog(store,root)['rebuilt']
    local.write_text(local.read_text(encoding='utf-8').replace('Body','Different mechanism explanation'),encoding='utf-8')
    assert not official._maybe_catalog(store,root)['rebuilt']
    local.write_text(local.read_text(encoding='utf-8').replace('First title','Second title'),encoding='utf-8')
    assert official._maybe_catalog(store,root)['rebuilt']
    assert 'Second title' in (root/'knowledge/projects/engine/README.md').read_text(encoding='utf-8')
    registry=read_json(root/'knowledge/sources.json');registry.append({'id':'new','repository':'org/new','ref':'main','paths':[]})
    write_json(root/'knowledge/sources.json',registry)
    assert official._maybe_catalog(store,root)['rebuilt']
    assert 'https://github.com/org/new' in (root/'knowledge/catalog/README.md').read_text(encoding='utf-8')


def test_unchanged_source_keeps_deferred_workflow_visible_even_in_cold_checkout(tmp_path, monkeypatch):
    import shutil
    root = project(tmp_path); store = Store(tmp_path/'private')
    target = root/'docs/guide.md';target.parent.mkdir();target.write_text('Needs review', encoding='utf-8')
    write_json(root/'knowledge/maintenance.json', [{'source':'engine','paths':['a.py'],'targets':['docs/guide.md']}])
    source = read_json(root/'knowledge/sources.json')[0]
    staged = wiki.stage_source_refresh(store,root,source,B,{'a.py':{'sha256':NEW}},[],'main')
    wiki.review_refresh(store,staged['stage_id'],{},root,defer_workflows='Site review remains required')
    official.apply_refresh(store,root,staged['stage_id'])
    cold = tmp_path/'cold';shutil.copytree(root,cold)
    monkeypatch.setattr(official,'api',api_at(B))
    monkeypatch.setattr(wiki,'refresh_source',lambda *a,**kw:pytest.fail('Unchanged fixed bytes need no download'))
    for checkout, private in [(root,store),(cold,Store(tmp_path/'cold-private'))]:
        result = official.update_source(private,checkout,'engine')
        content = result['stages']['content']
        assert result['status']=='pending-content-review' and content['body_read'] is False
        assert content['affected_workflows']==['docs/guide.md']
        assert content['next'][:1]==['wiki-review']
        decision={'decision':'still-applicable','note':'Completed the required fixed-version workflow review',
                  'page_sha256':hashlib.sha256((checkout/'docs/guide.md').read_bytes()).hexdigest(),
                  'source_commit':B}
        wiki.review_refresh(private,content['stage_id'],{},checkout,workflow_decisions={'docs/guide.md':decision})
        official.apply_refresh(private,checkout,content['stage_id'])
        assert official.update_source(private,checkout,'engine')['status']=='unchanged'


@pytest.mark.parametrize('change', ['author-edited','author-added','citation-removed','workflow-edited'])
def test_unchanged_source_checks_portable_review_hashes_without_fetching(tmp_path,monkeypatch,change):
    import shutil
    root = project(tmp_path); store = Store(tmp_path/'private')
    page = root/'knowledge/topic.md'
    page.write_text('---\nid: topic\nsources: [{source: engine}]\n---\nKnown explanation',encoding='utf-8')
    target = root/'docs/guide.md';target.parent.mkdir();target.write_text('Known workflow',encoding='utf-8')
    write_json(root/'knowledge/maintenance.json',[{'source':'engine','paths':['a.py'],'targets':['docs/guide.md']}])
    source = read_json(root/'knowledge/sources.json')[0]
    staged = wiki.stage_source_refresh(store,root,source,B,{'a.py':{'sha256':NEW}},[],'main')
    decision = lambda p:{'decision':'still-applicable','note':'Checked fixed source and consumers',
                        'page_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'source_commit':B}
    wiki.review_refresh(store,staged['stage_id'],{'knowledge/topic.md':decision(page)},root,
                        workflow_decisions={'docs/guide.md':decision(target)})
    official.apply_refresh(store,root,staged['stage_id'])
    cold = tmp_path/'cold';shutil.copytree(root,cold)
    page = cold/'knowledge/topic.md';target = cold/'docs/guide.md'
    if change=='workflow-edited':
        target.write_text('New workflow contract',encoding='utf-8')
    elif change=='author-added':
        (cold/'knowledge/new.md').write_text(page.read_text(encoding='utf-8').replace('id: topic','id: new'),encoding='utf-8')
    else:
        page.write_text(page.read_text(encoding='utf-8').replace(
            'sources: [{source: engine}]' if change=='citation-removed' else 'Known explanation',
            'sources: []' if change=='citation-removed' else 'Changed explanation'),encoding='utf-8')
    monkeypatch.setattr(official,'api',api_at(B))
    monkeypatch.setattr(wiki,'refresh_source',lambda *a,**kw:pytest.fail('Do not refetch unchanged source'))
    result=official.update_source(Store(tmp_path/'cold-private'),cold,'engine')
    assert result['status']=='pending-content-review'
    content=result['stages']['content']
    assert content['body_read'] is False
    if change=='workflow-edited':
        assert content['affected_workflows']==['docs/guide.md']
    else:
        assert [r['page'] for r in content['affected_pages']]==[
            'knowledge/new.md' if change=='author-added' else 'knowledge/topic.md']


@pytest.mark.parametrize('consumer', ['author','workflow'])
def test_private_review_for_another_version_cannot_certify_current_consumers(tmp_path,monkeypatch,consumer):
    root=project(tmp_path);store=Store(tmp_path/'private')
    page=root/'knowledge/topic.md'
    page.write_text('---\nid: topic\nsources: [{source: engine}]\n---\nOriginal',encoding='utf-8')
    workflow=root/'guide.md';workflow.write_text('Original workflow',encoding='utf-8')
    registry=read_json(root/'knowledge/sources.json')
    source=registry[0]
    source['baseline_page_hashes']={'knowledge/topic.md':hashlib.sha256(page.read_bytes()).hexdigest()}
    source['baseline_workflow_hashes']={'guide.md':hashlib.sha256(workflow.read_bytes()).hexdigest()}
    write_json(root/'knowledge/sources.json',registry)
    changed=page if consumer=='author' else workflow
    changed.write_text(changed.read_text(encoding='utf-8')+'\nChanged for another version',encoding='utf-8')
    write_json(store.root/'wiki/reviewed-sources/engine.json',{'commit':B,'files':{'a.py':{'sha256':NEW}},
               'page_hashes':{'knowledge/topic.md':hashlib.sha256(page.read_bytes()).hexdigest()},
               'workflow_hashes':{'guide.md':hashlib.sha256(workflow.read_bytes()).hexdigest()}})
    monkeypatch.setattr(official,'api',api_at(A))
    monkeypatch.setattr(wiki,'refresh_source',lambda *a,**kw:pytest.fail('The applied fixed source did not change'))
    result=official.update_source(store,root,'engine')
    assert result['status']=='pending-content-review'
    content=result['stages']['content']
    assert content['changed_paths']==[]  # Compare against applied A, not private un-applied B.
    if consumer=='author':
        assert [r['page'] for r in content['affected_pages']]==['knowledge/topic.md']
    else:
        assert content['affected_workflows']==['guide.md']


def test_legacy_review_hashes_still_detect_authored_edits(tmp_path):
    root=project(tmp_path);store=Store(tmp_path/'private')
    page=root/'knowledge/topic.md'
    page.write_text('---\nid: topic\nsources: [{source: engine}]\n---\nBefore',encoding='utf-8')
    previous=hashlib.sha256(page.read_bytes()).hexdigest()
    write_json(store.root/'wiki/reviewed-sources/engine.json',{'commit':A,
               'affected_pages':[{'page':'knowledge/topic.md','page_sha256':previous}]})
    source=read_json(root/'knowledge/sources.json')[0]
    assert not wiki.source_review_needed(store,root,source)
    page.write_text(page.read_text(encoding='utf-8')+'\nChanged',encoding='utf-8')
    assert wiki.source_review_needed(store,root,source)


@pytest.mark.parametrize('consumer', ['author','workflow'])
def test_same_revision_private_review_cannot_hide_pending_public_apply(tmp_path,monkeypatch,consumer):
    import shutil
    root=project(tmp_path);store=Store(tmp_path/'private')
    page=root/'knowledge/topic.md'
    page.write_text('---\nid: topic\nsources: [{source: engine}]\n---\nKnown',encoding='utf-8')
    workflow=root/'guide.md';workflow.write_text('Known workflow',encoding='utf-8')
    write_json(root/'knowledge/maintenance.json',[{'source':'engine','paths':['a.py'],'targets':['guide.md']}])
    decide=lambda path:{'decision':'still-applicable','note':'Verified the fixed source consumers',
                        'page_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'source_commit':B}
    source=read_json(root/'knowledge/sources.json')[0]
    staged=wiki.stage_source_refresh(store,root,source,B,{'a.py':{'sha256':NEW}},[],'main')
    wiki.review_refresh(store,staged['stage_id'],{'knowledge/topic.md':decide(page)},root,
                        workflow_decisions={'guide.md':decide(workflow)})
    official.apply_refresh(store,root,staged['stage_id'])
    changed=page if consumer=='author' else workflow
    changed.write_text(changed.read_text(encoding='utf-8')+'\nNew explanation',encoding='utf-8')
    source=read_json(root/'knowledge/sources.json')[0]
    staged=wiki.stage_source_refresh(store,root,source,B,source['baseline_files'],[],'main')
    wiki.review_refresh(store,staged['stage_id'],
        {'knowledge/topic.md':decide(page)} if consumer=='author' else {},root,
        workflow_decisions={'guide.md':decide(workflow)} if consumer=='workflow' else {})
    # Deliberately stop before apply: neither the source revision nor the
    # reviewed public consumer hashes have advanced.
    public_binding=(root/'knowledge/sources.json').read_bytes()
    cold=tmp_path/'cold';shutil.copytree(root,cold)
    monkeypatch.setattr(official,'api',api_at(B))
    monkeypatch.setattr(wiki,'refresh_source',lambda *a,**kw:pytest.fail('Unchanged source bytes need no download'))
    for checkout, private in [(root,store),(cold,Store(tmp_path/'cold-private'))]:
        result=official.update_source(private,checkout,'engine')
        assert result['status']=='pending-content-review'
        content=result['stages']['content']
        if consumer=='author':
            assert [row['page'] for row in content['affected_pages']]==['knowledge/topic.md']
        else:
            assert content['affected_workflows']==['guide.md']
    assert (root/'knowledge/sources.json').read_bytes()==public_binding
