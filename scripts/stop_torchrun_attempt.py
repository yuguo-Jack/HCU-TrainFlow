#!/usr/bin/env python3
"""Stop one recorded torchrun descendant, inside its original PID namespace.

For an explicitly authorized recovery owner. Never matches arbitrary Python
processes, never kills a node/container, never starts a replacement. A successful
receipt still requires fresh device admission before another attempt.
"""
import argparse
import json
import os
from pathlib import Path
import signal
import sys
import time

_SOURCE = Path(__file__).resolve().parents[1] / 'src'
if _SOURCE.exists():
    sys.path.insert(0, str(_SOURCE))
from hcu_trainflow.core import FlowError, read_json, write_json
from hcu_trainflow.training_logs import process_identity, validate_manifest


def command(pid):
    return [x.decode('utf8') for x in (Path('/proc') / str(pid) / 'cmdline').read_bytes().split(b'\0') if x]


def parent(pid):
    stat = (Path('/proc') / str(pid) / 'stat').read_text()
    return int(stat[stat.rfind(')') + 2:].split()[1])


def descendant(pid, ancestor):
    seen = set()
    while pid > 1 and pid not in seen:
        if pid == ancestor:
            return True
        seen.add(pid)
        try:
            pid = parent(pid)
        except FileNotFoundError:
            return False
    return False


def same(identity):
    current = process_identity(identity['pid'])
    return current.get('status') == 'alive' and current.get('identity') == identity


def gone(identity):
    """An unreadable /proc identity is uncertainty, not exit confirmation."""
    current = process_identity(identity['pid'])
    return (current.get('status') == 'exited'
            or (current.get('status') == 'alive' and current.get('identity') != identity))


def find_torchrun(root):
    matches = []
    for p in Path('/proc').iterdir():
        if not p.name.isdecimal():
            continue
        pid = int(p.name)
        try:
            if not descendant(pid, root):
                continue
            argv = command(pid)
            if any(argv[i:i+2] == ['-m', 'torch.distributed.run'] for i in range(len(argv)-1)):
                identity = process_identity(pid)
                if identity.get('status') == 'alive':
                    matches.append((identity['identity'], argv))
        except (FileNotFoundError, ProcessLookupError):
            continue
    if len(matches) != 1:
        raise FlowError('Expected exactly one live torchrun descendant; no signal sent')
    return matches[0]


def stop(directory, *, context, attempt_id, timeout=60):
    if not (hasattr(os, 'pidfd_open') and hasattr(signal, 'pidfd_send_signal')):
        raise FlowError('Linux pidfd is required; no numeric PID fallback')
    if type(timeout) not in (int, float) or not 0 < timeout <= 300:
        raise FlowError('Stop timeout must be positive and <= 300 seconds')
    directory = Path(directory).resolve(strict=True)
    manifest = validate_manifest(read_json(directory / 'attempt.json'))
    if manifest['context'] != context or manifest['attempt_id'] != attempt_id:
        raise FlowError('Attempt/context mismatch; no signal sent')
    receipt_path = directory / 'exit.json'
    if receipt_path.exists():
        raise FlowError('Attempt already has an exit receipt; reconcile it instead of signaling')
    wrapper = manifest['process']
    if not same(wrapper):
        raise FlowError('Original wrapper identity is unavailable; reconcile before signaling')
    child = read_json(directory / 'child.json')
    if child.get('wrapper_process') != wrapper or parent(child['pid']) != wrapper['pid']:
        raise FlowError('Training child no longer belongs to the original wrapper')
    identity, argv = find_torchrun(child['pid'])
    fd = os.pidfd_open(identity['pid'])
    try:
        if (not same(wrapper) or not same(identity) or command(identity['pid']) != argv
                or not descendant(identity['pid'], child['pid'])
                or parent(child['pid']) != wrapper['pid']):
            raise FlowError('Process ancestry changed before signaling; no signal sent')
        requested_at = time.time()
        signal.pidfd_send_signal(fd, signal.SIGTERM)
    finally:
        os.close(fd)
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if receipt_path.exists() and gone(identity):
            receipt = read_json(receipt_path)
            if (receipt.get('process') != wrapper or receipt.get('context') != context
                    or receipt.get('attempt_id') != attempt_id):
                raise FlowError('Exit receipt does not match the stopped attempt')
            result = {'status': 'terminal-receipt-observed', 'attempt_id': attempt_id,
                      'context': context, 'target': identity, 'signal': 'SIGTERM',
                      'requested_at': requested_at, 'confirmed_at': time.time(),
                      'exit_code': receipt['exit_code'],
                      'scope': 'torchrun descendant stopped; device/other-member cleanup and checkpoint recovery remain separate checks'}
            write_json(directory / 'stop-receipt.json', result)
            return result
        time.sleep(.2)
    raise FlowError('Stop unconfirmed at deadline; no escalation or replacement launch')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--attempt-dir', type=Path, required=True)
    p.add_argument('--context', required=True)
    p.add_argument('--attempt-id', required=True)
    p.add_argument('--timeout', type=float, default=60)
    a = p.parse_args()
    try:
        print(json.dumps(stop(a.attempt_dir, context=a.context, attempt_id=a.attempt_id, timeout=a.timeout)))
        return 0
    except (FlowError, OSError, ValueError, KeyError) as error:
        print(json.dumps({'status': 'unconfirmed', 'error': str(error), 'restart_allowed': False}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
