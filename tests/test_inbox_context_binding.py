"""CPU-only event admission across context changes and A -> B -> A resets."""
import json

import pytest

from hcu_trainflow import core, execution, monitor
from hcu_trainflow.coordination import dispatch_inbox
from hcu_trainflow.core import FlowError, Store
from test_runtime_recovery_guards import command, event, inbox_item, make_store


def assert_no_launch(store, tmp_path):
    with store.db() as db:
        assert db.execute("SELECT count(*) FROM operations").fetchone()[0] == 0
    assert not (tmp_path / "launched").exists()


def bridge(tmp_path):
    return command(tmp_path, "from pathlib import Path; Path('launched').write_text('cpu-only')")


def test_context_change_at_claim_cannot_execute_event_under_replacement_context(tmp_path, monkeypatch):
    store = make_store(tmp_path)
    eid = event(store)
    old_context = store.task("t")["context"]
    lease = store.lease("cpu-delivery", "controller", ttl=60)
    original = monitor.inbox
    switched = False

    def switch_at_claim(s, action="list", event_id=None, owner=None):
        nonlocal switched
        if action == "claim" and not switched:
            switched = True
            s.change_context("t", {"source": "replacement CPU context"})
        return original(s, action, event_id, owner)

    monkeypatch.setattr(monitor, "inbox", switch_at_claim)
    with pytest.raises(FlowError, match="Bound execution context/epoch"):
        dispatch_inbox(store, eid, "consumer", bridge(tmp_path), lease)
    assert store.task("t")["context"] != old_context
    assert inbox_item(store, eid)["status"] == "retry"
    assert inbox_item(store, eid)["attempts"] == 1
    assert_no_launch(store, tmp_path)


def test_old_event_remains_stale_after_aba_without_consuming_claim(tmp_path):
    store = make_store(tmp_path)
    original_spec = store.task("t")["spec"]["context"]
    eid = event(store)
    store.change_context("t", {"source": "intermediate CPU context"})
    store.change_context("t", original_spec)
    assert json.loads(inbox_item(store, eid)["payload"])["context"] == store.task("t")["context"]
    lease = store.lease("cpu-delivery", "controller", ttl=60)
    with pytest.raises(FlowError, match="predates.*epoch"):
        dispatch_inbox(Store(store.root), eid, "consumer", bridge(tmp_path), lease)
    assert inbox_item(store, eid)["status"] == "pending"
    assert inbox_item(store, eid)["attempts"] == 0
    assert_no_launch(store, tmp_path)


def test_aba_between_claim_and_runner_is_rejected_by_bound_epoch(tmp_path, monkeypatch):
    store = make_store(tmp_path)
    original_task = store.task("t")
    eid = event(store)
    lease = store.lease("cpu-delivery", "controller", ttl=60)
    original = execution.run_command

    def change_before_runner(s, *args, **kwargs):
        assert kwargs["expected_context"] == original_task["context"]
        assert kwargs["expected_context_epoch"] == original_task["context_epoch"]
        s.change_context("t", {"source": "intermediate CPU context"})
        s.change_context("t", original_task["spec"]["context"])
        return original(s, *args, **kwargs)

    monkeypatch.setattr(execution, "run_command", change_before_runner)
    with pytest.raises(FlowError, match="Bound execution context/epoch"):
        dispatch_inbox(store, eid, "consumer", bridge(tmp_path), lease)
    assert store.task("t")["context"] == original_task["context"]
    assert store.task("t")["context_epoch"] > original_task["context_epoch"]
    assert inbox_item(store, eid)["status"] == "retry"
    assert_no_launch(store, tmp_path)


def test_context_change_after_runner_snapshot_is_checked_in_intent_transaction(tmp_path, monkeypatch):
    store = make_store(tmp_path)
    original_task = store.task("t")
    eid = event(store)
    lease = store.lease("cpu-delivery", "controller", ttl=60)
    original = execution.command_plan
    calls = 0

    def change_during_plan(card):
        nonlocal calls
        calls += 1
        plan = original(card)
        if calls == 2:  # dispatch precheck first; runner planning after its snapshot second.
            store.change_context("t", {"source": "replacement CPU context"})
        return plan

    monkeypatch.setattr(execution, "command_plan", change_during_plan)
    with pytest.raises(FlowError, match="Bound execution context/epoch"):
        dispatch_inbox(store, eid, "consumer", bridge(tmp_path), lease)
    assert calls == 2
    assert store.task("t")["context_epoch"] > original_task["context_epoch"]
    assert inbox_item(store, eid)["status"] == "retry"
    assert_no_launch(store, tmp_path)


def test_new_event_after_context_reset_can_dispatch_and_retains_epoch_binding(tmp_path):
    store = make_store(tmp_path)
    store.change_context("t", {"source": "new CPU context"})
    task = store.task("t")
    eid = event(store)
    lease = store.lease("cpu-delivery", "controller", ttl=60)
    result = dispatch_inbox(store, eid, "consumer", bridge(tmp_path), lease)
    assert result["status"] == "complete" and result["incident_resolution"] == "pending-consumer-ack"
    assert (tmp_path / "launched").read_text() == "cpu-only"
    delivery = core.read_json(store.root / "dispatch" / (core.fingerprint(eid) + ".json"))
    assert delivery["dispatch_context"]["context"] == task["context"]
    assert delivery["dispatch_context"]["context_epoch"] == task["context_epoch"]
    assert delivery["dispatch_context"]["local_event_seq"] > task["context_epoch"]
    assert inbox_item(store, eid)["status"] == "claimed"


@pytest.mark.parametrize("binding", [
    {"expected_context": "0" * 64},
    {"expected_context_epoch": 0},
    {"expected_context": "not-a-hash", "expected_context_epoch": 0},
    {"expected_context": "0" * 64, "expected_context_epoch": True},
    {"expected_context": "0" * 64, "expected_context_epoch": -1},
])
def test_partial_or_invalid_execution_binding_cannot_write_intent(tmp_path, binding):
    store = make_store(tmp_path)
    lease = store.lease("cpu-delivery", "controller", ttl=60)
    with pytest.raises(FlowError, match="context binding"):
        execution.run_command(store, "t", "bound-invalid", bridge(tmp_path), lease,
                              control_plane=True, **binding)
    assert_no_launch(store, tmp_path)
