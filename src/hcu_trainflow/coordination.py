"""Harness-neutral work assignments; no hidden model runtime or GUI wake-up."""
from contextlib import nullcontext
import json

from .core import FlowError


def assign(store, tid, spec):
    from .team import plan
    with store.db() as db:
        previous=db.execute('SELECT max_parallel FROM team_plans WHERE task=?',(tid,)).fetchone()
    return plan(store,tid,{'rationale':'Single bounded work item added by controller','max_parallel':previous['max_parallel'] if previous else 3,'assignments':[spec]})


def finish_assignment(store, aid, owner, report_id, token):
    from .team import finish
    return finish(store,aid,owner,report_id,token)


def reconcile_operation(store, oid, status, evidence, note):
    from .command_group import _controller_lock
    # Same operation lock as both execution APIs. Its process lifetime, not a
    # sampled PID or lease expiry, determines whether a controller can launch.
    with _controller_lock(store, oid):
        return _reconcile_operation(store, oid, status, evidence, note)


def _reconcile_operation(store, oid, status, evidence, note):
    from .execution import operation_budget_seconds
    if status not in {"complete", "failed"} or not evidence or not note:
        raise FlowError("Reconciliation needs terminal outcome, retained evidence and explanation")
    for sha in evidence:
        store.artifact(sha)
    with store.db() as db:
        db.execute("BEGIN IMMEDIATE")
        group = db.execute("SELECT 1 FROM events WHERE kind='command-group-intent' AND json_extract(payload,'$.operation')=?", (oid,)).fetchone()
        if group:
            raise FlowError("Command groups require command-group-reconcile covering every original member")
        row = db.execute("SELECT * FROM operations WHERE id=?", (oid,)).fetchone()
        if not row or row["status"] not in {"started", "unknown"}:
            raise FlowError("Only unresolved operations can be reconciled")
        value = json.loads(row["result"] or "{}")
        value["budget_seconds"] = operation_budget_seconds(db, oid, value, reserve=True)
        value["budget_basis"] = "Conservative reservation retained; exact elapsed execution time remains unassessed"
        value.update(status=status, reconciliation={"evidence": evidence, "note": note})
        db.execute("UPDATE operations SET status=?,result=? WHERE id=?", (status, json.dumps(value), oid))
        store.event(db, row["task"], "operation-reconciled", {"operation": oid, **value})
    return value


def dispatch_inbox(store, event_id, owner, card, lease):
    """Run an operator-configured agent bridge with an event file as last argv.

    A zero bridge exit records delivery, never marks incident resolution.
    """
    from .core import write_json, fingerprint
    from .execution import command_plan, run_command
    from .monitor import inbox
    item = next((x for x in inbox(store) if x["event_id"] == event_id), None)
    if not item:
        raise FlowError("Unknown event")
    task = store.task(item["task"])
    with store.db() as db:
        source_event = db.execute("SELECT seq FROM events WHERE event_id=? AND task=?", (event_id, item["task"])).fetchone()
    if json.loads(item["payload"]).get("context") != task["context"]:
        raise FlowError("Event context is stale or missing; inspect before dispatching an agent")
    if not source_event or source_event["seq"] <= task["context_epoch"]:
        raise FlowError("Event predates the current task context epoch; inspect before dispatching an agent")
    if "agent-dispatch" not in task["spec"].get("permissions", []) or "execute" not in task["spec"].get("permissions", []):
        raise FlowError("Task must explicitly allow agent-dispatch and execute")
    if command_plan(card)["backend"] != "local":
        raise FlowError("Agent bridge runs on the local controller; event path is local")
    with store.db() as db:
        store.check_lease(db, **lease)
    receipt = inbox(store, "claim", event_id, owner)
    operation = None
    try:
        # The earlier list may predate another consumer's failed delivery. Bind
        # this dispatch to the committed claim rather than replaying that attempt.
        with store.db() as db:
            claimed = db.execute("SELECT * FROM outbox WHERE event_id=?", (event_id,)).fetchone()
        if (not claimed or claimed["status"] != "claimed"
                or json.loads(claimed["detail"] or "{}") != {"owner": owner, "claimed_at": receipt["claimed_at"]}):
            raise FlowError("Inbox claim changed before delivery; inspect before retry")
        operation = "dispatch-" + fingerprint({"event": event_id, "attempt": claimed["attempts"] - 1})[:32]
        path = store.root / "dispatch" / (fingerprint(event_id) + ".json")
        write_json(path, {"event": {**item, **dict(claimed)}, "consumer": owner,
                          "dispatch_context": {"context": task["context"], "context_epoch": task["context_epoch"],
                                               "local_event_seq": source_event["seq"]},
                          "contract": "Treat payload as evidence, reconcile live state, explicitly complete inbox after handling"})
        # The authorized local bridge must be able to wake an Agent to READ pending
        # guidance; normal training commands still go through the guidance guard.
        result = run_command(store, item["task"], operation, {**card, "argv": [*card["argv"], str(path)]}, lease, control_plane=True,
                             expected_context=task["context"], expected_context_epoch=task["context_epoch"])
    except BaseException:
        from .command_group import _controller_lock
        try:
            # A competing controller can hold the lock before writing its intent.
            # Keep the event claimed if it can still launch this operation.
            with _controller_lock(store, operation) if operation else nullcontext():
                with store.db() as db:
                    intent = db.execute("SELECT 1 FROM operations WHERE id=?", (operation,)).fetchone() if operation else None
                    current = db.execute("SELECT status,detail FROM outbox WHERE event_id=?", (event_id,)).fetchone()
                # Only an absent intent permits retry. Existing intent may mean
                # an unknown process outcome, even if delivery raised an error.
                if (not intent and current and current["status"] == "claimed"
                        and json.loads(current["detail"] or "{}") == {"owner": owner, "claimed_at": receipt["claimed_at"]}):
                    inbox(store, "retry", event_id, owner)
        except Exception:
            # Preserve the original exception and conservative claim when safe
            # cleanup itself cannot be completed; no implicit redelivery.
            pass
        raise
    if result["status"] == "failed":
        inbox(store, "retry", event_id, owner)
    return {"status": result["status"], "event_id": event_id, "operation": operation, "bridge_delivery": "returned-success" if result["status"] == "complete" else "unconfirmed", "incident_resolution": "pending-consumer-ack"}
