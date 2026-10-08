"""Harness-neutral work assignments; no hidden model runtime or GUI wake-up."""
import json

from .core import FlowError, safe_id


def assign(store, tid, spec):
    task = store.task(tid)
    required = {"id", "owner", "goal", "scope", "allowed_paths", "acceptance", "budget", "context"}
    if required - spec.keys() or any(not spec[x] for x in required) or spec["context"] != task["context"]:
        raise FlowError("Assignment needs bounded scope, owner, acceptance, budget and current context")
    safe_id(spec["id"])
    with store.db() as db:
        db.execute("INSERT INTO assignments VALUES(?,?,?,'pending')", (spec["id"], tid, json.dumps(spec)))
        store.event(db, tid, "assignment-ready", spec, channel="agent")
    return {"id": spec["id"], "status": "pending", "dispatch": "Controller must claim and launch using its installed agent harness"}


def finish_assignment(store, aid, owner, report_id):
    store.artifact(report_id)
    with store.db() as db:
        db.execute("BEGIN IMMEDIATE")
        row = db.execute("SELECT * FROM assignments WHERE id=?", (aid,)).fetchone()
        if not row or json.loads(row["payload"])["owner"] != owner or row["status"] != "pending":
            raise FlowError("Assignment is unavailable or belongs to another owner")
        context = db.execute("SELECT context FROM tasks WHERE id=?", (row["task"],)).fetchone()[0]
        if json.loads(row["payload"])["context"] != context:
            raise FlowError("Assignment context became stale; reassess against current task")
        db.execute("UPDATE assignments SET status='returned' WHERE id=?", (aid,))
        store.event(db, row["task"], "assignment-returned", {"id": aid, "report": report_id, "acceptance": "main-controller-review-required"}, channel="agent")
    return {"id": aid, "status": "returned"}


def reconcile_operation(store, oid, status, evidence, note):
    if status not in {"complete", "failed"} or not evidence or not note:
        raise FlowError("Reconciliation needs terminal outcome, retained evidence and explanation")
    for sha in evidence:
        store.artifact(sha)
    with store.db() as db:
        db.execute("BEGIN IMMEDIATE")
        row = db.execute("SELECT * FROM operations WHERE id=?", (oid,)).fetchone()
        if not row or row["status"] not in {"started", "unknown"}:
            raise FlowError("Only unresolved operations can be reconciled")
        value = json.loads(row["result"] or "{}")
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
    if "agent-dispatch" not in task["spec"].get("permissions", []) or "execute" not in task["spec"].get("permissions", []):
        raise FlowError("Task must explicitly allow agent-dispatch and execute")
    if card.get("backend", "local") != "local":
        raise FlowError("Agent bridge runs on the local controller; event path is local")
    receipt = inbox(store, "claim", event_id, owner)
    path = store.root / "dispatch" / (fingerprint(event_id) + ".json")
    write_json(path, {"event": item, "consumer": owner, "contract": "Treat payload as evidence, reconcile live state, explicitly complete inbox after handling"})
    operation = "dispatch-" + fingerprint({"event": event_id, "attempt": item["attempts"]})[:32]
    result = run_command(store, item["task"], operation, {**card, "argv": [*card["argv"], str(path)]}, lease)
    if result["status"] == "failed":
        inbox(store, "retry", event_id, owner)
    return {"status": result["status"], "event_id": event_id, "operation": operation, "bridge_delivery": "returned-success" if result["status"] == "complete" else "unconfirmed", "incident_resolution": "pending-consumer-ack"}
