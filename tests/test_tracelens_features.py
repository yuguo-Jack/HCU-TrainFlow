import json
from pathlib import Path
import subprocess

import pytest

from hcu_trainflow import tracelens_features as features
from hcu_trainflow.core import FlowError, Store, write_json


def setup(tmp_path, monkeypatch):
    trace = tmp_path / 'profile.json'
    trace.write_text('{}')
    request = tmp_path / 'request.json'
    write_json(request, {'mode': 'hipprof', 'trace': trace.name})
    monkeypatch.setattr(features, 'require_checkout', lambda *args: (tmp_path, {'commit': 'f' * 40}))
    return Store(tmp_path / 'state'), request, trace


@pytest.mark.parametrize('receipt,expected', [({'status': 'generated'}, 'generated'),
    ({'status': 'incomplete'}, 'incomplete'), ({'status': 'needs-agent-review'}, 'needs-agent-review'),
    ({'status': 'passed'}, 'failed'), (None, 'failed')])
def test_feature_preserves_partial_and_review_status(tmp_path, monkeypatch, receipt, expected):
    store, request, trace = setup(tmp_path, monkeypatch)
    def run(argv, **kwargs):
        folder = Path(argv[-1]).parent
        assert Path(kwargs['env']['TMPDIR']).is_relative_to(folder)
        assert Path(kwargs['env']['MPLCONFIGDIR']).is_relative_to(folder)
        assert Path(kwargs['env']['TRACELENS_CACHE_DIR']).is_relative_to(folder)
        (folder / 'partial.csv').write_text('a\n1\n')
        if receipt is not None:
            write_json(folder / 'worker.json', receipt)
        return subprocess.CompletedProcess(argv, 0)
    monkeypatch.setattr(features, 'run_bounded', run)
    result = features.run_feature(store, '.', request)
    assert result['status'] == expected
    assert result['source_commit'] == 'f' * 40
    assert result['artifacts']
    assert result['training_assessment'].startswith('unassessed')


def test_mutated_input_cannot_pass(tmp_path, monkeypatch):
    store, request, trace = setup(tmp_path, monkeypatch)
    def run(argv, **kwargs):
        trace.write_text('{"changed":true}')
        write_json(Path(argv[-1]).parent / 'worker.json', {'status': 'generated'})
        return subprocess.CompletedProcess(argv, 0)
    monkeypatch.setattr(features, 'run_bounded', run)
    assert features.run_feature(store, '.', request)['status'] == 'failed'


def test_timeout_retains_logs_without_claiming_success(tmp_path, monkeypatch):
    store, request, trace = setup(tmp_path, monkeypatch)
    def run(argv, **kwargs):
        raise subprocess.TimeoutExpired(argv, 1)
    monkeypatch.setattr(features, 'run_bounded', run)
    result = features.run_feature(store, '.', request, timeout=1)
    assert result['status'] == 'failed'
    assert Path(result['output_directory'], 'stderr.log').exists()


@pytest.mark.parametrize('value', [{'mode': 'execute'}, {'mode': 'hipprof'},
    {'mode': 'hipprof', 'trace': 't.json', 'command': 'launch training'},
    {'mode': 'roofline', 'perf_csv': 't.json', 'gpu_arch_json': 't.json', 'wallclock_time_us': -1}])
def test_rejects_unbounded_or_invalid_requests(tmp_path, value):
    (tmp_path / 't.json').write_text('{}')
    with pytest.raises(FlowError):
        features.prepare_request(value, tmp_path)


def test_graph_snapshots_nested_capture_files(tmp_path):
    for name in ('capture.json', 'replay.json'):
        (tmp_path / name).write_text('{}')
    write_json(tmp_path / 'manifest.json', {'replay_file': 'replay.json', 'captures': [{'file': 'capture.json'}]})
    request, inputs = features.prepare_request({'mode': 'graph', 'manifest': 'manifest.json', 'capture_folder': '.'}, tmp_path)
    assert len(inputs) == 3
    assert all(Path(path).is_absolute() for path in inputs)
    write_json(tmp_path / 'manifest.json', {'replay_file': '../escape.json', 'captures': []})
    with pytest.raises(FlowError, match='escapes'):
        features.prepare_request({'mode': 'graph', 'manifest': 'manifest.json', 'capture_folder': '.'}, tmp_path)


def test_cli_exposes_unified_offline_request():
    from hcu_trainflow.cli import parser
    args = parser().parse_args(['tracelens-analyze', 'request.json', '--timeout', '25'])
    assert args.timeout == 25 and args.request == 'request.json'


@pytest.mark.parametrize('selection', ['all', 'auto', '-1', '2:2', '4:1', 2, True, '1:3:4'])
def test_split_requires_explicit_nonempty_range(tmp_path, selection):
    (tmp_path / 't.json').write_text('{}')
    with pytest.raises(FlowError):
        features.prepare_request({'mode': 'split', 'trace': 't.json', 'iterations': selection}, tmp_path)


def test_merge_preserves_actual_rank_ids_and_hashes_each_file(tmp_path):
    for name in ('a.json', 'b.json'):
        (tmp_path / name).write_text('{}')
    value, inputs = features.prepare_request({'mode': 'merge', 'traces': {'7': 'b.json', '3': 'a.json'}}, tmp_path)
    assert list(value['traces']) == ['3', '7'] and len(inputs) == 2
    with pytest.raises(FlowError, match='reuse'):
        features.prepare_request({'mode': 'merge', 'traces': {'3': 'a.json', '7': './a.json'}}, tmp_path)
    with pytest.raises(FlowError, match='canonical'):
        features.prepare_request({'mode': 'merge', 'traces': {'03': 'a.json', '7': 'b.json'}}, tmp_path)


def test_comparison_binds_both_inputs(tmp_path):
    for name in ('before.json', 'after.json'):
        (tmp_path / name).write_text('{}')
    value, inputs = features.prepare_request({'mode': 'compare', 'trace': 'before.json',
        'comparison_trace': 'after.json'}, tmp_path)
    assert len(inputs) == 2 and Path(value['comparison_trace']).is_absolute()


@pytest.mark.parametrize('actual,expected', [('1:3', 'generated'), ('1:2', 'incomplete'), (None, 'incomplete')])
def test_split_does_not_accept_silent_truncation(tmp_path, monkeypatch, actual, expected):
    from hcu_trainflow import tracelens_feature_worker as worker
    def native(*args):
        if actual:
            target = tmp_path / 'split/part.json.gz'
            target.parent.mkdir()
            target.write_bytes(b'trace fixture')
            write_json(target.parent / 'execution_details.json',
                       [{'idx': actual, 'output_path': str(target), 'event_count': 4}])
    monkeypatch.setattr(worker, 'run_native', native)
    result = worker.analyze({'mode': 'split', 'trace': 'trace.json', 'iterations': '1:3'}, tmp_path)
    assert result['status'] == expected


def test_compare_rejects_timeline_only_tables(tmp_path, monkeypatch):
    import sys
    from types import SimpleNamespace
    from hcu_trainflow.tracelens_feature_worker import analyze
    monkeypatch.setitem(sys.modules, 'TraceLens.Reporting.generate_perf_report_pytorch',
        SimpleNamespace(generate_perf_report_pytorch=lambda **kwargs: {'gpu_timeline': [1]}))
    result = analyze({'mode': 'compare', 'trace': 'before', 'comparison_trace': 'after'}, tmp_path)
    assert result['status'] == 'incomplete'


def test_merge_rejects_an_empty_rank(tmp_path, monkeypatch):
    import gzip
    import sys
    from types import SimpleNamespace
    from hcu_trainflow.tracelens_feature_worker import analyze
    path = tmp_path / 'merged.json.gz'
    with gzip.open(path, 'wt') as stream:
        json.dump({'traceEvents': [{'ph': 'X', 'args': {'rank': 3}}]}, stream)
    monkeypatch.setitem(sys.modules, 'TraceLens.TraceFusion.trace_fuse',
        SimpleNamespace(TraceFuse=lambda ranks: SimpleNamespace(merge_and_save=lambda name: str(path))))
    result = analyze({'mode': 'merge', 'traces': {'3': 'one', '7': 'two'}}, tmp_path)
    assert result['status'] == 'incomplete' and result['duration_events_by_rank'][7] == 0


def test_cli_does_not_report_pending_agent_review_as_success(tmp_path, monkeypatch):
    from hcu_trainflow import cli
    monkeypatch.setattr(cli, 'execute', lambda *args: {'status': 'needs-agent-review'})
    assert cli.main(['--workspace', str(tmp_path), 'tracelens-analyze', 'request.json']) == 2


@pytest.mark.parametrize('native,expected', [
    ({'status': 'parsed', 'captures': [{'id': 'one'}], 'gaps': []}, 'generated'),
    ({'status': 'parsed', 'captures': [], 'gaps': []}, 'incomplete'),
    ({'status': 'incomplete', 'captures': [{'id': 'one'}], 'gaps': ['unknown units']}, 'incomplete')])
def test_worker_uses_native_counter_status(tmp_path, monkeypatch, native, expected):
    import sys
    from types import SimpleNamespace
    from hcu_trainflow.tracelens_feature_worker import analyze
    monkeypatch.setitem(sys.modules, 'TraceLens.Reporting.xcompute', SimpleNamespace(generate_perf_report_xcompute=lambda *a: native))
    result = analyze({'mode': 'counters', 'manifest': str(tmp_path / 'capture.json')}, tmp_path)
    assert result['status'] == expected


def test_outer_timeout_reaps_native_grandchild(tmp_path):
    import sys
    import time
    marker = tmp_path / 'orphan-wrote.txt'
    child = 'import time,pathlib; time.sleep(1.5); pathlib.Path(' + repr(str(marker)) + ').write_text("orphan")'
    script = 'import subprocess,sys,time; subprocess.Popen([sys.executable,"-c",' + repr(child) + ']); time.sleep(30)'
    with pytest.raises(subprocess.TimeoutExpired):
        features.run_bounded([sys.executable, '-c', script], timeout=0.7,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.2)
    assert not marker.exists()
