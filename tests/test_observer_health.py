import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time

import pytest

from hcu_trainflow.core import FlowError, Store, fingerprint, write_json
from hcu_trainflow.observer_health import capture_sources, evaluate, record_health, validate_contract


@pytest.fixture
def site(tmp_path):
    root = tmp_path / 'source'
    run = root / 'observer/launches/l1'
    observer = {'pid': 20, 'start_ticks': '100', 'boot_id': 'source-boot', 'pid_namespace': 'pid:[1]'}
    training = {**observer, 'pid': 10, 'start_ticks': '90'}
    manifest = {'schema_version': 1, 'attempt_id': 'a1', 'context': 'context', 'process': training,
                'started_at': 90, 'start_step': 0, 'expected_final_step': 3, 'log_start_offset': 0,
                'log_path': str(root / 'train.log'), 'log_timezone': 'UTC'}
    spec = {'workspace': str(root / 'store'), 'task': 'train', 'state_dir': str(root / 'observer'),
            'manifest': str(root / 'manifest.json'), 'manifest_hash': fingerprint(manifest),
            'policy': str(root / 'policy.json'), 'policy_hash': 'a' * 64, 'interval_seconds': 5,
            'exit_receipt': str(root / 'training-exit.json'), 'attempt_id': 'a1', 'context': 'context'}
    expected = {'launch_id': 'l1', 'spec_hash': fingerprint(spec), 'observer_process': observer,
                'attempt_id': 'a1', 'manifest_hash': fingerprint(manifest), 'observer_started_at': 100,
                'training_process': training, 'attempt_started_at': 90, 'expected_final_step': 3, 'start_step': 0}
    contract = {'schema_version': 1, 'observer_id': 'health-a1', 'task_id': 'train', 'context': 'context',
                'context_epoch': 7, 'source_domain': 'host-a', 'observer_domain': 'host-b',
                'source_root': str(root), 'source_workspace': spec['workspace'], 'record_path': str(root / 'observer-process.json'),
                'manifest_path': spec['manifest'], 'training_exit_path': spec['exit_receipt'], 'lifecycle_dir': str(run),
                'expected': expected, 'policy': {'heartbeat_max_age_seconds': 10, 'startup_timeout_seconds': 20,
                                                'source_read_timeout_seconds': 0.1}}
    binding = {'launch_id': 'l1', 'spec_hash': fingerprint(spec), 'process': observer, 'attempt_id': 'a1', 'context': 'context'}
    heartbeat = {**binding, 'checked_at': 110, 'result': {'status': 'healthy-observed', 'monitor': {
        'task_id': 'train', 'context': 'context', 'context_epoch': 7, 'checked_at': 109,
        'status': 'healthy-observed', 'issues': [], 'completion_verified': False,
        'last_observation': {'attempt_id': 'a1', 'context': 'context', 'step': 1, 'phase': 'training', 'completed': False}}}}
    write_json(Path(contract['record_path']), {'schema_version': 1, 'launch_id': 'l1', 'spec': spec,
        'spec_hash': fingerprint(spec), 'process': observer, 'started_at': 100, 'run_dir': str(run)})
    write_json(Path(spec['manifest']), manifest)
    write_json(run / 'request.json', {'schema_version': 1, 'launch_id': 'l1', 'spec': spec})
    write_json(run / 'identity.json', binding)
    write_json(run / 'heartbeat.json', heartbeat)
    store = Store(tmp_path / 'sentinel-local')
    return contract, store, heartbeat, binding


def health(site, now=111):
    contract, store, _, _ = site
    return record_health(store, contract, capture_sources(contract), now=now)


def test_observing_does_not_create_a_training_task_or_claim_recovery(site):
    value = health(site)
    assert value['status'] == 'observing'
    assert value['completion_verified'] is False
    assert value['recovery_action'] == 'none'
    assert value['notification_delivery'] == 'not configured'
    with site[1].db() as db:
        assert db.execute('SELECT COUNT(*) FROM tasks').fetchone()[0] == 0


def test_disappearance_dedup_and_fresh_recovery(site):
    contract, store, heartbeat, _ = site
    assert health(site)['status'] == 'observing'
    assert health(site, 121)['status'] == 'attention'
    health(site, 122)
    events = [e for e in store.events() if e['kind'] == 'incident-opened']
    assert len(events) == 1 and events[0]['payload']['kind'] == 'observer-heartbeat-stale'
    heartbeat['checked_at'] = 123
    heartbeat['result']['monitor']['checked_at'] = 123
    write_json(Path(contract['lifecycle_dir']) / 'heartbeat.json', heartbeat)
    assert health(site, 124)['status'] == 'observing'
    assert len([e for e in store.events() if e['kind'] == 'incident-cleared']) == 1
    health(site, 125)
    assert len([e for e in store.events() if e['kind'] == 'incident-cleared']) == 1
    with store.db() as db:
        assert db.execute('SELECT COUNT(*) FROM outbox').fetchone()[0] == 2


def test_missing_cfs_does_not_clear_existing_stale_alert(site):
    contract, store, _, _ = site
    health(site, 121)
    result = record_health(store, contract, {'error': 'source-read-timeout', 'files': {}}, now=122)
    assert result['status'] == 'attention'
    assert 'observer-heartbeat-stale' in result['unresolved_incidents']
    assert not any(e['kind'] == 'incident-cleared' for e in store.events())


def test_startup_has_independent_deadline(site):
    contract = site[0]
    (Path(contract['lifecycle_dir']) / 'heartbeat.json').unlink()
    assert health(site, 115)['status'] == 'starting'
    result = health(site, 121)
    assert {i['kind'] for i in result['issues']} == {'observer-startup-timeout'}


def test_missing_heartbeat_after_success_never_reenters_startup(site):
    health(site)
    (Path(site[0]['lifecycle_dir']) / 'heartbeat.json').unlink()
    result = health(site, 121)
    assert {i['kind'] for i in result['issues']} == {'observer-heartbeat-missing'}


@pytest.mark.parametrize('field,value', [('launch_id', 'old'), ('process', {'pid': 20}), ('attempt_id', 'old'), ('context', 'old')])
def test_wrong_lifecycle_identity_never_healthy(site, field, value):
    contract, _, heartbeat, _ = site
    heartbeat[field] = value
    write_json(Path(contract['lifecycle_dir']) / 'heartbeat.json', heartbeat)
    assert 'observer-source-identity-mismatch' in {i['kind'] for i in health(site)['issues']}


@pytest.mark.parametrize('epoch', [6, True, '7'])
def test_epoch_exact_and_typed(site, epoch):
    contract, _, heartbeat, _ = site
    heartbeat['result']['monitor']['context_epoch'] = epoch
    write_json(Path(contract['lifecycle_dir']) / 'heartbeat.json', heartbeat)
    assert health(site)['status'] == 'attention'


def terminal(site):
    contract, _, heartbeat, binding = site
    receipt = {'attempt_id': 'a1', 'context': 'context', 'process': contract['expected']['training_process'],
               'finished_at': 120, 'exit_code': 0}
    write_json(Path(contract['training_exit_path']), receipt)
    heartbeat['checked_at'] = 124
    monitor = heartbeat['result']['monitor']
    monitor.update(checked_at=123, completion_verified=True)
    monitor['last_observation'].update(step=3, phase='finished', completed=True, exit_receipt=receipt,
        expected_final_step=3, process_identity=contract['expected']['training_process'], loss=1.0,
        timestamp=123, job_alive=False)
    write_json(Path(contract['lifecycle_dir']) / 'heartbeat.json', heartbeat)
    write_json(Path(contract['lifecycle_dir']) / 'observer-exit.json', {
        **binding, 'finished_at': 125, 'exit_code': 0, 'reason': 'training-completion-verified'})


def test_legitimate_old_completed_is_terminal_but_current_source_must_remain_valid(site):
    terminal(site)
    assert health(site, 10000)['completion_verified'] is True
    Path(site[0]['manifest_path']).unlink()
    assert health(site, 10001)['status'] == 'attention'
    assert health(site, 10002)['completion_verified'] is False


@pytest.mark.parametrize('mutation', ['new-record', 'epoch', 'exit-missing', 'exit-nonzero', 'step-short', 'observer-killed', 'nonfinite'])
def test_stale_completed_cannot_mask_failures(site, mutation):
    terminal(site)
    contract, _, heartbeat, binding = site
    if mutation == 'new-record':
        path = Path(contract['record_path']); value = json.loads(path.read_text()); value['launch_id'] = 'new'; write_json(path, value)
    elif mutation == 'epoch':
        heartbeat['result']['monitor']['context_epoch'] += 1
    elif mutation == 'exit-missing':
        Path(contract['training_exit_path']).unlink()
    elif mutation == 'exit-nonzero':
        path = Path(contract['training_exit_path']); value = json.loads(path.read_text()); value['exit_code'] = 1; write_json(path, value)
    elif mutation == 'step-short':
        heartbeat['result']['monitor']['last_observation']['step'] = 2
    elif mutation == 'nonfinite':
        heartbeat['result']['monitor']['last_observation']['loss'] = 'nan'
    else:
        write_json(Path(contract['lifecycle_dir']) / 'observer-exit.json', {
            **binding, 'finished_at': 125, 'exit_code': 143, 'reason': 'observer-stop-requested'})
    write_json(Path(contract['lifecycle_dir']) / 'heartbeat.json', heartbeat)
    result = health(site, 10000)
    assert result['status'] == 'attention' and result['completion_verified'] is False


def test_source_and_observer_clock_watermarks_do_not_reset_after_regression(site):
    contract, _, heartbeat, _ = site
    health(site, 112)
    assert 'observer-health-clock-regressed' in {i['kind'] for i in health(site, 111)['issues']}
    assert 'observer-health-clock-regressed' in {i['kind'] for i in health(site, 111.5)['issues']}
    heartbeat['checked_at'] = 109
    write_json(Path(contract['lifecycle_dir']) / 'heartbeat.json', heartbeat)
    assert 'observer-source-clock-invalid' in {i['kind'] for i in health(site, 113)['issues']}


@pytest.mark.parametrize('value', [True, None, float('inf'), 99999])
def test_bad_or_future_heartbeat_is_unknown_not_a_dead_process_claim(site, value):
    contract, _, heartbeat, _ = site
    heartbeat['checked_at'] = value
    # Exercise evaluator directly for nonfinite input; file reader rejects it.
    bundle = capture_sources(contract); bundle['files']['heartbeat']['value'] = heartbeat
    result = evaluate(contract, bundle, now=111)
    assert result['status'] == 'attention'
    assert result['remote_process_liveness'].startswith('not directly probed')


def test_capture_bad_json_and_size_are_read_errors(site):
    path = Path(site[0]['lifecycle_dir']) / 'heartbeat.json'
    for raw in ('[]', '{"checked_at":NaN}', '{partial'):
        path.write_text(raw)
        assert capture_sources(site[0])['files']['heartbeat']['status'] == 'error'
    path.write_text('{"long":"' + 'x' * 500 + '"}')
    assert capture_sources(site[0], max_bytes=100)['files']['heartbeat']['status'] == 'error'


def test_changed_contract_and_shared_store_refused(site):
    contract, store, _, _ = site
    health(site)
    changed = copy.deepcopy(contract); changed['policy']['heartbeat_max_age_seconds'] = 20
    with pytest.raises(FlowError, match='Pinned observer contract changed'):
        record_health(store, changed, capture_sources(changed), now=112)
    with pytest.raises(FlowError, match='separate Store'):
        record_health(Store(Path(contract['source_workspace'])), contract, capture_sources(contract), now=112)


@pytest.mark.parametrize('invalid', [None, [], 'bad'])
def test_malformed_monitor_never_crashes_or_passes(site, invalid):
    contract, _, heartbeat, _ = site
    heartbeat['result']['monitor'] = invalid
    write_json(Path(contract['lifecycle_dir']) / 'heartbeat.json', heartbeat)
    assert health(site)['status'] == 'attention'


def test_future_clock_is_not_silently_tolerated(site):
    contract, _, heartbeat, _ = site
    heartbeat['checked_at'] = 111.001
    write_json(Path(contract['lifecycle_dir']) / 'heartbeat.json', heartbeat)
    value = health(site, 111)
    assert 'observer-source-clock-invalid' in {i['kind'] for i in value['issues']}
    assert value['status'] == 'attention'


def test_does_not_stat_remote_source_during_contract_validation(site, monkeypatch):
    monkeypatch.setattr(Path, 'resolve', lambda *a, **k: pytest.fail('remote source stat in sentinel process'))
    validate_contract(site[0])


def test_posix_contract_can_be_reviewed_on_windows_without_stat(site):
    contract = copy.deepcopy(site[0])
    root = contract['source_root']
    for key in ('source_root', 'source_workspace', 'record_path', 'manifest_path', 'training_exit_path', 'lifecycle_dir'):
        contract[key] = '/task-source' + contract[key][len(root):].replace('\\', '/')
    validate_contract(contract)


def test_invalid_failure_domain_and_source_escape_refused(site):
    contract = copy.deepcopy(site[0]); contract['observer_domain'] = contract['source_domain']
    with pytest.raises(FlowError): validate_contract(contract)
    contract = copy.deepcopy(site[0]); contract['record_path'] = str(Path(contract['source_root']).parent / 'outside.json')
    with pytest.raises(FlowError): validate_contract(contract)


def load_script():
    path = Path(__file__).resolve().parents[1] / 'scripts/observe_remote_health.py'
    spec = importlib.util.spec_from_file_location('remote_health_script', path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def test_reader_timeout_is_bounded_and_only_its_child_is_signalled(tmp_path):
    module = load_script()
    sleeper = tmp_path / 'sleeper.py'; sleeper.write_text('import time; time.sleep(30)')
    reader = module.BoundedReader(tmp_path / 'readers', 0.1, script=sleeper)
    started = time.monotonic()
    result = reader.collect(tmp_path / 'unused.json')
    assert time.monotonic() - started < 3
    assert result['error'].startswith('source-read-timeout')
    assert reader.state_path.exists()
    reader.pending.wait(timeout=3)  # owned, killable fixture only, not production NFS


def test_unresolved_previous_reader_never_spawns_more(tmp_path, monkeypatch):
    module = load_script()
    reader = module.BoundedReader(tmp_path, 0.1)
    identity = {'pid': 123, 'start_ticks': '10', 'boot_id': 'b', 'pid_namespace': 'p'}
    write_json(reader.state_path, {'process': identity})
    monkeypatch.setattr(module, 'process_identity', lambda pid: {'status': 'alive', 'identity': identity})
    monkeypatch.setattr(module.subprocess, 'Popen', lambda *a, **k: pytest.fail('must not spawn'))
    assert reader.collect(tmp_path / 'config.json')['error'].startswith('previous-source-reader-still-running')
