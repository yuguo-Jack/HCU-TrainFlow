"""Synthetic environment facts exercise decisions, not hardware thresholds."""
import copy
import json

import pytest

from hcu_trainflow.core import FlowError, Store, digest
from hcu_trainflow.environment import assess_health


RAW = b"synthetic current performance measurement"
REFERENCE = b"synthetic partially matched reference table"


def case():
    conditions = {"dtype": "bf16", "elements": 128, "unit": "GB/s", "ranks": 2}
    contract = {"context": "fixture", "required": [
        {"node": "allocated-fixture", "device": "0", "check": "bandwidth", "kind": "performance",
         "conditions": conditions, "minimum": 100, "basis": "synthetic matched expectation"}]}
    observation = {"context": "fixture", "node": "allocated-fixture", "device": "0", "check": "bandwidth",
                   "conditions": copy.deepcopy(conditions), "value": 120, "status": "pass", "executed": 3,
                   "evidence": [digest(RAW), digest(REFERENCE)]}
    discrepancy = {"summary": "A separate relevant table exposes an unexplained gap; its build is unknown",
                   "evidence": [digest(REFERENCE), digest(RAW)], "missing_conditions": ["reference library build"]}
    return contract, observation, discrepancy


def test_matched_failure_requires_diagnosis_without_inventing_threshold():
    contract, observation, _ = case()
    observation["value"] = 80
    before = copy.deepcopy(contract)
    result = assess_health(contract, [observation])
    row = result["checks"][0]
    assert result["status"] == "fail" and result["failures"] == 1
    assert result["follow_up_required"] is True
    assert row["follow_up"]["classification"] == "matched-performance-failure"
    assert "run-authorized-bounded-single-variable-a-b-a" in row["follow_up"]["steps"]
    assert "verify-correctness-effective-path-and-regression" in row["follow_up"]["steps"]
    assert contract == before


@pytest.mark.parametrize("value", [120, 10000])
def test_unresolved_gap_blocks_pass_even_after_old_minimum_is_met(value):
    contract, observation, discrepancy = case()
    observation.update(value=value, performance_discrepancy=discrepancy)
    result = assess_health(contract, [observation])
    row = result["checks"][0]
    assert result["status"] == "incomplete" and result["failures"] == 0
    assert result["required_missing"] == [row]
    assert row["follow_up"]["classification"] == "provisional-performance-discrepancy"
    assert row["performance_discrepancy"] == discrepancy
    assert "unresolved-performance-discrepancy" in row["reasons"]
    assert set(result["evidence"]) == set(observation["evidence"])


def test_provisional_gap_does_not_erase_an_established_failure():
    contract, observation, discrepancy = case()
    observation.update(value=80, performance_discrepancy=discrepancy)
    result = assess_health(contract, [observation])
    assert result["status"] == "fail"
    assert result["checks"][0]["follow_up"]["classification"] == "matched-performance-failure"
    assert "unresolved-performance-discrepancy" in result["checks"][0]["reasons"]


@pytest.mark.parametrize("change", [{"dtype": "fp32"}, {"unit": "GiB/s"}, {"ranks": True}])
def test_mismatched_conditions_remain_provisional_not_numeric_failure(change):
    contract, observation, discrepancy = case()
    # True must not match integer 1 under Python's loose equality.
    contract["required"][0]["conditions"]["ranks"] = 1
    observation["conditions"]["ranks"] = 1
    observation["conditions"].update(change)
    observation.update(value=1, performance_discrepancy=discrepancy)
    result = assess_health(contract, [observation])
    assert result["status"] == "incomplete" and result["failures"] == 0
    assert "environment-or-workload-mismatch" in result["checks"][0]["reasons"]
    assert "below-matched-expectation" not in result["checks"][0]["reasons"]


def test_missing_reference_is_evidence_gap_not_an_inferred_threshold():
    contract, observation, _ = case()
    contract["required"][0].pop("minimum")
    result = assess_health(contract, [observation])
    assert result["status"] == "incomplete"
    assert result["checks"][0]["follow_up"]["classification"] == "evidence-gap"
    assert result["checks"][0]["reasons"] == ["missing-matched-expectation"]


def test_actual_test_failure_is_separate_from_performance_comparison():
    contract, observation, discrepancy = case()
    observation.update(status="fail", reason="numerical mismatch", performance_discrepancy=discrepancy)
    result = assess_health(contract, [observation])
    assert result["status"] == "fail"
    assert result["checks"][0]["follow_up"]["classification"] == "check-failure"
    assert "numerical mismatch" in result["checks"][0]["reasons"]


@pytest.mark.parametrize("invalid", [
    None, False, {}, {"summary": ""}, {"summary": "   "}, {"summary": 1},
    {"evidence": []}, {"evidence": "a" * 64}, {"evidence": ["not-a-sha"]},
    {"evidence": [None]}, {"evidence": ["f" * 64]},
    {"missing_conditions": "unknown"}, {"missing_conditions": False},
    {"missing_conditions": {}}, {"missing_conditions": [None]}, {"missing_conditions": [" "]},
    {"resolved": True},
])
def test_malformed_discrepancy_cannot_silently_bypass_follow_up(invalid):
    contract, observation, discrepancy = case()
    value = {**discrepancy, **invalid} if isinstance(invalid, dict) and invalid else invalid
    observation["performance_discrepancy"] = value
    with pytest.raises(FlowError, match="Performance discrepancy"):
        assess_health(contract, [observation])


def test_discrepancy_cannot_hide_in_an_unrequired_or_nonperformance_check():
    contract, observation, discrepancy = case()
    observation["performance_discrepancy"] = discrepancy
    with pytest.raises(FlowError, match="required check"):
        assess_health(contract, [{**observation, "check": "untracked"}])
    contract["required"][0]["kind"] = "health"
    with pytest.raises(FlowError, match="performance check"):
        assess_health(contract, [observation])


def test_existing_report_rules_verify_artifacts_and_cannot_relabel_gap_pass(tmp_path):
    store = Store(tmp_path / "private")
    store.create({"schema_version": 1, "task_id": "t", "mode": "environment", "objective": "Synthetic fixture",
                  "context": {"fixture": "environment-discrepancy"}})
    contract, observation, discrepancy = case()
    contract["context"] = observation["context"] = store.task("t")["context"]
    observation["performance_discrepancy"] = discrepancy
    result = assess_health(contract, [observation])
    with pytest.raises(FlowError, match="Unknown artifact"):
        store.report("t", "environment", result)
    store.put_many([RAW, REFERENCE])
    assert store.report("t", "environment", result)["status"] == "incomplete"
    with pytest.raises(FlowError, match="PASS requires"):
        store.report("t", "environment", {**result, "status": "pass"})


def test_reassessment_preserves_prior_incomplete_artifact(tmp_path):
    store = Store(tmp_path / "private")
    contract, observation, discrepancy = case()
    observation["performance_discrepancy"] = discrepancy
    old = assess_health(contract, [observation])
    retained = store.put(json.dumps(old).encode())
    new_measurement = store.put(b"synthetic rechecked measurement; closure review retained separately")
    fresh = {key: value for key, value in observation.items() if key != "performance_discrepancy"}
    fresh["evidence"] = [new_measurement]
    current = assess_health(contract, [fresh])
    assert current["status"] == "pass" and current["follow_up_required"] is False
    assert json.loads(store.artifact(retained))["status"] == "incomplete"


def test_cli_returns_incomplete_for_unresolved_gap(tmp_path, capsys):
    from hcu_trainflow.cli import main
    contract, observation, discrepancy = case()
    observation["performance_discrepancy"] = discrepancy
    cpath, opath = tmp_path / "contract.json", tmp_path / "observations.json"
    cpath.write_text(json.dumps(contract), encoding="utf-8")
    opath.write_text(json.dumps([observation]), encoding="utf-8")
    assert main(["--workspace", str(tmp_path / "private"), "environment-check", str(cpath), str(opath)]) == 2
    result = json.loads(capsys.readouterr().out)
    assert result["follow_up_required"] is True and result["required_missing"]
