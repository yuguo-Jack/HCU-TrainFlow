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


@pytest.mark.parametrize('result', [None, {'seconds':1, 'status':'unknown'}, {'seconds':15, 'status':'unknown'}])
def test_reconciliation_preserves_timeout_budget(store, tmp_path, result):
    lease = store.lease('cpu', 'audit')
    with store.db() as db:
        spec = store.task('t')['spec']
        spec['budget'] = {'max_seconds':10}
        db.execute("UPDATE tasks SET spec=? WHERE id='t'", (json.dumps(spec),))
        db.execute("INSERT INTO operations VALUES('lost','t','hash','started',?,'now')",
                   (json.dumps(result) if result else None,))
        store.event(db, 't', 'operation-started', {'operation':'lost', 'lease':lease, 'timeout_seconds':10})
    reconciled = reconcile_operation(store, 'lost', 'complete', [store.put(b'Original operation confirmed ended')],
                                    'Controller lost its result; verified terminal outcome')
    assert reconciled['budget_seconds'] == max(10, result['seconds'] if result else 0)
    assert reconciled.get('seconds') == (result['seconds'] if result else None)
    card = {'schema_version':1, 'argv':[sys.executable, '--version'], 'cwd':str(tmp_path),
            'timeout_seconds':1, 'basis':'Local budget fixture'}
    with pytest.raises(FlowError, match='remaining execution budget'):
        run_command(store, 't', 'overspend', card, lease)


def test_legacy_reconciled_result_cannot_erase_timeout_budget(store, tmp_path):
    lease = store.lease('cpu', 'audit')
    with store.db() as db:
        spec = store.task('t')['spec']
        spec['budget'] = {'max_seconds':10}
        db.execute("UPDATE tasks SET spec=? WHERE id='t'", (json.dumps(spec),))
        db.execute("INSERT INTO operations VALUES('legacy','t','hash','complete',?,'now')",
                   (json.dumps({'status':'complete', 'reconciliation':{'note':'Old terminal receipt'}}),))
        store.event(db, 't', 'operation-started', {'operation':'legacy', 'lease':lease, 'timeout_seconds':10})
    card = {'schema_version':1, 'argv':[sys.executable, '--version'], 'cwd':str(tmp_path),
            'timeout_seconds':1, 'basis':'Local budget fixture'}
    with pytest.raises(FlowError, match='remaining execution budget'):
        run_command(store, 't', 'overspend', card, lease)


def _reserve_assignment(store, scope='assignment'):
    from hcu_trainflow import team
    spec = {'id':'worker', 'owner':'worker-owner', 'goal':'Check fixture', 'scope':'Local execution fixture',
            'allowed_paths':['.'], 'acceptance':'Retain result', 'mode':'read', 'resources':['cpu'],
            'resource_scope':scope, 'budget':{'max_seconds':10}, 'context':store.task('t')['context']}
    team.plan(store, 't', {'rationale':'Local reservation fixture', 'max_parallel':1, 'assignments':[spec]})
    return team.claim(store, 'worker', 'worker-owner')


def test_assignment_budget_retains_reconciled_runtime(store, tmp_path):
    claim = _reserve_assignment(store)
    lease = store.lease('cpu', 'worker-owner')
    with store.db() as db:
        db.execute("INSERT INTO operations VALUES('lost','t','hash','started',NULL,'now')")
        db.execute("INSERT INTO assignment_operations VALUES('lost','worker',?)", (claim['token'],))
        store.event(db, 't', 'operation-started', {'operation':'lost', 'lease':lease, 'timeout_seconds':10})
    reconcile_operation(store, 'lost', 'complete', [store.put(b'Ended')], 'Verified terminal fixture')
    card = {'schema_version':1, 'argv':[sys.executable, '--version'], 'cwd':str(tmp_path),
            'timeout_seconds':1, 'basis':'Local assignment budget fixture'}
    with pytest.raises(FlowError, match='Assignment execution budget exhausted'):
        run_command(store, 't', 'overspend', card, lease,
                    assignment='worker', owner='worker-owner', token=claim['token'])


@pytest.mark.parametrize('target', ['t', 'other'])
def test_unassigned_execution_cannot_bypass_claimed_resource(store, tmp_path, target):
    claim = _reserve_assignment(store)
    if target == 'other':
        store.create({'schema_version':1, 'task_id':target, 'mode':'analyze', 'objective':'Other local fixture',
                      'context':{'fixture':'other'}, 'permissions':['execute']})
    lease = store.lease('cpu', 'worker-owner')
    card = {'schema_version':1, 'argv':[sys.executable, '--version'], 'cwd':str(tmp_path),
            'timeout_seconds':1, 'basis':'Local resource fixture'}
    with pytest.raises(FlowError, match='reserved by a claimed assignment'):
        run_command(store, target, 'unassigned', card, lease)
    assert run_command(store, 't', 'assigned', card, lease, assignment='worker',
                       owner='worker-owner', token=claim['token'])['status'] == 'complete'


def test_operation_scope_resource_remains_available_between_commands(store, tmp_path):
    _reserve_assignment(store, scope='operation')
    lease = store.lease('cpu', 'controller')
    card = {'schema_version':1, 'argv':[sys.executable, '--version'], 'cwd':str(tmp_path),
            'timeout_seconds':1, 'basis':'Local resource sharing fixture'}
    assert run_command(store, 't', 'shared', card, lease)['status'] == 'complete'


def test_execution_identity_does_not_reuse_result_after_context_returns(store, tmp_path):
    lease = store.lease('cpu', 'controller')
    card = {'schema_version':1, 'argv':[sys.executable, '--version'], 'cwd':str(tmp_path),
            'timeout_seconds':1, 'basis':'Local context fixture'}
    run_command(store, 't', 'original', card, lease)
    store.change_context('t', {'source':'b'})
    store.change_context('t', {'source':'a'})
    with pytest.raises(FlowError, match='different request'):
        run_command(store, 't', 'original', card, lease)
    assert run_command(store, 't', 'current', card, lease)['status'] == 'complete'


def test_execution_admission_detects_context_reset_race(store, tmp_path, monkeypatch):
    from hcu_trainflow import execution
    original = execution.command_plan
    def reset_context(card):
        plan = original(card)
        store.change_context('t', {'source':'b'})
        store.change_context('t', {'source':'a'})
        return plan
    monkeypatch.setattr(execution, 'command_plan', reset_context)
    card = {'schema_version':1, 'argv':[sys.executable, '--version'], 'cwd':str(tmp_path),
            'timeout_seconds':1, 'basis':'Local context fixture'}
    with pytest.raises(FlowError, match='context/state changed'):
        run_command(store, 't', 'raced', card, store.lease('cpu', 'controller'))
