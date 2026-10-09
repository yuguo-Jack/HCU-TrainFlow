"""Run the pinned TraceLens API locally, retaining its native tables and logs."""
import ast
import copy
import csv
from collections import Counter, defaultdict
import gzip
import hashlib
import inspect
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import uuid
import re

from .core import FlowError, fingerprint, utc, write_json
from .dependencies import require_checkout


def _group_ranks(value):
    if isinstance(value, str):
        try:
            value = ast.literal_eval(value)
        except (ValueError, SyntaxError):
            return None
    if not isinstance(value, (list, tuple)) or not value:
        return None
    if any(isinstance(rank, bool) or not isinstance(rank, int) or rank < 0 for rank in value):
        return None
    return list(value) if len(set(value)) == len(value) else None


def file_hash(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def read_trace(path):
    """Read native JSON or gzip traces without rewriting their source bytes."""
    path = Path(path)
    with (gzip.open if path.suffix.lower() == '.gz' else open)(path, 'rt', encoding='utf-8-sig') as stream:
        return json.load(stream, parse_constant=lambda value: (_ for _ in ()).throw(FlowError('Non-finite trace JSON: ' + value)))


def export_attribution(trace_path, window, rank=None, tracelens_commit=None):
    """Export exact-event CPU context from the native tree without rewriting input.

    CPU input shapes describe the launching op, not automatically each kernel's
    arithmetic workload. Consumers must keep that distinction when building bounds.
    """
    from TraceLens.Trace2Tree.trace_to_tree import TraceToTree
    from TraceLens import util as trace_util
    from .analysis import number

    start, end = (number(window[k], k) for k in ('start_us', 'end_us'))
    if end <= start:
        raise FlowError('Attribution requires a positive explicit training window')
    path = Path(trace_path).resolve()
    raw_hash = file_hash(path)
    trace = read_trace(path)
    events = trace.get('traceEvents') if isinstance(trace, dict) else trace
    if not isinstance(events, list) or not events or any(not isinstance(e, dict) for e in events):
        raise FlowError('Attribution requires a nonempty traceEvents array of objects')
    content_hash = fingerprint(trace)
    tree = TraceToTree(copy.deepcopy(events), prune_nongpu_paths=False)
    tree.build_tree(add_python_func=True, link_fwd_bwd=True)
    # UID is assigned before native filtering: it is the original list index.
    if len(tree.events) != len(events):
        raise FlowError('Native tree changed original event ordering/count')
    for index, event in enumerate(tree.events):
        if event.get('UID') != index:
            raise FlowError('Native tree no longer preserves original event indices')

    def ancestors(event):
        result, seen = [], set()
        while event.get('parent') is not None:
            uid = event['parent']
            if uid in seen or uid not in tree.events_by_uid:
                raise FlowError('Native CPU/GPU parent chain is cyclic or unresolved')
            seen.add(uid)
            event = tree.events_by_uid[uid]
            result.append(event)
        return result

    def cpu_owner(chain):
        return next((e for e in chain if e.get('cat') == 'cpu_op' and e.get('name') != 'execute'), None)

    # Check all native parent edges before trusting the last assigned parent.
    # Reused correlations can otherwise make one kernel look owned by two ops.
    parent_edges = defaultdict(list)
    for event in tree.events:
        for child in event.get('children', []):
            parent_edges[child].append(event)
    owners, chains = {}, {}
    owner_counts = Counter()
    gpu_categories = {'kernel', 'gpu_memcpy', 'gpu_memset'}
    for index, event in enumerate(tree.events):
        if event.get('cat') not in gpu_categories:
            continue
        chain = ancestors(event)
        owner = cpu_owner(chain)
        candidates = {candidate['UID'] if candidate is not None else None
                      for parent in parent_edges[index]
                      for candidate in [cpu_owner([parent, *ancestors(parent)])]}
        ambiguous = len(candidates) > 1
        owners[index] = (owner, ambiguous)
        chains[index] = chain
        if owner is not None and not ambiguous:
            owner_counts[owner['UID']] += 1
    entries, counts = [], Counter()
    for index, original in enumerate(events):
        if original.get('ph') != 'X' or original.get('cat') not in gpu_categories:
            continue
        begin, duration = number(original.get('ts'), 'ts'), number(original.get('dur'), 'dur')
        if duration <= 0 or begin + duration <= start or begin >= end:
            continue
        owner, ambiguous = owners[index]
        chain = chains[index]
        status = 'ambiguous' if ambiguous else 'matched' if owner is not None else 'unlinked'
        row = {'event_index': index, 'event_hash': fingerprint(original), 'status': status,
               'kernel_name': original.get('name'), 'cpu_op': None, 'shape': None, 'dtype': None, 'input_strides': None,
               'shape_scope': 'unavailable', 'shape_source': None, 'callsite': [], 'callsite_kind': 'unavailable',
               'phase': 'unknown', 'phase_basis': None, 'linked_forward': None,
               'owner_gpu_event_count': 0, 'issues': []}
        if ambiguous:
            row['issues'].append('conflicting-native-cpu-owners')
        elif owner is None:
            row['issues'].append('no-native-cpu-owner')
        else:
            row['cpu_op'] = {'event_index': owner['UID'], 'name': owner.get('name')}
            row['owner_gpu_event_count'] = owner_counts[owner['UID']]
            row['callsite'] = [{'name': e.get('name'), 'category': e.get('cat')}
                               for e in reversed(chain) if e.get('cat') in {'python_function', 'cpu_op'}]
            row['callsite_kind'] = 'python-and-operator' if any(e.get('cat') == 'python_function' for e in chain) else 'operator-chain-only'
            owner_position = next(i for i, e in enumerate(chain) if e['UID'] == owner['UID'])
            cpu_chain = [e for e in chain[owner_position:] if e.get('cat') == 'cpu_op']
            shaped = next((e for e in cpu_chain if (e.get('args') or {}).get('Input Dims')), None)
            if shaped is not None:
                row['shape'] = shaped['args']['Input Dims']
                row['dtype'] = shaped['args'].get('Input type')
                row['input_strides'] = shaped['args'].get('Input Strides')
                row['shape_source'] = {'event_index': shaped['UID'], 'name': shaped.get('name')}
                row['shape_scope'] = 'cpu-op-inputs' if shaped['UID'] == owner['UID'] else 'ancestor-cpu-op-inputs'
                if shaped['UID'] != owner['UID']:
                    row['issues'].append('ancestor-shapes-are-context-not-kernel-workload')
            row['issues'].append('cpu-input-shapes-do-not-establish-kernel-flops-or-bytes')
            for event in chain:
                explicit_phase = (event.get('args') or {}).get('phase')
                if explicit_phase in {'forward', 'backward', 'optimizer'}:
                    row['phase'], row['phase_basis'] = explicit_phase, 'explicit-event-argument'
                    break
                if str(event.get('name', '')).startswith('autograd::engine::evaluate_function:'):
                    row['phase'], row['phase_basis'] = 'backward', 'autograd-wrapper'
                    linked = tree.events_by_uid.get(event.get('fwd_event'))
                    if linked is not None and linked.get('ts', float('inf')) < event.get('ts', -float('inf')):
                        row['linked_forward'] = {'event_index': linked['UID'], 'name': linked.get('name')}
                    break
                if event.get('bwd_events'):
                    row['phase'], row['phase_basis'] = 'forward', 'native-backward-sequence-link'
                    break
        counts[status] += 1
        entries.append(row)
    if file_hash(path) != raw_hash:
        raise FlowError('Trace changed while exporting attribution')
    return {'schema_version': 1, 'tool': 'TraceLens', 'status': 'exported' if entries else 'incomplete',
            'source': {'path': str(path), 'sha256': raw_hash, 'content_hash': content_hash},
            'parser': {'source_commit': tracelens_commit,
                       'native_tree_sha256': file_hash(inspect.getfile(TraceToTree)),
                       'native_util_sha256': file_hash(inspect.getfile(trace_util)),
                       'adapter_sha256': file_hash(__file__)},
            'window': window, 'window_hash': fingerprint(window), 'rank': rank,
            'event_count': len(events), 'events': entries, 'counts': dict(counts),
            'limits': ['Nearest native CPU owner; no parent-subtree time duplication',
                       'Inherited shapes are CPU context, not proven per-kernel FLOPs/bytes',
                       'Unknown phases remain unknown; no timestamp or rank-clock alignment is inferred']}


def trace_inventory(path):
    """Inventory observed fields, without inventing shape/rank/phase attribution.

    Kineto on HIP can retain CUDA category names. A category name therefore does
    not establish the hardware vendor. Missing metadata is retained as a gap;
    this inventory is not a performance or correctness validation.
    """
    path = Path(path).resolve()
    opener = gzip.open if path.suffix == '.gz' else open
    before = file_hash(path)
    try:
        with opener(path, 'rt', encoding='utf-8-sig') as stream:
            trace = json.load(stream)
    except (OSError, ValueError, UnicodeError) as exc:
        raise FlowError('Cannot read trace JSON: ' + str(path)) from exc
    if file_hash(path) != before:
        raise FlowError('Trace changed while being inventoried; collect a completed trace')
    events = trace.get('traceEvents', []) if isinstance(trace, dict) else trace
    if not isinstance(events, list) or not events:
        raise FlowError('Trace has no events')
    counts = {'gpu_kernels': 0, 'cpu_ops': 0}
    categories, fields = Counter(), Counter()
    runtime_categories = {'cuda_runtime', 'cuda_driver', 'hip_runtime', 'hip_driver'}
    groups = {}
    for event in events:
        if not isinstance(event, dict):
            fields['invalid_events'] += 1
            continue
        category = str(event.get('cat', '')).lower()
        categories[category or 'uncategorized'] += 1
        args = event.get('args') if isinstance(event.get('args'), dict) else {}
        name = str(event.get('name', ''))
        fields['memory_events'] += name == '[memory]' or 'Total Allocated' in args or 'Total Reserved' in args
        if event.get('ph') != 'X':
            continue
        duration = event.get('dur')
        if isinstance(duration, bool) or not isinstance(duration, (int, float)) or not math.isfinite(duration) or duration < 0:
            fields['invalid_duration_events'] += 1
            continue
        if duration == 0:
            fields['zero_duration_events'] += 1
            continue
        counts['gpu_kernels'] += category == 'kernel'
        counts['cpu_ops'] += category == 'cpu_op'
        fields['runtime_events'] += category in runtime_categories
        fields['python_frames'] += category == 'python_function'
        fields['user_annotations'] += category == 'user_annotation'
        fields['step_annotations'] += name.startswith('ProfilerStep#')
        fields['cpu_step_annotations'] += category == 'user_annotation' and name.startswith('ProfilerStep#')
        fields['gpu_step_annotations'] += category == 'gpu_user_annotation' and name.startswith('ProfilerStep#')
        fields['backward_annotations'] += 'backward' in name.lower() or 'autograd::engine::evaluate_function' in name
        fields['cpu_ops_with_shapes'] += category == 'cpu_op' and bool(args.get('Input Dims'))
        fields['cpu_ops_with_dtypes'] += category == 'cpu_op' and bool(args.get('Input type'))
        fields['cpu_ops_with_sequence'] += category == 'cpu_op' and args.get('Sequence number') is not None
        fields['gpu_kernels_with_link_id'] += category == 'kernel' and any(args.get(k) is not None for k in ('correlation', 'External id'))
        communication = category == 'kernel' and bool(re.search(r'nccl|rccl', name, re.I) or args.get('Collective name'))
        if communication:
            fields['collective_kernels'] += 1
            group_name, ranks = args.get('Process Group Name'), _group_ranks(args.get('Process Group Ranks'))
            if group_name not in (None, '', 'Unknown_Group') and ranks:
                fields['collective_kernels_with_group'] += 1
                key = json.dumps([group_name, ranks], sort_keys=True)
                groups[key] = {'name': group_name, 'ranks': ranks, 'size': args.get('Group size')}
            fields['collective_kernels_with_link_id'] += any(args.get(k) is not None for k in ('correlation', 'External id'))
    metadata = trace if isinstance(trace, dict) else {}
    distributed = metadata.get('distributedInfo') or {}
    if not isinstance(distributed, dict):
        distributed = {}
    gaps = []
    for field, code in [('runtime_events', 'runtime-correlation-unavailable'),
                        ('cpu_ops_with_shapes', 'input-shapes-unavailable'),
                        ('cpu_ops_with_dtypes', 'input-dtypes-unavailable'),
                        ('cpu_step_annotations', 'training-step-window-unidentified'),
                        ('backward_annotations', 'backward-phase-unidentified'),
                        ('memory_events', 'allocator-memory-events-unavailable')]:
        if not fields[field]:
            gaps.append(code)
    if fields['collective_kernels'] > fields['collective_kernels_with_group']:
        gaps.append('collective-process-group-metadata-incomplete')
    if counts['gpu_kernels'] > fields['gpu_kernels_with_link_id']:
        gaps.append('gpu-cpu-link-metadata-incomplete')
    if fields['invalid_events'] or fields['invalid_duration_events']:
        gaps.append('malformed-events')
    return {'path': str(path), 'sha256': before, **counts,
            'categories': dict(sorted(categories.items())), 'observed_fields': dict(fields),
            'process_groups': list(groups.values()), 'training_gaps': gaps,
            'recorded_rank': distributed.get('rank', metadata.get('rank')),
            'recorded_world_size': distributed.get('world_size'),
            'limits': 'Field presence does not prove CPU/GPU linkage, complete sampling, synchronized rank clocks or a steady training window.'}


def run_report(store, project, trace=None, trace_pattern=None, world_size=None,
               gpu_arch_json=None, timeout=1800, rank=None, window=None):
    checkout, dependency = require_checkout(project, 'tracelens')
    if not 1 <= timeout <= 86400:
        raise FlowError('TraceLens timeout must be between 1 and 86400 seconds')
    if bool(trace) == bool(trace_pattern):
        raise FlowError('Provide exactly one trace or a complete-rank trace pattern')
    if window is not None:
        from .analysis import number
        if not isinstance(window, dict) or 'start_us' not in window or 'end_us' not in window:
            raise FlowError('Attribution window requires start_us and end_us')
        if number(window['end_us'], 'end_us') <= number(window['start_us'], 'start_us'):
            raise FlowError('Attribution requires a positive explicit training window')
    if trace_pattern:
        if isinstance(world_size, bool) or not isinstance(world_size, int) or not 2 <= world_size <= 65536 or trace_pattern.count('*') != 1:
            raise FlowError('Collective report requires world_size >= 2 and one rank placeholder (*)')
        paths = [Path(trace_pattern.replace('*', str(i))).resolve() for i in range(world_size)]
        if not all(p.is_file() for p in paths):
            raise FlowError('TraceLens collective analysis requires every rank 0..world_size-1; keep partial sampling explicit')
        inventories = [dict(trace_inventory(p), rank=i) for i, p in enumerate(paths)]
        kwargs = {'trace_pattern': str(Path(trace_pattern).resolve()), 'world_size': world_size}
    else:
        if rank is not None and (isinstance(rank, bool) or not isinstance(rank, int) or rank < 0):
            raise FlowError('Rank must be nonnegative')
        inventories = [dict(trace_inventory(trace), rank=rank)]
        kwargs = {'profile_json_path': inventories[0]['path'], 'include_unlinked_kernels': True,
                  'kernel_summary': True, 'include_overlap_info': True, 'include_call_stack': True}
    for inventory in inventories:
        recorded = inventory['recorded_rank']
        if recorded is not None and inventory['rank'] is not None and str(recorded) != str(inventory['rank']):
            raise FlowError('Requested rank conflicts with the trace distributedInfo/rank metadata')
        if trace_pattern and inventory['recorded_world_size'] is not None and str(inventory['recorded_world_size']) != str(world_size):
            raise FlowError('Requested world_size conflicts with trace distributedInfo metadata')
        if trace_pattern:
            for group in inventory['process_groups']:
                if inventory['rank'] not in group['ranks'] or max(group['ranks']) >= world_size:
                    raise FlowError('Collective process-group ranks conflict with the file rank/world_size mapping')
    arch = None
    if gpu_arch_json:
        if trace_pattern:
            raise FlowError('GPU architecture modeling applies to the single-trace report')
        arch = Path(gpu_arch_json).resolve()
        with arch.open(encoding='utf-8-sig') as stream:
            if not isinstance(json.load(stream), dict):
                raise FlowError('GPU architecture must be a JSON object verified for this HCU environment')
        kwargs['gpu_arch_json_path'] = str(arch)
    output = store.root / 'tracelens' / uuid.uuid4().hex
    output.mkdir(parents=True)
    kwargs['output_csvs_dir'] = str(output / 'tables')
    if window is not None:
        if trace_pattern:
            raise FlowError('Attribution exports use one fixed rank trace and explicit window at a time')
        kwargs['_trainflow_attribution'] = {'window': window, 'rank': rank, 'tracelens_commit': dependency['commit']}
    write_json(output / 'request.json', kwargs)
    argv = [sys.executable, '-B', '-m', 'hcu_trainflow.tracelens_worker',
            'collective' if trace_pattern else 'pytorch', str(output / 'request.json')]
    # Force the reviewed checkout, even when a different TraceLens happens to be installed.
    env = {**os.environ, 'PYTHONPATH': os.pathsep.join([str(checkout), str(Path(__file__).resolve().parent.parent)]), 'PYTHONUTF8': '1', 'MPLBACKEND': 'Agg'}
    returncode, failure = None, None
    with (output / 'stdout.log').open('wb') as stdout, (output / 'stderr.log').open('wb') as stderr:
        try:
            proc = subprocess.run(argv, cwd=output, env=env, stdout=stdout, stderr=stderr, timeout=timeout)
            returncode = proc.returncode
            if returncode:
                failure = 'TraceLens execution failed; inspect stderr.log and installed dependencies'
        except subprocess.TimeoutExpired:
            failure = 'TraceLens timed out; partial tables are not a completed report'
        except OSError as exc:
            failure = 'TraceLens worker could not start: ' + str(exc)
    tables = []
    # Full call stacks can exceed csv's default field bound; Windows C long is 32-bit.
    csv.field_size_limit(min(sys.maxsize, 2**31 - 1))
    for path in sorted((output / 'tables').glob('*.csv')):
        try:
            with path.open(encoding='utf-8-sig', newline='') as stream:
                rows = csv.reader(stream, strict=True); columns = next(rows, [])
                count = sum(1 for _ in rows)
            tables.append({'name': path.stem, 'path': str(path), 'rows': count, 'columns': columns, 'sha256': file_hash(path)})
        except (OSError, UnicodeError, csv.Error):
            failure = failure or 'Unreadable or truncated TraceLens table; inspect retained tables and logs'
            tables.append({'name': path.stem, 'path': str(path), 'rows': 0, 'status': 'unreadable'})
    gaps = []
    if not all(x['gpu_kernels'] for x in inventories): gaps.append('No recognized GPU kernel events in one or more traces')
    if not all(x['cpu_ops'] for x in inventories): gaps.append('CPU-op attribution unavailable in one or more traces')
    if not any(x['rows'] for x in tables): gaps.append('No nonempty report tables')
    worker = None
    attribution = None
    attribution_path = output / 'attribution.json'
    if window is not None:
        if attribution_path.is_file():
            try:
                with attribution_path.open(encoding='utf-8') as stream:
                    exported = json.load(stream)
                if not isinstance(exported, dict) or not isinstance(exported.get('source'), dict):
                    raise ValueError('Malformed attribution export')
                if exported['source'].get('sha256') != inventories[0]['sha256'] or exported.get('window_hash') != fingerprint(window):
                    failure = failure or 'Attribution export source/window does not match the requested evidence'
                if not exported.get('events'):
                    gaps.append('No GPU events in the requested attribution window')
                attribution = {'path': str(attribution_path), 'sha256': file_hash(attribution_path), 'counts': exported.get('counts', {})}
            except (OSError, ValueError, UnicodeError):
                failure = failure or 'Unreadable CPU/GPU attribution export'
        else:
            gaps.append('Requested CPU/GPU attribution export is missing')
    worker_path = output / 'worker.json'
    if worker_path.is_file():
        try:
            with worker_path.open(encoding='utf-8') as stream:
                worker = json.load(stream)
            if not isinstance(worker, dict) or not isinstance(worker.get('tables'), dict):
                raise ValueError('Malformed worker summary')
            if not isinstance(worker.get('native_warnings', []), list):
                raise ValueError('Malformed native warning summary')
            if not trace_pattern and not worker.get('cpu_attribution_rows'):
                gaps.append('Native report has no CPU operator attribution rows; GPU-only tables do not establish launch linkage')
            if any(row.get('code') == 'native-kernel-detail-samples-skipped'
                   for row in worker.get('native_warnings', []) if isinstance(row, dict)):
                gaps.append('Native kernel-detail summaries skipped variable-length samples; inspect warnings and use exact events for coverage')
        except (OSError, ValueError, UnicodeError):
            failure = failure or 'Unreadable TraceLens worker summary'
    for inventory in inventories:
        try:
            changed = file_hash(inventory['path']) != inventory['sha256']
        except OSError:
            changed = True
        if changed:
            failure = 'Trace input changed or disappeared during analysis; retain outputs for diagnosis and recapture fixed evidence'
        if 'malformed-events' in inventory['training_gaps']:
            gaps.append('Malformed trace events require inspection')
        if trace_pattern:
            fields = inventory['observed_fields']
            if not fields.get('collective_kernels'):
                gaps.append('No identified collective kernels for rank ' + str(inventory['rank']))
            elif fields.get('collective_kernels_with_group', 0) != fields['collective_kernels']:
                gaps.append('Collective process-group metadata incomplete for rank ' + str(inventory['rank']) + '; inference stream-order matching is not validated training evidence')
            if fields.get('collective_kernels_with_link_id', 0) != fields.get('collective_kernels', 0):
                gaps.append('Collective correlation metadata incomplete for rank ' + str(inventory['rank']))
    result = {'status': 'failed' if failure else 'incomplete' if gaps else 'generated',
              'tool': 'TraceLens', 'source_commit': dependency['commit'],
              'source_repository': dependency.get('url'), 'upstream_commit': dependency.get('upstream_commit'), 'created_at': utc(),
              'mode': 'collective' if trace_pattern else 'pytorch', 'inputs': inventories,
              'argv': argv, 'output_directory': str(output), 'returncode': returncode,
              'worker': worker,
              'attribution_export': attribution,
              'tables': tables, 'gaps': gaps, 'failure': failure,
              'training_gaps': [{'rank': x['rank'], 'gaps': x['training_gaps']} for x in inventories if x['training_gaps']],
              'timing_contract': {'native_timeline_denominator': 'first GPU event start through last GPU event end; native tables span the supplied trace',
                                  'end_to_end_step_denominator': 'explicit caller-selected window for attribution/profile-analyze; native tables are not clipped' if window is not None else 'not established by the native report',
                                  'requested_window': window,
                                  'rank_clock_alignment': 'unverified',
                                  'overlap': 'overlapping time intervals do not prove useful overlap or dependency causality'},
              'gpu_arch': {'path': str(arch), 'sha256': file_hash(arch)} if arch else None,
              'training_assessment': 'unassessed: validate steady-state window, process groups, shapes and efficiency separately'}
    write_json(output / 'report.json', result)
    return result
