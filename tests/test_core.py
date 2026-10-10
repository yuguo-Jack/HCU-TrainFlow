import json
import sys
import pytest
from hcu_trainflow.core import Store, FlowError, fingerprint
from hcu_trainflow.execution import command_plan, run_command, snapshot, materialize
from hcu_trainflow.coordination import reconcile_operation
from quality_fixtures import stage_report

@pytest.fixture
def store(tmp_path):
    s=Store(tmp_path/'state')
    s.create({'schema_version':1,'task_id':'t','mode':'optimize','objective':'test','context':{'source':'a'},'permissions':['execute']})
    return s

def test_context_invalidates_report(store):
    store.report('t','stage-quality',stage_report(store, store.task('t')['context']))
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


def test_competing_immutable_writers_reuse_verified_object(store, monkeypatch):
    from concurrent.futures import ThreadPoolExecutor
    from pathlib import Path
    import threading
    from hcu_trainflow import core
    operation = 'rename' if core.os.name == 'nt' else 'link'
    original = getattr(core.os, operation)
    original_read = Path.read_bytes
    both = threading.Barrier(2)
    published = threading.Event()
    guard = threading.Lock()
    calls, denied = 0, 0
    payload = b'same complete object'
    def racing_write(source, path):
        nonlocal calls
        with guard:
            slot = calls
            calls += 1
        both.wait(timeout=5)
        if slot == 0:
            original(source, path)
            published.set()
        else:
            assert published.wait(timeout=5)
            error = PermissionError('Synthetic Windows occupied destination')
            error.winerror = 5
            raise error
    def transient_read(path):
        nonlocal denied
        if path.name == core.digest(payload) and published.is_set():
            with guard:
                if denied < 2:
                    denied += 1
                    error = PermissionError('Synthetic Windows sharing violation')
                    error.winerror = 32
                    raise error
        return original_read(path)
    monkeypatch.setattr(core.os, operation, racing_write)
    monkeypatch.setattr(Path, 'read_bytes', transient_read)
    with ThreadPoolExecutor(max_workers=2) as pool:
        jobs = [pool.submit(store.put, payload, visibility)
                for visibility in ('private', 'public')]
        hashes = [job.result(timeout=10) for job in jobs]
    assert calls == 2 and denied == 2
    assert hashes[0] == hashes[1]
    assert store.artifact(hashes[0]) == b'same complete object'
    with store.db() as db:
        assert db.execute('SELECT visibility FROM artifacts WHERE id=?', (hashes[0],)).fetchone()[0] == 'private'


@pytest.mark.parametrize('competing', [None, b'corrupted'])
def test_failed_object_publication_does_not_hide_missing_or_corrupt_target(store, monkeypatch, competing):
    from hcu_trainflow import core
    def failed_write(source, path):
        if competing is not None:
            path.write_bytes(competing)
            raise FileExistsError('Synthetic competing object')
        raise PermissionError('actual publication failure')
    monkeypatch.setattr(core.os, 'rename' if core.os.name == 'nt' else 'link', failed_write)
    expected = PermissionError if competing is None else FlowError
    with pytest.raises(expected):
        store.put(b'expected bytes')
    with store.db() as db:
        assert db.execute('SELECT count(*) FROM artifacts').fetchone()[0] == 0
    assert not list((store.root/'objects').rglob('.write-*'))
    if competing is not None:
        assert (store.root/'objects'/core.digest(b'expected bytes')[:2]/core.digest(b'expected bytes')).read_bytes() == competing


def test_unreadable_competing_object_keeps_publication_error(store, monkeypatch):
    from pathlib import Path
    from hcu_trainflow import core
    original = Path.read_bytes
    error = PermissionError('actual publication failure')
    error.winerror = 5
    attempts = []
    def fail(source, path):
        path.write_bytes(b'expected bytes')
        raise error
    def unreadable(path):
        if 'objects' in path.parts and path.exists():
            attempts.append(path)
            error = PermissionError('object cannot be verified')
            error.winerror = 32
            raise error
        return original(path)
    monkeypatch.setattr(core.os, 'rename' if core.os.name == 'nt' else 'link', fail)
    monkeypatch.setattr(Path, 'read_bytes', unreadable)
    monkeypatch.setattr(core.time, 'sleep', lambda _: None)
    with pytest.raises(PermissionError) as caught:
        store.put(b'expected bytes')
    assert caught.value is error
    assert len(attempts) == len(core._OBJECT_READ_DELAYS) + 1
    with store.db() as db:
        assert db.execute('SELECT count(*) FROM artifacts').fetchone()[0] == 0


def test_real_competing_publications_never_replace_an_object(store, monkeypatch):
    from concurrent.futures import ThreadPoolExecutor
    import threading
    from hcu_trainflow import core
    original = core._publish_object
    both = threading.Barrier(2)
    def simultaneous(path, data):
        both.wait(timeout=5)
        return original(path, data)
    def forbidden_replace(*args):
        pytest.fail('Immutable objects must not replace published bytes')
    monkeypatch.setattr(core, '_publish_object', simultaneous)
    monkeypatch.setattr(core.os, 'replace', forbidden_replace)
    with ThreadPoolExecutor(max_workers=2) as pool:
        jobs = [pool.submit(store.put, b'complete immutable object') for _ in range(2)]
        hashes = [job.result(timeout=10) for job in jobs]
    assert hashes[0] == hashes[1]
    assert store.artifact(hashes[0]) == b'complete immutable object'
    assert not list((store.root/'objects').rglob('.write-*'))


@pytest.mark.parametrize('winerror', [5, 32, 33, None])
def test_artifact_read_retries_only_bounded_windows_conflicts(store, monkeypatch, winerror):
    from pathlib import Path
    from hcu_trainflow import core
    sha = store.put(b'verified reader fixture')
    original = Path.read_bytes
    error = PermissionError('Synthetic reader failure')
    if winerror is not None:
        error.winerror = winerror
    calls, delays = [], []
    def blocked(path):
        if path.name == sha:
            calls.append(path)
            raise error
        return original(path)
    monkeypatch.setattr(Path, 'read_bytes', blocked)
    monkeypatch.setattr(core.time, 'sleep', delays.append)
    with pytest.raises(PermissionError) as caught:
        store.artifact(sha)
    assert caught.value is error
    assert len(calls) == (1 if winerror is None else len(core._OBJECT_READ_DELAYS) + 1)
    assert delays == ([] if winerror is None else list(core._OBJECT_READ_DELAYS))


@pytest.mark.parametrize('corrupt', [False, True])
def test_streamed_artifact_reader_checks_hash_after_transient_conflict(store, monkeypatch, corrupt):
    from pathlib import Path
    from hcu_trainflow import core
    sha = store.put(b'verified reader fixture')
    path = store.root/'objects'/sha[:2]/sha
    if corrupt:
        path.write_bytes(b'corrupted reader bytes')
    original = Path.read_bytes
    attempts = []
    def blocked_once(target):
        if target == path:
            attempts.append(target)
            if len(attempts) == 1:
                error = PermissionError('Synthetic sharing violation')
                error.winerror = 32
                raise error
        return original(target)
    monkeypatch.setattr(Path, 'read_bytes', blocked_once)
    monkeypatch.setattr(core.time, 'sleep', lambda _: None)
    if corrupt:
        with pytest.raises(FlowError, match='hash mismatch'):
            list(store.iter_artifacts([sha]))
        assert original(path) == b'corrupted reader bytes'
    else:
        assert list(store.iter_artifacts([sha])) == [(sha, b'verified reader fixture')]
    assert len(attempts) == 2


@pytest.mark.parametrize('failure', ['permission', 'disk-full', 'io', 'unsupported-link'])
def test_real_publication_failures_are_not_masked_by_matching_competitor(store, monkeypatch, failure):
    import errno
    from hcu_trainflow import core
    errors = {'permission': PermissionError(errno.EACCES, 'permission'),
              'disk-full': OSError(errno.ENOSPC, 'disk-full'),
              'io': OSError(errno.EIO, 'io'),
              'unsupported-link': OSError(errno.EOPNOTSUPP, 'unsupported-link')}
    error = errors[failure]
    def fail(source, path):
        # Even a valid competitor does not excuse an unrelated I/O failure.
        path.write_bytes(b'expected bytes')
        raise error
    monkeypatch.setattr(core.os, 'rename' if core.os.name == 'nt' else 'link', fail)
    with pytest.raises(OSError) as caught:
        store.put(b'expected bytes')
    assert caught.value is error
    with store.db() as db:
        assert db.execute('SELECT count(*) FROM artifacts').fetchone()[0] == 0
    assert not list((store.root/'objects').rglob('.write-*'))


@pytest.mark.parametrize('unsupported', [False, True])
def test_posix_object_publication_uses_no_clobber_hardlink(store, monkeypatch, unsupported):
    import errno
    from types import SimpleNamespace
    from hcu_trainflow import core
    # Exercise the POSIX branch also on Windows without changing global os.name.
    proxy = SimpleNamespace(**vars(core.os))
    proxy.name = 'posix'
    calls = []
    original_link = core.os.link
    error = OSError(errno.EOPNOTSUPP, 'Filesystem does not support hard links')
    def link(source, path):
        calls.append((source, path))
        if unsupported:
            raise error
        return original_link(source, path)
    def overwrite(*args):
        pytest.fail('No rename/replace fallback is allowed for POSIX CAS')
    proxy.link, proxy.rename, proxy.replace = link, overwrite, overwrite
    monkeypatch.setattr(core, 'os', proxy)
    if unsupported:
        with pytest.raises(OSError) as caught:
            store.put(b'POSIX publication fixture')
        assert caught.value is error
        with store.db() as db:
            assert db.execute('SELECT count(*) FROM artifacts').fetchone()[0] == 0
    else:
        sha = store.put(b'POSIX publication fixture')
        path = store.root/'objects'/sha[:2]/sha
        # A staged competing publication must verify, not replace, that inode.
        inode = path.stat().st_ino
        core._publish_object(path, b'POSIX publication fixture')
        assert path.stat().st_ino == inode
        assert store.artifact(sha) == b'POSIX publication fixture'
    assert len(calls) == (1 if unsupported else 2)
    assert not list((store.root/'objects').rglob('.write-*'))


def test_failed_object_fsync_does_not_publish_or_register(store, monkeypatch):
    import errno
    from hcu_trainflow import core
    error = OSError(errno.EIO, 'Synthetic staged-file fsync failure')
    def fail(fd):
        raise error
    monkeypatch.setattr(core.os, 'fsync', fail)
    with pytest.raises(OSError) as caught:
        store.put(b'not durable')
    assert caught.value is error
    assert not list((store.root/'objects').rglob('.write-*'))
    assert not (store.root/'objects'/core.digest(b'not durable')[:2]/core.digest(b'not durable')).exists()
    with store.db() as db:
        assert db.execute('SELECT count(*) FROM artifacts').fetchone()[0] == 0

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
