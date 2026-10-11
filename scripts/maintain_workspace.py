#!/usr/bin/env python3
"""Bounded cache/retired-output maintenance and disk capacity; dry-run by default."""
import argparse
import json
from pathlib import Path
import sys
import time

SOURCE = Path(__file__).resolve().parents[1] / "src"
if SOURCE.exists(): sys.path.insert(0, str(SOURCE))
from hcu_trainflow.core import FlowError, Store, read_json
from hcu_trainflow.retention import (TEMP_KINDS, MAINTENANCE_TRIGGERS, register_cache, register_temporary,
                                     retire_temporary, pin_cache, apply_retention, capacity_status,
                                     sweep_workspace, maintenance_tick)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    commands = parser.add_subparsers(dest="action")
    register = commands.add_parser("register", help="Attest a standalone cache generation is reproducible")
    register.add_argument("path"); register.add_argument("--rebuild", required=True)
    temporary = commands.add_parser("register-temporary", help="Register an owned temporary output, protected until retired")
    temporary.add_argument("path"); temporary.add_argument("--kind", choices=sorted(TEMP_KINDS), required=True)
    temporary.add_argument("--owner", required=True)
    retire = commands.add_parser("retire", help="Retire stopped temporary output after preserving necessary evidence")
    retire.add_argument("path"); retire.add_argument("--owner", required=True)
    retire.add_argument("--reason", required=True); retire.add_argument("--evidence", required=True, help="Retained artifact SHA-256")
    retire.add_argument("--producer-stopped", action="store_true")
    pin = commands.add_parser("pin", help="Acquire/release a cache-use pin before/after use")
    pin.add_argument("path"); pin.add_argument("--owner", required=True); pin.add_argument("--release", action="store_true")
    commands.add_parser("plan", help="Dry-run; never delete")
    commands.add_parser("capacity", help="Check filesystem headroom without walking any output trees")
    apply = commands.add_parser("apply", help="Apply one retained plan after all guards are rechecked")
    apply.add_argument("plan_hash"); apply.add_argument("--enable-delete", action="store_true")
    tick = commands.add_parser("tick", help="Low-frequency maintenance hook; defaults to one dry-run")
    tick.add_argument("--trigger", choices=sorted(MAINTENANCE_TRIGGERS), default="periodic")
    tick.add_argument("--scan-interval-hours", type=float, default=6)
    tick.add_argument("--resume-after-review", action="store_true", help="Only after reconciling a previous partial/failed sweep")
    tick.add_argument("--iterations", type=int, default=1)
    tick.add_argument("--interval-seconds", type=float, default=300)
    tick.add_argument("--enable-delete", action="store_true", help="Explicitly opt in to applying fresh generated plans")
    # Shared policy fields precede the subcommand to keep shell usage unambiguous.
    parser.add_argument("--keep-last", type=int, default=3)
    parser.add_argument("--min-age-days", type=float, default=7)
    parser.add_argument("--max-scan-seconds", type=float, default=60)
    parser.add_argument("--temporary-min-age-hours", type=float, default=1)
    parser.add_argument("--min-free-gib", type=float, default=20)
    parser.add_argument("--min-free-percent", type=float, default=10)
    args = parser.parse_args(argv)
    try:
        if not (args.workspace / "state.sqlite3").is_file():
            raise FlowError("Use an existing private TrainFlow workspace")
        store = Store(args.workspace)
        action = args.action or "plan"
        if action == "register":
            results = [register_cache(store, args.path, args.rebuild)]
        elif action == "register-temporary":
            results = [register_temporary(store, args.path, args.kind, args.owner)]
        elif action == "retire":
            results = [retire_temporary(store, args.path, args.owner, args.reason, args.evidence,
                                        producer_stopped=args.producer_stopped)]
        elif action == "pin":
            results = [pin_cache(store, args.path, args.owner, release=args.release)]
        elif action == "capacity":
            results = [capacity_status(store, min_free_bytes=args.min_free_gib * 1024**3,
                                       min_free_percent=args.min_free_percent)]
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
                options = {"plan_options": {"keep_last": args.keep_last, "min_age_seconds": args.min_age_days * 86400,
                    "max_scan_seconds": args.max_scan_seconds, "temporary_min_age_seconds": args.temporary_min_age_hours * 3600},
                    "capacity_options": {"min_free_bytes": args.min_free_gib * 1024**3, "min_free_percent": args.min_free_percent}}
                if action == "tick":
                    result = maintenance_tick(store, trigger=args.trigger, scan_interval_seconds=args.scan_interval_hours * 3600,
                        enabled=args.enable_delete, resume_after_review=args.resume_after_review and i == 0, **options)
                else:
                    result = sweep_workspace(store, **options)
                results.append(result)
                # Surface pressure immediately, not after up to an hour of polls.
                if result["capacity_after"]["status"] == "low-space": break
                if i + 1 < iterations: time.sleep(interval)
        print(json.dumps({"results": results}, ensure_ascii=False, allow_nan=False, indent=2))
        if any(r.get("capacity_after", r).get("status") == "low-space" for r in results):
            return 2
        return 0
    except (FlowError, OSError, ValueError, KeyError) as exc:
        print(json.dumps({"status": "attention", "message": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
