import json

import pytest

from hcu_trainflow.core import Store, FlowError, utc
from hcu_trainflow.quality import compare_loss
from quality_fixtures import stage_report


@pytest.fixture
def stage(tmp_path):
    store = Store(tmp_path / "store")
    task = store.create({"schema_version": 1, "task_id": "t", "mode": "optimize",
                         "objective": "Synthetic stage gate regression", "context": {"source": "fixture"}})
    return store, stage_report(store, task["context"])


def replace_inputs(store, report, inputs):
    pointer = store.put(json.dumps(inputs).encode())
    return {**report, "quality_inputs": pointer, "evidence": [*report["evidence"], pointer]}


def test_current_stage_recomputes_retained_comparison(stage):
    store, report = stage
    result = store.report("t", "stage-quality", report)
    assert result["status"] == "pass"
    with store.db() as db:
        assert store.current_reports(db, "t", report["context"])["stage-quality"]["artifact"] == result["artifact"]


@pytest.mark.parametrize("change", ["missing-inputs", "legacy", "state-mismatch", "undeclared-mismatch",
                                    "snapshot-mismatch", "context-mismatch", "missing-raw", "loss-regression"])
def test_claimed_pass_cannot_replace_stage_evidence(stage, change):
    store, report = stage
    inputs = json.loads(store.artifact(report["quality_inputs"]))
    if change == "missing-inputs":
        report.pop("quality_inputs")
    else:
        if change == "legacy":
            for record in inputs.values():
                record.pop("initial_state_fingerprint")
                record.pop("training_recipe_fingerprint")
            result = compare_loss(**inputs)
            assert result["status"] == "pass" and result["stage_eligible"] is False
        elif change == "state-mismatch":
            inputs["candidate"]["initial_state_fingerprint"] = "advanced-state"
        elif change == "undeclared-mismatch":
            inputs["contract"].pop("initial_state_fingerprint")
            inputs["candidate"]["initial_state_fingerprint"] = "advanced-state"
            assert compare_loss(**inputs)["status"] == "incomplete"
        elif change == "snapshot-mismatch":
            inputs["candidate"]["candidate_snapshot"] = store.put(b"different candidate")
        elif change == "context-mismatch":
            for record in inputs.values():
                record["context"] = "another-context"
        elif change == "missing-raw":
            inputs["candidate"]["evidence"] = ["0" * 64]
        elif change == "loss-regression":
            inputs["candidate"]["loss"] = [3., 3., 3.]
        report = replace_inputs(store, report, inputs)
    report["stage_eligible"] = True  # Self-reported eligibility does not bypass recomputation.
    with pytest.raises(FlowError):
        store.report("t", "stage-quality", report)


def test_legacy_pass_remains_readable_but_cannot_grant_a_new_transition(stage):
    store, report = stage
    report.pop("quality_inputs")
    sha = store.put(json.dumps(report).encode())
    # Restore the shape of a pre-upgrade Store, not a new accepted report.
    with store.db() as db:
        db.execute("INSERT INTO reports VALUES(?,?,?,?,?,?)", ("t", "stage-quality", report["context"], sha, "pass", utc()))
        store.event(db, "t", "report-recorded", {"kind": "stage-quality", "artifact": sha})
        assert "stage-quality" not in store.current_reports(db, "t", report["context"])
    assert json.loads(store.artifact(sha))["status"] == "pass"
    with pytest.raises(FlowError, match="deliverable"):
        store.transition("t", "completed")


def test_missing_recipe_declaration_is_explicitly_ineligible_even_if_losses_match(stage):
    store, report = stage
    inputs = json.loads(store.artifact(report["quality_inputs"]))
    for record in inputs.values():
        record.pop("training_recipe_fingerprint")
    result = compare_loss(**inputs)
    assert result["status"] == "pass" and result["stage_eligible"] is False
    assert result["stage_missing"] == ["training_recipe_fingerprint"]
