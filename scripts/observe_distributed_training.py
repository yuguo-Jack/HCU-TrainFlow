#!/usr/bin/env python3
"""Bounded CPU-only distributed member collection and aggregate verification."""
import argparse
import json
from pathlib import Path
import sys
import time

_SOURCE = Path(__file__).resolve().parents[1] / 'src'
if _SOURCE.exists():
    sys.path.insert(0, str(_SOURCE))

from hcu_trainflow.core import FlowError, read_json
from hcu_trainflow.distributed_observation import aggregate_members, collect_member, validate_group


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    for name in ('member', 'aggregate'):
        command = sub.add_parser(name)
        command.add_argument('--group', type=Path, required=True)
        command.add_argument('--state-dir', type=Path, required=True)
        command.add_argument('--output', type=Path, required=True)
        command.add_argument('--iterations', type=int, default=1)
        command.add_argument('--interval-seconds', type=float, default=30)
        if name == 'member':
            command.add_argument('--member', required=True)
            command.add_argument('--manifest', type=Path, required=True)
            command.add_argument('--exit-receipt', type=Path, required=True)
        else:
            command.add_argument('--member-file', action='append', default=[], metavar='ID=PATH')
    args = parser.parse_args()
    if not 1 <= args.iterations <= 2880 or not 1 <= args.interval_seconds <= 300:
        parser.error('Require bounded 1..2880 iterations and 1..300 second interval')
    if args.action == 'member' and sys.platform != 'linux':
        parser.error('Member collector must run in the launcher Linux PID namespace')
    try:
        group = validate_group(read_json(args.group))
        paths = {}
        for item in getattr(args, 'member_file', []):
            mid, sep, path = item.partition('=')
            if not sep or not path or mid in paths:
                raise FlowError('Each --member-file needs a unique ID=PATH')
            paths[mid] = Path(path)
        if args.action == 'aggregate' and set(paths) != {m['id'] for m in group['members']}:
            raise FlowError('Supply exactly one --member-file for every mandatory member')
        inputs = [args.group, *paths.values()]
        if args.action == 'member':
            inputs += [args.manifest, args.exit_receipt]
        if args.output.resolve() in {path.resolve() for path in inputs}:
            raise FlowError('Latest output cannot overwrite an observation input')
        status = None
        for index in range(args.iterations):
            if index:
                time.sleep(args.interval_seconds)
            if args.action == 'member':
                result = collect_member(group, args.member, args.manifest, args.state_dir,
                                        exit_path=args.exit_receipt, output_path=args.output)
                status = result['state']
            else:
                snapshots = {}
                for mid, path in paths.items():
                    try:
                        if path.stat().st_size > 2 * 1024**2:
                            raise FlowError('Member snapshot exceeds bounded JSON size')
                        snapshots[mid] = read_json(path)
                    except (OSError, ValueError) as exc:
                        snapshots[mid] = {'error': str(exc)}
                result = aggregate_members(group, snapshots, args.state_dir, output_path=args.output)
                status = result['status']
            print(json.dumps({'status': status, 'output': str(args.output), 'sha256': result['sha256'],
                              'completion_verified': result.get('completion_verified', False)}), flush=True)
        return 2 if status == 'attention' else 0
    except (OSError, ValueError) as exc:
        print(json.dumps({'status': 'error', 'message': str(exc)}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
