"""CPU-only recovery boundaries; simulated intents are explicitly labeled."""
import json
import sys

import pytest

from hcu_trainflow import core, execution, flow, monitor
from hcu_trainflow.command_group import _controller_lock
from hcu_trainflow.coordination import dispatch_inbox, reconcile_operation
from hcu_trainflow.core import FlowError, Store, utc


def make_store(tmp_path, *, dispatch=True):
    store = Store(tmp_path / "store")
    store.create({"schema_version": 1, "task_id": "t", "mode": "analyze",
                  "objective": "CPU recovery protocol regression",
                  "context": {"source": "CPU fixture, no training validation"},
                  "permissions": ["execute", "agent-dispatch"] if dispatch else ["execute"]})
    flow.start(store, "t", {"acceptance": {"analysis": "Retain reviewed CPU evidence"}})
    return store


def command(tmp_path, program="print('cpu-only')", timeout=5, **changes):
    return {"schema_version": 1, "backend": "local",
            "argv": [sys.executable, "-B", "-c", program], "cwd": str(tmp_path),
            "timeout_seconds": timeout, "basis": "Harmless local CPU regression", **changes}


def unknown_operation(store, tmp_path):
    lease = store.lease("cpu-original", "controller", ttl=60)
    result = execution.run_command(store, "t", "original",
                                   command(tmp_path, "import time;time.sleep(.5)", .03), lease)
    assert result["status"] == "unknown"
    return lease


def event(store):
    with store.db() as db:
        return store.event(db, "t", "incident-opened",
                           {"context": store.task("t")["context"], "kind": "CPU fixture"}, channel="agent")


def inbox_item(store, eid):
    return next(row for row in monitor.inbox(store) if row["event_id"] == eid)


def test_cancelled_task_keeps_unknown_visible_until_explicit_reconciliation(tmp_path):
    store = make_store(tmp_path)
    unknown_operation(store, tmp_path)
    store.transition("t", "cancelled", reason="Stop coordinator scope; process evidence still needs reconciliation")
    fresh = Store(store.root)
    decision = flow.next_step(fresh, "t")
    assert decision["action"] == "reconcile" and decision["operations"] == ["original"]
    assert decision["state"] == fresh.task("t")["state"] == "cancelled"
    with pytest.raises(FlowError, match="unresolved"):
        fresh.lease("cpu-original", "replacement")
    proof = fresh.put(b"CPU-only original child killed and waited by local execution timeout")
    reconcile_operation(fresh, "original", "failed", [proof], "Original local child exited; no replacement started")
    assert flow.next_step(fresh, "t")["action"] == "cancelled"


@pytest.mark.parametrize("terminal", ["completed", "cancelled"])
def test_terminal_task_does_not_hide_linked_started_operation(tmp_path, monkeypatch, terminal):
    store = make_store(tmp_path)
    # Legacy/crash-shaped DB fixture only: normal completed gates prevent this.
    with store.db() as db:
        db.execute("INSERT INTO operations VALUES(?,?,?,'started',NULL,?)", ("legacy-start", "t", "synthetic", utc()))
        db.execute("UPDATE tasks SET state=? WHERE id='t'", (terminal,))
    monkeypatch.setattr("hcu_trainflow.team.active_operation", lambda *args: True)
    decision = flow.next_step(Store(store.root), "t")
    assert decision["action"] == "reconcile" and decision["operations"] == ["legacy-start"]
    assert store.task("t")["state"] == terminal


def test_case_alias_rejected_before_intent_and_exact_replay_remains_idempotent(tmp_path):
    store = make_store(tmp_path)
    lease = store.lease("cpu-case", "controller", ttl=60)
    card = command(tmp_path, "from pathlib import Path; p=Path('calls'); p.write_text(p.read_text()+'x' if p.exists() else 'x')")
    result = execution.run_command(store, "t", "CaseOp", card, lease)
    assert result["status"] == "complete"
    with pytest.raises(FlowError, match="case-insensitive"):
        execution.run_command(Store(store.root), "t", "caseop", card, lease)
    assert execution.run_command(Store(store.root), "t", "CaseOp", card, lease) == result
    assert (tmp_path / "calls").read_text() == "x"
    with store.db() as db:
        assert [(r["id"], r["status"]) for r in db.execute("SELECT id,status FROM operations")] == [("CaseOp", "complete")]


@pytest.mark.parametrize("ttl", [float("nan"), float("inf"), -float("inf"), True, "60", None, 0, -1, 86401, 10 ** 1000])
def test_invalid_lease_and_renew_ttl_cannot_poison_persisted_expiry(tmp_path, ttl):
    store = make_store(tmp_path)
    with pytest.raises(FlowError, match="TTL"):
        store.lease("invalid", "controller", ttl)
    lease = store.lease("valid", "controller", ttl=60)
    with store.db() as db:
        before = db.execute("SELECT expires FROM leases WHERE resource='valid'").fetchone()[0]
    with pytest.raises(FlowError, match="TTL"):
        store.renew(lease, ttl)
    with store.db() as db:
        assert db.execute("SELECT count(*) FROM leases WHERE resource='invalid'").fetchone()[0] == 0
        assert db.execute("SELECT expires FROM leases WHERE resource='valid'").fetchone()[0] == before
    assert store.renew(lease, 60.5) == lease


@pytest.mark.parametrize("expiry", [None, float("inf"), -float("inf"), "invalid"])
def test_corrupt_legacy_expiry_requires_inspection_without_takeover(tmp_path, expiry):
    store = make_store(tmp_path)
    lease = store.lease("cpu-legacy", "controller", ttl=60)
    with store.db() as db:
        db.execute("UPDATE leases SET expires=? WHERE resource='cpu-legacy'", (expiry,))
    with store.db() as db, pytest.raises(FlowError, match="persisted lease expiry"):
        store.check_lease(db, **lease)
    with pytest.raises(FlowError, match="persisted lease expiry"):
        store.renew(lease, 60)
    with pytest.raises(FlowError, match="persisted lease expiry"):
        store.lease("cpu-legacy", "new-controller", ttl=60)
    with store.db() as db:
        row = db.execute("SELECT owner,token FROM leases WHERE resource='cpu-legacy'").fetchone()
        assert (row["owner"], row["token"]) == ("controller", 1)


def test_control_plane_requires_explicit_dispatch_permission_before_intent(tmp_path, monkeypatch):
    store = make_store(tmp_path, dispatch=False)
    lease = store.lease("cpu-delivery", "controller", ttl=60)
    monkeypatch.setattr(execution.subprocess, "Popen", lambda *a, **k: pytest.fail("must not launch"))
    with pytest.raises(FlowError, match="agent-dispatch"):
        execution.run_command(store, "t", "unauthorized", command(tmp_path), lease, control_plane=True)
    with store.db() as db:
        assert db.execute("SELECT count(*) FROM operations").fetchone()[0] == 0


@pytest.mark.parametrize("backend", ["ssh", "ssh-docker", "ssh-slurm", "k8s"])
def test_control_plane_cannot_bypass_gates_with_remote_backend(tmp_path, monkeypatch, backend):
    store = make_store(tmp_path)
    lease = store.lease("cpu-delivery", "controller", ttl=60)
    card = command(tmp_path, backend=backend, ssh_target="fixture", container="fixture", allocation="1",
                   namespace="fixture", pod="fixture")
    monkeypatch.setattr(execution.subprocess, "Popen", lambda *a, **k: pytest.fail("no remote process may launch"))
    with pytest.raises(FlowError, match="local controller backend"):
        execution.run_command(store, "t", "remote-bypass", card, lease, control_plane=True)
    with store.db() as db:
        assert db.execute("SELECT count(*) FROM operations").fetchone()[0] == 0


def test_authorized_local_bridge_can_deliver_while_unknown_and_guidance_remain(tmp_path):
    store = make_store(tmp_path)
    unknown_operation(store, tmp_path)
    flow.board_paths(store, "t")[2].write_text("# Review unresolved process before experiments\n", encoding="utf-8")
    flow.sync_guidance(store, "t", force=True)
    lease = store.lease("cpu-delivery", "controller", ttl=60)
    with pytest.raises(FlowError):
        execution.run_command(store, "t", "experiment", command(tmp_path), lease)
    result = execution.run_command(store, "t", "delivery", command(tmp_path), lease, control_plane=True)
    assert result["status"] == "complete"
    assert flow.next_step(store, "t")["action"] == "reconcile"


def test_invalid_inbox_card_does_not_claim_or_consume_attempt(tmp_path):
    store = make_store(tmp_path)
    eid = event(store)
    lease = store.lease("cpu-delivery", "controller", ttl=60)
    with pytest.raises(FlowError, match="Unknown command-card"):
        dispatch_inbox(store, eid, "consumer", command(tmp_path, schema_version=999), lease)
    assert inbox_item(store, eid)["status"] == "pending"
    assert inbox_item(store, eid)["attempts"] == 0
    with store.db() as db:
        assert db.execute("SELECT count(*) FROM operations").fetchone()[0] == 0


def test_invalid_inbox_lease_does_not_claim_event(tmp_path):
    store = make_store(tmp_path)
    eid = event(store)
    lease = store.lease("cpu-delivery", "controller", ttl=60)
    with pytest.raises(FlowError, match="stale fencing"):
        dispatch_inbox(store, eid, "consumer", command(tmp_path), {**lease, "token": 2})
    assert inbox_item(store, eid)["status"] == "pending"


def test_preintent_delivery_write_failure_allows_replacement_consumer(tmp_path, monkeypatch):
    store = make_store(tmp_path)
    eid = event(store)
    lease = store.lease("cpu-delivery", "controller", ttl=60)
    original = core.write_json
    monkeypatch.setattr(core, "write_json", lambda *args: (_ for _ in ()).throw(OSError("synthetic write failure")))
    with pytest.raises(OSError, match="synthetic write failure"):
        dispatch_inbox(store, eid, "old-consumer", command(tmp_path), lease)
    assert inbox_item(store, eid)["status"] == "retry"
    with store.db() as db:
        assert db.execute("SELECT count(*) FROM operations").fetchone()[0] == 0
    monkeypatch.setattr(core, "write_json", original)
    result = dispatch_inbox(Store(store.root), eid, "replacement-consumer", command(tmp_path), lease)
    assert result["status"] == "complete" and result["incident_resolution"] == "pending-consumer-ack"
    assert inbox_item(store, eid)["status"] == "claimed"


def test_postintent_exception_preserves_claim_and_unresolved_operation(tmp_path, monkeypatch):
    store = make_store(tmp_path)
    eid = event(store)
    lease = store.lease("cpu-delivery", "controller", ttl=60)

    def interrupted(s, tid, oid, *args, **kwargs):
        with s.db() as db:
            db.execute("INSERT INTO operations VALUES(?,?,?,'started',NULL,?)", (oid, tid, "synthetic interrupted fixture", utc()))
        raise RuntimeError("synthetic interrupted controller")

    monkeypatch.setattr(execution, "run_command", interrupted)
    with pytest.raises(RuntimeError, match="synthetic interrupted"):
        dispatch_inbox(store, eid, "consumer", command(tmp_path), lease)
    assert inbox_item(store, eid)["status"] == "claimed"
    with pytest.raises(FlowError, match="already claimed"):
        dispatch_inbox(Store(store.root), eid, "replacement", command(tmp_path), lease)
    assert flow.next_step(Store(store.root), "t")["action"] == "reconcile"


def test_active_preintent_controller_prevents_automatic_delivery_retry(tmp_path, monkeypatch):
    store = make_store(tmp_path)
    eid = event(store)
    lease = store.lease("cpu-delivery", "controller", ttl=60)
    oid = "dispatch-" + core.fingerprint({"event": eid, "attempt": 0})[:32]
    with _controller_lock(store, oid), pytest.raises(FlowError, match="controller is active"):
        dispatch_inbox(store, eid, "consumer", command(tmp_path), lease)
    assert inbox_item(store, eid)["status"] == "claimed"
    with store.db() as db:
        assert db.execute("SELECT count(*) FROM operations").fetchone()[0] == 0


def test_intervening_failed_dispatch_does_not_replay_stale_attempt(tmp_path, monkeypatch):
    store = make_store(tmp_path)
    eid = event(store)
    lease = store.lease("cpu-delivery", "controller", ttl=60)
    bridge = command(tmp_path, "from pathlib import Path; p=Path('calls'); p.write_text(p.read_text()+'x' if p.exists() else 'x'); raise SystemExit(7)")
    original = monitor.inbox
    nested = []
    pending = True

    def intervening_dispatch(s, action="list", event_id=None, owner=None):
        nonlocal pending
        if action == "list" and pending:
            pending = False
            stale = original(s)
            nested.append(dispatch_inbox(s, eid, "earlier-consumer", bridge, lease))
            return stale
        return original(s, action, event_id, owner)

    monkeypatch.setattr(monitor, "inbox", intervening_dispatch)
    result = dispatch_inbox(store, eid, "later-consumer", bridge, lease)
    assert nested[0]["status"] == result["status"] == "failed"
    assert nested[0]["operation"] != result["operation"]
    assert (tmp_path / "calls").read_text() == "xx"
    assert inbox_item(store, eid)["attempts"] == 2 and inbox_item(store, eid)["status"] == "retry"
