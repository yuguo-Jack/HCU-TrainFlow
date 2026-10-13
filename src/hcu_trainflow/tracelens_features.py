"""Pinned, offline advanced TraceLens analyses with immutable input receipts.

This entry never starts a GPU experiment or an LLM service. Native Agent metrics
are prepared for the active workflow Agent to interpret and independently review.
"""
import json
import os
import re
from pathlib import Path
import signal
import subprocess
import sys
import uuid

from .core import FlowError, read_json, write_json, utc
from .dependencies import require_checkout
from .tracelens import file_hash, worker_environment


FIELDS = {
    'hipprof': ({'trace'}, {'traceconv_path'}),
    'graph': ({'manifest', 'capture_folder'}, {'gpu_arch_json'}),
    'roofline': ({'perf_csv', 'gpu_arch_json'}, {'wallclock_time_us'}),
    'agent': ({'trace', 'gpu_arch_json'}, set()),
    'counters': ({'manifest'}, set()),
    'compare': ({'trace', 'comparison_trace'}, {'gpu_arch_json'}),
    'split': ({'trace', 'iterations'}, set()),
    'merge': ({'traces'}, set()),
}


def run_bounded(argv, *, timeout, **kwargs):
    """Reap the whole offline analysis tree, including native converters."""
    options = {'creationflags': subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == 'nt' else {'start_new_session': True}
    process = subprocess.Popen(argv, **kwargs, **options)
    try:
        return subprocess.CompletedProcess(argv, process.wait(timeout=timeout))
    except subprocess.TimeoutExpired:
        if os.name == 'nt':
            cleanup = subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'],
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
            if cleanup.returncode and process.poll() is None:
                process.kill()
                process.wait(timeout=10)
                raise OSError('Analysis process-tree cleanup failed; inspect retained operation before retry')
        else:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        process.wait(timeout=10)
        raise


def prepare_request(request, base):
    if not isinstance(request, dict) or request.get('mode') not in FIELDS:
        raise FlowError('Expected an advanced TraceLens mode: ' + ', '.join(FIELDS))
    required, optional = FIELDS[request['mode']]
    if required - request.keys() or request.keys() - (required | optional | {'mode'}):
        raise FlowError('Missing or unknown fields for TraceLens ' + request['mode'])
    value = dict(request)
    inputs = {}

    def add(path):
        path = Path(path)
        path = (base / path).resolve() if not path.is_absolute() else path.resolve()
        if not path.is_file():
            raise FlowError('Missing analysis input: ' + str(path))
        inputs[str(path)] = file_hash(path)
        return str(path)

    for field in ('trace', 'comparison_trace', 'traceconv_path', 'perf_csv', 'gpu_arch_json', 'manifest'):
        if field in value:
            if not isinstance(value[field], str) or not value[field]:
                raise FlowError('Expected a file path: ' + field)
            value[field] = add(value[field])
    if value['mode'] == 'split':
        selection = value['iterations']
        if not isinstance(selection, str) or not re.fullmatch(r'\d+(?::\d+)?', selection):
            raise FlowError('iterations must be an explicit zero-based N or START:END (end exclusive)')
        if ':' in selection:
            start, end = map(int, selection.split(':'))
            if end <= start:
                raise FlowError('Iteration range must be nonempty and increasing')
    if value['mode'] == 'merge':
        traces = value['traces']
        if not isinstance(traces, dict) or len(traces) < 2:
            raise FlowError('traces must map at least two actual rank IDs to files')
        if any(not isinstance(rank, str) or not re.fullmatch(r'0|[1-9]\d*', rank) for rank in traces):
            raise FlowError('Rank IDs must be canonical nonnegative integers')
        if any(not isinstance(path, str) or not path for path in traces.values()):
            raise FlowError('Each rank needs a trace file path')
        value['traces'] = {rank: add(traces[rank]) for rank in sorted(traces, key=int)}
        if len(set(value['traces'].values())) != len(traces):
            raise FlowError('Different ranks must not reuse the same trace file')
    if value['mode'] == 'hipprof' and str(value['trace']).lower().endswith(('.pftrace', '.pftrace.gz')) and not value.get('traceconv_path'):
        raise FlowError('Offline pftrace analysis requires an explicit installed traceconv_path')
    if 'wallclock_time_us' in value:
        from .analysis import number
        if number(value['wallclock_time_us'], 'wallclock_time_us') <= 0:
            raise FlowError('Wall-clock span must be positive')
    if value['mode'] == 'graph':
        if not isinstance(value['capture_folder'], str):
            raise FlowError('capture_folder must be a directory path')
        folder = (base / value['capture_folder']).resolve()
        if not folder.is_dir():
            raise FlowError('Graph capture folder is missing')
        value['capture_folder'] = str(folder)
        manifest = read_json(value['manifest'])
        try:
            files = [manifest['replay_file']] + [row['file'] for row in manifest['captures']]
            for name in files:
                path = (folder / name).resolve()
                if not path.is_relative_to(folder):
                    raise FlowError('Graph input escapes its capture folder')
                add(path)
        except (KeyError, TypeError) as exc:
            raise FlowError('Invalid training Graph manifest') from exc
    if value['mode'] == 'counters':
        # The native parser validates the manifest and every nested file hash.
        # Snapshot all local files referenced by path/file for the outer receipt.
        root = Path(value['manifest']).parent
        def visit(item):
            if isinstance(item, dict):
                for key, val in item.items():
                    if key in {'path', 'file'} and isinstance(val, str):
                        p = (root / val).resolve()
                        if p.is_file():
                            add(p)
                    else:
                        visit(val)
            elif isinstance(item, list):
                for child in item:
                    visit(child)
        visit(read_json(value['manifest']))
    return value, inputs


def run_feature(store, project, request_path, timeout=1800):
    if isinstance(timeout, bool) or not isinstance(timeout, int) or not 1 <= timeout <= 86400:
        raise FlowError('TraceLens timeout must be 1..86400 seconds')
    request_path = Path(request_path).resolve()
    request_hash = file_hash(request_path)
    request, inputs = prepare_request(read_json(request_path), request_path.parent)
    inputs[str(request_path)] = request_hash
    checkout, dependency = require_checkout(project, 'tracelens')
    output = store.root / 'tracelens' / uuid.uuid4().hex
    output.mkdir(parents=True)
    write_json(output / 'request.json', request)
    argv = [sys.executable, '-B', '-m', 'hcu_trainflow.tracelens_feature_worker', str(output / 'request.json')]
    env = worker_environment(checkout, output)
    failure, code, worker = None, None, None
    with (output / 'stdout.log').open('wb') as stdout, (output / 'stderr.log').open('wb') as stderr:
        try:
            code = run_bounded(argv, cwd=output, env=env, stdout=stdout, stderr=stderr, timeout=timeout).returncode
            if code:
                failure = 'Native analysis failed; retained logs are in the output directory'
        except (subprocess.TimeoutExpired, OSError) as exc:
            failure = 'Native analysis did not complete: ' + type(exc).__name__
    if (output / 'worker.json').is_file():
        try:
            worker = read_json(output / 'worker.json')
            if not isinstance(worker, dict) or worker.get('status') not in {'generated', 'incomplete', 'needs-agent-review'}:
                failure = failure or 'Invalid native worker receipt'
        except (ValueError, OSError):
            failure = failure or 'Unreadable native worker receipt'
    else:
        failure = failure or 'Missing native worker receipt; output files alone do not prove completion'
    for path, digest in inputs.items():
        if not Path(path).is_file() or file_hash(path) != digest:
            failure = 'Analysis input changed or disappeared during the run'
    artifacts = [{'path': str(p.relative_to(output)), 'sha256': file_hash(p), 'bytes': p.stat().st_size}
                 for p in sorted(output.rglob('*')) if p.is_file()]
    result = {'status': 'failed' if failure else worker['status'], 'mode': request['mode'],
              'source_repository': dependency.get('url'), 'source_commit': dependency['commit'],
              'created_at': utc(), 'output_directory': str(output), 'returncode': code,
              'inputs': [{'path': path, 'sha256': digest} for path, digest in inputs.items()],
              'artifacts': artifacts, 'worker': worker, 'failure': failure,
              'training_assessment': 'unassessed; artifact generation is not a workflow gate, loss validation or end-to-end speedup',
              'execution_scope': 'offline CPU analysis; no GPU admission or training launch'}
    write_json(output / 'report.json', result)
    return result
