import hashlib
import json

import pytest

from hcu_trainflow.delivery import monitor_report, monitor_series
from hcu_trainflow.core import FlowError


def sample(**updates):
    return {"context": "a" * 64, "attempt_id": "attempt-one", "timestamp": 100,
            "observation_kind": "iteration", "progress_observed": True, "timestamp_basis": "source-log-clock",
            "step": 1, "loss": 2.0, **updates}


def test_heartbeat_cannot_extend_step_loss_or_memory_curve():
    first = sample(memory_by_rank={"0": {"observed_at": 99, "allocator_allocated_bytes": 2**30}})
    carried = {**first, "timestamp": 200, "observation_kind": "heartbeat", "progress_observed": False}
    series = monitor_series([first, carried, carried])
    assert list(series["loss"].values()) == [[(100, 2.0)]]
    assert list(series["rank 0 / allocator_allocated_bytes (GiB)"].values()) == [[(99, 1.0)]]


def test_attempt_context_rank_and_allocator_metrics_remain_distinct():
    points = [sample(memory_by_rank={"0": {"observed_at": 100, "allocator_allocated_bytes": 2**30,
                                           "allocator_reserved_bytes": 2 * 2**30},
                                   "1": {"observed_at": 101, "allocator_allocated_bytes": 3 * 2**30}}),
              sample(attempt_id="attempt-two", timestamp=200), sample(context="b" * 64, timestamp=300)]
    series = monitor_series(points)
    assert len(series["loss"]) == 3
    assert list(series["rank 1 / allocator_allocated_bytes (GiB)"].values()) == [[(101, 3.0)]]
    assert list(series["rank 0 / allocator_reserved_bytes (GiB)"].values()) == [[(100, 2.0)]]


def test_nonfinite_and_boolean_metrics_are_not_numeric_evidence():
    series = monitor_series([sample(loss=float("nan"), grad_norm=float("inf"), step=True)])
    assert series == {}


@pytest.mark.parametrize("value", [True, False, float("nan"), float("inf"), -1, "1024", 10**400])
def test_physical_memory_rejects_boolean_and_invalid_values_before_conversion(value):
    diagnostics = {}
    points = monitor_series([sample(observation_kind="memory", progress_observed=False,
                                    device_memory_bytes=value)], diagnostics=diagnostics)
    assert points == {}
    assert diagnostics["skipped"]["invalid-numeric:physical device memory"] == 1


def test_carried_physical_value_on_iteration_is_not_a_new_memory_measurement():
    first = sample(observation_kind="memory", progress_observed=False, device_memory_bytes=2**30)
    later = sample(timestamp=200, device_memory_bytes=2**30)
    points = monitor_series([first, later])
    assert list(points["physical device memory (GiB)"].values()) == [[(100, 1)]]


def test_heartbeat_with_invalid_true_progress_cannot_create_iteration_point():
    diagnostics = {}
    assert monitor_series([sample(observation_kind="heartbeat")], diagnostics=diagnostics) == {}
    assert diagnostics["skipped"]["progress-on-noniteration-record"] == 1


def test_source_and_collector_fallback_clocks_are_separate_series():
    points = monitor_series([sample(timestamp_basis="source-log-clock"),
                             sample(step=2, timestamp=200, timestamp_basis="first-observed-no-source-clock")])
    assert list(points["loss"].values()) == [[(100, 2.0)]]
    assert list(points["loss [collector clock; event time unverified]"].values()) == [[(200, 2.0)]]


def test_distinct_clockless_steps_at_same_collection_time_are_retained():
    one = sample(timestamp_basis="first-observed-no-source-clock")
    two = {**one, "step": 2}
    points = monitor_series([one, two, one])
    assert list(points["loss [collector clock; event time unverified]"].values()) == [[(100, 2.0), (100, 2.0)]]


def test_modern_missing_clock_basis_is_not_assumed_to_be_source_or_collector():
    row = sample()
    del row["timestamp_basis"]
    diagnostics = {}
    points = monitor_series([row], diagnostics=diagnostics)
    assert "loss [unknown clock; event time unverified]" in points
    assert diagnostics["clock_bases"] == {"unknown-clock": 1}
    legacy = {"context": "a" * 64, "attempt_id": "old", "timestamp": 100, "step": 1, "loss": 2}
    assert "loss" in monitor_series([legacy])


@pytest.mark.parametrize("value", [None, [], "bad", {"0": None}, {"0": {"observed_at": 100, "allocator_allocated_bytes": True}}])
def test_malformed_rank_memory_does_not_break_valid_loss_plot(value):
    points = monitor_series([sample(memory_by_rank=value)])
    assert list(points) == ["step", "loss"]


def test_rank_memory_requires_original_clock_and_no_future_timestamp():
    diagnostics = {}
    points = monitor_series([sample(observation_kind="heartbeat", progress_observed=False, observed_at=100,
        memory_by_rank={"0": {"allocator_allocated_bytes": 1024}, "1": {"observed_at": 200, "allocator_reserved_bytes": 1024}})], diagnostics=diagnostics)
    assert points == {}
    assert diagnostics["skipped"] == {"invalid-clock:rank 0 / allocator_allocated_bytes (GiB)": 1, "rank-memory-from-future": 1}


def test_changed_attempt_contract_and_clock_regression_are_visible():
    diagnostics = {}
    points = monitor_series([sample(attempt_started_at=1), sample(timestamp=90, step=2, attempt_started_at=1),
                             sample(timestamp=300, attempt_started_at=250)], diagnostics=diagnostics)
    assert len(points["loss"]) == 2
    assert any("Clock moved backwards" in x for x in diagnostics["warnings"])
    assert any("identity/epoch changed" in x for x in diagnostics["warnings"])


class EventStore:
    def __init__(self, events):
        self.records = events

    def task(self, tid):
        return {}

    def events(self):
        return self.records


def event(kind, payload, **values):
    return {"task": "t", "kind": kind, "payload": payload, **values}


def test_report_rejects_unrenderable_clock_and_keeps_gaps_explicit(tmp_path):
    records = [event("observation", sample(timestamp=1e308)), event("observation", sample(timestamp=True)),
               event("observation", sample(observation_kind="heartbeat", progress_observed=False))]
    result = monitor_report(EventStore(records), "t", tmp_path / "report.html")
    assert result["status"] == "incomplete" and result["series"] == 0
    assert "loss" in result["missing_metrics"]
    assert "invalid-clock:loss" in result["diagnostics"]["skipped"]


def test_sidecar_retains_selected_evidence_hash_and_incident_clear(tmp_path):
    records = [event("observation", sample(), event_id="remote:observation-a"),
               event("observation", sample(attempt_id="other")),
               event("incident-opened", {"attempt_id": "attempt-one", "context": "a"*64, "incident_id": "one"}),
               event("incident-cleared", {"context": "a"*64, "incident_id": "one"}),
               event("incident-opened", {"attempt_id": "other", "context": "a"*64, "detail": "unrelated"})]
    output = tmp_path / "report.html"
    result = monitor_report(EventStore(records), "t", output, attempt="attempt-one", context="a"*64)
    raw = output.with_suffix(".data.json").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == result["data_sha256"]
    data = json.loads(raw)
    assert len(data["events"]) == 1 and data["events"][0]["event_id"] == "remote:observation-a"
    assert result["incidents"] == 2 and data["selection"]["attempt"] == "attempt-one"
    assert result["data_sha256"] in output.read_text(encoding="utf8")
    with pytest.raises(FlowError, match="requested chart scope"):
        monitor_report(EventStore(records), "t", tmp_path / "none.html", attempt="not-observed")


def test_imported_context_reset_does_not_join_same_attempt_across_epochs(tmp_path):
    records = [event("observation", sample(), event_id="peer:a"),
               event("context-changed", {}, event_id="peer:b"),
               event("observation", sample(timestamp=200), event_id="peer:c")]
    result = monitor_report(EventStore(records), "t", tmp_path / "epochs.html")
    data = json.loads((tmp_path / "epochs.data.json").read_bytes())
    assert len([row for row in data["series"] if row["metric"] == "loss"]) == 2
    assert result["diagnostics"]["warnings"]


def test_extreme_finite_metric_values_do_not_generate_nan_svg_coordinates(tmp_path):
    records = [event("observation", sample(loss=-1e308)), event("observation", sample(step=2, timestamp=200, loss=1e308))]
    result = monitor_report(EventStore(records), "t", tmp_path / "extreme.html")
    body = (tmp_path / "extreme.html").read_text(encoding="utf8")
    assert 'cx="nan' not in body and 'cy="nan' not in body and 'inf,' not in body
    assert result["measurement_counts"]["loss"] == 2


def test_report_escapes_rank_clock_warning_and_incident_content(tmp_path):
    dangerous = '</pre><script>alert("bad")</script>'
    records = [event("observation", sample(attempt_id=dangerous, memory_by_rank={dangerous: {"observed_at": 100, "allocator_allocated_bytes": 1}})),
               event("incident-opened", {"detail": dangerous})]
    output = tmp_path / "safe.html"
    monitor_report(EventStore(records), "t", output)
    body = output.read_text(encoding="utf8")
    assert '<script>' not in body and '&lt;script&gt;' in body


def test_report_handles_single_points_and_escapes_untrusted_labels(tmp_path):
    class FakeStore:
        def task(self, tid):
            return {}

        def events(self):
            return [{"task": "t", "kind": "observation", "payload": sample(attempt_id="<script>" )},
                    {"task": "t", "kind": "incident-opened", "payload": {"error": "<bad>"}}]

    output = tmp_path / "report.html"
    result = monitor_report(FakeStore(), "t", output)
    body = output.read_text(encoding="utf-8")
    assert "<script>" not in body and "&lt;script&gt;" in body
    assert "&lt;bad&gt;" in body and "<circle" in body
    assert result["incidents"] == 1 and result["series"] == 2
    assert "Heartbeats do not create" in body
