import json
from pathlib import Path
import pytest

from hcu_trainflow import official, wiki, experience
from hcu_trainflow.core import Store, FlowError, write_json, read_json, digest
from hcu_trainflow.delivery import export_public


def project(tmp_path):
    root=tmp_path/'project';(root/'knowledge').mkdir(parents=True)
    write_json(root/'knowledge/sources.json',[{'id':'engine','repository':'org/engine','ref':'main','paths':['a.py'],'engine':'engine'}])
    write_json(root/'knowledge/source-lock.json',{'files':[]})
    return root


def pr_api(url,token=None):
    if url.endswith('/repos/org/engine'):return {'private':False},''
    if url.endswith('/pulls/1'):
        return {'title':'Preserve gradient','body':'Motivation','html_url':'https://github.com/org/engine/pull/1',
                'state':'closed','merged':True,'updated_at':'2026-10-08T10:00:00Z','changed_files':1,
                'head':{'sha':'a'*40,'repo':{'full_name':'fork/engine'}},
                'base':{'sha':'b'*40,'repo':{'full_name':'org/engine'}}},''
    if '/reviews?' in url:return [{'body':'Test backward','state':'CHANGES_REQUESTED','user':{'login':'reviewer'}}],''
    if '/files?' in url:return [{'filename':'a.py','patch':'diff','status':'modified'}],''
    return [],''


def test_pr_persistence_search_and_stable_raw(tmp_path,monkeypatch):
    root=project(tmp_path);store=Store(tmp_path/'private')
    monkeypatch.setattr(wiki,'_get_json',pr_api)
    first=official.read_pr(store,'org/engine',1)
    assert first['refs']['head']['repository']=='fork/engine'
    saved=official.retain_pr(store,root,first,'engine')
    second=official.read_pr(store,'org/engine',1)
    assert official.retain_pr(store,root,second,'engine')['artifact']==saved['artifact']
    assert len(list((root/'knowledge/evidence/prs').rglob('*.json')))==1
    wiki.index_wiki(store,root)
    assert wiki.search_wiki(store,'backward',engine='engine')['results']
    p=root/saved['page'];p.write_text(p.read_text()+'Manual note')
    with pytest.raises(FlowError,match='manual'):official.retain_pr(store,root,first,'engine')


def test_private_or_partial_pr_cannot_publish(tmp_path,monkeypatch):
    root=project(tmp_path);store=Store(tmp_path/'s')
    def api(url,token=None):
        if url.endswith('/repos/org/engine'):return {'private':True},''
        return pr_api(url,token)
    monkeypatch.setattr(wiki,'_get_json',api)
    r=official.read_pr(store,'org/engine',1)
    with pytest.raises(FlowError,match='public'):official.retain_pr(store,root,r,'engine')
    assert not (root/'knowledge/prs').exists()
    def broken(url,token=None):
        if '/reviews?' in url:raise FlowError('permission')
        return pr_api(url,token)
    monkeypatch.setattr(wiki,'_get_json',broken)
    r=official.read_pr(store,'org/engine',1)
    assert r['status']=='partial'
    with pytest.raises(FlowError,match='pagination'):official.retain_pr(store,root,r,'engine')


def test_inventory_tracks_unmonitored_file_changes_and_truncation(tmp_path,monkeypatch):
    root=project(tmp_path);store=Store(tmp_path/'s');current={'sha':'a'*40,'truncated':False}
    def api(repo,suffix,token=None):
        if not suffix:return {'private':False},''
        if '/commits/' in suffix:return {'sha':current['sha']},''
        return {'truncated':current['truncated'],'tree':[{'path':'new/feature.py','sha':current['sha'],'type':'blob','mode':'100644'}]},''
    monkeypatch.setattr(official,'api',api)
    r=official.inventory(store,root,'engine',retain=True)
    assert 'new/feature.py' in r['new_paths']
    current['sha']='b'*40
    assert official.inventory(store,root,'engine')['changed_paths']==['new/feature.py']
    current['truncated']=True
    with pytest.raises(FlowError,match='truncated'):official.inventory(store,root,'engine',retain=True)
    assert json.loads((root/'knowledge/catalog/repositories/engine.json').read_text())['commit']=='a'*40


def test_code_cache_requires_fixed_sha_and_no_second_network_read(tmp_path,monkeypatch):
    store=Store(tmp_path/'s')
    monkeypatch.setattr(official,'api',lambda *a:({'encoding':'base64','content':'cHJpbnQoMSkK'},''))
    r=official.read_code(store,'fork/engine','a'*40,'a.py',max_chars=3)
    assert r['truncated'] and store.artifact(r['artifact'])==b'print(1)\n'
    monkeypatch.setattr(official,'api',lambda *a: (_ for _ in ()).throw(AssertionError('network')))
    assert not official.read_code(store,'fork/engine','a'*40,'a.py')['truncated']
    with pytest.raises(FlowError):official.read_code(store,'fork/engine','main','a.py')


def test_pr_sync_resume_does_not_advance_cursor_on_failure(tmp_path,monkeypatch):
    root=project(tmp_path);store=Store(tmp_path/'s')
    monkeypatch.setattr(official,'api',lambda *a:([{'number':n,'updated_at':'2026-10-08T00:00:00Z'} for n in [1,2]],''))
    monkeypatch.setattr(official,'read_pr',lambda s,r,n,t=None:{'number':n})
    monkeypatch.setattr(official,'retain_pr',lambda s,p,r,e,t=None:{'id':str(r['number'])})
    r=official.sync_prs(store,root,'engine',max_prs=1,since='2026-10-01T00:00:00Z')
    assert r['pending']==1
    ledger=root/'knowledge/catalog/pr-ledgers/engine.json'
    assert 'discovered_through' not in json.loads(ledger.read_text())
    monkeypatch.setattr(official,'read_pr',lambda *a: (_ for _ in ()).throw(FlowError('limit')))
    assert official.sync_prs(store,root,'engine')['pending']==1
    monkeypatch.setattr(official,'read_pr',lambda s,r,n,t=None:{'number':n})
    assert official.sync_prs(store,root,'engine')['pending']==0
    assert json.loads(ledger.read_text())['discovered_through']


def test_deferred_workflow_stays_pending_on_unchanged_refresh(tmp_path):
    root=project(tmp_path);store=Store(tmp_path/'s')
    (root/'skill.md').write_text('instruction')
    write_json(root/'knowledge/maintenance.json',[{'source':'engine','paths':['a.py'],'targets':['skill.md']}])
    source=official.source_for(root,'engine');files={'a.py':{'sha256':'c'*64}}
    stage=wiki.stage_source_refresh(store,root,source,'a'*40,files,[],'main')
    receipt=wiki.review_refresh(store,stage['stage_id'],{},root,defer_workflows='Requires supplied site')
    assert receipt['workflow_deferred']==['skill.md']
    repeat=wiki.stage_source_refresh(store,root,source,'a'*40,files,[],'main')
    assert repeat['changed_paths']==[] and repeat['affected_workflows']==['skill.md']
    assert official.apply_refresh(store,root,stage['stage_id'])['workflow_pending']==['skill.md']


def training(tmp_path):
    s=Store(tmp_path/'private')
    s.create({'schema_version':1,'task_id':'t','mode':'optimize','objective':'overlap memory',
              'context':{'model':'m','environment':'e','source':'a','precision':'bf16','data':'d'},'permissions':[]})
    raw=s.put(b'raw test evidence')
    return s,raw


def test_report_milestone_replay_and_context_isolation(tmp_path):
    s,raw=training(tmp_path);context=s.task('t')['context']
    result=s.report('t','performance',{'context':context,'status':'complete','evidence':[raw],'step_ms':10})
    assert result['knowledge']['records']==1
    assert experience.sync(s)['records']==0
    hit=experience.search(s,'performance',model='m')['results'][0]
    s.change_context('t',{'model':'m','environment':'other','source':'b'})
    assert not experience.search(s,'performance',environment='other')['results']
    assert experience.search(s,'performance',context=s.task('t')['context'])['results'][0]['context_match'] is False
    assert experience.get(s,hit['id'])['record']['report']['step_ms']==10
    assert experience.rebuild(s)['records']==1


def test_numerical_and_measurement_contracts(tmp_path):
    s,raw=training(tmp_path)
    value={'context':s.task('t')['context'],'milestone':'tp-overlap','kind':'optimization','summary':'TP overlap','outcome':'accepted',
           'evidence':[raw],'metrics':[{'name':'step','value':10,'unit':'ms','scope':'end-to-end','aggregation':'median',
                                      'measurement_window':'steps 20-50','evidence':raw}]}
    result=experience.record(s,'t',value)
    assert experience.get(s,result['id'])['record']['loss']['status']=='not-run'
    with pytest.raises(FlowError,match='Loss'):experience.record(s,'t',{**value,'loss':{'status':'pass'}})
    value['metrics'][0]['value']=float('nan')
    with pytest.raises(FlowError,match='finite'):experience.record(s,'t',value)


def test_cookbook_provenance_and_private_export(tmp_path):
    s,raw=training(tmp_path);context=s.task('t')['context']
    r=experience.record(s,'t',{'context':context,'milestone':'baseline','kind':'baseline','summary':'baseline','outcome':'observed','evidence':[raw]})
    c={'context':context,'milestone':'cookbook','kind':'cookbook','summary':'TP overlap practice','outcome':'observed','evidence':[raw],
       'delivery':{'status':'submitted','public':True,'url':'https://github.com/org/cookbook/pull/1','experience_ids':[r['id']]}}
    with pytest.raises(FlowError,match='redaction'):experience.record(s,'t',c)
    c['delivery']['redaction_review']='Reviewed sanitized method only'
    assert experience.record(s,'t',c)['visibility']=='private'
    page=Path(r['page']);manifest={'reviewed_by':'test','files':[{'path':str(page.relative_to(s.root)),'sha256':digest(page.read_bytes())}]}
    with pytest.raises(FlowError,match='Private'):export_public(s.root,tmp_path/'public',manifest)


def test_generated_pages_normalize_upstream_newlines(tmp_path):
    p=tmp_path/'page.md'
    official.generated_page(p,{'id':'p'},'# Title\r\n\rText\n')
    meta,body=wiki.parse_page(p)
    assert meta['generated_body_sha256']==digest(body.encode())
    assert not p.read_bytes().endswith(b'\n\n')
    official.generated_page(p,{'id':'p'},'# Title\r\n\rText\n')


def test_document_discovery_retry_delete_and_restore(tmp_path,monkeypatch):
    root=project(tmp_path);store=Store(tmp_path/'private')
    tree=root/'knowledge/catalog/repositories/engine.json'
    write_json(tree,{'commit':'a'*40,'entries':{'docs/new.md':{'type':'blob','sha':'b'*40}}})
    monkeypatch.setattr(official,'api',lambda *a:({'private':False},''))
    def code(s,r,c,p,t=None,max_chars=None):return {'artifact':s.put(b'# New\r\n'), 'url':'https://github.com/org/engine/blob/'+c+'/'+p}
    monkeypatch.setattr(official,'read_code',code)
    r=official.sync_documents(store,root,'engine');assert r['pending']==0 and r['discovered']==1
    page=root/'knowledge/upstream-docs/engine/docs/new.md.md'
    assert page.exists()
    page.unlink()
    assert official.sync_documents(store,root,'engine')['processed']==['docs/new.md']
    write_json(tree,{'commit':'c'*40,'entries':{}})
    assert official.sync_documents(store,root,'engine')['discovered']==0 and page.exists()
    assert read_json(root/'knowledge/catalog/document-ledgers/engine.json')['historical_paths']==['docs/new.md']
    assert wiki.parse_page(page)[0]['source_state']=='removed-from-latest-tree'
    write_json(tree,{'commit':'d'*40,'entries':{'docs/new.md':{'type':'blob','sha':'b'*40}}})
    official.sync_documents(store,root,'engine')
    assert wiki.parse_page(page)[0]['source_state']=='current-scan'


def test_inventory_pending_survives_unchanged_fetch_and_requires_triage(tmp_path,monkeypatch):
    root=project(tmp_path);store=Store(tmp_path/'s')
    def api(repo,suffix,token=None):
        if not suffix:return {'private':False},''
        if '/commits/' in suffix:return {'sha':'a'*40},''
        return {'tree':[{'path':'a.py','sha':'b'*40,'type':'blob','mode':'100644'}]},''
    monkeypatch.setattr(official,'api',api)
    official.inventory(store,root,'engine',retain=True)
    r=official.inventory(store,root,'engine',retain=True)
    assert r['changed_paths']==[] and r['pending_paths']==['a.py']
    with pytest.raises(FlowError,match='commit'):official.triage_inventory(store,root,'engine',{'commit':'b'*40,'paths':{}})
    assert official.triage_inventory(store,root,'engine',{'commit':'a'*40,'paths':{'a.py':{'decision':'not-relevant','note':'Build-only metadata inspected'}}})['pending']==0


def test_read_full_page_and_filter_source_types(tmp_path):
    root=project(tmp_path);store=Store(tmp_path/'s')
    (root/'knowledge/topic.md').write_text(official.markdown({'id':'topic','engine':'engine'},'# Overlap\n\nA reviewed mechanism'))
    official.generated_page(root/'knowledge/map.md',{'id':'map','kind':'source-map','engine':'engine'},'# Overlap directory')
    wiki.index_wiki(store,root)
    assert wiki.read_page(store,'topic')['body'].endswith('A reviewed mechanism')
    assert [r['id'] for r in wiki.search_wiki(store,'overlap',kind='source-map')['results']]==['map']


def test_manual_experience_retry_and_missing_loss_execution(tmp_path):
    s,raw=training(tmp_path);context=s.task('t')['context']
    value={'context':context,'milestone':'trial','kind':'optimization','summary':'candidate','outcome':'observed','evidence':[raw]}
    assert experience.record(s,'t',value)['id']==experience.record(s,'t',value)['id']
    report=s.put(json.dumps({'context':context,'status':'pass','executed':True}).encode())
    with pytest.raises(FlowError,match='executed'):experience.record(s,'t',{**value,'evidence':[report],'loss':{'status':'pass','report':report,'scope':'stage'}})


def test_same_repo_topics_review_together(tmp_path):
    root=project(tmp_path);store=Store(tmp_path/'s')
    for name,path in [('overview','a.py'),('case','other.py')]:
        (root/'knowledge'/f'{name}.md').write_text(official.markdown({'id':name,'sources':[{'source':'engine','path':path}]},name))
    source=official.source_for(root,'engine')
    stage=wiki.stage_source_refresh(store,root,source,'a'*40,{'a.py':{'sha256':'b'*64}},[],'main')
    assert len(stage['affected_pages'])==2


def test_changed_pr_discussion_requires_related_page_review(tmp_path,monkeypatch):
    root=project(tmp_path);store=Store(tmp_path/'s')
    page=root/'knowledge/topic.md';page.write_text(official.markdown({'id':'topic','sources':[{'source':'engine','path':'a.py'}]},'# Gradient'))
    monkeypatch.setattr(wiki,'_get_json',pr_api)
    pr=official.read_pr(store,'org/engine',1);saved=official.retain_pr(store,root,pr,'engine')
    pending=read_json(store.root/'wiki/pr-review'/f'{saved["id"]}.json')
    assert pending['affected_pages']==['knowledge/topic.md']
    with pytest.raises(FlowError,match='every'):official.review_pr(store,root,saved['id'],{'artifact_sha256':saved['artifact'],'pages':{}})
    decisions={'artifact_sha256':saved['artifact'],'note':'Checked final behavior','pages':{'knowledge/topic.md':{'decision':'still-applicable','note':'Existing conclusion agrees with final code','page_sha256':digest(page.read_bytes())}}}
    assert official.review_pr(store,root,saved['id'],decisions)['status']=='content-reviewed'
    official.retain_pr(store,root,pr,'engine')
    assert read_json(store.root/'wiki/pr-review'/f'{saved["id"]}.json')['status']=='content-reviewed'
    def changed(url,token=None):
        body,links=pr_api(url,token)
        if '/reviews?' in url:body[0]['body']='New numerical caveat'
        return body,links
    monkeypatch.setattr(wiki,'_get_json',changed)
    official.retain_pr(store,root,official.read_pr(store,'org/engine',1),'engine')
    assert read_json(store.root/'wiki/pr-review'/f'{saved["id"]}.json')['status']=='pending-content-review'


def test_engine_scope_does_not_expand_into_incidental_tool_sources(tmp_path):
    root=project(tmp_path)
    sources=read_json(root/'knowledge/sources.json');sources.append({'id':'tool','repository':'org/tool','ref':'main','engine':'tooling'})
    write_json(root/'knowledge/sources.json',sources)
    (root/'knowledge/page.md').write_text(official.markdown({'engine':'engine','sources':[{'source':'tool'}]},'reference'))
    assert official.engine_repos(root,engine='engine')==['org/engine']


def test_failed_inventory_skips_document_refresh_and_preserves_run(tmp_path,monkeypatch):
    root=project(tmp_path);store=Store(tmp_path/'s')
    monkeypatch.setattr(official,'inventory',lambda *a:(_ for _ in ()).throw(FlowError('tree incomplete')))
    monkeypatch.setattr(official,'sync_documents',lambda *a:(_ for _ in ()).throw(AssertionError('must skip')))
    monkeypatch.setattr(official,'sync_prs',lambda *a:{'status':'collected-not-reviewed'})
    monkeypatch.setattr(wiki,'refresh_source',lambda *a:{'status':'collected-not-reviewed'})
    result=official.update_source(store,root,'engine')
    assert result['status']=='partial'
    assert {e['stage'] for e in result['errors']}=={'inventory','documents'}
    assert list((store.root/'wiki/update-runs').glob('*.json'))
    assert (root/'knowledge/catalog/README.md').is_file()


def test_local_edits_cannot_bypass_source_review_via_unchanged_refresh(tmp_path):
    root=project(tmp_path);store=Store(tmp_path/'s')
    page=root/'knowledge/topic.md'
    page.write_text(official.markdown({'id':'topic','sources':[{'source':'engine','path':'a.py'}]},'# First conclusion'))
    source=official.source_for(root,'engine');files={'a.py':{'sha256':'b'*64}}
    stage=wiki.stage_source_refresh(store,root,source,'a'*40,files,[],'main')
    def decisions():
        return {'knowledge/topic.md':{'decision':'updated','note':'Read source and reconciled conclusion',
            'page_sha256':digest(page.read_bytes()),'source_commit':'a'*40}}
    wiki.review_refresh(store,stage['stage_id'],decisions(),root)
    page.write_text(page.read_text()+'\nChanged conclusion')
    with pytest.raises(FlowError,match='stale'):official.apply_refresh(store,root,stage['stage_id'])
    repeat=wiki.stage_source_refresh(store,root,source,'a'*40,files,[],'main')
    assert not repeat['changed_paths'] and repeat['affected_pages']
    with pytest.raises(FlowError,match='Every'):wiki.review_refresh(store,repeat['stage_id'],{},root)
    wiki.review_refresh(store,repeat['stage_id'],decisions(),root)
    unchanged=wiki.stage_source_refresh(store,root,source,'a'*40,files,[],'main')
    assert not unchanged['affected_pages']
    wiki.review_refresh(store,unchanged['stage_id'],{},root)
    # A no-op review must retain page bindings for later edits, across restarts.
    page.write_text(page.read_text()+'\nAnother change')
    assert wiki.stage_source_refresh(Store(store.root),root,source,'a'*40,files,[],'main')['affected_pages']


def test_new_topic_after_staging_requires_review(tmp_path):
    root=project(tmp_path);store=Store(tmp_path/'s');source=official.source_for(root,'engine')
    stage=wiki.stage_source_refresh(store,root,source,'a'*40,{'a.py':{'sha256':'b'*64}},[],'main')
    (root/'knowledge/new.md').write_text(official.markdown({'id':'new','sources':[{'source':'engine','path':'a.py'}]},'# New claim'))
    with pytest.raises(FlowError,match='after staging'):wiki.review_refresh(store,stage['stage_id'],{},root)


def test_unchanged_pr_reopens_review_for_changed_related_topic(tmp_path,monkeypatch):
    root=project(tmp_path);store=Store(tmp_path/'s')
    page=root/'knowledge/topic.md';page.write_text(official.markdown({'id':'topic','sources':[{'source':'engine','path':'a.py'}]},'# Gradient'))
    monkeypatch.setattr(wiki,'_get_json',pr_api)
    pr=official.read_pr(store,'org/engine',1);saved=official.retain_pr(store,root,pr,'engine')
    decisions={'artifact_sha256':saved['artifact'],'note':'Inspected discussion','pages':{'knowledge/topic.md':{
        'decision':'still-applicable','note':'Inspected final source','page_sha256':digest(page.read_bytes())}}}
    official.review_pr(store,root,saved['id'],decisions)
    page.write_text(page.read_text()+'\nAltered interpretation')
    official.retain_pr(store,root,pr,'engine')
    assert read_json(store.root/'wiki/pr-review'/f'{saved["id"]}.json')['status']=='pending-content-review'


@pytest.mark.parametrize('association',['source','pr'])
def test_pr_review_discovers_new_related_page_after_capture(tmp_path,monkeypatch,association):
    root=project(tmp_path);store=Store(tmp_path/'s')
    old=root/'knowledge/topic.md'
    old.write_text(official.markdown({'id':'topic','sources':[{'source':'engine'}]},'# Existing topic'))
    monkeypatch.setattr(wiki,'_get_json',pr_api)
    saved=official.retain_pr(store,root,official.read_pr(store,'org/engine',1),'engine')
    added=root/'knowledge/new-topic.md'
    meta={'id':'new-topic','sources':[{'source':'engine'}]} if association=='source' else {'id':'new-topic','pr_sources':[saved['id']]}
    added.write_text(official.markdown(meta,'# New related conclusion'))
    decisions={'artifact_sha256':saved['artifact'],'note':'Reviewed API','pages':{'knowledge/topic.md':{
        'decision':'still-applicable','note':'Read final source','page_sha256':digest(old.read_bytes())}}}
    with pytest.raises(FlowError,match='every'):official.review_pr(store,root,saved['id'],decisions)
    pending=read_json(store.root/'wiki/pr-review'/f'{saved["id"]}.json')
    assert pending['status']=='pending-content-review'
    assert pending['affected_pages']==['knowledge/new-topic.md','knowledge/topic.md']
    decisions['pages']['knowledge/new-topic.md']={'decision':'updated','note':'Reconciled new topic','page_sha256':digest(added.read_bytes())}
    assert official.review_pr(store,root,saved['id'],decisions)['status']=='content-reviewed'


def test_pr_citation_removal_keeps_surviving_prose_pending(tmp_path,monkeypatch):
    root=project(tmp_path);store=Store(tmp_path/'s')
    page=root/'knowledge/topic.md'
    page.write_text(official.markdown({'id':'topic','sources':[{'source':'engine'}]},'# Claim'))
    monkeypatch.setattr(wiki,'_get_json',pr_api)
    pr=official.read_pr(store,'org/engine',1);saved=official.retain_pr(store,root,pr,'engine')
    page.write_text(official.markdown({'id':'topic','sources':[]},'# Claim still present'))
    official.retain_pr(store,root,pr,'engine')
    pending=read_json(store.root/'wiki/pr-review'/f'{saved["id"]}.json')
    assert pending['affected_pages']==['knowledge/topic.md']
    with pytest.raises(FlowError,match='every'):
        official.review_pr(store,root,saved['id'],{'artifact_sha256':saved['artifact'],'note':'Checked','pages':{}})


def test_pr_review_rejects_artifact_updated_by_another_store(tmp_path,monkeypatch):
    root=project(tmp_path);store=Store(tmp_path/'s')
    monkeypatch.setattr(wiki,'_get_json',pr_api)
    saved=official.retain_pr(store,root,official.read_pr(store,'org/engine',1),'engine')
    def changed(url,token=None):
        data,links=pr_api(url,token)
        if '/reviews?' in url:data[0]['body']='New API boundary'
        return data,links
    monkeypatch.setattr(wiki,'_get_json',changed)
    other=Store(tmp_path/'other-store')
    official.retain_pr(other,root,official.read_pr(other,'org/engine',1),'engine')
    with pytest.raises(FlowError,match='artifact changed'):
        official.review_pr(store,root,saved['id'],{'artifact_sha256':saved['artifact'],'note':'Old interpretation','pages':{}})


def test_pr_review_reads_legacy_pointer_without_page_binding(tmp_path,monkeypatch):
    root=project(tmp_path);store=Store(tmp_path/'s')
    monkeypatch.setattr(wiki,'_get_json',pr_api)
    saved=official.retain_pr(store,root,official.read_pr(store,'org/engine',1),'engine')
    pointer=store.root/'wiki/pr-review'/f'{saved["id"]}.json'
    pending=read_json(pointer);pending.pop('page');write_json(pointer,pending)
    assert official.review_pr(store,root,saved['id'],{'artifact_sha256':saved['artifact'],'note':'No authored topic affected','pages':{}})['status']=='content-reviewed'


def test_cli_search_refreshes_local_index_and_binds_requested_project(tmp_path):
    from hcu_trainflow.cli import execute, parser
    root=project(tmp_path);store=Store(tmp_path/'s')
    page=root/'knowledge/topic.md';page.write_text(official.markdown({'id':'first'},'# Original'))
    wiki.index_wiki(store,root)
    second=tmp_path/'other';(second/'knowledge').mkdir(parents=True)
    (second/'knowledge/topic.md').write_text(official.markdown({'id':'second'},'# Fresh claim'))
    def search(project):
        return execute(parser().parse_args(['--workspace',str(store.root),'wiki-search','fresh','--project',str(project),'--online-pr','off']))
    assert [r['id'] for r in search(second)['results']]==['second']
    page.write_text(official.markdown({'id':'first'},'# Fresh original project'))
    assert [r['id'] for r in search(root)['results']]==['first']


def test_concurrent_local_index_builds_are_independent(tmp_path):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier
    root=project(tmp_path);store=Store(tmp_path/'s');barrier=Barrier(2)
    (root/'knowledge/topic.md').write_text(official.markdown({'id':'topic'},'# Parallel search'))
    def build(_):
        barrier.wait()
        index=wiki.index_wiki(store,root)
        return wiki.search_wiki(store,'parallel',index=index)['results'][0]['id']
    with ThreadPoolExecutor(max_workers=2) as pool:assert list(pool.map(build,range(2)))==['topic','topic']
    assert not list((store.root/'wiki').glob('*.building'))


def test_cli_online_search_failure_is_partial_not_empty_success(tmp_path,monkeypatch,capsys):
    from hcu_trainflow.cli import main
    root=project(tmp_path)
    monkeypatch.setattr(official,'search_prs',lambda *a,**kw:{'status':'partial','results':[],
        'coverage':[{'repository':'org/engine','complete':False,'error':'rate limit'}]})
    code=main(['--workspace',str(tmp_path/'s'),'wiki-search','missing answer','--project',str(root),'--engine','engine'])
    result=json.loads(capsys.readouterr().out)
    assert code==2 and result['status']=='partial' and result['online_pr']['coverage'][0]['error']=='rate limit'


def test_multi_repository_search_exposes_combined_truncation(tmp_path,monkeypatch):
    def results(*a,**kw):
        return {'total_count':1,'items':[{'number':1,'title':'overlap','html_url':'https://github.com/org/repo/pull/1',
            'state':'open','updated_at':'2026-10-09T00:00:00Z'}]},''
    monkeypatch.setattr(wiki,'_get_json',results)
    result=official.search_prs(Store(tmp_path/'s'),'overlap',['org/one','org/two'],limit=1)
    assert all(c['complete'] for c in result['coverage'])
    assert result['display_truncated'] and result['status']=='partial' and len(result['results'])==1


def test_removing_source_binding_requires_review_of_surviving_prose(tmp_path):
    root=project(tmp_path);store=Store(tmp_path/'s');source=official.source_for(root,'engine')
    page=root/'knowledge/topic.md'
    page.write_text(official.markdown({'id':'topic','sources':[{'source':'engine','path':'a.py'}]},'# Claim'))
    files={'a.py':{'sha256':'b'*64}}
    def refresh():return wiki.stage_source_refresh(store,root,source,'a'*40,files,[],'main')
    def decisions():return {'knowledge/topic.md':{'decision':'updated','note':'Verified the surviving claim and its attribution',
        'page_sha256':digest(page.read_bytes()),'source_commit':'a'*40}}
    stage=refresh();wiki.review_refresh(store,stage['stage_id'],decisions(),root)
    noop=refresh();assert not noop['affected_pages']
    page.write_text(official.markdown({'id':'topic'},'# Changed claim without citation'))
    with pytest.raises(FlowError,match='after staging'):wiki.review_refresh(store,noop['stage_id'],{},root)
    stage=refresh();assert stage['affected_pages']
    with pytest.raises(FlowError,match='Every'):wiki.review_refresh(store,stage['stage_id'],{},root)
    wiki.review_refresh(store,stage['stage_id'],decisions(),root)
    assert official.apply_refresh(store,root,stage['stage_id'])['status']=='content-applied'
    assert not refresh()['affected_pages']


def test_read_binds_search_generation_even_after_other_project_index(tmp_path):
    from hcu_trainflow.cli import execute, parser
    store=Store(tmp_path/'s')
    for name in ['first','second']:
        root=tmp_path/name;(root/'knowledge').mkdir(parents=True)
        (root/'knowledge/topic.md').write_text(official.markdown({'id':'same'},'# '+name))
    first=wiki.index_wiki(store,tmp_path/'first')
    wiki.index_wiki(store,tmp_path/'second')
    args=['--workspace',str(store.root),'wiki-read','same','--generation',first['generation']]
    assert execute(parser().parse_args(args))['body']=='# first'
    args=['--workspace',str(store.root),'wiki-read','same','--project',str(tmp_path/'second')]
    assert execute(parser().parse_args(args))['body']=='# second'
