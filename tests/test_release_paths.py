import json
import subprocess
import sys
import zipfile
from pathlib import Path
import pytest
from hcu_trainflow.core import Store, FlowError, write_json
from hcu_trainflow.execution import snapshot, bundle, receive, run_command
from hcu_trainflow.coordination import dispatch_inbox
from hcu_trainflow.monitor import inbox
from hcu_trainflow.cli import main

def task(tmp_path):
    s=Store(tmp_path/'s');s.create({'schema_version':1,'task_id':'t','mode':'operate','objective':'test','context':{'s':'1'},'permissions':['execute','agent-dispatch']})
    return s

def test_bundle_roundtrip_and_tamper(tmp_path):
    s=task(tmp_path);p=tmp_path/'source';p.mkdir();(p/'a.py').write_text('print(1)')
    snap=snapshot(s,p,['a.py']);archive=tmp_path/'bundle.zip';bundle(s,snap['snapshot_id'],archive)
    remote=Store(tmp_path/'remote');result=receive(remote,archive,tmp_path/'received')
    assert result['verified'] and (tmp_path/'received/a.py').read_text()=='print(1)'
    bad=tmp_path/'bad.zip'
    with zipfile.ZipFile(archive) as z,zipfile.ZipFile(bad,'w') as out:
        for name in z.namelist():out.writestr(name,b'bad' if name.startswith('files/') else z.read(name))
    with pytest.raises(FlowError):receive(remote,bad,tmp_path/'bad-out')
    assert not (tmp_path/'bad-out').exists()

def test_expired_lease_with_running_operation_cannot_transfer(tmp_path):
    s=task(tmp_path);lease=s.lease('gpu','old')
    with s.db() as db:
        db.execute("INSERT INTO operations VALUES('in-flight','t','hash','started',NULL,'now')")
        s.event(db,'t','operation-started',{'operation':'in-flight','lease':lease})
        db.execute("UPDATE leases SET expires=0")
    with pytest.raises(FlowError):s.lease('gpu','new')

def test_same_lease_cannot_bypass_cross_task_resource_serialization(tmp_path):
    s=task(tmp_path);lease=s.lease('gpu','controller')
    s.create({'schema_version':1,'task_id':'other','mode':'analyze','objective':'test','context':{'s':'2'},'permissions':['execute']})
    with s.db() as db:
        db.execute("INSERT INTO operations VALUES('in-flight','t','hash','started',NULL,'now')")
        s.event(db,'t','operation-started',{'operation':'in-flight','lease':lease})
    card={'schema_version':1,'argv':[sys.executable,'--version'],'cwd':str(tmp_path),'basis':'test','timeout_seconds':5}
    with pytest.raises(FlowError):run_command(s,'other','bypass',card,lease)

def test_timeout_is_not_safe_retry(tmp_path):
    s=task(tmp_path);lease=s.lease('cpu','owner')
    result=run_command(s,'t','slow',{'schema_version':1,'argv':[sys.executable,'-c','import time;time.sleep(5)'],'cwd':str(tmp_path),'basis':'test','timeout_seconds':0.05},lease)
    assert result['status']=='unknown'
    with pytest.raises(FlowError):s.lease('cpu','other')

def test_agent_bridge_does_not_claim_resolution(tmp_path):
    s=task(tmp_path)
    with s.db() as db:eid=s.event(db,'t','incident-opened',{'kind':'training-stalled','context':s.task('t')['context']},channel='agent')
    card={'schema_version':1,'argv':[sys.executable,'-c','import sys,pathlib; assert pathlib.Path(sys.argv[-1]).is_file()'],'cwd':str(tmp_path),'basis':'local fake bridge','timeout_seconds':10}
    result=dispatch_inbox(s,eid,'consumer',card,s.lease('bridge','controller'))
    assert result['status']=='complete' and result['incident_resolution']=='pending-consumer-ack'
    assert inbox(s)[0]['status']=='claimed'

def test_stale_event_cannot_launch_bridge(tmp_path):
    s=task(tmp_path)
    with s.db() as db:eid=s.event(db,'t','incident-opened',{'kind':'training-stalled','context':'previous-context'},channel='agent')
    with pytest.raises(FlowError):dispatch_inbox(s,eid,'consumer',{},s.lease('bridge','controller'))
    assert inbox(s)[0]['status']=='pending'

def test_cli_incomplete_exit_and_output(tmp_path,capsys):
    p=tmp_path/'groups.json';write_json(p,{'groups':[{'domain':'tp','ranks':[0,1]}],'available':[0]})
    assert main(['--workspace',str(tmp_path/'w'),'profile-plan',str(p)])==2
    assert json.loads(capsys.readouterr().out)['status']=='incomplete'

def test_skill_install_idempotent_and_cleans_successful_backup(tmp_path):
    script=Path(__file__).resolve().parents[1]/'scripts/install_skills.py';target=tmp_path/'skills'
    # These tests exercise workflow replacement, independent of local private
    # dependency checkouts. Full required installation has separate fixtures.
    cmd=[sys.executable,str(script),'--target',str(target),'--workflow-only']
    assert subprocess.run(cmd,capture_output=True).returncode==0
    assert subprocess.run(cmd,capture_output=True).returncode==0
    changed=target/'hcu-train-environment-check-and-adapt/SKILL.md';changed.write_text('local modified')
    assert subprocess.run(cmd,capture_output=True).returncode!=0
    assert subprocess.run(cmd+['--replace'],capture_output=True).returncode==0
    assert not list((tmp_path/'trainflow-skill-backups').rglob('SKILL.md'))
    assert changed.read_bytes() == (script.parent.parent/'skills/hcu-train-environment-check-and-adapt/SKILL.md').read_bytes()


@pytest.mark.parametrize('old_name,new_name', [
    ('hcu-train-adapt','hcu-train-environment-check-and-adapt'),
    ('hcu-train-fault-tolerance','hcu-train-scale-and-stability'),
    ('hcu-train-prepare','hcu-train-environment-check-and-adapt'),
    ('hcu-train-operate','hcu-train-scale-and-stability'),
    ('hcu-engine-wiki-update','hcu-engine-wiki-skill-update'),
])
def test_skill_rename_removes_obsolete_entry_after_verified_replacement(tmp_path,old_name,new_name):
    script=Path(__file__).resolve().parents[1]/'scripts/install_skills.py';target=tmp_path/'skills'
    old=target/old_name;old.mkdir(parents=True)
    (old/'SKILL.md').write_text('old local customization')
    cmd=[sys.executable,str(script),'--target',str(target),'--workflow-only']
    assert subprocess.run(cmd,capture_output=True).returncode != 0
    assert not (target/'hcu-trainflow').exists()  # validate before any mutation
    assert subprocess.run(cmd+['--replace'],capture_output=True).returncode == 0
    assert not old.exists() and (target/new_name/'SKILL.md').is_file()
    assert f'name: {new_name}' in (target/new_name/'SKILL.md').read_text(encoding='utf8')
    assert (target/'hcu-train-scale-and-stability/SKILL.md').is_file()
    backups=list((tmp_path/'trainflow-skill-backups').rglob(old_name+'/SKILL.md'))
    assert not backups

def test_public_wiki_integrity():
    import importlib.util
    root=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('validator',root/'scripts/validate_knowledge.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    result=m.validate(root)
    assert not result['errors']

def test_wiki_real_queries(tmp_path):
    from hcu_trainflow.wiki import index_wiki,search_wiki
    root=Path(__file__).resolve().parents[1];s=Store(tmp_path/'wiki');result=index_wiki(s,root)
    assert result['pages']>=30
    cases=[('GPU_MAX_HW_QUEUES','official-megatron-wiki/overlap'),('hook compile','ecosystem/cases/primus-compile-ddp'),('逐层重算','ecosystem/cases/primus-layer-recompute'),('run_nhc','tooling/cluster-manager'),('loss mask','official-megatron-wiki/training-and-loss'),('恢复 checkpoint','official-megatron-wiki/checkpoint')]
    for query,expected in cases:
        assert expected in [x['id'] for x in search_wiki(s,query,10)['results']],query
