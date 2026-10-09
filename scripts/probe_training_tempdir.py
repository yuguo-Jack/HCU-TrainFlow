#!/usr/bin/env python3
"""Bounded Linux checkpoint IPC probe in an explicitly chosen task directory.

Stdlib only. No GPU imports, directory fallback, training restart or host setup.
The caller must already own/authorize the existing --task-root and --tempdir.
"""
import argparse
from datetime import datetime, timezone
import json
import multiprocessing
from multiprocessing.connection import Client, Listener
from multiprocessing.managers import SyncManager
import os
from pathlib import Path
import secrets
import signal
import stat
import subprocess
import sys
import tempfile
import time


def validate_directory(task_root, tempdir):
    root, directory = Path(task_root), Path(tempdir)
    if not root.is_absolute() or not directory.is_absolute():
        raise ValueError("task-root and tempdir must be absolute existing paths")
    root, directory = root.resolve(strict=True), directory.resolve(strict=True)
    if not root.is_dir() or not directory.is_dir():
        raise ValueError("task-root and tempdir must be directories")
    if directory == root or not directory.is_relative_to(root):
        raise ValueError("tempdir must be a strict descendant of the explicit task-root")
    metadata = directory.stat()
    if hasattr(os, "geteuid") and metadata.st_uid != os.geteuid():
        raise PermissionError("tempdir must be owned by the current effective UID")
    if os.name == "posix" and metadata.st_mode & (stat.S_IWUSR | stat.S_IXUSR) != (stat.S_IWUSR | stat.S_IXUSR):
        raise PermissionError("tempdir must grant its owner write and search permission")
    return root, directory


def _manager_tempdir_info():
    from multiprocessing.util import get_temp_dir
    return {"tempfile_tempdir": tempfile.gettempdir(), "multiprocessing_tempdir": get_temp_dir()}


def _manager_initialize(tempdir):
    # Spawn starts a fresh interpreter. Pin both stdlib selection and inherited
    # environment, so an unusable path cannot make tempfile choose /tmp instead.
    for name in ("TMPDIR", "TEMP", "TMP"):
        os.environ[name] = tempdir
    tempfile.tempdir = tempdir


class TempdirManager(SyncManager):
    pass


TempdirManager.register("tempdir_info", callable=_manager_tempdir_info)


def _inside_socket(address, probe_dir):
    if not isinstance(address, str) or address.startswith("\0"):
        raise RuntimeError("Expected a filesystem AF_UNIX socket, not TCP/abstract IPC")
    actual = Path(address)
    if actual.parent != Path(probe_dir):
        raise RuntimeError("IPC address escaped the exclusive probe directory")
    return {"address": address, "address_bytes": len(os.fsencode(address))}


def _worker(tempdir, probe_dir):
    record = {"status": "failed", "phase": "initialize", "platform": sys.platform}
    manager = None
    try:
        if sys.platform != "linux":
            raise RuntimeError("Linux AF_UNIX qualification requires Linux")
        _, selected_probe = validate_directory(tempdir, probe_dir)
        if selected_probe.parent != Path(tempdir) or not selected_probe.name.startswith("pymp-"):
            raise RuntimeError("Worker requires the selected exclusive pymp directory")
        _manager_initialize(tempdir)
        # get_temp_dir normally creates this pymp-* directory under gettempdir.
        # The supervisor created it exclusively, owns its cleanup and has its
        # inode even if this worker or Manager fails before sending a receipt.
        multiprocessing.current_process()._config["tempdir"] = probe_dir
        record["used_tempdir"] = _manager_tempdir_info()
        record["phase"] = "listener"
        with Listener(family="AF_UNIX") as listener:
            record["listener"] = _inside_socket(listener.address, probe_dir)
            with Client(listener.address, family="AF_UNIX") as client:
                with listener.accept() as server:
                    token = secrets.token_hex(16)
                    client.send(token)
                    if server.recv() != token:
                        raise RuntimeError("Listener payload mismatch")
                    server.send(token)
                    if client.recv() != token:
                        raise RuntimeError("Listener reply mismatch")
            record["listener"]["roundtrip"] = True
        record["phase"] = "spawn-manager"
        manager = TempdirManager(ctx=multiprocessing.get_context("spawn"))
        manager.start(initializer=_manager_initialize, initargs=(tempdir,))
        record["manager"] = {**_inside_socket(manager.address, probe_dir), "start_method": "spawn", "pid": manager._process.pid}
        info = manager.tempdir_info()._getvalue()
        if info != {"tempfile_tempdir": tempdir, "multiprocessing_tempdir": probe_dir}:
            raise RuntimeError("Manager did not use the exact selected temporary directory")
        record["manager"]["used_tempdir"] = info
        queue = manager.Queue()
        token = secrets.token_hex(16)
        queue.put(token)
        if queue.get(timeout=2) != token:
            raise RuntimeError("Manager queue payload mismatch")
        record["manager"]["queue_roundtrip"] = True
        record["phase"] = "shutdown"
        manager.shutdown()
        record["manager"]["exit_code"] = manager._process.exitcode
        record["manager"]["alive_after_shutdown"] = manager._process.is_alive()
        if manager._process.exitcode != 0 or manager._process.is_alive():
            raise RuntimeError("Manager did not exit cleanly")
        manager = None
        record.update(status="passed", phase="complete")
    except Exception as exc:
        record["error"] = {"type": type(exc).__name__, "message": str(exc)}
    finally:
        if manager is not None:
            try:
                manager.shutdown()
            except Exception as exc:
                record["shutdown_error"] = str(exc)
    print(json.dumps(record), flush=True)
    return 0 if record["status"] == "passed" else 2


def _cleanup(probe_dir, identity):
    """Remove only this exclusive directory and any abandoned listener sockets."""
    removed = []
    try:
        current = probe_dir.lstat()
        if not stat.S_ISDIR(current.st_mode) or (current.st_dev, current.st_ino) != identity:
            raise RuntimeError("Probe directory identity changed; cleanup refused")
        children = list(probe_dir.iterdir())
        for item in children:
            mode = item.lstat().st_mode
            if not item.name.startswith("listener-") or not stat.S_ISSOCK(mode):
                raise RuntimeError("Unexpected content in probe directory; cleanup refused")
        for item in children:
            item.unlink()
            removed.append(item.name)
        probe_dir.rmdir()
        return {"complete": True, "removed_sockets": removed, "removed_directory": str(probe_dir)}
    except Exception as exc:
        return {"complete": False, "error": str(exc), "retained_directory": str(probe_dir)}


def _stop_group(process):
    # start_new_session=True makes this PID the group we created. No PID search,
    # parent/other training group, or machine-wide process cleanup is allowed.
    actions = []
    errors = []
    for sig in (signal.SIGTERM, signal.SIGKILL):
        try:
            os.killpg(process.pid, sig)
            actions.append(sig.name)
        except ProcessLookupError:
            break
        except OSError as exc:
            errors.append(str(exc))
            break
        if sig == signal.SIGTERM:
            time.sleep(0.2)
    try:
        process.wait(timeout=3)
    except subprocess.TimeoutExpired:
        errors.append("Worker still has no exit receipt after bounded termination")
    return {"signals": actions, "worker_reaped": process.poll() is not None, "errors": errors}


def probe(task_root, tempdir, timeout_seconds=15):
    record = {"schema_version": 1, "status": "failed", "platform": sys.platform,
              "observed_at": datetime.now(timezone.utc).isoformat(), "linux_ipc_verified": False,
              "task_root": str(task_root), "requested_tempdir": str(tempdir),
              "timeout_seconds": timeout_seconds, "gpu_initialized": False}
    if not isinstance(timeout_seconds, (int, float)) or isinstance(timeout_seconds, bool) or not 1 <= timeout_seconds <= 300:
        record["error"] = "timeout_seconds must be between 1 and 300"
        return record
    if sys.platform != "linux":
        record.update(status="unsupported", error="Run this probe in the actual Linux training environment; no Linux IPC test was performed")
        return record
    probe_dir = None
    process = None
    identity = None
    try:
        root, directory = validate_directory(task_root, tempdir)
        record.update(task_root=str(root), resolved_tempdir=str(directory))
        # Explicit dir= is essential: tempfile's normal search may silently fall
        # back to a system directory if TMPDIR is missing/unwritable.
        probe_dir = Path(tempfile.mkdtemp(prefix="pymp-", dir=str(directory)))
        metadata = probe_dir.lstat()
        identity = (metadata.st_dev, metadata.st_ino)
        record["probe_directory"] = str(probe_dir)
        env = os.environ.copy()
        env.update(TMPDIR=str(directory), TEMP=str(directory), TMP=str(directory), PYTHONDONTWRITEBYTECODE="1")
        started = time.monotonic()
        process = subprocess.Popen([sys.executable, "-B", str(Path(__file__).resolve()),
                                    "--_worker", str(directory), str(probe_dir)],
                                   env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, start_new_session=True)
        record["worker_pid"] = process.pid
        try:
            stdout, stderr = process.communicate(timeout=timeout_seconds)
        except subprocess.TimeoutExpired:
            record["termination"] = _stop_group(process)
            record["error"] = "IPC worker exceeded its bounded timeout"
            try:
                stdout, stderr = process.communicate(timeout=3)
            except subprocess.TimeoutExpired as exc:
                # A stuck descendant can keep pipe handles open even after the
                # worker exits. Do not block indefinitely collecting its logs.
                stdout, stderr = exc.output or b"", exc.stderr or b""
                record["pipes_closed"] = False
        record.update(elapsed_seconds=time.monotonic() - started, worker_exit_code=process.returncode)
        record["stderr"] = stderr.decode("utf8", "replace")[-16384:]
        try:
            record["worker"] = json.loads(stdout.decode("utf8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            record.setdefault("error", "Worker did not return complete JSON evidence")
            record["worker_stdout"] = stdout.decode("utf8", "replace")[-16384:]
        worker = record.get("worker", {})
        if "error" not in record and process.returncode == 0 and worker.get("status") == "passed":
            record.update(status="passed", linux_ipc_verified=True)
        else:
            record.setdefault("error", worker.get("error", "IPC worker failed"))
    except Exception as exc:
        record["error"] = {"type": type(exc).__name__, "message": str(exc)}
        if process is not None and process.poll() is None:
            record["termination"] = _stop_group(process)
    finally:
        if probe_dir is not None and identity is not None:
            if process is not None and (process.poll() is None or record.get("pipes_closed") is False):
                record["cleanup"] = {"complete": False, "retained_directory": str(probe_dir),
                                     "error": "Process/pipe termination is unconfirmed; directory retained"}
            else:
                record["cleanup"] = _cleanup(probe_dir, identity)
            if not record["cleanup"]["complete"]:
                record.update(status="failed", linux_ipc_verified=False)
                record.setdefault("error", "Probe cleanup incomplete")
    return record


def main():
    if len(sys.argv) == 4 and sys.argv[1] == "--_worker":
        return _worker(sys.argv[2], sys.argv[3])
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task-root", type=Path, required=True)
    parser.add_argument("--tempdir", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=float, default=15)
    args = parser.parse_args()
    result = probe(args.task_root, args.tempdir, args.timeout_seconds)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "passed" else 3 if result["status"] == "unsupported" else 2


if __name__ == "__main__":
    raise SystemExit(main())
