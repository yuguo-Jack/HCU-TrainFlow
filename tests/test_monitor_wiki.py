import json
from pathlib import Path
import pytest
from hcu_trainflow.core import Store, FlowError, write_json, digest
from hcu_trainflow.monitor import poll_log, import_events, inbox, observation_issues
from hcu_trainflow import monitor, wiki
from hcu_trainflow.delivery import export_public
from hcu_trainflow.demo import run_demo

POLICY={'stall_seconds':30,'telemetry_seconds':60,'recovery_seconds':50,'min_progress_samples':2}
def setup(tmp_path):
    store=Store(tmp_path/'state');store.create({'schema_version':1,'task_id':'t','mode':'operate','objective':'watch','context':{'s':'1'}})
    path=tmp_path/'log.jsonl';path.write_text(json.dumps({'attempt_id':'a','step':0,'timestamp':100})+'\n')
    return store,path

def test_stall_deduplication_and_partial_lines(tmp_path):
    store,path=setup(tmp_path)
    with path.open('a') as f:f.write('{"attempt_id":')
    poll_log(store,'t',path,POLICY,now=150);poll_log(store,'t',path,POLICY,now=151)
    assert len([x for x in store.events() if x['kind']=='observation'])==1
    assert len([x for x in store.events() if x['kind']=='incident-opened'])==1
    with path.open('a') as f:f.write('"a","step":1,"timestamp":152}\n')
    assert poll_log(store,'t',path,POLICY,now=153)['status']=='healthy-observed'
    assert any(x['kind']=='incident-cleared' for x in store.events())

def test_heartbeat_write_crash_keeps_transaction(tmp_path,monkeypatch):
    store,path=setup(tmp_path)
    original=monitor.write_json
    monkeypatch.setattr(monitor,'write_json',lambda *a: (_ for _ in ()).throw(OSError('disk interruption')))
    with pytest.raises(OSError):poll_log(store,'t',path,POLICY,now=150)
    monkeypatch.setattr(monitor,'write_json',original)
    result=poll_log(store,'t',path,POLICY,now=151)
    assert result['last_observation']['step']==0
    assert len([x for x in store.events() if x['kind']=='incident-opened'])==1

def test_missing_log_is_incident(tmp_path):
    store,path=setup(tmp_path);path.unlink()
    assert poll_log(store,'t',path,POLICY,now=100)['status']=='attention'

def test_watcher_refuses_relabeling_old_observations(tmp_path):
    store,path=setup(tmp_path);poll_log(store,'t',path,POLICY,now=100)
    store.change_context('t',{'s':'new'})
    with pytest.raises(FlowError):poll_log(store,'t',path,POLICY,now=110)

def test_bad_json_shape_is_visible_warning(tmp_path):
    store,path=setup(tmp_path)
    path.write_text('[]\n')
    result=poll_log(store,'t',path,POLICY,now=110)
    assert result['status']=='attention' and any(x['kind']=='collector-input-warning' for x in result['issues'])

def test_recovery_requires_progress_and_checkpoint():
    sample={'attempt_id':'b','step':10,'timestamp':100,'recovery_state':'restored','checkpoint_verified':False}
    assert 'recovery-timeout' in [x['kind'] for x in observation_issues([sample],POLICY,now=160)]

def test_confirmed_completion_does_not_become_stall():
    sample={'attempt_id':'b','step':100,'timestamp':100,'completed':True,'job_alive':False}
    assert observation_issues([sample],POLICY,now=10000)==[]

def test_replay_and_claim(tmp_path):
    remote,path=setup(tmp_path);poll_log(remote,'t',path,POLICY,now=200)
    local=Store(tmp_path/'local');events=remote.events()
    assert import_events(local,'r',events)['imported']==len(events)
    assert import_events(local,'r',events)['imported']==0
    event=inbox(local)[0];inbox(local,'claim',event['event_id'],'a')
    with pytest.raises(FlowError):inbox(local,'complete',event['event_id'],'b')
    inbox(local,'complete',event['event_id'],'a')
    with pytest.raises(FlowError):import_events(Store(tmp_path/'gap'),'r',events[1:])

def project(tmp_path):
    root=tmp_path/'project';(root/'knowledge').mkdir(parents=True)
    (root/'knowledge/topic.md').write_text('---\nid: topic\ntitle: 通信重叠 overlap\nengine: megatron\nstages: [optimize]\nsources:\n  - source: m\n    path: code.py\n---\n# 通信重叠\nGPU_MAX_HW_QUEUES and memory headroom',encoding='utf-8')
    write_json(root/'knowledge/sources.json',[{'id':'m','repository':'NVIDIA/Megatron-LM','ref':'main','paths':['code.py']}])
    return root

def test_search_filters_and_changed_page(tmp_path):
    root=project(tmp_path);store=Store(tmp_path/'state');wiki.index_wiki(store,root)
    assert wiki.search_wiki(store,'通信重叠',engine='megatron')['results']
    assert not wiki.search_wiki(store,'通信',engine='other')['results']
    (root/'knowledge/topic.md').write_text('changed')
    assert 'changed' in wiki.search_wiki(store,'GPU_MAX_HW_QUEUES')['results'][0]['review_state']

def test_relocated_wiki_rebinds_paths(tmp_path):
    import shutil
    root=project(tmp_path);store=Store(tmp_path/'state');first=wiki.index_wiki(store,root)
    new=tmp_path/'moved';shutil.copytree(root,new);second=wiki.index_wiki(store,new)
    assert first['generation']!=second['generation']
    assert Path(wiki.search_wiki(store,'overlap')['results'][0]['path']).is_relative_to(new)

def test_pr_top_level_reviews_and_pagination(tmp_path,monkeypatch):
    seen=[]
    def get(url,token=None):
        seen.append(url)
        if url.endswith('/pulls/1'):return {'changed_files':1},''
        if '/reviews?' in url:return [{'body':'Please preserve precision','state':'CHANGES_REQUESTED'}],''
        if '/files?' in url:return [{'filename':'a','patch':'diff'}],''
        if 'page=2' in url:return [{'body':'second'}],''
        if '/issues/' in url:return [{'body':'first'}],'<https://api.github.com/repos/NVIDIA/Megatron-LM/issues/1/comments?page=2>; rel="next"'
        return [],''
    monkeypatch.setattr(wiki,'_get_json',get)
    s=Store(tmp_path/'s');result=wiki.collect_pr(s,'NVIDIA/Megatron-LM',1)
    value=json.loads(s.artifact(result['artifact']))
    assert len(value['issue_comments'])==2 and result['reviews']==1

def test_refresh_keeps_pending_and_requires_all_reviews(tmp_path,monkeypatch):
    root=project(tmp_path);store=Store(tmp_path/'state')
    monkeypatch.setattr(wiki,'_get_json',lambda *a:({'sha':'a'*40},''))
    class Response:
        def __enter__(self):return self
        def __exit__(self,*a):pass
        def read(self,*a):return b'code'
    monkeypatch.setattr(wiki.urllib.request,'urlopen',lambda *a,**kw:Response())
    first=wiki.refresh_source(store,root,'m');second=wiki.refresh_source(store,root,'m')
    assert first['affected_pages'] and second['affected_pages']
    with pytest.raises(FlowError):wiki.review_refresh(store,second['stage_id'],{},root)
    decision={'knowledge/topic.md':{'decision':'still-applicable','note':'Reviewed code control flow','page_sha256':digest((root/'knowledge/topic.md').read_bytes()),'source_commit':'a'*40}}
    wiki.review_refresh(store,second['stage_id'],decision,root)
    assert not wiki.refresh_source(store,root,'m')['affected_pages']

def test_public_export_blocks_unreviewed_or_sensitive(tmp_path):
    root=tmp_path/'src';root.mkdir();p=root/'page.md';p.write_text('Authorization: Bearer secret')
    manifest={'reviewed_by':'maintainer','files':[{'path':'page.md','sha256':digest(p.read_bytes())}]}
    with pytest.raises(FlowError):export_public(root,tmp_path/'export',manifest)
    p.write_text('Public explanation');manifest['files'][0]['sha256']=digest(p.read_bytes())
    assert export_public(root,tmp_path/'export',manifest)['files']==1

def test_end_to_end_demo(tmp_path):
    result=run_demo(tmp_path/'demo')
    assert result['command']=='complete' and result['analysis']=='complete' and result['loss_fixture']=='pass'
    assert result['stalled_watch']=='attention' and Path(result['report']).is_file()
