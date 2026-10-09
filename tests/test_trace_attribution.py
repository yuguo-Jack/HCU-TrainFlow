"""Fixed-source attribution contracts; synthetic traces are not GPU evidence."""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from hcu_trainflow.analysis import analyze_trace
from hcu_trainflow.core import FlowError, fingerprint, write_json
from hcu_trainflow.tracelens import export_attribution, file_hash


def event(category, name, ts, dur, tid=1, **args):
    return {'ph': 'X', 'cat': category, 'name': name, 'ts': ts, 'dur': dur,
            'pid': 0 if category == 'kernel' else 10, 'tid': tid, 'args': args}


def nested_trace():
    return {'rank': 0, 'traceEvents': [
        event('cpu_op', 'outer', 0, 100, **{'Input Dims': [[100, 100]], 'Input type': ['float']}),
        event('cpu_op', 'inner', 10, 20, **{'Input Dims': [[8, 16]], 'Input type': ['float']}),
        event('cuda_runtime', 'hipLaunchKernel', 12, 2, correlation=1),
        event('kernel', 'shared_kernel_name', 15, 5, tid=7, correlation=1, stream=7),
        event('cuda_runtime', 'hipLaunchKernel', 40, 2, correlation=2),
        event('kernel', 'shared_kernel_name', 45, 5, tid=7, correlation=2, stream=7),
    ]}


@pytest.fixture
def native(monkeypatch):
    checkout = Path(__file__).resolve().parents[1] / 'thirdparty/TraceLens'
    if checkout.is_dir():
        monkeypatch.syspath_prepend(str(checkout))
    pytest.importorskip('TraceLens.Trace2Tree.trace_to_tree', reason='Native adapter integration requires installed TraceLens dependencies')


def export(tmp_path, trace, window=None):
    path = tmp_path / 'trace.json'
    write_json(path, trace)
    return export_attribution(path, window or {'start_us': 0, 'end_us': 100}, rank=0)


def consumer_fixture():
    trace = nested_trace()
    window = {'start_us': 0, 'end_us': 100}
    mapping = {'schema_version': 1, 'source': {'sha256': 'a' * 64, 'content_hash': fingerprint(trace)},
               'window': window, 'window_hash': fingerprint(window), 'rank': 0,
               'event_count': len(trace['traceEvents']), 'counts': {'matched': 2}, 'events': []}
    for index, owner in [(3, 1), (5, 0)]:
        cpu = trace['traceEvents'][owner]
        mapping['events'].append({'event_index': index, 'event_hash': fingerprint(trace['traceEvents'][index]),
                                  'status': 'matched', 'shape': cpu['args']['Input Dims'], 'dtype': ['float'],
                                  'shape_source': {'event_index': owner}, 'shape_scope': 'cpu-op-inputs',
                                  'cpu_op': {'event_index': owner, 'name': cpu['name']}, 'phase': 'unknown', 'callsite': []})
    return trace, window, mapping


def test_native_nearest_owner_does_not_double_count_parent_subtree(tmp_path, native):
    trace = nested_trace()
    original = deepcopy(trace)
    mapping = export(tmp_path, trace)
    assert trace == original
    assert mapping['source']['sha256'] == file_hash(tmp_path / 'trace.json')
    assert len(mapping['parser']['native_tree_sha256']) == 64
    assert len(mapping['parser']['adapter_sha256']) == 64
    assert [(r['event_index'], r['cpu_op']['name'], r['owner_gpu_event_count']) for r in mapping['events']] == [(3, 'inner', 1), (5, 'outer', 1)]
    result = analyze_trace(trace, mapping['window'], attribution=mapping)
    assert result['ranks']['0']['busy_union_us'] == 10
    assert sum(x['attributed_us'] for x in result['ranks']['0']['operators']) == 10
    assert len(result['ranks']['0']['operators']) == 2  # Same kernel name, distinct CPU workloads.


def test_native_empty_leaf_shape_retains_explicit_ancestor_context(tmp_path, native):
    trace = nested_trace()
    trace['traceEvents'][1]['args']['Input Dims'] = []
    mapping = export(tmp_path, trace)
    row = mapping['events'][0]
    assert row['cpu_op']['name'] == 'inner'
    assert row['shape_source']['event_index'] == 0
    assert row['shape_scope'] == 'ancestor-cpu-op-inputs'
    assert 'ancestor-shapes-are-context-not-kernel-workload' in row['issues']


def test_native_execute_wrapper_does_not_replace_owning_op_workload(tmp_path, native):
    trace = nested_trace()
    trace['traceEvents'][1]['name'] = 'execute'
    mapping = export(tmp_path, trace)
    row = mapping['events'][0]
    assert row['cpu_op']['name'] == 'outer'
    assert row['shape'] == [[100, 100]]
    assert row['shape_scope'] == 'cpu-op-inputs'


def test_native_reused_correlation_preserves_ambiguity(tmp_path, native):
    trace = {'rank': 0, 'traceEvents': [
        event('cpu_op', 'first', 0, 20),
        event('cuda_runtime', 'hipLaunchKernel', 5, 2, correlation=7),
        event('cpu_op', 'second', 40, 20),
        event('cuda_runtime', 'hipLaunchKernel', 45, 2, correlation=7),
        event('kernel', 'ambiguous_kernel', 50, 5, tid=7, correlation=7, stream=7),
    ]}
    mapping = export(tmp_path, trace)
    assert mapping['events'][0]['status'] == 'ambiguous'
    assert mapping['events'][0]['shape'] is None
    result = analyze_trace(trace, mapping['window'], attribution=mapping)
    assert result['ranks']['0']['operators'][0]['assessment']['status'] == 'incomplete'


def test_native_forward_backward_phase_uses_real_sequence_link(tmp_path, native):
    trace = {'rank': 0, 'traceEvents': [
        event('cpu_op', 'aten::mm', 0, 20, **{'Sequence number': 1, 'Input Dims': [[4, 8], [8, 4]]}),
        event('cuda_runtime', 'hipLaunchKernel', 5, 2, correlation=1),
        event('kernel', 'gemm_fwd', 8, 5, tid=7, correlation=1, stream=7),
        event('cpu_op', 'autograd::engine::evaluate_function: MmBackward0', 40, 50, tid=9, **{'Sequence number': 1}),
        event('cpu_op', 'aten::mm', 42, 40, tid=9, **{'Input Dims': [[4, 4], [4, 8]]}),
        event('cuda_runtime', 'hipLaunchKernel', 43, 2, tid=9, correlation=2),
        event('kernel', 'gemm_bwd', 50, 5, tid=7, correlation=2, stream=7),
    ]}
    mapping = export(tmp_path, trace)
    assert [r['phase'] for r in mapping['events']] == ['forward', 'backward']
    assert mapping['events'][1]['linked_forward']['event_index'] == 0


def test_cpu_shapes_cannot_automatically_become_kernel_flops():
    trace, window, mapping = consumer_fixture()
    model = {'kind': 'gemm', 'm': 8, 'n': 16, 'k': 8, 'peak_flops_s': 1e12, 'basis': 'authored fixture'}
    result = analyze_trace(trace, window, {'shared_kernel_name': model}, attribution=mapping)
    assert all(x['assessment']['status'] == 'incomplete' for x in result['ranks']['0']['operators'])
    assert 'per-kernel workload evidence' in result['ranks']['0']['operators'][0]['assessment']['reason']


@pytest.mark.parametrize('change', ['trace', 'ordering', 'window', 'event-hash', 'duplicate', 'shape'])
def test_wrong_or_ambiguous_sidecar_is_rejected(change):
    trace, window, mapping = consumer_fixture()
    if change == 'trace':
        trace['traceEvents'][3]['dur'] += 1
    elif change == 'ordering':
        trace['traceEvents'].reverse()
    elif change == 'window':
        window = {'start_us': 1, 'end_us': 100}
    elif change == 'event-hash':
        mapping['events'][0]['event_hash'] = 'b' * 64
    elif change == 'duplicate':
        mapping['events'].append(deepcopy(mapping['events'][0]))
    else:
        mapping['events'][0]['shape'] = [[999]]
    with pytest.raises(FlowError):
        analyze_trace(trace, window, attribution=mapping)


def test_attribution_preserves_overlap_accounting_and_original_events():
    trace, window, mapping = consumer_fixture()
    trace['traceEvents'][3]['dur'] = 50
    mapping['source']['content_hash'] = fingerprint(trace)
    mapping['events'][0]['event_hash'] = fingerprint(trace['traceEvents'][3])
    original = deepcopy(trace)
    before = analyze_trace(trace, window)['ranks']['0']
    after = analyze_trace(trace, window, attribution=mapping)['ranks']['0']
    assert trace == original
    assert before['busy_union_us'] == after['busy_union_us'] == 50
    assert before['overlap_us'] == after['overlap_us'] == 5
    assert sum(x['attributed_us'] for x in after['operators']) == 50


def test_identical_dimensions_with_distinct_layouts_remain_separate_workloads():
    kernels = [event('kernel', 'gemm', 0, 10, **{'Input Dims': [[4, 4]], 'Input type': ['float'], 'Input Strides': [[4, 1]]}),
               event('kernel', 'gemm', 10, 10, **{'Input Dims': [[4, 4]], 'Input type': ['float'], 'Input Strides': [[1, 4]]})]
    result = analyze_trace({'rank': 0, 'traceEvents': kernels}, {'start_us': 0, 'end_us': 20})
    assert len(result['ranks']['0']['operators']) == 2
