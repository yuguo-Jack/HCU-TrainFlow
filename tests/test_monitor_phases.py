"""Synthetic observer contract regressions; these are not hardware evidence."""
import json

import pytest

from hcu_trainflow.core import FlowError, Store
from hcu_trainflow.monitor import check_policy, observation_issues, poll_log


POLICY = {"stall_seconds": 30, "telemetry_seconds": 60, "recovery_seconds": 50,
          "min_progress_samples": 2, "startup_timeout_seconds": 300}
IDENTITY = {"pid": 42, "start_ticks": "123", "boot_id": "synthetic-boot", "pid_namespace": "synthetic-ns"}


def sample(timestamp=100, step=0, kind="heartbeat", phase="startup", **extra):
    return {"attempt_id": "a", "context": "test-context", "attempt_started_at": 100,
            "timestamp": timestamp, "step": step, "phase": phase, "observation_kind": kind,
            "progress_observed": kind == "iteration", "expected_final_step": 10,
            "process_identity": IDENTITY, "adapter_warnings": [], "fatal_errors": [], **extra}


def kinds(samples, now, policy=POLICY):
    return {issue["kind"] for issue in observation_issues(samples, policy, now=now)}


def iteration(timestamp, step, **extra):
    return sample(timestamp, step, "iteration", "training", **extra)


def terminal(**extra):
    return sample(122, 10, phase="finished", completed=True, job_alive=False,
                  exit_receipt={"attempt_id": "a", "context": "test-context", "process": IDENTITY,
                                "exit_code": 0, "finished_at": 121}, **extra)


def stored(tmp_path):
    store = Store(tmp_path / "state")
    store.create({"schema_version": 1, "task_id": "t", "mode": "operate", "objective": "watch synthetic rows",
                  "context": {"purpose": "unit-test"}})
    return store, tmp_path / "observations.jsonl"


def append(path, rows, store):
    with path.open("a", encoding="utf-8") as stream:
        for row in rows:
            row = {**row, "context": store.task("t")["context"]}
            if row.get("exit_receipt"):
                row["exit_receipt"] = {**row["exit_receipt"], "context": row["context"]}
            stream.write(json.dumps(row) + "\n")


def test_compilation_uses_independent_startup_allowance():
    assert kinds([sample(100), sample(200)], 200) == set()
    assert kinds([sample(100), sample(401)], 401) == {"startup-timeout"}
    # An unknown liveness state does not reset the original startup clock.
    assert "startup-timeout" in kinds([sample(100), sample(401, phase="unknown")], 401)


@pytest.mark.parametrize("kind", ["memory", "heartbeat", "lifecycle"])
def test_non_iteration_cannot_reset_or_regress_progress(kind):
    rows = [iteration(110, 1), sample(145, 99, kind, "training")]
    assert kinds(rows, 145) == {"training-stalled"}
    rows[-1]["step"] = 0
    assert kinds(rows, 145) == {"training-stalled"}


def test_training_cannot_return_to_startup_to_hide_stall():
    assert kinds([iteration(110, 1), sample(145)], 145) == {"training-stalled"}
    assert kinds([iteration(110, 1), sample(145, phase="unknown")], 145) == {"training-stalled", "training-state-unknown"}


def test_only_explicit_advancing_iterations_recover():
    recovering = {"recovery_state": "restored", "checkpoint_verified": True}
    rows = [sample(100, **recovering), iteration(120, 7, **recovering),
            sample(160, 7, "memory", "training", **recovering)]
    assert {"training-stalled", "recovery-timeout"} <= kinds(rows, 160)
    assert kinds(rows + [iteration(161, 8, **recovering)], 161) == set()
    assert "recovery-timeout" in kinds(rows + [iteration(161, 8, **{**recovering, "checkpoint_verified": False})], 161)


def test_repeated_iterations_are_not_recovery_progress():
    recovery = {"recovery_state": "recovering", "checkpoint_verified": True}
    rows = [iteration(110, 5, **recovery), iteration(160, 5, **recovery)]
    assert {"training-stalled", "recovery-timeout"} <= kinds(rows, 160)


def test_new_attempt_may_resume_from_lower_checkpoint():
    rows = [iteration(110, 8), sample(150, 3, attempt_id="b", attempt_started_at=150),
            iteration(160, 4, attempt_id="b", attempt_started_at=150)]
    assert kinds(rows, 160) == set()


def test_step_rollback_is_durable_and_does_not_reset_clock():
    rows = [iteration(110, 5), iteration(130, 4), iteration(140, 5), sample(141, 5, phase="training")]
    assert kinds(rows, 141) == {"step-regressed", "training-stalled"}


def test_clock_rollback_cannot_supply_fresh_progress_or_completion():
    rows = [iteration(110, 9), iteration(109, 10), terminal()]
    assert {"observation-time-regressed", "completion-unverified"} <= kinds(rows, 122)
    assert "training-stalled" in kinds(rows, 141)


def test_late_source_log_is_not_compared_with_newer_heartbeat_clock():
    rows = [sample(115), iteration(110, 1, timestamp_basis="source-log-clock"),
            sample(125, 1, phase="training"), iteration(120, 2, timestamp_basis="source-log-clock")]
    assert kinds(rows, 125) == set()
    assert "observation-time-regressed" in kinds(rows + [iteration(119, 3, timestamp_basis="source-log-clock")], 125)


def test_collector_clock_regression_remains_an_incident():
    assert "observation-time-regressed" in kinds([sample(115), sample(114)], 115)


@pytest.mark.parametrize("name", ["loss", "grad_norm"])
@pytest.mark.parametrize("value", [float("nan"), float("inf"), "nan", "inf", True])
def test_nonfinite_is_not_erased_by_later_heartbeat(name, value):
    rows = [iteration(110, 9, **{name: value}), iteration(120, 10), terminal()]
    assert {"nonfinite-" + name, "completion-unverified"} <= kinds(rows, 122)


def test_adapter_warning_and_fatal_error_have_distinct_incidents():
    rows = [iteration(110, 1, fatal_errors=["traceback"]), sample(111, 1, phase="training",
             adapter_warnings=["clock-fallback"])]
    assert kinds(rows, 111) == {"training-fatal-error", "adapter-warning"}


def test_failure_phase_without_exit_receipt_is_not_success():
    assert "training-failed" in kinds([sample(110, phase="failed")], 110)


def test_matching_exit_receipt_and_actual_final_iteration_are_terminal():
    assert kinds([iteration(110, 9), iteration(120, 10), terminal()], 10000) == set()


@pytest.mark.parametrize("field,value", [("attempt_id", "b"), ("context", "other"), ("exit_code", 1),
                                        ("exit_code", False), ("process", {**IDENTITY, "start_ticks": "456"}),
                                        ("finished_at", 119), ("finished_at", 125)])
def test_mismatched_receipt_cannot_hide_exit(field, value):
    end = terminal()
    end["exit_receipt"][field] = value
    assert {"completion-unverified", "job-exited"} <= kinds([iteration(120, 10), end], 123)


def test_completion_needs_observed_iteration_not_heartbeat_step():
    assert "completion-unverified" in kinds([sample(), terminal()], 123)
    assert "completion-unverified" in kinds([iteration(110, 9), terminal()], 123)


@pytest.mark.parametrize("change", [{"attempt_started_at": 101}, {"expected_final_step": 11},
                                   {"process_identity": {**IDENTITY, "pid": 43}}])
def test_contract_cannot_change_inside_attempt(change):
    assert "attempt-contract-changed" in kinds([sample(), sample(110, **change)], 110)


def test_new_contract_requires_explicit_startup_threshold():
    legacy_policy = {key: val for key, val in POLICY.items() if key != "startup_timeout_seconds"}
    with pytest.raises(FlowError, match="startup_timeout_seconds"):
        observation_issues([sample()], legacy_policy, 100)
    assert observation_issues([{"attempt_id": "a", "timestamp": 100, "step": 1}], legacy_policy, 100) == []


@pytest.mark.parametrize("value", [0, -1, True, float("inf"), "300"])
def test_invalid_startup_timeout_rejected(value):
    with pytest.raises(FlowError):
        check_policy({**POLICY, "startup_timeout_seconds": value})


def test_retention_and_restart_keep_real_progress_clock(tmp_path):
    store, path = stored(tmp_path)
    append(path, [sample(), iteration(110, 1)] + [sample(111 + i / 100, 1, phase="training") for i in range(1100)], store)
    first = poll_log(store, "t", path, POLICY, now=150)
    assert {x["kind"] for x in first["issues"]} == {"training-stalled"}
    assert poll_log(Store(store.root), "t", path, POLICY, now=151)["issues"] == first["issues"]
    with store.db() as db:
        cursor = json.loads(db.execute("SELECT value FROM meta WHERE key='watch:t'").fetchone()[0])
        assert len(cursor["samples"]) == 1000
        assert cursor["progress"]["a"]["progress_samples"] == 1
        assert cursor["progress"]["a"]["last_progress_at"] == 110
        cursor.pop("progress_version")
        db.execute("UPDATE meta SET value=? WHERE key='watch:t'", (json.dumps(cursor),))
    assert poll_log(Store(store.root), "t", path, POLICY, now=151)["issues"] == first["issues"]
    append(path, [iteration(152, 2)], store)
    assert poll_log(store, "t", path, POLICY, now=152)["issues"] == []


def test_completion_receipt_preserved_by_watcher(tmp_path):
    store, path = stored(tmp_path)
    append(path, [iteration(110, 9), iteration(120, 10), terminal()], store)
    result = poll_log(store, "t", path, POLICY, now=10000)
    assert result["completion_verified"] is True and result["issues"] == []


def test_invalid_progress_claim_is_rejected_without_consuming_iteration(tmp_path):
    store, path = stored(tmp_path)
    append(path, [sample(), sample(105, 1, "memory", "training", progress_observed=True)], store)
    result = poll_log(store, "t", path, POLICY, now=105)
    assert result["last_observation"]["step"] == 0
    assert {x["kind"] for x in result["issues"]} == {"collector-input-warning"}


def test_slowdown_uses_iterations_not_repeated_heartbeats():
    rows = [iteration(110, 1)] + [sample(120 + i, 1, phase="training") for i in range(10)] + [iteration(140, 2)]
    policy = {**POLICY, "reference_step_seconds": 10, "performance_window": 2}
    assert kinds(rows, 140, policy) == {"sustained-slowdown"}


def test_adapter_faults_become_durable_incident_events(tmp_path):
    store, path = stored(tmp_path)
    append(path, [iteration(110, 1, adapter_warnings=["unparsed-iteration-record"], fatal_errors=["OOM"])], store)
    poll_log(store, "t", path, POLICY, now=110)
    opened = {event["payload"]["kind"] for event in store.events() if event["kind"] == "incident-opened"}
    assert opened == {"adapter-warning", "training-fatal-error"}


def test_collector_timing_does_not_become_wall_clock_slowdown():
    rows = [iteration(110, 1, timestamp_basis="first-observed-no-source-clock"),
            iteration(200, 2, timestamp_basis="first-observed-no-source-clock")]
    policy = {**POLICY, "reference_step_seconds": 10, "performance_window": 2}
    assert "sustained-slowdown" not in kinds(rows, 200, policy)


def test_incomplete_log_seal_cannot_verify_clockless_completion():
    source = {"path": "test.log", "offset": 0, "bytes": 80}
    row = iteration(122, 10, timestamp_basis="first-observed-no-source-clock", source=source)
    end = terminal(log_seal_verified=True)
    end["exit_receipt"]["log_evidence"] = {"path": "test.log", "bytes": 80}
    assert "completion-unverified" in kinds([row, end], 122)
    end["exit_receipt"]["log_evidence"]["sha256"] = "f" * 64
    assert "completion-unverified" not in kinds([row, end], 122)
    end["exit_receipt"]["log_evidence"]["bytes"] = 79
    assert "completion-unverified" in kinds([row, end], 122)
