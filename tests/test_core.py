import json
import sys
import pytest
from hcu_trainflow.core import Store, FlowError, fingerprint
from hcu_trainflow.execution import command_plan, run_command, snapshot, materialize
from hcu_trainflow.coordination import reconcile_operation

@pytest.fixture
def store(tmp_path):
    s=Store(tmp_path/'state')
    s.create({'schema_version':1,'task_id':'t','mode':'optimize','objective':'test','context':{'source':'a'},'permissions':['execute']})
    return s

def test_context_invalidates_report(store):
    sha=store.put(b'proof')
    store.report('t','stage-quality',{'context':store.task('t')['context'],'status':'pass','executed':1,'evidence':[sha]})
    store.change_context('t',{'source':'b'})
    with pytest.raises(FlowError):store.transition('t','completed')

@pytest.mark.parametrize('changes',[{'executed':0},{'failures':1},{'required_missing':['rank1']},{'context':'wrong'},{'evidence':[]}])
def test_report_rejects_invalid_pass(store,changes):
    value={'context':store.task('t')['context'],'status':'pass','executed':1,'evidence':[store.put(b'proof')]}
    with pytest.raises(FlowError):store.report('t','baseline',{**value,**changes})

def test_lease_fencing(store):
    first=store.lease('gpu','a')
    with pytest.raises(FlowError):store.lease('gpu','b')
    store.release(first);second=store.lease('gpu','b')
    assert second['token']>first['token']
    with pytest.raises(FlowError):store.renew(first)

def test_idempotent_command_and_snapshot(store,tmp_path):
    src=tmp_path/'repo';src.mkdir();(src/'test.py').write_text("print('ok')")
    snap=snapshot(store,src,['test.py']);dest=tmp_path/'out';materialize(store,snap['snapshot_id'],dest)
    card={'schema_version':1,'argv':[sys.executable,'test.py'],'cwd':str(dest),'basis':'test','timeout_seconds':5}
    lease=store.lease('cpu','a')
    one=run_command(store,'t','op',card,lease);two=run_command(store,'t','op',card,lease)
    assert one==two and one['returncode']==0
    with pytest.raises(FlowError):run_command(store,'t','op',{**card,'argv':[sys.executable,'--version']},lease)
    with pytest.raises(FlowError):materialize(store,snap['snapshot_id'],dest)

def test_unresolved_operation_blocks_new(store,tmp_path):
    with store.db() as db:db.execute("INSERT INTO operations VALUES('lost','t','x','started',NULL,'now')")
    lease=store.lease('cpu','a')
    card={'schema_version':1,'argv':[sys.executable,'--version'],'cwd':str(tmp_path),'basis':'test','timeout_seconds':5}
    with pytest.raises(FlowError):run_command(store,'t','new',card,lease)
    reconcile_operation(store,'lost','failed',[store.put(b'pid absent')],'Verified process ended')
    assert run_command(store,'t','new',card,lease)['status']=='complete'

def test_paths_and_artifact_integrity(store,tmp_path):
    with pytest.raises(FlowError):snapshot(store,tmp_path,['../outside'])
    with pytest.raises(FlowError):materialize(store,'../bad',tmp_path/'out')
    sha=store.put(b'x');store.put(b'x','public')
    with store.db() as db:assert db.execute('SELECT visibility FROM artifacts WHERE id=?',(sha,)).fetchone()[0]=='private'
    (store.root/'objects'/sha[:2]/sha).write_bytes(b'changed')
    with pytest.raises(FlowError):store.artifact(sha)

@pytest.mark.parametrize('backend',['ssh','ssh-docker','ssh-slurm','k8s'])
def test_remote_command_quoting(backend):
    card={'schema_version':1,'backend':backend,'argv':['python','file name.py','a; echo bad'], 'cwd':'/work/a b','env':{'X':'x;danger'},'basis':'reviewed','ssh_target':'site','container':'train','allocation':'123','pod':'worker','namespace':'train'}
    plan=command_plan(card)
    assert 'a; echo bad' in plan['argv'][-1] and plan['cwd'] is None

def test_event_id_collision(store):
    with store.db() as db:store.event(db,'t','observation',{'x':1},'unique')
    with pytest.raises(FlowError):
        with store.db() as db:store.event(db,'t','observation',{'x':2},'unique')
