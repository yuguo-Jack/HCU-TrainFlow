#!/usr/bin/env python3
"""Run the training log adapter and monitor on the remote host, without restart."""
import argparse
import json
import os
from pathlib import Path
import signal
import sqlite3
import sys
import time

_SOURCE = Path(__file__).resolve().parents[1] / "src"
if _SOURCE.exists():
    sys.path.insert(0, str(_SOURCE))

from hcu_trainflow.core import FlowError, fingerprint, read_json, write_json
from hcu_trainflow.training_logs import observe_once, observer_lock, process_identity


class ObserverStopped(Exception):
    pass


def _stop(signum, frame):
    raise ObserverStopped()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True, help="Remote private Store with the registered task")
    parser.add_argument("--task", required=True)
    parser.add_argument("--manifest", type=Path, required=True, help="Current immutable attempt manifest; replace atomically for a new attempt")
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--state-dir", type=Path, help="Private observer-owned directory; defaults to WORKSPACE/training-logs/TASK")
    parser.add_argument("--exit-receipt", type=Path, help="Atomically written real wrapper/scheduler exit receipt")
    parser.add_argument("--interval-seconds", type=float, default=30)
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--continue-after-finish", action="store_true", help="Keep watching for an explicitly registered next attempt")
    parser.add_argument("--lifecycle-dir", type=Path, help="Private immutable launch directory created by manage_training_observer.py")
    args = parser.parse_args()
    if sys.platform != "linux":
        parser.error("Remote observer requires Linux PID identity support")
    if not 0 < args.interval_seconds <= 300:
        parser.error("Observation interval must be in (0,300] seconds")
    state_dir = args.state_dir or args.workspace / "training-logs" / args.task
    lifecycle, handlers = None, {}
    outcome = {"exit_code": None, "reason": "observer-aborted-without-return-code"}
    try:
        if args.lifecycle_dir:
            request = read_json(args.lifecycle_dir / "request.json")
            # A managed daemon is pinned to one attempt and one policy. New
            # attempts require explicit stop/start, not an unnoticed path swap.
            expected = request["spec"]
            actual = {"workspace": str(args.workspace.resolve()), "task": args.task,
                      "manifest": str(args.manifest.resolve()), "policy": str(args.policy.resolve()),
                      "state_dir": str(state_dir.resolve()),
                      "exit_receipt": str(args.exit_receipt.resolve()) if args.exit_receipt else None,
                      "interval_seconds": args.interval_seconds}
            if any(expected.get(key) != value for key, value in actual.items()) or args.continue_after_finish:
                raise FlowError("Managed observer arguments differ from the recorded launch request")
            identity = process_identity(os.getpid())
            if identity.get("status") != "alive":
                raise FlowError("Cannot establish observer process identity")
            lifecycle = {"launch_id": request["launch_id"], "spec_hash": fingerprint(expected),
                         "process": identity["identity"], "attempt_id": expected["attempt_id"], "context": expected["context"]}
            write_json(args.lifecycle_dir / "identity.json", lifecycle)
            for sig in (signal.SIGTERM, signal.SIGINT):
                handlers[sig] = signal.signal(sig, _stop)
        with observer_lock(state_dir) as lease:
            return run_loop(args, state_dir, lease, lifecycle, outcome)
    except ObserverStopped:
        outcome.update(exit_code=143, reason="observer-stop-requested")
        return 143
    except (FlowError, OSError, ValueError, KeyError, TypeError, sqlite3.Error) as exc:
        outcome.update(exit_code=2, reason="observer-error")
        outcome["error"] = type(exc).__name__ + ": " + str(exc)
        print(json.dumps({"observer_error": outcome["error"], "timestamp": time.time(),
                          "recovery_action": "none"}), file=sys.stderr, flush=True)
        return 2
    finally:
        if lifecycle:
            write_json(args.lifecycle_dir / "observer-exit.json", {**lifecycle, **outcome, "finished_at": time.time()})
        for sig, handler in handlers.items():
            signal.signal(sig, handler)


def run_loop(args, state_dir, lease, lifecycle, outcome):
    while True:
        if lifecycle:
            spec = read_json(args.lifecycle_dir / "request.json")["spec"]
            if (fingerprint(spec) != lifecycle["spec_hash"]
                    or fingerprint(read_json(args.manifest)) != spec["manifest_hash"]
                    or fingerprint(read_json(args.policy)) != spec["policy_hash"]):
                raise FlowError("Managed observer attempt or policy changed; establish a new launch")
        result = observe_once(args.workspace, args.task, args.manifest, args.policy,
                              state_dir, args.exit_receipt, lease)
        print(json.dumps(result, ensure_ascii=False, allow_nan=False), flush=True)
        if lifecycle:
            heartbeat = {**lifecycle, "checked_at": time.time(), "result": result}
            write_json(args.lifecycle_dir / "heartbeat.json", heartbeat)
            if not (args.lifecycle_dir / "ready.json").exists():
                write_json(args.lifecycle_dir / "ready.json", heartbeat)
        # The adapter's terminal label is a claim. Monitor independently
        # checks progress, numerical failures, clocks and the exit proof.
        terminal = result["monitor"].get("completion_verified") is True
        if args.once:
            code = 0 if result["status"] == "healthy-observed" else 2
            outcome.update(exit_code=code, reason="single-poll-ended")
            return code
        if terminal and not args.continue_after_finish:
            outcome.update(exit_code=0, reason="training-completion-verified")
            return 0
        time.sleep(args.interval_seconds)

if __name__ == "__main__":
    raise SystemExit(main())
