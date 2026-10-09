#!/usr/bin/env python3
"""Manage a same-namespace observation process; never launch or stop training."""
import argparse
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import uuid

_SOURCE = Path(__file__).resolve().parents[1] / "src"
if _SOURCE.exists():
    sys.path.insert(0, str(_SOURCE))

from hcu_trainflow.core import FlowError, Store, fingerprint, read_json, write_json
from hcu_trainflow.monitor import check_policy
from hcu_trainflow.training_logs import observer_lock, process_identity, validate_manifest


SCOPE = "same process namespace only; no independent-node monitor, external alert or automatic restart"


def prepare_context_workspace(workspace, task, context_root):
    """Prepare an observation-only Store without mutating prior watcher history.

    A different parser state-dir alone does not migrate monitor.meta['watch:task'].
    Context epoch is included because A -> B -> A must not reuse A's old watcher.
    This helper does not stop/start observers or certify a safe runtime handoff.
    """
    workspace = Path(workspace).resolve()
    if not (workspace / "state.sqlite3").is_file():
        raise FlowError("Source workspace must already exist")
    source = Store(workspace)
    current = source.task(task)
    context_root = Path(context_root).resolve()
    destination = context_root / task / (current["context"] + "-e" + str(current["context_epoch"]))
    if destination == workspace:
        raise FlowError("Context observer Store must differ from source workspace")
    scope = {"schema_version": 1, "source_workspace": str(workspace), "task": task,
             "context": current["context"], "source_context_epoch": current["context_epoch"],
             "observer_workspace": str(destination),
             "purpose": "observation-only context scope; no training execution permission"}
    # Serialize preparation, never reinterpret an existing unknown Store.
    with observer_lock(destination.parent, name="context-prepare.lock"):
        marker = destination / "observer-scope.json"
        if destination.exists() and not marker.exists():
            raise FlowError("Existing destination lacks context-scope proof; preserve it and choose another root")
        if marker.exists():
            recorded_scope = read_json(marker)
            legacy_scope = {k: v for k, v in scope.items() if k != "observer_workspace"}
            if recorded_scope not in (scope, legacy_scope):
                raise FlowError("Observation Store belongs to a different source/context epoch")
        write_json(marker, scope)
        observer_store = Store(destination)
        with observer_store.db() as db:
            existing = db.execute("SELECT id FROM tasks WHERE id=?", (task,)).fetchone()
        spec = {**current["spec"], "permissions": []}
        if existing:
            registered = observer_store.task(task)
            if registered["context"] != current["context"] or registered["context_epoch"] != 0 or registered["spec"] != spec:
                raise FlowError("Prepared observation task was changed; do not overwrite it")
        else:
            observer_store.create(spec)
        refreshed = source.task(task)
        if (refreshed["context"], refreshed["context_epoch"], refreshed["spec"]) != (current["context"], current["context_epoch"], current["spec"]):
            raise FlowError("Source task changed during preparation; recheck scope before use")
    return {"status": "prepared-only", "workspace": str(destination), "task": task,
            "context": current["context"], "source_context_epoch": current["context_epoch"],
            "state_dir": str(destination / "training-logs" / task),
            "event_peer_suffix": fingerprint(scope),
            "handoff": "Verify/stop prior observer with its original scope, retain/export history, then start and verify the new observer. No process action performed."}


def _bound(value, name, maximum):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not 0 < value <= maximum:
        raise FlowError(name + " must be positive and <= " + str(maximum))
    return value


def make_spec(workspace, task, manifest, policy, state_dir=None, exit_receipt=None, interval=30):
    workspace = Path(workspace).resolve()
    manifest, policy = Path(manifest).resolve(), Path(policy).resolve()
    attempt, thresholds = validate_manifest(read_json(manifest)), read_json(policy)
    check_policy(thresholds)
    if "startup_timeout_seconds" not in thresholds:
        raise FlowError("Observer requires explicit startup_timeout_seconds")
    if Store(workspace).task(task)["context"] != attempt["context"]:
        raise FlowError("Observer attempt and task context differ")
    return {"workspace": str(workspace), "task": task, "manifest": str(manifest), "policy": str(policy),
            "state_dir": str(Path(state_dir or workspace / "training-logs" / task).resolve()),
            "exit_receipt": str(Path(exit_receipt).resolve()) if exit_receipt else None,
            "interval_seconds": _bound(interval, "interval", 300),
            "attempt_id": attempt["attempt_id"], "context": attempt["context"],
            "manifest_hash": fingerprint(attempt), "policy_hash": fingerprint(thresholds)}


def _record(spec):
    path = Path(spec["state_dir"]) / "observer-process.json"
    if not path.exists():
        return None
    record = read_json(path)
    if (record.get("schema_version") != 1 or not isinstance(record.get("spec"), dict)
            or record.get("spec_hash") != fingerprint(record["spec"])
            or not isinstance(record.get("argv"), list) or not record["argv"]):
        raise FlowError("Observer record is invalid; preserve it for manual reconciliation")
    return record


def _match_expected(record, spec):
    if record["spec"] != spec:
        raise FlowError("Existing observer belongs to a different attempt or configuration; inspect and explicitly stop its exact recorded scope")


def _receipt(record, filename):
    path = Path(record["run_dir"]) / filename
    if not path.exists():
        return None
    value = read_json(path)
    if (value.get("launch_id") != record["launch_id"] or value.get("spec_hash") != record["spec_hash"]
            or value.get("process") != record.get("process")
            or value.get("attempt_id") != record["spec"]["attempt_id"] or value.get("context") != record["spec"]["context"]):
        raise FlowError("Observer lifecycle receipt identity mismatch: " + filename)
    return value


def _process(record):
    identity = record.get("process")
    if not identity:
        return {"status": "unknown", "reason": "launch-process-identity-not-established"}
    current = process_identity(identity["pid"])
    if current.get("identity") and current["identity"] != identity:
        return {"status": "identity-mismatch", "reason": "PID reused or namespace changed"}
    return current


def inspect_record(record, *, now=None, freshness_seconds=120):
    now = time.time() if now is None else now
    _bound(freshness_seconds, "freshness_seconds", 86400)
    process = _process(record)
    heartbeat, exited = _receipt(record, "heartbeat.json"), _receipt(record, "observer-exit.json")
    freshness = "missing"
    if heartbeat:
        checked = heartbeat.get("checked_at")
        if not isinstance(checked, (int, float)) or not math.isfinite(checked):
            freshness = "invalid"
        else:
            age = now - checked
            freshness = "clock-mismatch" if age < -30 else "fresh" if age <= freshness_seconds else "stale"
    ready = _receipt(record, "ready.json") is not None
    result = heartbeat.get("result", {}) if heartbeat else {}
    terminal = bool(exited and exited.get("exit_code") == 0
                    and exited.get("reason") == "training-completion-verified"
                    and result.get("monitor", {}).get("completion_verified") is True)
    if terminal and process["status"] == "exited":
        status = "completed"
    elif process["status"] == "alive" and freshness == "fresh" and ready and not exited:
        status = "observing" if result.get("status") == "healthy-observed" else "attention"
    elif process["status"] == "exited" and exited and exited.get("reason") == "observer-stop-requested":
        status = "stopped"
    else:
        status = "attention"
    return {"status": status, "scope": SCOPE, "launch_id": record["launch_id"],
            "attempt_id": record["spec"]["attempt_id"], "process": process,
            "heartbeat_freshness": freshness, "ready": ready,
            "monitor_status": result.get("status"),
            "training_completion_verified": result.get("monitor", {}).get("completion_verified") is True,
            "observer_exit": exited, "run_dir": record["run_dir"]}


def observer_status(spec, *, freshness_seconds=120):
    with observer_lock(spec["state_dir"], name="observer-control.lock"):
        record = _record(spec)
        if record is None:
            return {"status": "not-started", "scope": SCOPE}
        _match_expected(record, spec)
        return inspect_record(record, freshness_seconds=freshness_seconds)


def start_observer(spec, *, script=None, startup_timeout=30, freshness_seconds=120):
    _bound(startup_timeout, "startup_timeout", 60)
    _bound(freshness_seconds, "freshness_seconds", 86400)
    root = Path(spec["state_dir"])
    with observer_lock(root, name="observer-control.lock"):
        old = _record(spec)
        if old:
            current = _process(old)
            if current["status"] == "alive":
                _match_expected(old, spec)
                result = inspect_record(old, freshness_seconds=freshness_seconds)
                return {**result, "start_action": "none; existing process retained"}
            if current["status"] != "exited":
                raise FlowError("Previous observer identity is unresolved; do not start a duplicate")
        # Detect unmanaged daemon/CLI/API owners before spawning. A racing CLI
        # may acquire it afterward; the child then fails visibly, never doubles.
        with observer_lock(root):
            pass
        launch_id = uuid.uuid4().hex
        run = root / "observer-launches" / launch_id
        run.mkdir(parents=True)
        script = Path(script or Path(__file__).with_name("observe_training.py")).resolve()
        if not script.is_file():
            raise FlowError("Observer script is missing")
        argv = [sys.executable, "-B", str(script), "--workspace", spec["workspace"], "--task", spec["task"],
                "--manifest", spec["manifest"], "--policy", spec["policy"], "--state-dir", spec["state_dir"],
                "--interval-seconds", str(spec["interval_seconds"]), "--lifecycle-dir", str(run)]
        if spec["exit_receipt"]:
            argv += ["--exit-receipt", spec["exit_receipt"]]
        request = {"schema_version": 1, "launch_id": launch_id, "spec": spec}
        write_json(run / "request.json", request)
        record = {**request, "spec_hash": fingerprint(spec), "run_dir": str(run), "argv": argv,
                  "process": None, "started_at": time.time(), "scope": SCOPE}
        with (run / "stdout.jsonl").open("ab") as stdout, (run / "stderr.log").open("ab") as stderr:
            try:
                child = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr, start_new_session=True)
            except OSError as exc:
                write_json(run / "start-result.json", {"status": "failed", "error": str(exc), "record": record})
                return {"status": "failed", "run_dir": str(run), "reason": "observer-spawn-failed"}
        current = process_identity(child.pid)
        record["process"] = current.get("identity")
        record["spawn_pid"] = child.pid
        write_json(root / "observer-process.json", record)
        write_json(run / "process.json", record)
        deadline = time.monotonic() + startup_timeout
        while True:
            # A short lived child may publish identity and terminal receipts
            # before the parent's first /proc read. Use only its matching PID.
            identity_path = run / "identity.json"
            if record["process"] is None and identity_path.exists():
                identity = read_json(identity_path)
                if (identity.get("launch_id") == launch_id and identity.get("spec_hash") == record["spec_hash"]
                        and identity.get("process", {}).get("pid") == child.pid):
                    record["process"] = identity["process"]
                    write_json(root / "observer-process.json", record)
                    write_json(run / "process.json", record)
            code = child.poll()  # Reap a failed/short-lived child while we still own it.
            result = inspect_record(record, freshness_seconds=freshness_seconds)
            if code is not None or result["ready"] or time.monotonic() >= deadline:
                if code is not None and not result["ready"]:
                    result.update(status="failed", reason="observer-exited-before-first-observation", process_exit_code=code)
                elif not result["ready"]:
                    result.update(status="attention", reason="startup-unconfirmed; inspect retained process and stderr before retry")
                write_json(run / "start-result.json", result)
                return result
            time.sleep(0.05)


def stop_observer(spec, *, timeout=10):
    _bound(timeout, "stop timeout", 60)
    with observer_lock(spec["state_dir"], name="observer-control.lock"):
        record = _record(spec)
        if record is None:
            return {"status": "not-started", "scope": SCOPE}
        _match_expected(record, spec)
        current = _process(record)
        if current["status"] == "alive":
            if not hasattr(os, "pidfd_open") or not hasattr(signal, "pidfd_send_signal"):
                raise FlowError("Safe stop requires Linux pidfd; no numeric-PID kill fallback")
            identity = record["process"]
            fd = os.pidfd_open(identity["pid"])
            try:
                # pidfd first, then recheck identity and exact argv. This closes
                # the numeric PID reuse race between inspection and signaling.
                if _process(record).get("identity") != identity:
                    raise FlowError("Observer identity changed; no signal sent")
                argv = [os.fsdecode(item) for item in Path(f"/proc/{identity['pid']}/cmdline").read_bytes().split(b"\0") if item]
                if argv != record["argv"]:
                    raise FlowError("Observer command changed; no signal sent")
                signal.pidfd_send_signal(fd, signal.SIGTERM)
            finally:
                os.close(fd)
            deadline = time.monotonic() + timeout
            while _process(record)["status"] == "alive" and time.monotonic() < deadline:
                time.sleep(0.05)
        elif current["status"] != "exited":
            raise FlowError("Observer identity unresolved; no signal sent")
        result = inspect_record(record)
        result["stop_action"] = "observer only; no signal escalation or training action"
        write_json(Path(record["run_dir"]) / ("stop-result-" + uuid.uuid4().hex + ".json"), result)
        return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["start", "status", "stop", "prepare-context"])
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--task", required=True)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--policy", type=Path)
    parser.add_argument("--context-root", type=Path, help="Explicit private root for independent observation Stores")
    parser.add_argument("--state-dir", type=Path)
    parser.add_argument("--exit-receipt", type=Path)
    parser.add_argument("--interval-seconds", type=float, default=30)
    parser.add_argument("--timeout-seconds", type=float, default=30)
    parser.add_argument("--freshness-seconds", type=float, default=120)
    args = parser.parse_args(argv)
    if args.action != "prepare-context" and sys.platform != "linux":
        parser.error("Observer lifecycle management requires Linux and the same /proc namespace")
    try:
        if args.action == "prepare-context":
            if args.context_root is None:
                parser.error("prepare-context requires --context-root")
            if args.manifest or args.policy or args.state_dir or args.exit_receipt:
                parser.error("prepare-context only prepares a Store; pass attempt inputs to start/status/stop separately")
            result = prepare_context_workspace(args.workspace, args.task, args.context_root)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        if args.manifest is None or args.policy is None:
            parser.error("start/status/stop require --manifest and --policy")
        if args.context_root is not None:
            parser.error("--context-root is only for prepare-context; use its returned workspace explicitly")
        spec = make_spec(args.workspace, args.task, args.manifest, args.policy, args.state_dir, args.exit_receipt, args.interval_seconds)
        if args.action == "start":
            result = start_observer(spec, startup_timeout=args.timeout_seconds, freshness_seconds=args.freshness_seconds)
        elif args.action == "stop":
            result = stop_observer(spec, timeout=args.timeout_seconds)
        else:
            result = observer_status(spec, freshness_seconds=args.freshness_seconds)
        print(json.dumps(result, ensure_ascii=False, allow_nan=False, indent=2))
        return 2 if result["status"] in {"attention", "failed", "not-started"} else 0
    except (FlowError, OSError, ValueError, KeyError) as exc:
        print(json.dumps({"status": "error", "message": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
