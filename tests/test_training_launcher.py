import importlib.util
import hashlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

from hcu_trainflow.core import FlowError


@pytest.fixture
def wrapper(monkeypatch):
    path = Path(__file__).parents[1] / "scripts/launch_training.py"
    spec = importlib.util.spec_from_file_location("training_launcher", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "sys", SimpleNamespace(platform="linux", stderr=sys.stderr))
    # Actual child execution below; only Linux /proc identity is synthetic for
    # Windows test hosts. Real identity is verified during site acceptance.
    monkeypatch.setattr(module, "process_identity", lambda pid: {
        "status": "alive", "identity": {"pid": pid, "start_ticks": "12345",
        "boot_id": "synthetic-boot", "pid_namespace": "pid:[synthetic]"}})
    return module


def test_real_child_exit_and_log_are_retained(wrapper, tmp_path):
    directory = tmp_path / "attempt"
    code = wrapper.launch_attempt(directory, "context", "attempt", tmp_path,
        [sys.executable, "-c", "print('only one step'); raise SystemExit(7)"],
        expected_final_step=3)
    assert code == 7
    manifest = json.loads((directory / "attempt.json").read_text())
    receipt = json.loads((directory / "exit.json").read_text())
    assert receipt["process"] == manifest["process"]
    assert receipt["exit_code"] == 7
    assert receipt["finished_at"] >= manifest["started_at"]
    assert (directory / "training.log").read_text().strip() == "only one step"
    assert "completed" not in receipt  # Observer must check actual final step.
    data = (directory / "training.log").read_bytes()
    assert receipt["log_evidence"] == {"path": str(directory / "training.log"), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
    with pytest.raises(FileExistsError):
        wrapper.launch_attempt(directory, "context", "attempt", tmp_path,
            [sys.executable, "-c", "raise SystemExit(0)"], expected_final_step=3)
    assert json.loads((directory / "exit.json").read_text())["exit_code"] == 7


def test_spawn_failure_has_failed_receipt(wrapper, tmp_path):
    directory = tmp_path / "missing-command"
    assert wrapper.launch_attempt(directory, "context", "missing", tmp_path,
        [str(tmp_path / "does-not-exist")], expected_final_step=1) == 127
    assert json.loads((directory / "exit.json").read_text())["exit_code"] == 127


def test_identity_failure_prevents_launch(wrapper, monkeypatch, tmp_path):
    monkeypatch.setattr(wrapper, "process_identity", lambda pid: {"status": "unknown"})
    with pytest.raises(FlowError, match="identity"):
        wrapper.launch_attempt(tmp_path / "attempt", "context", "attempt", tmp_path,
            [sys.executable, "-c", "print('unexpected')"], expected_final_step=1)
    assert not (tmp_path / "attempt").exists()


def test_wait_interruption_does_not_fabricate_exit_receipt(wrapper, monkeypatch, tmp_path):
    class InterruptedChild:
        pid = 100
        def wait(self):
            raise KeyboardInterrupt()
    monkeypatch.setattr(wrapper.subprocess, "Popen", lambda *args, **kwargs: InterruptedChild())
    with pytest.raises(KeyboardInterrupt):
        wrapper.launch_attempt(tmp_path / "attempt", "context", "attempt", tmp_path, ["synthetic"], expected_final_step=1)
    assert (tmp_path / "attempt/attempt.json").exists()
    assert not (tmp_path / "attempt/exit.json").exists()


def test_string_command_is_not_treated_as_argv(wrapper, tmp_path):
    with pytest.raises(FlowError, match="argv"):
        wrapper.launch_attempt(tmp_path / "attempt", "context", "attempt", tmp_path, "python model.py", expected_final_step=1)
    assert not (tmp_path / "attempt").exists()


def test_observer_does_not_stop_on_adapter_only_completion(monkeypatch, tmp_path):
    import types
    path = Path(__file__).parents[1] / "scripts/observe_training.py"
    spec = importlib.util.spec_from_file_location("training_observer", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "sys", SimpleNamespace(platform="linux", stderr=sys.stderr))
    monkeypatch.setitem(sys.modules, "fcntl", SimpleNamespace(LOCK_EX=1, LOCK_NB=2, flock=lambda *args: None))
    monkeypatch.setattr(sys, "argv", [str(path), "--workspace", str(tmp_path), "--task", "fixture",
                                      "--manifest", str(tmp_path / "attempt.json"), "--policy", str(tmp_path / "policy.json")])
    replies = iter([
        {"adapter": {"last_observation": {"completed": True}}, "monitor": {"completion_verified": False}, "status": "attention"},
        {"adapter": {"last_observation": {"completed": True}}, "monitor": {"completion_verified": True}, "status": "healthy-observed"},
    ])
    monkeypatch.setattr(module, "observe_once", lambda *args: next(replies))
    waited = []
    monkeypatch.setattr(module.time, "sleep", lambda duration: waited.append(duration))
    assert module.main() == 0 and waited == [30]


def test_once_observer_exits_nonzero_for_attention(monkeypatch, tmp_path):
    path = Path(__file__).parents[1] / "scripts/observe_training.py"
    spec = importlib.util.spec_from_file_location("training_observer", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "sys", SimpleNamespace(platform="linux", stderr=sys.stderr))
    monkeypatch.setitem(sys.modules, "fcntl", SimpleNamespace(LOCK_EX=1, LOCK_NB=2, flock=lambda *args: None))
    monkeypatch.setattr(sys, "argv", [str(path), "--workspace", str(tmp_path), "--task", "fixture", "--once",
                                      "--manifest", str(tmp_path / "attempt.json"), "--policy", str(tmp_path / "policy.json")])
    monkeypatch.setattr(module, "observe_once", lambda *args: {"adapter": {"last_observation": {"completed": False}},
                                                              "monitor": {"completion_verified": False}, "status": "attention"})
    assert module.main() == 2


def test_real_local_child_clockless_log_reaches_verified_completion(wrapper, tmp_path):
    from hcu_trainflow.core import Store
    from hcu_trainflow.monitor import poll_log
    from hcu_trainflow.training_logs import collect_training_log
    store = Store(tmp_path / "monitor")
    store.create({"schema_version": 1, "task_id": "fixture", "mode": "operate", "objective": "synthetic child plumbing",
                  "context": {"source": "synthetic local child; not GPU training"}})
    directory = tmp_path / "attempt"
    text = "iteration 1/1 | elapsed time per iteration (ms): 2.0 | lm loss: 1.0 | grad norm: 0.1 |"
    assert wrapper.launch_attempt(directory, store.task("fixture")["context"], "attempt", tmp_path,
        [sys.executable, "-c", "print(" + repr(text) + ")"], expected_final_step=1) == 0
    manifest = json.loads((directory / "attempt.json").read_text())
    receipt = json.loads((directory / "exit.json").read_text())
    observed_at = receipt["finished_at"] + 10
    adapted = collect_training_log(tmp_path / "adapter", manifest, now=observed_at,
        process_status={"status": "exited"}, exit_receipt=receipt)
    policy = {"startup_timeout_seconds": 300, "stall_seconds": 30, "telemetry_seconds": 60,
              "recovery_seconds": 120, "min_progress_samples": 2}
    result = poll_log(store, "fixture", adapted["normalized_log"], policy, now=observed_at)
    assert result["completion_verified"] is True
    assert {issue["kind"] for issue in result["issues"]} == {"adapter-warning"}
