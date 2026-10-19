"""Project migration must preserve evidence and resume review without auto-approval."""
import json
from pathlib import Path

import pytest

from hcu_trainflow import official, wiki, knowledge_layout as layout
from hcu_trainflow.core import Store, FlowError, write_json, read_json, digest
from test_official_experience import project, pr_api


def test_grouped_sources_publish_pr_documents_and_maps_in_one_project(tmp_path, monkeypatch):
    root=project(tmp_path); store=Store(tmp_path/'cache')
    sources=read_json(root/'knowledge/sources.json'); sources[0]['knowledge_project']='ecosystem'
    write_json(root/'knowledge/sources.json',sources)
    monkeypatch.setattr(wiki,'_get_json',pr_api)
    saved=official.retain_pr(store,root,official.read_pr(store,'org/engine',1),'engine')
    pr=root/saved['page']; meta,body=wiki.parse_page(pr)
    assert saved['page']=='knowledge/projects/ecosystem/knowledgebase/upstream/prs/org--engine/PR-1.md'
    assert meta['id']=='pr-org--engine-1' and 'Test backward' in body
    evidence=root/meta['artifact_path']; assert digest(evidence.read_bytes())==meta['artifact_sha256']
    import re
    link=re.search(r'\[Original JSON, discussions and patches\]\(([^)]+)\)',body)[1]
    assert (pr.parent/link).resolve()==evidence.resolve()
    write_json(root/'knowledge/catalog/repositories/engine.json',
               {'commit':'a'*40,'entries':{'docs/guide.md':{'type':'blob','sha':'b'*40}}})
    monkeypatch.setattr(official,'api',lambda *args:({'private':False},''))
    monkeypatch.setattr(official,'read_code',lambda *args,**kwargs:
                        {'artifact':store.put(b'# Original [link](relative.md)\n'), 'url':'https://example.com/guide'})
    assert official.sync_documents(store,root,'engine')['pending']==0
    doc=layout.document_root(root,'engine')/'docs/guide.md.md'
    assert doc.is_file() and '[link](relative.md)' in doc.read_text()
    assert not (root/'knowledge/prs').exists() and not (root/'knowledge/upstream-docs').exists()
    official.project_catalog(root)
    first=(root/'knowledge/projects/ecosystem/README.md').read_bytes()
    official.project_catalog(root)
    assert first==(root/'knowledge/projects/ecosystem/README.md').read_bytes()
    wiki.index_wiki(store,root)
    assert wiki.read_page(store,'pr-org--engine-1')['path']==str(pr)


def test_hcu_sources_route_outside_collection_before_network(tmp_path, monkeypatch):
    root=project(tmp_path);store=Store(tmp_path/'cache')
    route={'id':'hcu-tool','repository':'HYGON-AI/tool','owner':'HCU-Knowledge','entry':'route.md'}
    write_json(root/'knowledge/catalog/external-knowledge.json',{'routes':[route]})
    def unexpected(*args,**kwargs):raise AssertionError('No collection network call allowed')
    monkeypatch.setattr(official,'api',unexpected)
    monkeypatch.setattr(wiki,'_get_json',unexpected)
    for action in (official.inventory,official.sync_documents,official.sync_prs,official.update_source,wiki.refresh_source):
        with pytest.raises(FlowError,match='HCU-Knowledge'):
            action(store,root,'hcu-tool')
    write_json(root/'knowledge/sources.json',[{'id':'new-source','repository':'HYGON-AI/new-tool','ref':'main'}])
    with pytest.raises(FlowError,match='HCU-Knowledge'):
        official.inventory(store,root,'new-source',retain=True)
    raw=store.put(json.dumps({'repository':'HYGON-AI/new-tool','number':1}).encode())
    with pytest.raises(FlowError,match='HCU-Knowledge'):
        official.retain_pr(store,root,{'artifact':raw},'tool')
    assert not (root/'knowledge/evidence').exists()


def test_moved_page_cannot_escape_review_by_removing_citation(tmp_path):
    root=project(tmp_path);store=Store(tmp_path/'cache')
    old='knowledge/old.md';new='knowledge/projects/engine/knowledgebase/local/topics/lifetime.md'
    write_json(root/'knowledge/catalog/path-migrations.json',{'paths':{old:new}})
    target=root/new;target.parent.mkdir(parents=True)
    target.write_text(official.markdown({'id':'stable-id','sources':[]},'# Changed conclusion; citation removed'))
    files={'a.py':{'sha256':'b'*64}}
    write_json(store.root/'wiki/reviewed-sources/engine.json',
               {'files':files,'page_hashes':{old:digest(b'Old conclusion')}})
    write_json(store.root/'wiki/workflow-pending/engine.json',{'targets':[old]})
    stage=wiki.stage_source_refresh(store,root,official.source_for(root,'engine'),'a'*40,files,[],'main')
    assert not stage['changed_paths']
    assert [p['page'] for p in stage['affected_pages']]==[new]
    assert stage['affected_workflows']==[new]
    with pytest.raises(FlowError,match='Every affected'):
        wiki.review_refresh(store,stage['stage_id'],{},root)


def test_old_pr_pointer_resolves_new_page_without_reapproving_old_body(tmp_path,monkeypatch):
    root=project(tmp_path);store=Store(tmp_path/'cache');monkeypatch.setattr(wiki,'_get_json',pr_api)
    saved=official.retain_pr(store,root,official.read_pr(store,'org/engine',1),'engine')
    old='knowledge/prs/org--engine/PR-1.md'
    write_json(root/'knowledge/catalog/path-migrations.json',{'prefixes':{
        'knowledge/prs/org--engine/':'knowledge/projects/engine/knowledgebase/upstream/prs/org--engine/'}})
    pointer=store.root/'wiki/pr-review'/f'{saved["id"]}.json'; pending=read_json(pointer)
    pending['page']=old; write_json(pointer,pending)
    result=official.review_pr(store,root,saved['id'],{'artifact_sha256':saved['artifact'],
        'pages':{},'note':'No associated authored interpretation; verified current original PR.'})
    assert result['page']==saved['page']


def test_migration_paths_cannot_escape_project(tmp_path):
    root=project(tmp_path)
    write_json(root/'knowledge/catalog/path-migrations.json',{'paths':{'old':'../outside'}})
    with pytest.raises(FlowError):layout.current_path(root,'old')
    with pytest.raises(FlowError):layout.pr_root(root,'../outside')


def test_old_document_ledger_resumes_without_duplicate_download(tmp_path,monkeypatch):
    root=project(tmp_path);store=Store(tmp_path/'cache')
    write_json(root/'knowledge/catalog/repositories/engine.json',{
        'commit':'a'*40,'entries':{'docs/a.md':{'type':'blob','sha':'b'*40}}})
    monkeypatch.setattr(official,'api',lambda *args:({'private':False},''))
    monkeypatch.setattr(official,'read_code',lambda *args,**kwargs:
        {'artifact':store.put(b'# source'), 'url':'https://example.com/a'})
    official.sync_documents(store,root,'engine')
    ledger=root/'knowledge/catalog/document-ledgers/engine.json'; data=read_json(ledger)
    data['records']['docs/a.md']['page']='knowledge/upstream-docs/engine/docs/a.md.md';write_json(ledger,data)
    write_json(root/'knowledge/catalog/path-migrations.json',{'prefixes':{
        'knowledge/upstream-docs/engine/':'knowledge/projects/engine/knowledgebase/upstream/docs/engine/'}})
    def forbidden(*args,**kwargs):raise AssertionError('Unchanged document must reuse migrated evidence')
    monkeypatch.setattr(official,'read_code',forbidden)
    result=official.sync_documents(store,root,'engine')
    assert result['pending']==0 and result['processed']==[]
    assert read_json(ledger)['records']['docs/a.md']['page'].startswith('knowledge/projects/')


def test_cli_external_reference_filter_and_search(tmp_path):
    from hcu_trainflow.cli import parser, execute
    root=project(tmp_path)
    (root/'knowledge/route.md').write_text(official.markdown({
        'id':'hcu-tool-route','kind':'external-reference','hcu_project':'cluster-manager',
        'search_skill':'hcu-knowledge-search'}, '# hcu-envcheck run_nhc 联查 HCU-Knowledge'), encoding='utf-8')
    args=parser().parse_args(['--workspace',str(tmp_path/'cache'),'wiki-search','run_nhc',
                             '--project',str(root),'--kind','external-reference','--online-pr','off'])
    result=execute(args)
    assert result['results'][0]['id']=='hcu-tool-route'
    assert result['results'][0]['metadata']['hcu_project']=='cluster-manager'


def test_review_scans_keep_live_author_pages_without_parsing_generated_sources(tmp_path, monkeypatch):
    root=project(tmp_path)
    upstream=layout.upstream_root(root,source='engine')/'docs/raw.md'
    upstream.parent.mkdir(parents=True)
    upstream.write_text(official.markdown({'kind':'source-document','sources':[]},'# Original'),encoding='utf-8')
    authored=root/'knowledge/projects/engine/knowledgebase/local/topics/state.md'
    authored.parent.mkdir(parents=True)
    meta={'id':'state','sources':[{'source':'engine'}]}
    authored.write_text(official.markdown(meta,'# Initial state'),encoding='utf-8')
    parse=wiki.parse_page
    def authored_only(path):
        assert not Path(path).is_relative_to(upstream.parents[1])
        return parse(path)
    monkeypatch.setattr(wiki,'parse_page',authored_only)
    first=official.pr_page_hashes(root,'pr-org--engine-1','org/engine')
    assert first==wiki.source_page_hashes(root,'engine')
    assert set(first)=={authored.relative_to(root).as_posix()}
    # A later batch must see both changed prose and a newly added experience.
    authored.write_text(official.markdown(meta,'# Updated state'),encoding='utf-8')
    experience=root/'knowledge/sites/shared.md'
    experience.parent.mkdir()
    experience.write_text(official.markdown(meta,'# Reusable site condition'),encoding='utf-8')
    current=official.pr_page_hashes(root,'pr-org--engine-1','org/engine')
    assert current==wiki.source_page_hashes(root,'engine')
    assert current[authored.relative_to(root).as_posix()]!=first[authored.relative_to(root).as_posix()]
    assert experience.relative_to(root).as_posix() in current
    # Citation removal is still covered by the prior affected-page inventory.
    authored.write_text(official.markdown({'id':'state','sources':[]},'# Citation removed'),encoding='utf-8')
    assert authored.relative_to(root).as_posix() in official.pr_page_hashes(
        root,'pr-org--engine-1','org/engine',previous=current)


def test_relative_cli_project_can_retain_and_regenerate_catalog(tmp_path,monkeypatch):
    root=project(tmp_path);store=Store(tmp_path/'cache');monkeypatch.setattr(wiki,'_get_json',pr_api)
    monkeypatch.chdir(root)
    saved=official.retain_pr(store,'.',official.read_pr(store,'org/engine',1),'engine')
    assert saved['page'].startswith('knowledge/projects/engine/')
    assert official.catalog('.')['status']=='catalogued'
    assert (root/'knowledge/projects/engine/README.md').is_file()
    assert official.annotate_prs('.',{'results':[{'repository':'org/engine','number':1,'updated_at':'now'}]})['results'][0]['locally_retained']
