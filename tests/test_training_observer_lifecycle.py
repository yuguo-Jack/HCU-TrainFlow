"""Synthetic lifecycle receipts/identities; local locking tests run real processes."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import pytest

from hcu_trainflow.core import FlowError, Store, fingerprint, write_json
from hcu_trainflow.training_logs import collect_training_log, observe_once, observer_lock


def load_script(name):
    path = Path(__file__).parents[1] / "scripts" / (name + ".py")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def manager():
    return load_script("manage_training_observer")


@pytest.fixture
def spec(tmp_path, manager):
    workspace = tmp_path / "workspace"
    store = Store(workspace)
    store.create({"schema_version": 1, "task_id": "fixture", "mode": "operate", "objective": "synthetic lifecycle",
                  "context": {"source": "synthetic lifecycle; no GPU execution"}})
    manifest = {"schema_version": 1, "context": store.task("fixture")["context"], "attempt_id": "a1",
                "log_path": str(tmp_path / "training.log"), "log_start_offset": 0, "start_step": 0,
                "expected_final_step": 3, "started_at": 100, "log_timezone": "UTC",
                "process": {"pid": 123, "start_ticks": "1", "boot_id": "synthetic", "pid_namespace": "synthetic"}}
    Path(manifest["log_path"]).write_text("")
    write_json(tmp_path / "attempt.json", manifest)
    write_json(tmp_path / "policy.json", {"startup_timeout_seconds": 300, "stall_seconds": 60,
               "telemetry_seconds": 120, "recovery_seconds": 180, "min_progress_samples": 2})
    return manager.make_spec(workspace, "fixture", tmp_path / "attempt.json", tmp_path / "policy.json")


def recorded(spec, **changes):
    run = Path(spec["state_dir"]) / "observer-launches/fixture-launch"
    run.mkdir(parents=True, exist_ok=True)
    record = {"schema_version": 1, "launch_id": "fixture-launch", "spec": spec, "spec_hash": fingerprint(spec),
              "process": {"pid": 456, "start_ticks": "2", "boot_id": "synthetic", "pid_namespace": "synthetic"},
              "argv": ["python", "observer.py"], "run_dir": str(run), **changes}
    write_json(Path(spec["state_dir"]) / "observer-process.json", record)
    return record


def receipt(record, filename, **extra):
    value = {key: record[key] for key in ("launch_id", "spec_hash", "process")}
    value.update({key: record["spec"][key] for key in ("attempt_id", "context")})
    value.update(extra)
    write_json(Path(record["run_dir"]) / filename, value)
    return value


def alive(record):
    return {"status": "alive", "identity": record["process"], "process_state": "S"}


def test_real_cross_process_lock_prevents_parser_writer(spec):
    script = "from hcu_trainflow.training_logs import observer_lock\nfrom hcu_trainflow.core import FlowError\nimport sys\ntry:\n with observer_lock(sys.argv[1]): pass\nexcept FlowError:\n raise SystemExit(7)\n"
    with observer_lock(spec["state_dir"]):
        child = subprocess.run([sys.executable, "-B", "-c", script, spec["state_dir"]], capture_output=True)
        assert child.returncode == 7, child.stderr
        with pytest.raises(FlowError, match="Another observer"):
            collect_training_log(spec["state_dir"], json.loads(Path(spec["manifest"]).read_text()))
        with pytest.raises(FlowError, match="Another observer"):
            observe_once(spec["workspace"], spec["task"], spec["manifest"], spec["policy"], spec["state_dir"])
    child = subprocess.run([sys.executable, "-B", "-c", script, spec["state_dir"]], capture_output=True)
    assert child.returncode == 0


def test_cli_once_cannot_bypass_daemon_lock(spec):
    with observer_lock(spec["state_dir"]):
        result = subprocess.run([sys.executable, "-B", "-m", "hcu_trainflow", "--workspace", spec["workspace"],
                                 "observe-training", spec["task"], spec["manifest"], spec["policy"]], capture_output=True, text=True)
    assert result.returncode == 1
    assert "Another observer" in result.stderr


def test_expired_or_foreign_lease_rejected(spec, tmp_path):
    with observer_lock(spec["state_dir"]) as lease:
        with pytest.raises(FlowError, match="lease"):
            collect_training_log(tmp_path / "wrong", {}, lease=lease)
    with pytest.raises(FlowError, match="lease"):
        collect_training_log(spec["state_dir"], {}, lease=lease)


@pytest.mark.parametrize("age,freshness", [(1, "fresh"), (300, "stale"), (-100, "clock-mismatch")])
def test_process_alive_does_not_imply_fresh_or_healthy(manager, spec, monkeypatch, age, freshness):
    record = recorded(spec)
    monkeypatch.setattr(manager, "process_identity", lambda pid: alive(record))
    data = {"checked_at": 1000 - age, "result": {"status": "attention", "monitor": {"completion_verified": False}}}
    receipt(record, "ready.json", **data)
    receipt(record, "heartbeat.json", **data)
    result = manager.inspect_record(record, now=1000)
    assert result["status"] == "attention" and result["heartbeat_freshness"] == freshness
    assert result["process"]["status"] == "alive" and not result["training_completion_verified"]


def test_wrong_launch_heartbeat_rejected(manager, spec):
    record = recorded(spec)
    receipt(record, "heartbeat.json", launch_id="old-launch", checked_at=1)
    with pytest.raises(FlowError, match="receipt identity"):
        manager.inspect_record(record)


def test_successful_iterations_but_checkpoint_failure_cannot_complete(manager, spec, monkeypatch):
    record = recorded(spec)
    monkeypatch.setattr(manager, "process_identity", lambda pid: {"status": "exited", "identity": record["process"], "process_state": "Z"})
    result = {"status": "attention", "adapter": {"last_observation": {"step": 3, "phase": "failed"}},
              "monitor": {"completion_verified": False}}
    receipt(record, "heartbeat.json", checked_at=900, result=result)
    receipt(record, "ready.json", checked_at=900, result=result)
    receipt(record, "observer-exit.json", exit_code=143, reason="observer-stop-requested")
    status = manager.inspect_record(record, now=1000)
    assert status["status"] == "stopped" and not status["training_completion_verified"]
    assert status["monitor_status"] == "attention"


def test_refuses_old_attempt_live_process(manager, spec, monkeypatch):
    record = recorded(spec)
    monkeypatch.setattr(manager, "process_identity", lambda pid: alive(record))
    newer = {**spec, "attempt_id": "new-attempt"}
    with pytest.raises(FlowError, match="different attempt"):
        manager.start_observer(newer)
    with pytest.raises(FlowError, match="different attempt"):
        manager.stop_observer(newer)


def test_pid_reuse_never_signaled_or_replaced(manager, spec, monkeypatch):
    record = recorded(spec)
    monkeypatch.setattr(manager, "process_identity", lambda pid: {"status": "alive", "identity": {**record["process"], "start_ticks": "3"}})
    with pytest.raises(FlowError, match="unresolved"):
        manager.start_observer(spec)
    with pytest.raises(FlowError, match="unresolved"):
        manager.stop_observer(spec)


def test_start_existing_same_attempt_keeps_unhealthy_process(manager, spec, monkeypatch):
    record = recorded(spec)
    monkeypatch.setattr(manager, "process_identity", lambda pid: alive(record))
    monkeypatch.setattr(manager.subprocess, "Popen", lambda *a, **k: pytest.fail("must not start duplicate"))
    result = manager.start_observer(spec)
    assert result["status"] == "attention" and result["heartbeat_freshness"] == "missing"
    assert result["start_action"].startswith("none")


def test_unmanaged_writer_blocks_start(manager, spec, monkeypatch):
    monkeypatch.setattr(manager.subprocess, "Popen", lambda *a, **k: pytest.fail("must not spawn"))
    with observer_lock(spec["state_dir"]):
        with pytest.raises(FlowError, match="Another observer"):
            manager.start_observer(spec)


def test_spawn_error_is_retained(manager, spec, monkeypatch):
    def fail(*args, **kwargs):
        raise OSError("synthetic executable unavailable")
    monkeypatch.setattr(manager.subprocess, "Popen", fail)
    result = manager.start_observer(spec)
    assert result["status"] == "failed"
    assert "synthetic" in json.loads((Path(result["run_dir"]) / "start-result.json").read_text())["error"]
    assert (Path(result["run_dir"]) / "stderr.log").exists()


def test_immediate_exit_is_not_successful_start(manager, spec, monkeypatch):
    monkeypatch.setattr(manager.subprocess, "Popen", lambda *a, **k: SimpleNamespace(pid=99, poll=lambda: 2))
    monkeypatch.setattr(manager, "process_identity", lambda pid: {"status": "exited"})
    result = manager.start_observer(spec)
    assert result["status"] == "failed" and result["process_exit_code"] == 2
    assert not result["ready"]


def test_stop_requires_pidfd(manager, spec, monkeypatch):
    record = recorded(spec)
    monkeypatch.setattr(manager, "process_identity", lambda pid: alive(record))
    monkeypatch.delattr(manager.os, "pidfd_open", raising=False)
    with pytest.raises(FlowError, match="pidfd"):
        manager.stop_observer(spec)


def test_identity_race_after_pidfd_open_never_signals(manager, spec, monkeypatch):
    record = recorded(spec)
    replies = iter([alive(record), {"status": "identity-mismatch"}])
    monkeypatch.setattr(manager, "_process", lambda r: next(replies))
    monkeypatch.setattr(manager.os, "pidfd_open", lambda pid: 999, raising=False)
    closed = []
    monkeypatch.setattr(manager.os, "close", lambda fd: closed.append(fd))
    monkeypatch.setattr(manager.signal, "pidfd_send_signal", lambda *a: pytest.fail("must not signal reused PID"), raising=False)
    with pytest.raises(FlowError, match="identity changed"):
        manager.stop_observer(spec)
    assert closed == [999]


def test_exact_pidfd_stop_signals_only_observer(manager, spec, monkeypatch):
    record = recorded(spec)
    state = [alive(record)]
    monkeypatch.setattr(manager, "process_identity", lambda pid: state[0])
    monkeypatch.setattr(manager.os, "pidfd_open", lambda pid: 999 if pid == record["process"]["pid"] else pytest.fail("training PID"), raising=False)
    monkeypatch.setattr(manager.os, "close", lambda fd: None)
    original_read = Path.read_bytes
    monkeypatch.setattr(Path, "read_bytes", lambda path: b"python\0observer.py\0" if str(path).replace("\\", "/") == "/proc/456/cmdline" else original_read(path))
    signals = []
    def send(fd, sig):
        signals.append((fd, sig))
        state[0] = {"status": "exited", "identity": record["process"], "process_state": "Z"}
        receipt(record, "observer-exit.json", reason="observer-stop-requested", exit_code=143)
    monkeypatch.setattr(manager.signal, "pidfd_send_signal", send, raising=False)
    result = manager.stop_observer(spec)
    assert result["status"] == "stopped"
    assert signals == [(999, manager.signal.SIGTERM)]
    assert list(Path(record["run_dir"]).glob("stop-result-*.json"))


def test_changed_command_never_signaled(manager, spec, monkeypatch):
    record = recorded(spec)
    monkeypatch.setattr(manager, "process_identity", lambda pid: alive(record))
    monkeypatch.setattr(manager.os, "pidfd_open", lambda pid: 999, raising=False)
    monkeypatch.setattr(manager.os, "close", lambda fd: None)
    monkeypatch.setattr(Path, "read_bytes", lambda path: b"python\0train.py\0")
    monkeypatch.setattr(manager.signal, "pidfd_send_signal", lambda *args: pytest.fail("must not stop training"), raising=False)
    with pytest.raises(FlowError, match="command changed"):
        manager.stop_observer(spec)


def test_start_requires_first_poll_not_only_alive_pid(manager, spec, monkeypatch):
    ident = {"pid": 99, "start_ticks": "2", "boot_id": "synthetic", "pid_namespace": "synthetic"}
    monkeypatch.setattr(manager.subprocess, "Popen", lambda *args, **kwargs: SimpleNamespace(pid=99, poll=lambda: None))
    monkeypatch.setattr(manager, "process_identity", lambda pid: {"status": "alive", "identity": ident})
    clock = iter([0, 10])
    monkeypatch.setattr(manager.time, "monotonic", lambda: next(clock))
    result = manager.start_observer(spec, startup_timeout=1)
    assert result["status"] == "attention" and not result["ready"]
    assert result["reason"].startswith("startup-unconfirmed")


def test_start_accepts_real_child_first_poll_even_if_training_failed(manager, spec, monkeypatch):
    ident = {"pid": 99, "start_ticks": "2", "boot_id": "synthetic", "pid_namespace": "synthetic"}
    def spawn(argv, **kwargs):
        run = Path(argv[argv.index("--lifecycle-dir") + 1])
        request = json.loads((run / "request.json").read_text())
        record = {**request, "run_dir": str(run), "process": ident, "spec_hash": fingerprint(request["spec"])}
        data = {"checked_at": manager.time.time(), "result": {"status": "attention", "monitor": {"completion_verified": False}}}
        receipt(record, "ready.json", **data)
        receipt(record, "heartbeat.json", **data)
        return SimpleNamespace(pid=99, poll=lambda: None)
    monkeypatch.setattr(manager.subprocess, "Popen", spawn)
    monkeypatch.setattr(manager, "process_identity", lambda pid: {"status": "alive", "identity": ident})
    result = manager.start_observer(spec)
    assert result["ready"] and result["status"] == "attention"
    assert result["heartbeat_freshness"] == "fresh"


def test_verified_terminal_with_matching_observer_exit_is_completed(manager, spec, monkeypatch):
    record = recorded(spec)
    monkeypatch.setattr(manager, "process_identity", lambda pid: {"status": "exited"})
    data = {"checked_at": 800, "result": {"status": "healthy-observed", "monitor": {"completion_verified": True}}}
    receipt(record, "ready.json", **data)
    receipt(record, "heartbeat.json", **data)
    receipt(record, "observer-exit.json", reason="training-completion-verified", exit_code=0)
    result = manager.inspect_record(record, now=1000)
    assert result["status"] == "completed" and result["heartbeat_freshness"] == "stale"
    assert result["training_completion_verified"]  # Terminal evidence, not ongoing health.


def test_daemon_holds_shared_lock_and_records_managed_stop(manager, spec, monkeypatch):
    module = load_script("observe_training")
    record = recorded(spec)
    run = Path(record["run_dir"])
    write_json(run / "request.json", {"launch_id": record["launch_id"], "spec": spec})
    monkeypatch.setattr(module, "sys", SimpleNamespace(platform="linux", stderr=sys.stderr))
    monkeypatch.setattr(module, "process_identity", lambda pid: alive(record))
    monkeypatch.setattr(sys, "argv", ["observe_training", "--workspace", spec["workspace"], "--task", spec["task"],
        "--manifest", spec["manifest"], "--policy", spec["policy"], "--lifecycle-dir", str(run)])
    def observe(*args):
        with pytest.raises(FlowError, match="Another observer"):
            observe_once(spec["workspace"], spec["task"], spec["manifest"], spec["policy"], spec["state_dir"])
        return {"status": "attention", "monitor": {"completion_verified": False}}
    monkeypatch.setattr(module, "observe_once", observe)
    def stop(seconds):
        raise module.ObserverStopped()
    monkeypatch.setattr(module.time, "sleep", stop)
    assert module.main() == 143
    assert json.loads((run / "ready.json").read_text())["result"]["status"] == "attention"
    assert json.loads((run / "observer-exit.json").read_text())["reason"] == "observer-stop-requested"
    with observer_lock(spec["state_dir"]):
        pass
