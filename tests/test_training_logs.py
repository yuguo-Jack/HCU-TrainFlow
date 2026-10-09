"""Synthetic Megatron logs and process identities; no training is executed."""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3

import pytest

from hcu_trainflow.core import FlowError
from hcu_trainflow.core import Store
from hcu_trainflow.monitor import poll_log
from hcu_trainflow import training_logs
from hcu_trainflow.training_logs import collect_training_log, parse_megatron_line, process_identity


@pytest.fixture
def attempt(tmp_path):
    log = tmp_path / "training.log"
    log.write_bytes(b"")
    return {"schema_version": 1, "context": "fixture-context", "attempt_id": "attempt-1",
            "log_path": str(log), "log_start_offset": 0, "start_step": 0, "expected_final_step": 3,
            "started_at": 100.0, "log_timezone": "UTC",
            "process": {"pid": 123, "start_ticks": "321", "boot_id": "fixture-boot", "pid_namespace": "pid:[fixture]"}}


def line(step, *, at=None, total=3, loss="6.123456E+00", grad="0.234", nan=0):
    clock = datetime.fromtimestamp(at if at is not None else 100 + step * 10, timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")
    return (f" [{clock}] iteration {step:8d}/{total:8d} | consumed samples: {step * 4:12d} |"
            f" elapsed time per iteration (ms): 1234.5 | learning rate: 1.000000E-04 |"
            f" global batch size: 4 | lm loss: {loss} | loss scale: 1.0 | grad norm: {grad} |"
            f" number of skipped iterations: 0 | number of nan iterations: {nan} |\n")


def alive(attempt):
    return {"status": "alive", "identity": attempt["process"], "process_state": "S"}


def receipt(attempt, code=0, finished=140):
    return {"attempt_id": attempt["attempt_id"], "context": attempt["context"], "process": attempt["process"],
            "exit_code": code, "finished_at": finished}


def sealed_receipt(attempt, code=0, finished=140):
    content = Path(attempt["log_path"]).read_bytes()
    return {**receipt(attempt, code, finished), "log_evidence": {
        "path": attempt["log_path"], "bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()}}


def records(result):
    return [json.loads(x) for x in Path(result["normalized_log"]).read_text(encoding="utf-8").splitlines()]


def test_actual_source_iteration_format_and_timezone():
    sample = parse_megatron_line(line(1), log_timezone="UTC", observed_at=200)
    assert sample["step"] == 1 and sample["total_steps"] == 3
    assert sample["timestamp"] == 110
    assert sample["loss"] == 6.123456
    assert sample["grad_norm"] == 0.234
    assert sample["step_seconds_reported"] == 1.2345
    assert sample["metrics"]["consumed samples"] == 4
    assert sample["metrics"]["learning rate"] == 0.0001
    shifted = parse_megatron_line(line(1), log_timezone="+08:00", observed_at=200)
    assert shifted["timestamp"] == 110 - 8 * 3600


@pytest.mark.parametrize("text", [
    "[rank0]: torch.AcceleratorError: CUDA error: out of memory",
    "[rank12]: FileNotFoundError: missing checkpoint shard",
    "torch.distributed.checkpoint.api.CheckpointException: failed to write shard",
])
def test_qualified_exception_keeps_checkpoint_failure_reason(text):
    sample = parse_megatron_line(text, observed_at=200)
    assert sample["kind"] == "fatal" and sample["fatal"] == text


def test_exception_type_in_explanatory_prose_is_not_fatal():
    assert parse_megatron_line("Supported exception type torch.AcceleratorError: shown in troubleshooting guide") is None


@pytest.mark.parametrize("loss,grad,nan", [("nan", "0.1", 0), ("6.0", "inf", 0), ("6.0", "0.1", 1)])
def test_numerical_incidents_include_nan_counter_when_loss_not_printed(loss, grad, nan):
    content = line(1, loss=loss, grad=grad, nan=nan)
    if nan:
        content = content.replace(" lm loss: 6.0 |", "")
    sample = parse_megatron_line(content, observed_at=200)
    assert sample["nonfinite"] is True
    if nan:
        assert sample["loss"] == "nan"
    json.dumps(sample, allow_nan=False)


def test_memory_reports_distinguish_allocator_from_total_device():
    allocator = parse_megatron_line("[Rank 7] (after 2 iterations) memory (MB) | allocated: 20.50 | max allocated: 30.00 | reserved: 40.00 | max reserved: 50.00\n")
    assert allocator["rank"] == "7" and allocator["memory"]["allocator_allocated_bytes"] == int(20.5 * 1024**2)
    assert "device_memory_bytes" not in allocator["memory"]
    physical = parse_megatron_line("[Rank 7] (after 2 iterations) memory (MB) | allocated: 20.50 | total device memory used: 60.00\n")
    assert physical["memory"]["device_memory_bytes"] == 60 * 1024**2


def test_partial_lines_replay_and_heartbeats_do_not_advance_steps(tmp_path, attempt):
    path = Path(attempt["log_path"])
    first, second = line(1).encode(), line(2).encode()
    path.write_bytes(first + second[:90])
    state = tmp_path / "observer"
    result = collect_training_log(state, attempt, now=125, process_status=alive(attempt))
    assert result["raw_offset"] == len(first) and result["backlog"] is True
    assert result["last_observation"]["step"] == 1
    assert result["last_observation"]["progress_observed"] is False
    with path.open("ab") as stream:
        stream.write(second[90:])
    result = collect_training_log(state, attempt, now=130, process_status=alive(attempt))
    assert result["last_observation"]["step"] == 2
    result = collect_training_log(state, attempt, now=150, process_status=alive(attempt))
    progress = [r for r in records(result) if r["progress_observed"]]
    assert [r["step"] for r in progress] == [1, 2]
    assert result["last_observation"]["step"] == 2 and result["last_observation"]["timestamp"] == 150
    assert result["last_observation"]["metrics"]["consumed samples"] == 8


def test_startup_and_memory_never_fabricate_training_progress(tmp_path, attempt):
    Path(attempt["log_path"]).write_text("compiling fused kernels...\n[Rank 0] (after 1 iterations) memory (MB) | allocated: 10.00\n")
    result = collect_training_log(tmp_path / "state", attempt, now=500, process_status=alive(attempt))
    assert result["last_observation"]["phase"] == "startup"
    assert all(r["step"] == 0 and r["progress_observed"] is False for r in records(result))
    assert "device_memory_bytes" not in result["last_observation"]


def test_completion_needs_matching_exit_and_observed_expected_step(tmp_path, attempt):
    Path(attempt["log_path"]).write_text(line(1) + line(2) + line(3))
    state = tmp_path / "state"
    result = collect_training_log(state, attempt, now=150, process_status={"status": "exited"})
    assert result["last_observation"]["completed"] is False
    assert result["last_observation"]["job_alive"] is False
    bad = receipt(attempt)
    bad["attempt_id"] = "another-attempt"
    result = collect_training_log(state, attempt, now=151, process_status={"status": "exited"}, exit_receipt=bad)
    assert result["last_observation"]["completed"] is False
    result = collect_training_log(state, attempt, now=152, process_status={"status": "exited"}, exit_receipt=receipt(attempt))
    last = result["last_observation"]
    assert last["completed"] is True and last["phase"] == "finished"
    assert last["expected_final_step"] == 3 and last["process_identity"] == attempt["process"]
    # A later writer replacing the same path cannot add progress to a finished attempt.
    Path(attempt["log_path"]).write_text(line(4, total=4, at=160))
    result = collect_training_log(state, attempt, now=170, process_status={"status": "exited"}, exit_receipt=receipt(attempt))
    assert result["last_observation"]["step"] == 3
    assert len([r for r in records(result) if r["progress_observed"]]) == 3


@pytest.mark.parametrize("kind", ["short", "nonzero", "numerics"])
def test_exit_receipt_does_not_turn_failure_into_success(tmp_path, attempt, kind):
    content = line(1) if kind == "short" else line(1) + line(2) + line(3, loss="nan" if kind == "numerics" else "6.0")
    Path(attempt["log_path"]).write_text(content)
    result = collect_training_log(tmp_path / "state", attempt, now=160, process_status={"status": "exited"},
                                  exit_receipt=receipt(attempt, code=1 if kind == "nonzero" else 0))
    assert result["last_observation"]["completed"] is False
    assert result["last_observation"]["phase"] == "failed"
    assert result["last_observation"]["fatal_errors"]


def test_exit_receipt_can_finalize_a_last_line_without_newline(tmp_path, attempt):
    Path(attempt["log_path"]).write_text(line(1) + line(2) + line(3).rstrip("\n"))
    state = tmp_path / "state"
    result = collect_training_log(state, attempt, now=135, process_status=alive(attempt))
    assert result["last_observation"]["step"] == 2 and result["backlog"]
    result = collect_training_log(state, attempt, now=150, process_status={"status": "exited"}, exit_receipt=receipt(attempt))
    assert result["last_observation"]["completed"] is True


def test_pid_reuse_cannot_consume_new_logs_as_old_attempt(tmp_path, attempt):
    Path(attempt["log_path"]).write_text(line(1))
    reused = {"status": "alive", "identity": {**attempt["process"], "start_ticks": "999"}}
    result = collect_training_log(tmp_path / "state", attempt, now=150, process_status=reused)
    assert result["last_observation"]["step"] == 0
    assert result["last_observation"]["job_alive"] is False
    assert "pid-reused-or-observer-namespace-mismatch" in result["last_observation"]["adapter_warnings"]


def test_rotation_replays_identical_lines_without_duplicate_progress(tmp_path, attempt):
    path = Path(attempt["log_path"])
    path.write_text(line(1) + line(2))
    state = tmp_path / "state"
    collect_training_log(state, attempt, now=125, process_status=alive(attempt))
    path.rename(path.with_suffix(".old"))
    path.write_text(line(2) + line(3))
    result = collect_training_log(state, attempt, now=140, process_status=alive(attempt))
    assert [r["step"] for r in records(result) if r["progress_observed"]] == [1, 2, 3]
    assert any("rotated" in x for x in result["last_observation"]["adapter_warnings"])


def test_new_attempt_resets_progress_but_cannot_reactivate_old_attempt(tmp_path, attempt):
    path = Path(attempt["log_path"])
    path.write_text(line(1))
    state = tmp_path / "state"
    collect_training_log(state, attempt, now=125, process_status=alive(attempt))
    changed = {**attempt, "attempt_id": "attempt-2", "started_at": 200, "process": {**attempt["process"], "start_ticks": "999"}}
    path.write_text(line(1, at=210))
    result = collect_training_log(state, changed, now=220, process_status=alive(changed))
    assert result["last_observation"]["attempt_id"] == "attempt-2"
    with pytest.raises(FlowError, match="reactivate"):
        collect_training_log(state, attempt, now=230, process_status=alive(attempt))


def test_manifest_and_context_changes_are_not_silent_relabels(tmp_path, attempt):
    state = tmp_path / "state"
    collect_training_log(state, attempt, now=120, process_status=alive(attempt))
    with pytest.raises(FlowError, match="manifest changed"):
        collect_training_log(state, {**attempt, "expected_final_step": 4}, now=130, process_status=alive(attempt))
    with pytest.raises(FlowError, match="context changed"):
        collect_training_log(state, {**attempt, "context": "new"}, now=130, process_status=alive(attempt))


def test_export_failure_retains_atomic_raw_cursor_and_sample_outbox(tmp_path, attempt, monkeypatch):
    Path(attempt["log_path"]).write_text(line(1))
    state = tmp_path / "state"
    original = training_logs.atomic_write
    monkeypatch.setattr(training_logs, "atomic_write", lambda *a: (_ for _ in ()).throw(OSError("fixture write interruption")))
    with pytest.raises(OSError):
        collect_training_log(state, attempt, now=120, process_status=alive(attempt))
    monkeypatch.setattr(training_logs, "atomic_write", original)
    result = collect_training_log(state, attempt, now=130, process_status=alive(attempt))
    assert [r["step"] for r in records(result) if r["progress_observed"]] == [1]
    Path(result["normalized_log"]).write_bytes(b"interrupted export")
    result = collect_training_log(state, attempt, now=140, process_status=alive(attempt))
    assert [r["step"] for r in records(result) if r["progress_observed"]] == [1]


def test_fatal_lines_use_lifecycle_kind(tmp_path, attempt):
    Path(attempt["log_path"]).write_text("RuntimeError: HIP out of memory\n")
    result = collect_training_log(tmp_path / "state", attempt, now=120, process_status=alive(attempt))
    events = records(result)
    assert events[0]["observation_kind"] == "lifecycle"
    assert events[0]["source_record_kind"] == "fatal"
    assert events[0]["progress_observed"] is False


def test_linux_process_identity_handles_parens_and_zombie(tmp_path, monkeypatch):
    process = tmp_path / "123"
    process.mkdir()
    boot = tmp_path / "sys/kernel/random"
    boot.mkdir(parents=True)
    (boot / "boot_id").write_text("boot-fixture")
    (process / "stat").write_text("123 (name with ) parens) " + " ".join(["S"] + ["0"] * 18 + ["321"]))
    monkeypatch.setattr(training_logs.os, "readlink", lambda path: "pid:[fixture]")
    assert process_identity(123, tmp_path)["identity"]["start_ticks"] == "321"
    (process / "stat").write_text("123 (name) " + " ".join(["Z"] + ["0"] * 18 + ["321"]))
    assert process_identity(123, tmp_path)["status"] == "exited"
    assert process_identity(999, tmp_path)["status"] == "exited"
    (boot / "boot_id").unlink()
    assert process_identity(123, tmp_path)["status"] == "unknown"


def test_checkpoint_start_step_is_not_new_training_progress(tmp_path, attempt):
    attempt.update(start_step=10, expected_final_step=13)
    Path(attempt["log_path"]).write_text(line(10, at=110, total=13))
    result = collect_training_log(tmp_path / "state", attempt, now=120, process_status=alive(attempt))
    assert all(not r["progress_observed"] for r in records(result))
    assert result["last_observation"]["phase"] == "startup"


def test_verified_exit_receipt_survives_observer_restart_without_external_file(tmp_path, attempt):
    Path(attempt["log_path"]).write_text(line(1) + line(2) + line(3))
    state = tmp_path / "state"
    first = collect_training_log(state, attempt, now=150, process_status={"status": "exited"}, exit_receipt=receipt(attempt))
    assert first["last_observation"]["completed"]
    later = collect_training_log(state, attempt, now=200, process_status={"status": "exited"})
    assert later["last_observation"]["completed"]
    assert later["last_observation"]["exit_receipt"] == receipt(attempt)


def test_iteration_beyond_declared_total_is_not_valid_completion(tmp_path, attempt):
    Path(attempt["log_path"]).write_text(line(5, total=3))
    result = collect_training_log(tmp_path / "state", attempt, now=180, process_status={"status": "exited"},
                                  exit_receipt=receipt(attempt, finished=170))
    assert not result["last_observation"]["completed"]
    assert "iteration-step-outside-attempt-contract" in result["last_observation"]["fatal_errors"]


def test_adapter_monitor_integration_startup_stall_and_verified_completion(tmp_path, attempt):
    store = Store(tmp_path / "monitor")
    store.create({"schema_version": 1, "task_id": "fixture", "mode": "operate", "objective": "synthetic observation test",
                  "context": {"source": "synthetic"}})
    attempt["context"] = store.task("fixture")["context"]
    policy = {"startup_timeout_seconds": 100, "stall_seconds": 30, "telemetry_seconds": 60,
              "recovery_seconds": 120, "min_progress_samples": 2}
    state, path = tmp_path / "adapter", Path(attempt["log_path"])
    observed = collect_training_log(state, attempt, now=145, process_status=alive(attempt))
    heartbeat = poll_log(store, "fixture", observed["normalized_log"], policy, now=145)
    assert not any(x["kind"] == "training-stalled" for x in heartbeat["issues"])
    path.write_text(line(1, at=150))
    observed = collect_training_log(state, attempt, now=155, process_status=alive(attempt))
    heartbeat = poll_log(store, "fixture", observed["normalized_log"], policy, now=155)
    assert heartbeat["status"] == "healthy-observed"
    observed = collect_training_log(state, attempt, now=190, process_status=alive(attempt))
    heartbeat = poll_log(store, "fixture", observed["normalized_log"], policy, now=190)
    assert "training-stalled" in {x["kind"] for x in heartbeat["issues"]}
    with path.open("a") as stream:
        stream.write(line(2, at=192) + line(3, at=195))
    observed = collect_training_log(state, attempt, now=205, process_status={"status": "exited"},
                                    exit_receipt=receipt(attempt, finished=200))
    heartbeat = poll_log(store, "fixture", observed["normalized_log"], policy, now=205)
    assert heartbeat["completion_verified"] is True
    assert heartbeat["status"] == "healthy-observed"


def test_late_iteration_delivery_is_not_clock_regression(tmp_path, attempt):
    store = Store(tmp_path / "monitor")
    store.create({"schema_version": 1, "task_id": "fixture", "mode": "operate", "objective": "synthetic clock test",
                  "context": {"source": "synthetic"}})
    attempt["context"] = store.task("fixture")["context"]
    policy = {"startup_timeout_seconds": 100, "stall_seconds": 30, "telemetry_seconds": 60,
              "recovery_seconds": 120, "min_progress_samples": 2}
    state, path = tmp_path / "adapter", Path(attempt["log_path"])
    path.write_text(line(1, at=110))
    observed = collect_training_log(state, attempt, now=130, process_status=alive(attempt))
    poll_log(store, "fixture", observed["normalized_log"], policy, now=130)
    with path.open("a") as stream:
        stream.write(line(2, at=125))
    observed = collect_training_log(state, attempt, now=135, process_status=alive(attempt))
    heartbeat = poll_log(store, "fixture", observed["normalized_log"], policy, now=135)
    assert not any(x["kind"] == "observation-time-regressed" for x in heartbeat["issues"])


def test_clockless_late_reads_require_verified_sealed_log(tmp_path, attempt):
    from hcu_trainflow.monitor import observation_issues
    text = "".join(line(i).split("]", 1)[1] for i in (1, 2, 3))
    Path(attempt["log_path"]).write_text(text)
    policy = {"startup_timeout_seconds": 100, "stall_seconds": 30, "telemetry_seconds": 60,
              "recovery_seconds": 120, "min_progress_samples": 2}
    unsealed = collect_training_log(tmp_path / "unsealed", attempt, now=200,
        process_status={"status": "exited"}, exit_receipt=receipt(attempt))
    assert "completion-unverified" in {x["kind"] for x in observation_issues(records(unsealed), policy, 200)}
    sealed = collect_training_log(tmp_path / "sealed", attempt, now=200,
        process_status={"status": "exited"}, exit_receipt=sealed_receipt(attempt))
    assert sealed["last_observation"]["log_seal_verified"] is True
    assert "completion-unverified" not in {x["kind"] for x in observation_issues(records(sealed), policy, 200)}
    # Timing is still collector time and retains its warning; no invented event time.
    assert all(x["timestamp"] == 200 for x in records(sealed) if x["progress_observed"])
    assert any("performance-unverified" in x for x in sealed["last_observation"]["adapter_warnings"])


def test_fallback_clock_does_not_poison_later_source_iteration(tmp_path, attempt):
    from hcu_trainflow.monitor import observation_issues
    attempt["started_at"] = 100.5
    # Text clocks may have seconds precision. First source stamp precedes the
    # fractional launcher start, while the next two are valid event timestamps.
    Path(attempt["log_path"]).write_text(line(1, at=100) + line(2, at=110) + line(3, at=120))
    result = collect_training_log(tmp_path / "state", attempt, now=200, process_status={"status": "exited"},
                                  exit_receipt=sealed_receipt(attempt))
    policy = {"startup_timeout_seconds": 100, "stall_seconds": 30, "telemetry_seconds": 60,
              "recovery_seconds": 120, "min_progress_samples": 2}
    issues = {x["kind"] for x in observation_issues(records(result), policy, 200)}
    assert "observation-time-regressed" not in issues and "completion-unverified" not in issues


def test_tampered_exit_seal_cannot_complete(tmp_path, attempt):
    Path(attempt["log_path"]).write_text(line(1) + line(2) + line(3))
    proof = sealed_receipt(attempt)
    Path(attempt["log_path"]).write_text(line(1, loss="9.000000E+00") + line(2) + line(3))
    result = collect_training_log(tmp_path / "state", attempt, now=200, process_status={"status": "exited"}, exit_receipt=proof)
    assert not result["last_observation"]["completed"]
    assert "exit-log-seal-hash-or-size-mismatch" in result["last_observation"]["fatal_errors"]


def test_sealed_completion_survives_log_path_reuse_and_restart(tmp_path, attempt):
    Path(attempt["log_path"]).write_text(line(1) + line(2) + line(3))
    state = tmp_path / "state"
    first = collect_training_log(state, attempt, now=200, process_status={"status": "exited"}, exit_receipt=sealed_receipt(attempt))
    assert first["last_observation"]["log_seal_verified"]
    Path(attempt["log_path"]).write_text("new unrelated log\n")
    later = collect_training_log(state, attempt, now=250, process_status={"status": "exited"})
    assert later["last_observation"]["completed"] and later["last_observation"]["log_seal_verified"]


def test_changed_matching_receipt_is_not_silent_terminal_rewrite(tmp_path, attempt):
    Path(attempt["log_path"]).write_text(line(1) + line(2) + line(3))
    state = tmp_path / "state"
    collect_training_log(state, attempt, now=200, process_status={"status": "exited"}, exit_receipt=receipt(attempt))
    changed = collect_training_log(state, attempt, now=210, process_status={"status": "exited"}, exit_receipt=receipt(attempt, code=1))
    assert not changed["last_observation"]["completed"]
    assert "exit-receipt-changed-after-observation" in changed["last_observation"]["fatal_errors"]


def test_seal_cannot_cover_prior_clockless_progress_after_log_replacement(tmp_path, attempt):
    path = Path(attempt["log_path"])
    text = "".join(line(i).split("]", 1)[1] for i in (1, 2, 3))
    path.write_text(text)
    state = tmp_path / "state"
    collect_training_log(state, attempt, now=135, process_status=alive(attempt))
    path.write_text("unrelated replacement log\n" + "x" * (len(text) + 10) + "\n")
    result = collect_training_log(state, attempt, now=200, process_status={"status": "exited"},
                                  exit_receipt=sealed_receipt(attempt))
    assert not result["last_observation"]["completed"]
    assert "exit-log-seal-does-not-cover-clockless-progress" in result["last_observation"]["fatal_errors"]
