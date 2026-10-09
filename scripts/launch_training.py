#!/usr/bin/env python3
"""Launch one explicitly admitted attempt and retain its real exit receipt.

This wrapper does not reserve resources, choose a model, restart a failed job or
provide daemon supervision. Invoke it through a reviewed TrainFlow command card
inside the selected execution environment. The observer tracks this wrapper's
stable process identity while it waits for its own training child.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

_SOURCE = Path(__file__).resolve().parents[1] / "src"
if _SOURCE.exists():
    sys.path.insert(0, str(_SOURCE))

from hcu_trainflow.core import FlowError, safe_id, write_json
from hcu_trainflow.training_logs import process_identity, validate_manifest


def launch_attempt(directory, context, attempt_id, cwd, argv, *, expected_final_step,
                   start_step=0, log_timezone="UTC"):
    if sys.platform != "linux":
        raise FlowError("Training wrapper requires Linux process identity")
    safe_id(attempt_id)
    if not isinstance(argv, (list, tuple)) or not argv or any(not isinstance(x, str) or "\0" in x for x in argv):
        raise FlowError("Training command must be a nonempty argv array")
    cwd = Path(cwd).resolve(strict=True)
    if not cwd.is_dir():
        raise FlowError("Training cwd must be an existing directory")
    directory = Path(directory).resolve()
    observed = process_identity(os.getpid())
    if observed.get("status") != "alive":
        raise FlowError("Cannot establish wrapper process identity")
    identity = observed["identity"]
    manifest = validate_manifest({
        "schema_version": 1, "context": context, "attempt_id": attempt_id,
        "log_path": str(directory / "training.log"), "log_start_offset": 0,
        "start_step": start_step, "expected_final_step": expected_final_step,
        "started_at": time.time(), "log_timezone": log_timezone,
        "process": identity,
    })
    # New attempt directories prevent overwriting another run or reusing a PID
    # receipt after an uncertain dispatch. Recovery uses a new explicit attempt.
    directory.mkdir(parents=True, exist_ok=False)
    write_json(directory / "command.json", {
        "argv": argv, "cwd": str(cwd), "attempt_id": attempt_id,
        "context": context, "process_role": "wrapper-waits-for-training-child",
        "environment": "inherited from reviewed command card; not dumped here",
    })
    with (directory / "training.log").open("xb") as log:
        write_json(directory / "attempt.json", manifest)
        print(json.dumps({"attempt": str(directory / "attempt.json"),
                          "log": str(directory / "training.log")}), flush=True)
        try:
            child = subprocess.Popen(argv, cwd=cwd, stdout=log, stderr=subprocess.STDOUT)
        except OSError as exc:
            log.write(("TrainFlow launch failed: " + str(exc) + "\n").encode("utf8"))
            code = 127
        else:
            write_json(directory / "child.json", {
                "pid": child.pid, "wrapper_process": identity,
                "meaning": "Child PID is informational; observer verifies wrapper identity",
            })
            # Interrupted or lost wrappers leave no invented completion receipt.
            # The remote observer will report missing proof, and the coordinator
            # must inspect the existing child before launching another attempt.
            code = child.wait()
        finished_at = time.time()
        log.flush()
        os.fsync(log.fileno())
    log_path = directory / "training.log"
    before = log_path.stat()
    sha = hashlib.sha256()
    with log_path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            sha.update(chunk)
    after = log_path.stat()
    if (before.st_size, before.st_mtime_ns, before.st_ino) != (after.st_size, after.st_mtime_ns, after.st_ino):
        raise FlowError("Training log changed after child exit; reconcile writers before recording completion")
    receipt = {"attempt_id": attempt_id, "context": context, "process": identity,
               "exit_code": code, "finished_at": finished_at,
               "log_evidence": {"path": str(log_path), "bytes": after.st_size, "sha256": sha.hexdigest()}}
    write_json(directory / "exit.json", receipt)
    print(json.dumps({"exit_receipt": str(directory / "exit.json"),
                      "exit_code": code}), flush=True)
    return code


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--attempt-dir", type=Path, required=True)
    parser.add_argument("--context", required=True)
    parser.add_argument("--attempt-id", required=True)
    parser.add_argument("--cwd", type=Path, required=True)
    parser.add_argument("--expected-final-step", type=int, required=True)
    parser.add_argument("--start-step", type=int, default=0)
    parser.add_argument("--log-timezone", required=True, help="Actual training log UTC or fixed offset")
    parser.add_argument("argv", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    argv = args.argv[1:] if args.argv[:1] == ["--"] else args.argv
    try:
        return launch_attempt(args.attempt_dir, args.context, args.attempt_id,
                              args.cwd, argv, expected_final_step=args.expected_final_step,
                              start_step=args.start_step, log_timezone=args.log_timezone)
    except (FlowError, OSError) as exc:
        print(json.dumps({"status": "error", "message": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
