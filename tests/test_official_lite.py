import copy
import json
from pathlib import Path

import pytest

from hcu_trainflow import official, wiki
from hcu_trainflow.core import FlowError, Store, read_json, write_json


def project(tmp_path):
    root=tmp_path/'project'
    (root/'knowledge').mkdir(parents=True)
    write_json(root/'knowledge/sources.json',[{'id':'engine','repository':'org/engine','ref':'main',
               'baseline_commit':'a'*40,'paths':['a.py'],
               'capture_policy':{'mode':'federated','changes':'discover','write_views':False}}])
    write_json(root/'knowledge/source-lock.json',{'files':[{'repo':'org/engine','ref':'main',
               'path':'a.py','commit':'b'*40,'status':'collected','sha256':'c'*64}]})
    return root


def pr_detail():
    return {'number':1,'title':'Gradient fix','body':'Preserve gradient',
            'html_url':'https://github.com/org/engine/pull/1','state':'closed','merged':True,
            'updated_at':'2026-11-05T01:00:00Z','changed_files':1,
            'head':{'sha':'a'*40,'repo':{'full_name':'fork/engine','size':123,'pushed_at':'2026-11-05T00:00:00Z'}},
            'base':{'sha':'b'*40,'repo':{'full_name':'org/engine','size':555}}}


def test_body_only_pr_and_explicit_discussion_reading(tmp_path,monkeypatch):
    store=Store(tmp_path/'private')
    calls=[]
    def get(url,token=None):
        calls.append(url)
        if url.endswith('/pulls/1'):return pr_detail(),''
        if '/reviews?' in url:raise FlowError('review permission denied')
        return [],''
    monkeypatch.setattr(wiki,'_get_json',get)
    result=official.read_pr(store,'org/engine',1,discussions=False,files=False)
    assert len(calls)==1 and result['body']=='Preserve gradient'
    assert result['refs']['head']=={'repository':'fork/engine','commit':'a'*40}
    assert result['status']=='collected-not-reviewed' and not result['coverage']['reviews']['complete']
    assert result['coverage']['reviews']['requested'] is False
    result=official.read_pr(store,'org/engine',1,discussions=True,files=False)
    assert result['status']=='partial' and result['coverage']['reviews']['error']
    assert not result['coverage']['files']['requested']
    assert not any('/files?' in url for url in calls)


def test_explicit_body_only_retention_preserves_public_guard(tmp_path,monkeypatch):
    root=project(tmp_path);store=Store(tmp_path/'private')
    monkeypatch.setattr(wiki,'_get_json',lambda *args:(pr_detail(),''))
    result=official.read_pr(store,'org/engine',1,discussions=False,files=False)
    monkeypatch.setattr(official,'api',lambda *args:({'private':False},''))
    retained=official.retain_pr(store,root,result,'engine')
    meta,body=wiki.parse_page(root/retained['page'])
    assert 'on demand' in meta['coverage'] and 'Not requested' in body
    assert not meta['runtime_validated']
    monkeypatch.setattr(official,'api',lambda *args:({'private':True},''))
    with pytest.raises(FlowError,match='public'):
        official.retain_pr(store,root,result,'engine')


def test_semantic_noop_does_not_downgrade_richer_original(tmp_path,monkeypatch):
    root=project(tmp_path);store=Store(tmp_path/'private')
    detail=pr_detail()
    def get(url,token=None):
        if url.endswith('/pulls/1'):return copy.deepcopy(detail),''
        if '/reviews?' in url:return [{'state':'CHANGES_REQUESTED','body':'check backward'}],''
        if '/files?' in url:return [{'filename':'a.py','status':'modified','patch':'full patch'}],''
        return [],''
    monkeypatch.setattr(wiki,'_get_json',get)
    monkeypatch.setattr(official,'api',lambda *args:({'private':False},''))
    retained=official.retain_pr(store,root,official.read_pr(store,'org/engine',1),'engine')
    before={p:p.read_bytes() for p in (root/'knowledge').rglob('*') if p.is_file()}
    detail['updated_at']='2026-11-05T02:00:00Z'
    detail['head']['repo']['size']=99999
    detail['head']['repo']['pushed_at']='2026-11-05T02:00:00Z'
    detail['comments']=42
    detail['review_comments']=70
    light=official.read_pr(store,'org/engine',1,discussions=False,files=False)
    same=official.retain_pr(store,root,light,'engine')
    assert same['unchanged'] and same['artifact']==retained['artifact']
    assert before=={p:p.read_bytes() for p in (root/'knowledge').rglob('*') if p.is_file()}
    detail['head']['sha']='d'*40
    changed=official.retain_pr(store,root,official.read_pr(store,'org/engine',1,discussions=False,files=False),'engine')
    assert changed['artifact']!=retained['artifact']
    assert len(list((root/'knowledge/evidence/prs').rglob('*.json')))==2


def test_discovery_keeps_history_and_never_retains_bodies(tmp_path,monkeypatch):
    root=project(tmp_path);store=Store(tmp_path/'private')
    old_state=store.root/'wiki/pr-sync/engine.json'
    write_json(old_state,{'pending':[19,20],'errors':[{'number':19,'error':'old native 404'}]})
    old=old_state.read_bytes()
    calls=[]
    def api(repo,suffix,token=None):
        calls.append(suffix)
        assert suffix=='/pulls?state=all&sort=updated&direction=desc&per_page=10&page=1'
        return [{'number':1,'title':'candidate','updated_at':'2026-11-05T00:00:00Z'}],'<next>; rel="next"'
    monkeypatch.setattr(official,'api',api)
    monkeypatch.setattr(official,'read_pr',lambda *args,**kwargs:pytest.fail('Discovery must not fetch body/discussion'))
    monkeypatch.setattr(official,'retain_pr',lambda *args,**kwargs:pytest.fail('Discovery must not create pages/raw'))
    result=official.sync_prs(store,root,'engine')
    assert len(calls)==1 and result['status']=='discovered' and not result['history_complete']
    assert result['captured']==0 and result['results'][0]['url']=='https://github.com/org/engine/pull/1'
    assert result['historical_capture']['pending']==2 and old_state.read_bytes()==old
    assert not list((root/'knowledge').rglob('PR-*.md'))
    assert official.sync_prs(store,root,'engine')['unchanged']


def test_discovery_failure_keeps_last_success_and_validates_whole_page(tmp_path,monkeypatch):
    root=project(tmp_path);store=Store(tmp_path/'private')
    monkeypatch.setattr(official,'api',lambda *args:([{'number':1,'updated_at':'2026-11-05T00:00:00Z'}],''))
    official.sync_prs(store,root,'engine')
    path=store.root/'wiki/pr-discovery/engine.json';original=path.read_bytes()
    monkeypatch.setattr(official,'api',lambda *args:([{'number':2,'updated_at':'2026-11-05T00:00:00Z'},{'number':3}],''))
    result=official.sync_prs(store,root,'engine')
    assert result['status']=='partial' and result['errors'] and path.read_bytes()==original


def test_unchanged_source_uses_actual_lock_and_skips_inventory_docs(tmp_path,monkeypatch):
    root=project(tmp_path);store=Store(tmp_path/'private')
    calls=[]
    def api(repo,suffix,token=None):
        calls.append(suffix)
        if suffix=='/commits/main':return {'sha':'b'*40},''
        if suffix.startswith('/pulls?'):return [],''
        pytest.fail('Unexpected branch/detailed source request')
    monkeypatch.setattr(official,'api',api)
    for name in ['inventory','sync_documents','catalog']:
        monkeypatch.setattr(official,name,lambda *args:pytest.fail('No full inventory/doc/catalog sweep'))
    monkeypatch.setattr(wiki,'refresh_source',lambda *args,**kwargs:pytest.fail('Unchanged inputs do not refresh bytes'))
    result=official.update_source(store,root,'engine')
    assert result['status']=='unchanged' and len(calls)==2
    assert result['stages']['check']['locked_commit']=='b'*40
    assert result['stages']['content']['body_read'] is False


def test_changed_source_stages_only_monitored_paths_after_public_check(tmp_path,monkeypatch):
    root=project(tmp_path);store=Store(tmp_path/'private')
    calls=[]
    def api(repo,suffix,token=None):
        calls.append(suffix)
        if suffix=='/commits/main':return {'sha':'d'*40},''
        if not suffix:return {'private':False},''
        if suffix.startswith('/pulls?'):return [],''
        pytest.fail('No full tree request')
    monkeypatch.setattr(official,'api',api)
    staged=[]
    def refresh(store_arg,project_arg,source,token,fixed_commit=None):
        staged.append((source,fixed_commit))
        return {'stage_id':'new-stage','changed_paths':['a.py'],'status':'collected-not-reviewed'}
    monkeypatch.setattr(wiki,'refresh_source',refresh)
    result=official.update_source(store,root,'engine')
    assert result['status']=='pending-content-review' and staged==[('engine','d'*40)]
    assert not any('/git/trees' in suffix for suffix in calls)


def test_private_context_is_not_sent_to_public_pr_search(tmp_path,monkeypatch):
    store=Store(tmp_path/'private')
    monkeypatch.setattr(wiki,'_get_json',lambda *args:pytest.fail('Pasted private context must stay local'))
    result=official.search_prs(store,'run_id=internal_job\n10.2.3.4 failure',['org/engine'])
    assert result['status']=='public-query-required' and not result['results']


def test_light_catalog_does_not_expand_historical_ledgers_or_ordinary_prs(tmp_path):
    root=project(tmp_path)
    write_json(root/'knowledge/storage.json',{'profile':'discovery-first'})
    historical=root/'knowledge/catalog/repositories/engine.json'
    historical.parent.mkdir(parents=True)
    historical.write_text('Deliberately invalid historical inventory; light navigation must not read this',encoding='utf-8')
    page=root/'knowledge/projects/engine/knowledgebase/upstream/prs/org--engine/PR-999.md'
    page.parent.mkdir(parents=True)
    page.write_text('---\ninvalid: [\n---\nOrdinary PR must not be parsed for the source hub',encoding='utf-8')
    related=root/'knowledge/extra-topic.md'
    related.write_text('---\nid: extra\ntitle: Retained mechanism\n---\n# Mechanism\n',encoding='utf-8')
    write_json(root/'knowledge/coverage.json',{'schema':2,'projects':[{'id':'engine','related_pages':['knowledge/extra-topic.md']}]})
    result=official.catalog(root)
    assert result['profile']=='discovery-first'
    _,body=wiki.parse_page(root/'knowledge/catalog/README.md')
    assert 'https://github.com/org/engine/pulls' in body and 'PR-999' not in body
    _,body=wiki.parse_page(root/'knowledge/projects/engine/README.md')
    assert 'Retained mechanism' in body and '完整源码路径' not in body
    assert not (root/'knowledge/COVERAGE.md').exists()


def test_new_registered_path_prevents_unchanged_commit_shortcut(tmp_path,monkeypatch):
    root=project(tmp_path);store=Store(tmp_path/'private')
    registry=read_json(root/'knowledge/sources.json')
    registry[0]['paths'].append('new.py')
    write_json(root/'knowledge/sources.json',registry)
    def api(repo,suffix,token=None):
        if suffix=='/commits/main':return {'sha':'b'*40},''
        if not suffix:return {'private':False},''
        if suffix.startswith('/pulls?'):return [],''
        pytest.fail('Unexpected API request')
    monkeypatch.setattr(official,'api',api)
    staged=[]
    monkeypatch.setattr(wiki,'refresh_source',lambda *args,**kwargs:staged.append(kwargs['fixed_commit']) or {'status':'collected-not-reviewed'})
    result=official.update_source(store,root,'engine')
    assert result['status']=='pending-content-review' and staged==['b'*40]
