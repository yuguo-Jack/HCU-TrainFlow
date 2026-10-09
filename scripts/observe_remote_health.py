#!/usr/bin/env python3
"""Observe a pinned remote watcher through read-only files, in an independent Store.

No training commands, automatic recovery, SSH, notifications or Agent launches.
Use a node-local task-owned workspace. File reads run in a bounded subprocess;
an uninterruptible filesystem read is reported and never multiplied into a fork loop.
"""
import argparse
import json
import os
from pathlib import Path
import signal
import sqlite3
import subprocess
import sys
import time
import uuid

_SOURCE = Path(__file__).resolve().parents[1] / 'src'
if _SOURCE.exists():
    sys.path.insert(0, str(_SOURCE))

from hcu_trainflow.core import FlowError, Store, fingerprint, read_json, write_json
from hcu_trainflow.observer_health import capture_sources, record_health, validate_contract
from hcu_trainflow.training_logs import observer_lock, process_identity


class BoundedReader:
    def __init__(self, directory, timeout, *, script=None):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.timeout = timeout
        self.script = str(script or Path(__file__).resolve())
        self.pending = None
        self.state_path = self.directory / 'reader-process.json'

    def collect(self, contract_path):
        if self.pending is not None and self.pending.poll() is not None:
            self.pending = None  # reap only a returned child; never blocking wait
        if self.state_path.exists():
            old = read_json(self.state_path)
            identity = old.get('process')
            current = process_identity(identity['pid']) if identity else {'status': 'unknown'}
            # On restart, never signal a PID based only on a stale numeric PID.
            if current['status'] != 'exited' and current.get('identity') == identity:
                return {'error': 'previous-source-reader-still-running; no new reader spawned', 'files': {}}
            if current['status'] == 'unknown':
                return {'error': 'previous-source-reader-identity-unresolved', 'files': {}}
            self.state_path.unlink()
        read_id = uuid.uuid4().hex
        output = self.directory / (read_id + '.json')
        stderr_path = self.directory / (read_id + '.stderr.log')
        argv = [sys.executable, '-B', self.script, '--collect', str(contract_path), '--result', str(output)]
        with stderr_path.open('ab') as stderr:
            child = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                     stderr=stderr, start_new_session=True)
        self.pending = child
        identity = process_identity(child.pid).get('identity')
        write_json(self.state_path, {'pid': child.pid, 'process': identity, 'argv': argv,
                                     'started_at': time.time(), 'output': str(output)})
        deadline = time.monotonic() + self.timeout
        while child.poll() is None and time.monotonic() < deadline:
            time.sleep(min(0.05, max(0, deadline - time.monotonic())))
        if child.poll() is None:
            # We own this exact Popen child. kill is nonblocking; do not wait on
            # a task stuck in kernel D state. Keep its receipt for the next poll.
            child.kill()
            return {'error': 'source-read-timeout; own reader signalled, remote state unknown', 'files': {}}
        self.state_path.unlink()
        self.pending = None
        if child.returncode != 0 or not output.exists():
            return {'error': 'source-reader-failed; exit=' + str(child.returncode), 'files': {}}
        if output.stat().st_size > 32 * 1024**2:
            return {'error': 'source-reader-output-too-large', 'files': {}}
        return read_json(output)


class Stopped(Exception):
    pass


def _stop(signum, frame):
    raise Stopped()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, help='Dedicated node-local task Store; never the watched Store')
    parser.add_argument('--contract', type=Path, help='Local immutable contract copy')
    parser.add_argument('--interval-seconds', type=float, default=30)
    parser.add_argument('--max-polls', type=int, default=0, help='Positive limit for bounded qualification; 0 continues')
    parser.add_argument('--once', action='store_true')
    parser.add_argument('--collect', type=Path, help=argparse.SUPPRESS)
    parser.add_argument('--result', type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.collect:
        if args.result is None:
            parser.error('Internal source reader requires result path')
        write_json(args.result, capture_sources(read_json(args.collect)))
        return 0
    if args.workspace is None or args.contract is None:
        parser.error('workspace and local contract are required')
    if (not 0 < args.interval_seconds <= 300 or args.max_polls < 0 or args.max_polls > 100000):
        parser.error('Bounded positive interval and nonnegative max-polls required')
    contract = validate_contract(read_json(args.contract))
    root = args.workspace.resolve()
    source_root = Path(os.path.normpath(contract['source_root']))
    if args.contract.resolve().is_relative_to(source_root):
        parser.error('Copy the contract to the observer local filesystem first')
    if root.is_relative_to(source_root):
        parser.error('Health Store must be outside the watched shared source filesystem root')
    current = process_identity(os.getpid())
    if current.get('status') != 'alive':
        parser.error('Linux observer process identity is required')
    if current['identity']['boot_id'] == contract['expected']['observer_process']['boot_id']:
        parser.error('Same kernel boot ID as watched observer; choose an independent host')
    store = Store(root)
    config_hash = fingerprint(contract)
    local = root / 'observer-health'
    result = {'exit_code': None, 'reason': 'sentinel-aborted', 'contract_hash': config_hash,
              'process': current['identity'], 'started_at': time.time()}
    handlers, owned = {}, False
    run_dir = local / 'sentinel-launches' / uuid.uuid4().hex
    result['run_dir'] = str(run_dir)
    try:
        with observer_lock(local, name='independent-health.lock'):
            # One concrete node owns this Store; a copied DB cannot silently
            # become concurrent shared-node coordination.
            owner_path = local / 'owner.json'
            owner = {'observer_domain': contract['observer_domain'], 'boot_id': current['identity']['boot_id']}
            if owner_path.exists() and read_json(owner_path) != owner:
                raise FlowError('Health Store belongs to another observer domain/boot; reconcile before reuse')
            write_json(owner_path, owner)
            owned = True
            write_json(run_dir / 'identity.json', result)
            write_json(local / 'sentinel-process.json', result)
            for sig in (signal.SIGINT, signal.SIGTERM):
                handlers[sig] = signal.signal(sig, _stop)
            reader = BoundedReader(local / 'readers', contract['policy']['source_read_timeout_seconds'])
            count = 0
            while True:
                if fingerprint(read_json(args.contract)) != config_hash:
                    raise FlowError('Pinned local contract changed; explicitly launch a new observer scope')
                bundle = reader.collect(args.contract)
                health = record_health(store, contract, bundle)
                print(json.dumps(health, ensure_ascii=False, allow_nan=False), flush=True)
                count += 1
                if args.once or (args.max_polls and count >= args.max_polls):
                    result.update(exit_code=0, reason='bounded-observation-finished')
                    return 0
                # Keep checking even after completion, so an unexpected new
                # attempt/launch cannot hide behind an old terminal receipt.
                time.sleep(args.interval_seconds)
    except Stopped:
        result.update(exit_code=143, reason='sentinel-stop-requested')
        return 143
    except (FlowError, OSError, ValueError, KeyError, TypeError, sqlite3.Error) as exc:
        result.update(exit_code=2, reason='sentinel-error', error=type(exc).__name__ + ': ' + str(exc))
        print(json.dumps(result), file=sys.stderr, flush=True)
        return 2
    finally:
        result['finished_at'] = time.time()
        # If the independent disk is unavailable, this write can also fail.
        # The deployment supervisor must monitor our own process/heartbeat.
        if owned:
            write_json(run_dir / 'sentinel-exit.json', result)
        for sig, handler in handlers.items():
            signal.signal(sig, handler)


if __name__ == '__main__':
    raise SystemExit(main())
