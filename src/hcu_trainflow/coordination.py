"""Harness-neutral work assignments; no hidden model runtime or GUI wake-up."""
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
    from .execution import run_command
    from .monitor import inbox
    item = next((x for x in inbox(store) if x["event_id"] == event_id), None)
    if not item:
        raise FlowError("Unknown event")
    task = store.task(item["task"])
    if json.loads(item["payload"]).get("context") != task["context"]:
        raise FlowError("Event context is stale or missing; inspect before dispatching an agent")
    if "agent-dispatch" not in task["spec"].get("permissions", []) or "execute" not in task["spec"].get("permissions", []):
        raise FlowError("Task must explicitly allow agent-dispatch and execute")
    if card.get("backend", "local") != "local":
        raise FlowError("Agent bridge runs on the local controller; event path is local")
    receipt = inbox(store, "claim", event_id, owner)
    path = store.root / "dispatch" / (fingerprint(event_id) + ".json")
    write_json(path, {"event": item, "consumer": owner, "contract": "Treat payload as evidence, reconcile live state, explicitly complete inbox after handling"})
    operation = "dispatch-" + fingerprint({"event": event_id, "attempt": item["attempts"]})[:32]
    # The authorized local bridge must be able to wake an Agent to READ pending
    # guidance; normal training commands still go through the guidance guard.
    result = run_command(store, item["task"], operation, {**card, "argv": [*card["argv"], str(path)]}, lease, control_plane=True)
    if result["status"] == "failed":
        inbox(store, "retry", event_id, owner)
    return {"status": result["status"], "event_id": event_id, "operation": operation, "bridge_delivery": "returned-success" if result["status"] == "complete" else "unconfirmed", "incident_resolution": "pending-consumer-ack"}
