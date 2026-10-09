"""Synthetic CPU contracts; these tests are not HCU training acceptance."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

from hcu_trainflow.core import FlowError, fingerprint, read_json, write_json
from hcu_trainflow.distributed_observation import aggregate_members, collect_member, validate_group


def fixture(tmp_path):
    manifests, paths, exits = {}, {}, {}
    for i in range(2):
        mid = 'node' + str(i)
        root = tmp_path / mid
        root.mkdir()
        log = root / 'training.log'
        log.write_text('Synthetic CPU fixture: wrapper started\n', encoding='utf8')
        manifests[mid] = {'schema_version': 1, 'context': 'context-a', 'attempt_id': 'attempt-' + mid,
            'log_path': str(log), 'log_start_offset': 0, 'start_step': 0, 'expected_final_step': 6,
            'started_at': 100.0, 'log_timezone': 'UTC',
            'process': {'pid': 1000 + i, 'start_ticks': '20000', 'boot_id': 'boot-' + mid, 'pid_namespace': 'pid:[123]'}}
        paths[mid] = root / 'attempt.json'
        exits[mid] = root / 'exit.json'
        write_json(paths[mid], manifests[mid])
    group = {'schema_version': 1, 'task': 'synthetic', 'context': 'context-a', 'context_epoch': 2,
             'group_attempt': 'synthetic-distributed', 'progress_member': 'node0', 'start_step': 0,
             'expected_final_step': 6, 'members': [{'id': mid, 'node': mid,
                'manifest_sha256': hashlib.sha256(path.read_bytes()).hexdigest()} for mid, path in paths.items()],
             'policy': {'heartbeat_max_age_seconds': 120, 'clock_skew_seconds': 5}}
    return group, manifests, paths, exits


def append(manifest, text):
    with Path(manifest['log_path']).open('a', encoding='utf8') as stream:
        stream.write(text)


def iteration(step=6, loss='2.5', newline=True):
    return f' iteration {step}/ 6 | elapsed time per iteration (ms): 100 | lm loss: {loss} |' + ('\n' if newline else '')


def seal(manifest, path, code=0, finished=120):
    raw = Path(manifest['log_path']).read_bytes()
    value = {k: manifest[k] for k in ('context', 'attempt_id', 'process')}
    value.update(exit_code=code, finished_at=finished,
                 log_evidence={'path': manifest['log_path'], 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()})
    write_json(path, value)
    return value


def collect(tmp_path, data, mid, *, now=130, status='alive', **kwargs):
    group, manifests, paths, exits = data
    process = {'status': status, 'identity': manifests[mid]['process'], 'process_state': 'S' if status == 'alive' else 'Z'}
    process = kwargs.pop('process_status', process)
    collector = kwargs.pop('collector_identity', manifests[mid]['process'])
    return collect_member(group, mid, paths[mid], tmp_path / ('state-' + mid),
                          exit_path=exits[mid], now=now, process_status=process, collector_identity=collector, **kwargs)


def completed(tmp_path):
    data = fixture(tmp_path)
    group, manifests, _, exits = data
    append(manifests['node0'], iteration())
    for mid in manifests:
        seal(manifests[mid], exits[mid])
    rows = {mid: collect(tmp_path, data, mid, status='exited') for mid in manifests}
    return data, rows


def resign(row):
    row['sha256'] = fingerprint({k: v for k, v in row.items() if k != 'sha256'})


def test_peer_without_iterations_exits_success_and_group_completes(tmp_path):
    data, rows = completed(tmp_path)
    assert rows['node1']['iterations'] == 0
    assert rows['node1']['step'] == 0
    assert rows['node1']['fatal_errors'] == []
    result = aggregate_members(data[0], rows, tmp_path / 'aggregate', now=131)
    assert result['completion_verified'] is True
    assert result['status'] == 'completed'
    assert result['members']['node1']['exit_verified'] is True


def test_rankzero_final_step_does_not_imply_peer_completion(tmp_path):
    data = fixture(tmp_path)
    append(data[1]['node0'], iteration())
    seal(data[1]['node0'], data[3]['node0'])
    rows = {mid: collect(tmp_path, data, mid) for mid in data[1]}
    result = aggregate_members(data[0], rows, tmp_path / 'agg', now=131)
    assert result['completion_verified'] is False
    assert result['status'] == 'observing'
    assert result['members']['node1']['state'] == 'running'


def test_silent_running_peer_has_no_fabricated_stall(tmp_path):
    data = fixture(tmp_path)
    rows = {mid: collect(tmp_path, data, mid, now=1000) for mid in data[1]}
    result = aggregate_members(data[0], rows, tmp_path / 'agg', now=1001)
    assert result['status'] == 'observing'
    assert result['progress_step'] == 0
    assert result['completion_verified'] is False


@pytest.mark.parametrize('change', ['missing', 'stale', 'future', 'tamper', 'epoch', 'node', 'process', 'stopped', 'unknown', 'receipt', 'offset', 'bool'])
def test_rankzero_cannot_hide_bad_peer(tmp_path, change):
    data, rows = completed(tmp_path)
    peer = rows['node1']
    if change == 'missing':
        rows.pop('node1')
    elif change == 'stale':
        peer['observed_at'] = 100
    elif change == 'future':
        peer['observed_at'] = 1000
    elif change == 'tamper':
        peer['step'] = 999
    elif change == 'epoch':
        peer['context_epoch'] += 1
    elif change == 'node':
        peer['node'] = 'foreign'
    elif change == 'process':
        peer['process_observation']['identity'] = {**peer['process_observation']['identity'], 'start_ticks': '9'}
    elif change == 'stopped':
        peer['process_observation'].update(status='alive', process_state='T')
    elif change == 'unknown':
        peer['process_observation'] = {'status': 'unknown'}
    elif change == 'receipt':
        peer['exit_receipt']['process'] = {**peer['exit_receipt']['process'], 'pid': 99}
    elif change == 'offset':
        peer['log_offset'] -= 1
    elif change == 'bool':
        peer['exit_verified'] = 1
    if change not in {'tamper', 'missing'}:
        resign(peer)
    result = aggregate_members(data[0], rows, tmp_path / 'agg', now=251 if change == 'stale' else 131)
    assert result['completion_verified'] is False
    assert result['status'] == 'attention'


@pytest.mark.parametrize('line', ['RuntimeError: synthetic peer failure\n', iteration(loss='nan'),
                                iteration(5) + iteration(4), 'torch.AcceleratorError: synthetic device fault\n'])
def test_peer_errors_preserved_even_with_zero_exit(tmp_path, line):
    data = fixture(tmp_path)
    append(data[1]['node0'], iteration())
    append(data[1]['node1'], line)
    for mid in data[1]:
        seal(data[1][mid], data[3][mid])
    rows = {mid: collect(tmp_path, data, mid, status='exited') for mid in data[1]}
    result = aggregate_members(data[0], rows, tmp_path / 'agg', now=131)
    assert result['status'] == 'attention'
    assert rows['node1']['fatal_errors']
    assert result['completion_verified'] is False


def test_exit_nonzero_and_absent_receipt_are_not_completion(tmp_path):
    data = fixture(tmp_path)
    append(data[1]['node0'], iteration())
    seal(data[1]['node0'], data[3]['node0'])
    rows = {mid: collect(tmp_path, data, mid, status='exited') for mid in data[1]}
    assert 'member-exited-without-verified-receipt' in rows['node1']['issues']
    seal(data[1]['node1'], data[3]['node1'], code=1)
    rows['node1'] = collect(tmp_path, data, 'node1', now=132, status='exited')
    result = aggregate_members(data[0], rows, tmp_path / 'agg', now=133)
    assert result['completion_verified'] is False
    assert result['members']['node1']['exit_code'] == 1


def test_no_final_step_anywhere_cannot_complete(tmp_path):
    data = fixture(tmp_path)
    for mid in data[1]:
        seal(data[1][mid], data[3][mid])
    rows = {mid: collect(tmp_path, data, mid, status='exited') for mid in data[1]}
    result = aggregate_members(data[0], rows, tmp_path / 'agg', now=131)
    assert result['completion_verified'] is False
    assert 'expected-final-step-not-observed-on-progress-member' in result['issues']


def test_completed_peer_snapshot_still_needs_fresh_observation(tmp_path):
    data, rows = completed(tmp_path)
    result = aggregate_members(data[0], rows, tmp_path / 'agg', now=300)
    assert result['completion_verified'] is False
    assert result['status'] == 'attention'


def test_manifest_file_byte_hash_and_step_contract_are_frozen(tmp_path):
    data = fixture(tmp_path)
    data[2]['node0'].write_text(data[2]['node0'].read_text() + '\n')
    with pytest.raises(FlowError, match='SHA256'):
        collect(tmp_path, data, 'node0')
    data[0]['members'][0]['manifest_sha256'] = hashlib.sha256(data[2]['node0'].read_bytes()).hexdigest()
    data[0]['expected_final_step'] = 7
    with pytest.raises(FlowError, match='step contract'):
        collect(tmp_path, data, 'node0')


def test_restarting_collector_keeps_identity_cursor_and_history(tmp_path):
    data = fixture(tmp_path)
    append(data[1]['node0'], iteration(3))
    first = collect(tmp_path, data, 'node0')
    second = collect(tmp_path, data, 'node0', now=131)
    assert second['sequence'] == 2
    assert second['iterations'] == 1
    assert second['previous_sha256'] == first['sha256']
    assert len(list((tmp_path / 'state-node0/observations').glob('*.json'))) == 2
    changed = copy.deepcopy(data[0]); changed['context_epoch'] += 1
    with pytest.raises(FlowError, match='scope changed'):
        collect_member(changed, 'node0', data[2]['node0'], tmp_path / 'state-node0', now=132)


@pytest.mark.parametrize('kind', ['truncate', 'replace', 'seal', 'receipt-disappears', 'receipt-changes'])
def test_source_changes_do_not_retain_green(tmp_path, kind):
    data, rows = completed(tmp_path)
    log = Path(data[1]['node1']['log_path'])
    if kind == 'truncate':
        log.write_bytes(b'')
    elif kind == 'replace':
        old = log.with_suffix('.old'); log.rename(old); log.write_bytes(old.read_bytes())
    elif kind == 'seal':
        log.write_text('Tampered synthetic fixture of another size\n')
    elif kind == 'receipt-disappears':
        data[3]['node1'].unlink()
    elif kind == 'receipt-changes':
        receipt = read_json(data[3]['node1']); receipt['finished_at'] += 1; write_json(data[3]['node1'], receipt)
    rows['node1'] = collect(tmp_path, data, 'node1', now=132, status='exited')
    result = aggregate_members(data[0], rows, tmp_path / 'agg', now=133)
    assert result['completion_verified'] is False
    assert result['status'] == 'attention'


def test_clockless_progress_must_exist_in_final_sealed_bytes(tmp_path):
    data = fixture(tmp_path)
    append(data[1]['node0'], 'padding\n' * 40 + iteration())
    first = collect(tmp_path, data, 'node0')
    assert first['iterations'] == 1
    path = Path(data[1]['node0']['log_path'])
    path.write_bytes(path.read_bytes().replace(b'iteration 6', b'iteration 5'))
    seal(data[1]['node0'], data[3]['node0'])
    row = collect(tmp_path, data, 'node0', now=132, status='exited')
    assert row['state'] == 'attention'
    assert any('originally observed' in s for s in row['fatal_errors'])


def test_partial_last_line_only_read_after_real_exit(tmp_path):
    data = fixture(tmp_path)
    append(data[1]['node0'], iteration(newline=False))
    first = collect(tmp_path, data, 'node0')
    assert first['iterations'] == 0 and first['backlog']
    seal(data[1]['node0'], data[3]['node0'])
    final = collect(tmp_path, data, 'node0', now=131, status='exited')
    assert final['step'] == 6 and final['log_seal_verified'] is True


def test_clock_regression_remains_attention_after_clock_recovers(tmp_path):
    data, rows = completed(tmp_path)
    collect(tmp_path, data, 'node1', now=129, status='exited')
    rows['node1'] = collect(tmp_path, data, 'node1', now=132, status='exited')
    assert rows['node1']['state'] == 'attention'
    agg = tmp_path / 'agg'
    aggregate_members(data[0], rows, agg, now=140)
    aggregate_members(data[0], rows, agg, now=139)
    assert 'aggregator-clock-regressed' in aggregate_members(data[0], rows, agg, now=141)['issues']


def test_sequence_replay_cannot_overwrite_newer_state(tmp_path):
    data, rows = completed(tmp_path)
    old = copy.deepcopy(rows)
    root = tmp_path / 'agg'
    aggregate_members(data[0], rows, root, now=131)
    rows['node1'] = collect(tmp_path, data, 'node1', now=132, status='exited')
    aggregate_members(data[0], rows, root, now=133)
    result = aggregate_members(data[0], old, root, now=134)
    assert result['completion_verified'] is False
    state = read_json(root / 'aggregate-state.json')
    assert state['members']['node1']['sequence'] == 2


def test_same_sequence_changed_payload_and_hash_chain_break_refused(tmp_path):
    data, rows = completed(tmp_path)
    aggregate_members(data[0], rows, tmp_path / 'agg', now=131)
    row = rows['node1']; row['warnings'] = ['changed']; resign(row)
    assert aggregate_members(data[0], rows, tmp_path / 'agg', now=132)['status'] == 'attention'
    rows['node1'] = collect(tmp_path, data, 'node1', now=132, status='exited')
    rows['node1']['previous_sha256'] = 'a' * 64; resign(rows['node1'])
    assert aggregate_members(data[0], rows, tmp_path / 'other', now=133)['completion_verified'] is True
    # A collector can begin at a later retained snapshot. Once pinned, an
    # immediately next sequence must link to the previously observed hash.
    rows['node1']['sequence'] += 1; resign(rows['node1'])
    assert aggregate_members(data[0], rows, tmp_path / 'other', now=134)['status'] == 'attention'


def test_aggregate_scope_epoch_and_unknown_members_rejected(tmp_path):
    data, rows = completed(tmp_path)
    aggregate_members(data[0], rows, tmp_path / 'agg', now=131)
    other = copy.deepcopy(data[0]); other['context_epoch'] += 1
    with pytest.raises(FlowError, match='scope changed'):
        aggregate_members(other, rows, tmp_path / 'agg', now=132)
    with pytest.raises(FlowError, match='Unexpected'):
        aggregate_members(data[0], {**rows, 'other': rows['node0']}, tmp_path / 'x', now=132)


def test_resume_requires_actual_new_progress_not_restored_step_only(tmp_path):
    data = fixture(tmp_path)
    data[0]['start_step'] = 3
    for mid, manifest in data[1].items():
        manifest['start_step'] = 3
        write_json(data[2][mid], manifest)
        next(m for m in data[0]['members'] if m['id'] == mid)['manifest_sha256'] = hashlib.sha256(data[2][mid].read_bytes()).hexdigest()
    append(data[1]['node0'], iteration(3))
    for mid in data[1]: seal(data[1][mid], data[3][mid])
    rows = {mid: collect(tmp_path, data, mid, status='exited') for mid in data[1]}
    assert aggregate_members(data[0], rows, tmp_path / 'agg', now=131)['completion_verified'] is False


@pytest.mark.parametrize('field,value', [('context_epoch', True), ('expected_final_step', False), ('progress_member', 'missing')])
def test_group_validation(tmp_path, field, value):
    group = fixture(tmp_path)[0]; group[field] = value
    with pytest.raises(FlowError): validate_group(group)


def test_duplicate_member_nodes_ids_and_policy_rejected(tmp_path):
    group = fixture(tmp_path)[0]
    for field in ('id', 'node', 'manifest_sha256'):
        copy_group = copy.deepcopy(group); copy_group['members'][1][field] = group['members'][0][field]
        with pytest.raises(FlowError): validate_group(copy_group)
    group['policy']['heartbeat_max_age_seconds'] = True
    with pytest.raises(FlowError): validate_group(group)


def test_linux_manifest_can_be_aggregated_on_windows_controller(tmp_path):
    data, rows = completed(tmp_path)
    for member in data[0]['members']:
        row = rows[member['id']]
        manifest = json.loads(row['manifest_utf8']); manifest['log_path'] = '/private/task/training.log'
        raw = json.dumps(manifest).encode(); row['manifest_utf8'] = raw.decode()
        member['manifest_sha256'] = row['manifest_sha256'] = hashlib.sha256(raw).hexdigest()
        row['exit_receipt']['log_evidence']['path'] = manifest['log_path']
        if row.get('progress'):
            row['progress']['source']['path'] = manifest['log_path']
    for row in rows.values(): row['group_hash'] = fingerprint(data[0]); resign(row)
    assert aggregate_members(data[0], rows, tmp_path / 'agg', now=131)['completion_verified'] is True


def test_cli_aggregate_missing_member_emits_attention(tmp_path):
    data = fixture(tmp_path)
    group_path = tmp_path / 'group.json'; write_json(group_path, data[0])
    output = tmp_path / 'summary.json'
    script = Path(__file__).resolve().parents[1] / 'scripts/observe_distributed_training.py'
    result = subprocess.run([sys.executable, '-B', str(script), 'aggregate', '--group', str(group_path),
        '--state-dir', str(tmp_path / 'aggregate'), '--output', str(output),
        '--member-file', 'node0=' + str(tmp_path / 'missing0'), '--member-file', 'node1=' + str(tmp_path / 'missing1')],
        capture_output=True, text=True)
    assert result.returncode == 2, result.stderr
    assert read_json(output)['completion_verified'] is False
    assert read_json(output)['status'] == 'attention'


def test_atomic_latest_output_matches_retained_observation(tmp_path):
    data = fixture(tmp_path)
    latest = tmp_path / 'latest.json'
    row = collect(tmp_path, data, 'node0', output_path=latest)
    assert read_json(latest) == row
    retained = list((tmp_path / 'state-node0/observations').glob('*.json'))
    assert read_json(retained[0]) == row


def test_wrong_node_cannot_validate_exited_member_via_shared_files(tmp_path):
    data, rows = completed(tmp_path)
    rows['node1'] = collect(tmp_path, data, 'node1', now=132, status='exited',
                            collector_identity=data[1]['node0']['process'])
    assert 'collector-not-in-frozen-member-boot-or-pid-namespace' in rows['node1']['issues']
    assert aggregate_members(data[0], rows, tmp_path / 'agg', now=133)['completion_verified'] is False


def test_progress_source_clock_after_exit_is_invalid(tmp_path):
    data = fixture(tmp_path)
    append(data[1]['node0'], '[1970-01-01 00:02:05] ' + iteration())
    seal(data[1]['node0'], data[3]['node0'], finished=120)
    row = collect(tmp_path, data, 'node0', now=130, status='exited')
    assert row['state'] == 'attention'
    assert any('after the member exit' in x for x in row['fatal_errors'])


@pytest.mark.parametrize('target', ['log', 'manifest', 'receipt', 'state', 'lock', 'history'])
def test_latest_output_cannot_overwrite_original_evidence_or_state(tmp_path, target):
    data = fixture(tmp_path)
    paths = {'log': Path(data[1]['node0']['log_path']), 'manifest': data[2]['node0'], 'receipt': data[3]['node0'],
             'state': tmp_path / 'state-node0/member-state.json', 'lock': tmp_path / 'state-node0/observer.lock',
             'history': tmp_path / 'state-node0/observations/retained.json'}
    with pytest.raises(FlowError, match='cannot overwrite'):
        collect(tmp_path, data, 'node0', output_path=paths[target])
    assert Path(data[1]['node0']['log_path']).read_text().startswith('Synthetic CPU fixture')


def test_progress_source_is_configurable_and_not_assumed_rank_zero(tmp_path):
    data = fixture(tmp_path)
    data[0]['progress_member'] = 'node1'
    append(data[1]['node1'], iteration())
    for mid in data[1]: seal(data[1][mid], data[3][mid])
    rows = {mid: collect(tmp_path, data, mid, status='exited') for mid in data[1]}
    result = aggregate_members(data[0], rows, tmp_path / 'correct', now=131)
    assert result['completion_verified'] is True and result['progress_member'] == 'node1'
    assert result['members']['node0']['step'] == 0
    # Selecting a different source creates a different frozen contract, not an
    # in-place rewrite of prior member evidence or the original collector state.
    wrong = copy.deepcopy(data[0]); wrong['progress_member'] = 'node0'
    other = {}
    for mid in data[1]:
        other[mid] = collect_member(wrong, mid, data[2][mid], tmp_path / ('wrong-' + mid),
            exit_path=data[3][mid], now=130, process_status={'status': 'exited'}, collector_identity=data[1][mid]['process'])
    result = aggregate_members(wrong, other, tmp_path / 'wrong-group', now=131)
    assert result['completion_verified'] is False
    assert 'expected-final-step-not-observed-on-progress-member' in result['issues']
