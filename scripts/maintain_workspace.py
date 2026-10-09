#!/usr/bin/env python3
"""Explicit private cache registry and bounded retention; dry-run by default."""
import argparse
import json
from pathlib import Path
import sys
import time

SOURCE = Path(__file__).resolve().parents[1] / "src"
if SOURCE.exists(): sys.path.insert(0, str(SOURCE))
from hcu_trainflow.core import FlowError, Store, read_json
from hcu_trainflow.retention import register_cache, pin_cache, plan_retention, apply_retention


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    commands = parser.add_subparsers(dest="action")
    register = commands.add_parser("register", help="Attest a standalone cache generation is reproducible")
    register.add_argument("path"); register.add_argument("--rebuild", required=True)
    pin = commands.add_parser("pin", help="Acquire/release a cache-use pin before/after use")
    pin.add_argument("path"); pin.add_argument("--owner", required=True); pin.add_argument("--release", action="store_true")
    commands.add_parser("plan", help="Dry-run; never delete")
    apply = commands.add_parser("apply", help="Apply one retained plan after all guards are rechecked")
    apply.add_argument("plan_hash"); apply.add_argument("--enable-delete", action="store_true")
    tick = commands.add_parser("tick", help="Bounded maintenance hook; defaults to one dry-run")
    tick.add_argument("--iterations", type=int, default=1)
    tick.add_argument("--interval-seconds", type=float, default=300)
    tick.add_argument("--enable-delete", action="store_true", help="Explicitly opt in to applying fresh generated plans")
    # Shared policy fields precede the subcommand to keep shell usage unambiguous.
    parser.add_argument("--keep-last", type=int, default=3)
    parser.add_argument("--min-age-days", type=float, default=7)
    parser.add_argument("--max-scan-seconds", type=float, default=60)
    args = parser.parse_args(argv)
    try:
        if not (args.workspace / "state.sqlite3").is_file():
            raise FlowError("Use an existing private TrainFlow workspace")
        store = Store(args.workspace)
        action = args.action or "plan"
        if action == "register":
            results = [register_cache(store, args.path, args.rebuild)]
        elif action == "pin":
            results = [pin_cache(store, args.path, args.owner, release=args.release)]
        elif action == "apply":
            if len(args.plan_hash) != 64 or any(c not in "0123456789abcdef" for c in args.plan_hash):
                raise FlowError("Use the exact hexadecimal plan hash from dry-run")
            plan = read_json(store.root / ".maintenance/plans" / (args.plan_hash + ".json"))
            results = [apply_retention(store, plan, args.plan_hash, enabled=args.enable_delete)]
        else:
            iterations = args.iterations if action == "tick" else 1
            interval = args.interval_seconds if action == "tick" else 300
            if not 1 <= iterations <= 12 or not 60 <= interval <= 300:
                raise FlowError("A maintenance invocation is bounded to 1..12 polls and 60..300 second intervals")
            results = []
            for i in range(iterations):
                plan = plan_retention(store, keep_last=args.keep_last, min_age_seconds=args.min_age_days * 86400,
                                      max_scan_seconds=args.max_scan_seconds)
                candidates = [r for r in plan["entries"] if r["action"] == "remove"]
                result = {"status": "dry-run", "plan_hash": plan["plan_hash"], "remove_bytes": sum(r["tree"]["bytes"] for r in candidates),
                    "entries": [{"path": r["path"], "action": r["action"], "reasons": r["reasons"]} for r in plan["entries"]],
                    "plan_path": str(store.root / ".maintenance/plans" / (plan["plan_hash"] + ".json"))}
                if action == "tick" and args.enable_delete and candidates:
                    result = apply_retention(store, plan, plan["plan_hash"], enabled=True)
                results.append(result)
                if i + 1 < iterations: time.sleep(interval)
        print(json.dumps({"results": results}, ensure_ascii=False, allow_nan=False, indent=2))
        return 0
    except (FlowError, OSError, ValueError, KeyError) as exc:
        print(json.dumps({"status": "attention", "message": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
