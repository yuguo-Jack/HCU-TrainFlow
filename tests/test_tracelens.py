"""Trace evidence contracts; fixtures are synthetic, not hardware validation."""
import gzip
import json
from pathlib import Path
import subprocess

import pytest

from hcu_trainflow import tracelens
from hcu_trainflow.core import FlowError, Store, write_json


def event(category, name, **args):
    return {'ph': 'X', 'cat': category, 'name': name, 'ts': 10, 'dur': 5,
            'pid': 1, 'tid': 1, 'args': args}


def kineto_events():
    return [event('cpu_op', 'aten::mm', **{'Input Dims': [[4, 8], [8, 4]],
                                           'Input type': ['float', 'float'], 'Sequence number': 0}),
            event('hip_runtime', 'hipLaunchKernel', correlation=7),
            event('kernel', 'gemm', correlation=7),
            event('user_annotation', 'ProfilerStep#3'),
            event('cpu_op', 'autograd::engine::evaluate_function: MmBackward0'),
            {'ph': 'i', 'name': '[memory]', 'args': {'Total Allocated': 128}}]


def prepare(tmp_path, monkeypatch, events=None, metadata=None):
    checkout = tmp_path / 'checkout'
    checkout.mkdir()
    monkeypatch.setattr(tracelens, 'require_checkout', lambda *a: (checkout, {'commit': 'a' * 40}))
    trace = tmp_path / 'rank0.json'
    write_json(trace, {'traceEvents': events if events is not None else kineto_events(), **(metadata or {})})
    return Store(tmp_path / 'state'), trace


def native_tables(argv, **kwargs):
    request = json.loads(Path(argv[-1]).read_text())
    folder = Path(request['output_csvs_dir'])
    folder.mkdir()
    (folder / 'kernel_summary.csv').write_text('kernel,duration\ngemm,5\n')
    return subprocess.CompletedProcess(argv, 0)


def test_inventory_records_training_metadata_without_vendor_guess(tmp_path):
    path = tmp_path / 'rank0.json.gz'
    with gzip.open(path, 'wt', encoding='utf-8') as stream:
        json.dump({'traceEvents': kineto_events(), 'distributedInfo': {'rank': 3, 'world_size': 8}}, stream)
    inventory = tracelens.trace_inventory(path)
    assert inventory['gpu_kernels'] == 1
    assert inventory['observed_fields']['runtime_events'] == 1
    assert inventory['observed_fields']['cpu_ops_with_sequence'] == 1  # zero is a valid sequence id
    assert inventory['recorded_rank'] == 3 and inventory['recorded_world_size'] == 8
    assert not inventory['training_gaps']
    assert 'vendor' not in inventory


def test_gpu_step_annotations_do_not_create_extra_training_steps(tmp_path):
    path = tmp_path / 'trace.json'
    gpu_steps = [event('gpu_user_annotation', 'ProfilerStep#3'),
                 event('gpu_user_annotation', 'ProfilerStep#3')]
    write_json(path, {'traceEvents': kineto_events() + gpu_steps})
    inventory = tracelens.trace_inventory(path)
    fields = inventory['observed_fields']
    assert fields['step_annotations'] == 3  # Retain the raw legacy count.
    assert fields['cpu_step_annotations'] == 1
    assert fields['gpu_step_annotations'] == 2
    write_json(path, {'traceEvents': gpu_steps})
    assert 'training-step-window-unidentified' in tracelens.trace_inventory(path)['training_gaps']


def test_native_warning_summary_preserves_sample_loss():
    import warnings
    from hcu_trainflow.tracelens_worker import summarize_warnings
    with warnings.catch_warnings(record=True) as records:
        warnings.simplefilter('always')
        for _ in range(2):
            warnings.warn('Inconsistent kernel list length found. Skipping a row.', UserWarning)
        warnings.warn('Mean of empty slice', RuntimeWarning)
    rows = summarize_warnings(records)
    assert len(rows) == 2
    skipped = next(x for x in rows if x['code'] == 'native-kernel-detail-samples-skipped')
    assert skipped['count'] == 2 and skipped['filename'].endswith('test_tracelens.py')
    assert next(x for x in rows if x['category'] == 'RuntimeWarning')['code'] == 'native-warning'


@pytest.mark.parametrize('code,expected', [('native-kernel-detail-samples-skipped', 'incomplete'),
                                         ('native-warning', 'generated')])
def test_skipped_native_detail_samples_are_not_a_complete_report(tmp_path, monkeypatch, code, expected):
    store, trace = prepare(tmp_path, monkeypatch)
    def run(argv, **kwargs):
        result = native_tables(argv, **kwargs)
        write_json(Path(argv[-1]).parent / 'worker.json', {
            'tables': {'ops_summary': {'rows': 1}}, 'cpu_attribution_rows': 1,
            'native_warnings': [{'code': code, 'count': 2, 'message': 'retained diagnostic'}]})
        return result
    monkeypatch.setattr(tracelens.subprocess, 'run', run)
    result = tracelens.run_report(store, '.', trace=trace)
    assert result['status'] == expected
    assert len(result['tables']) == 1  # Valid aggregate tables remain usable.
    assert result['worker']['native_warnings'][0]['count'] == 2
    assert bool(result['gaps']) is (expected == 'incomplete')


def test_worker_keeps_native_warning_when_analysis_raises(tmp_path, monkeypatch, capsys):
    import sys
    import types
    import warnings
    from hcu_trainflow import tracelens_worker

    name = 'TraceLens.Reporting.generate_perf_report_pytorch'
    module = types.ModuleType(name)
    def fail(**kwargs):
        warnings.warn('Inconsistent kernel list length found. Skipping a row.', UserWarning)
        raise RuntimeError('native analysis failed')
    module.generate_perf_report_pytorch = fail
    monkeypatch.setitem(sys.modules, name, module)
    request = tmp_path / 'request.json'
    write_json(request, {})
    monkeypatch.setattr(sys, 'argv', ['worker', 'pytorch', str(request)])
    with pytest.raises(RuntimeError, match='native analysis failed'):
        tracelens_worker.main()
    assert 'Skipping a row.' in capsys.readouterr().err
    assert not (tmp_path / 'worker.json').exists()


@pytest.mark.parametrize('duration', [None, '5', -1, True, float('nan'), float('inf')])
def test_malformed_duration_is_never_counted_as_measured_kernel(tmp_path, duration):
    path = tmp_path / 'trace.json'
    malformed = event('kernel', 'bad')
    malformed['dur'] = duration
    path.write_text(json.dumps({'traceEvents': [malformed]}), encoding='utf-8')
    inventory = tracelens.trace_inventory(path)
    assert inventory['gpu_kernels'] == 0
    assert 'malformed-events' in inventory['training_gaps']


def test_successful_tables_keep_missing_metadata_explicit(tmp_path, monkeypatch):
    store, trace = prepare(tmp_path, monkeypatch, [event('kernel', 'gemm'), event('cpu_op', 'aten::mm')])
    monkeypatch.setattr(tracelens.subprocess, 'run', native_tables)
    result = tracelens.run_report(store, '.', trace=trace)
    assert result['status'] == 'generated'  # Native tables exist; training is still unassessed.
    assert result['training_assessment'].startswith('unassessed')
    assert 'input-shapes-unavailable' in result['training_gaps'][0]['gaps']
    assert result['timing_contract']['end_to_end_step_denominator'].startswith('not established')
    request = json.loads((Path(result['output_directory']) / 'request.json').read_text())
    assert request['include_call_stack'] is True


def test_changed_input_cannot_become_fixed_evidence(tmp_path, monkeypatch):
    store, trace = prepare(tmp_path, monkeypatch)
    def run(argv, **kwargs):
        result = native_tables(argv, **kwargs)
        trace.write_text('{}')
        return result
    monkeypatch.setattr(tracelens.subprocess, 'run', run)
    result = tracelens.run_report(store, '.', trace=trace)
    assert result['status'] == 'failed'
    assert 'changed or disappeared' in result['failure']
    assert result['tables'][0]['rows'] == 1  # Preserve diagnostic output.


def test_worker_start_failure_is_retained(tmp_path, monkeypatch):
    store, trace = prepare(tmp_path, monkeypatch)
    def fail(*args, **kwargs):
        raise OSError('interpreter unavailable')
    monkeypatch.setattr(tracelens.subprocess, 'run', fail)
    result = tracelens.run_report(store, '.', trace=trace)
    assert result['status'] == 'failed' and result['returncode'] is None
    assert Path(result['output_directory'], 'report.json').is_file()


def test_gpu_only_native_tables_cannot_imply_cpu_attribution(tmp_path, monkeypatch):
    store, trace = prepare(tmp_path, monkeypatch)
    def run(argv, **kwargs):
        result = native_tables(argv, **kwargs)
        write_json(Path(argv[-1]).parent / 'worker.json',
                   {'tables': {'kernel_summary': {'rows': 1}}, 'cpu_attribution_rows': 0})
        return result
    monkeypatch.setattr(tracelens.subprocess, 'run', run)
    result = tracelens.run_report(store, '.', trace=trace)
    assert result['status'] == 'incomplete'
    assert any('no CPU operator attribution' in gap for gap in result['gaps'])


@pytest.mark.parametrize('outcome,expected', [('missing', 'incomplete'), ('truncated', 'failed')])
def test_requested_attribution_export_must_be_readable(tmp_path, monkeypatch, outcome, expected):
    store, trace = prepare(tmp_path, monkeypatch)
    def run(argv, **kwargs):
        result = native_tables(argv, **kwargs)
        if outcome == 'truncated':
            (Path(argv[-1]).parent / 'attribution.json').write_text('{')
        return result
    monkeypatch.setattr(tracelens.subprocess, 'run', run)
    result = tracelens.run_report(store, '.', trace=trace, window={'start_us': 0, 'end_us': 100})
    assert result['status'] == expected


def test_explicit_rank_cannot_override_captured_global_rank(tmp_path, monkeypatch):
    store, trace = prepare(tmp_path, monkeypatch, metadata={'distributedInfo': {'rank': 7, 'world_size': 8}})
    monkeypatch.setattr(tracelens.subprocess, 'run', lambda *a, **kw: pytest.fail('rank mismatch must not dispatch'))
    with pytest.raises(FlowError, match='rank conflicts'):
        tracelens.run_report(store, '.', trace=trace, rank=0)


@pytest.mark.parametrize('group_metadata', [False, True])
def test_collective_inference_fallback_is_not_complete_training_evidence(tmp_path, monkeypatch, group_metadata):
    args = {'correlation': 9, 'stream': 7}
    if group_metadata:
        args.update({'Process Group Name': 'tp', 'Process Group Ranks': [0, 1], 'Group size': 2})
    events = kineto_events() + [event('kernel', 'void rcclKernel_AllReduce()', **args)]
    store, trace = prepare(tmp_path, monkeypatch, events)
    write_json(tmp_path / 'rank1.json', {'traceEvents': events})
    monkeypatch.setattr(tracelens.subprocess, 'run', native_tables)
    result = tracelens.run_report(store, '.', trace_pattern=str(tmp_path / 'rank*.json'), world_size=2)
    assert result['status'] == ('generated' if group_metadata else 'incomplete')
    assert bool(result['gaps']) is not group_metadata
    assert result['timing_contract']['rank_clock_alignment'] == 'unverified'


def test_invalid_json_gives_actionable_error(tmp_path):
    path = tmp_path / 'trace.json'
    path.write_text('{"traceEvents":[')
    with pytest.raises(FlowError, match='Cannot read trace JSON'):
        tracelens.trace_inventory(path)


@pytest.mark.parametrize('ranks', ['garbage', '[0, 0]', '[true, 1]', [False, 1], [-1, 1]])
def test_malformed_process_group_is_never_treated_as_complete(tmp_path, ranks):
    path = tmp_path / 'trace.json'
    write_json(path, {'traceEvents': [event('kernel', 'rcclAllReduce', **{
        'Process Group Name': 'tp', 'Process Group Ranks': ranks, 'correlation': 5})]})
    inventory = tracelens.trace_inventory(path)
    assert not inventory['process_groups']
    assert 'collective-process-group-metadata-incomplete' in inventory['training_gaps']
