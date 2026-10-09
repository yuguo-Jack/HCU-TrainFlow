"""Run the pinned TraceLens API locally, retaining its native tables and logs."""
import csv
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid

from .core import FlowError, utc, write_json
from .dependencies import require_checkout


def file_hash(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def trace_inventory(path):
    path = Path(path).resolve()
    opener = gzip.open if path.suffix == '.gz' else open
    with opener(path, 'rt', encoding='utf-8-sig') as stream:
        trace = json.load(stream)
    events = trace.get('traceEvents', []) if isinstance(trace, dict) else trace
    if not isinstance(events, list) or not events:
        raise FlowError('Trace has no events')
    counts = {'gpu_kernels': 0, 'cpu_ops': 0}
    for event in events:
        if not isinstance(event, dict):
            continue
        category = str(event.get('cat', '')).lower()
        if event.get('ph') == 'X' and event.get('dur', 0) > 0:
            counts['gpu_kernels'] += category == 'kernel'
            counts['cpu_ops'] += category == 'cpu_op'
    return {'path': str(path), 'sha256': file_hash(path), **counts}


def run_report(store, project, trace=None, trace_pattern=None, world_size=None,
               gpu_arch_json=None, timeout=1800, rank=None):
    checkout, dependency = require_checkout(project, 'tracelens')
    if not 1 <= timeout <= 86400:
        raise FlowError('TraceLens timeout must be between 1 and 86400 seconds')
    if bool(trace) == bool(trace_pattern):
        raise FlowError('Provide exactly one trace or a complete-rank trace pattern')
    if trace_pattern:
        if not isinstance(world_size, int) or not 2 <= world_size <= 65536 or trace_pattern.count('*') != 1:
            raise FlowError('Collective report requires world_size >= 2 and one rank placeholder (*)')
        paths = [Path(trace_pattern.replace('*', str(i))).resolve() for i in range(world_size)]
        if not all(p.is_file() for p in paths):
            raise FlowError('TraceLens collective analysis requires every rank 0..world_size-1; keep partial sampling explicit')
        inventories = [dict(trace_inventory(p), rank=i) for i, p in enumerate(paths)]
        kwargs = {'trace_pattern': str(Path(trace_pattern).resolve()), 'world_size': world_size}
    else:
        if rank is not None and rank < 0:
            raise FlowError('Rank must be nonnegative')
        inventories = [dict(trace_inventory(trace), rank=rank)]
        kwargs = {'profile_json_path': inventories[0]['path'], 'include_unlinked_kernels': True,
                  'kernel_summary': True, 'include_overlap_info': True}
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
    result = {'status': 'failed' if failure else 'incomplete' if gaps else 'generated',
              'tool': 'TraceLens', 'source_commit': dependency['commit'], 'created_at': utc(),
              'mode': 'collective' if trace_pattern else 'pytorch', 'inputs': inventories,
              'argv': argv, 'output_directory': str(output), 'returncode': returncode,
              'tables': tables, 'gaps': gaps, 'failure': failure,
              'gpu_arch': {'path': str(arch), 'sha256': file_hash(arch)} if arch else None,
              'training_assessment': 'unassessed: validate steady-state window, process groups, shapes and efficiency separately'}
    write_json(output / 'report.json', result)
    return result
