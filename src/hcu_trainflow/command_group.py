"""One distributed job, explicit member commands, one durable execution intent."""
from contextlib import ExitStack, contextmanager
import json
import os
from pathlib import Path
import subprocess
import time

from .core import FlowError, context_epoch, fingerprint, safe_id, utc, write_json
from .execution import command_plan, operation_budget_seconds


def _path_id(value):
    safe_id(value)
    if value.endswith(".") or value.split(".", 1)[0].upper() in {"CON", "PRN", "AUX", "NUL", *[f"COM{i}" for i in range(1, 10)], *[f"LPT{i}" for i in range(1, 10)]}:
        raise FlowError("Group/member identifier is not a portable evidence directory name")


def group_plan(card):
    if (not isinstance(card, dict) or set(card) - {"schema_version", "basis", "timeout_seconds", "shared_resources", "members"}
            or type(card.get("schema_version")) is not int or card["schema_version"] != 1):
        raise FlowError("Unknown command-group fields or version")
    if not isinstance(card.get("basis"), str) or not card["basis"].strip():
        raise FlowError("Command group requires a reviewed distributed-job basis")
    timeout = card.get("timeout_seconds")
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not 0 < timeout <= 86400:
        raise FlowError("Group timeout_seconds must be in (0,86400]")
    shared = _resources(card.get("shared_resources"), "shared_resources")
    if not shared:
        raise FlowError("Distributed group must declare its shared network/communication resource")
    members = card.get("members")
    if not isinstance(members, list) or not 2 <= len(members) <= 256:
        raise FlowError("A command group needs 2..256 explicit node members")
    nodes, ids, allocated, plans = set(), set(), set(shared), []
    for member in members:
        if not isinstance(member, dict) or set(member) != {"id", "node", "resources", "card"}:
            raise FlowError("Each member requires exactly id/node/resources/card")
        _path_id(member["id"])
        if member["id"].casefold() in {"group-plan.json", "result.json"}:
            raise FlowError("Member ID collides with a reserved group evidence path")
        if not isinstance(member["node"], str) or not member["node"].strip() or "\0" in member["node"]:
            raise FlowError("Member node must identify the reviewed physical execution domain")
        if member["id"].casefold() in ids or member["node"] in nodes:
            raise FlowError("Member IDs and node domains must be unique")
        resources = _resources(member["resources"], "member resources")
        if not resources or allocated.intersection(resources):
            raise FlowError("Member resources must be nonempty and disjoint; shared domains belong in shared_resources")
        plan = command_plan(member["card"])
        if plan["timeout_seconds"] > timeout:
            raise FlowError("Member timeout cannot exceed the overall group timeout")
        plans.append({"id": member["id"], "node": member["node"], "resources": resources, "plan": plan})
        allocated.update(resources)
        ids.add(member["id"].casefold())
        nodes.add(member["node"])
    result = {"schema_version": 1, "kind": "distributed-command-group", "basis": card["basis"],
            "card_hash": fingerprint(card), "timeout_seconds": timeout, "shared_resources": shared,
            "resources": sorted(allocated), "members": plans}
    # Freeze mutable argv/env/resource arrays supplied through the Python API.
    return json.loads(json.dumps(result, allow_nan=False))


def _resources(values, name):
    if (not isinstance(values, list) or any(not isinstance(x, str) or not x.strip() or "\0" in x for x in values)
            or len(values) != len(set(values))):
        raise FlowError(name + " must be a list of distinct resource IDs")
    return values


def _leases(values, plan):
    if not isinstance(values, list) or any(not isinstance(x, dict) or set(x) != {"resource", "owner", "token"} for x in values):
        raise FlowError("Group leases must be an array of fencing receipts")
    if any(not isinstance(x["resource"], str) or not isinstance(x["owner"], str) or type(x["token"]) is not int for x in values):
        raise FlowError("Malformed group lease resource/owner/token")
    if (len({x["resource"] for x in values}) != len(values)
            or {x["resource"] for x in values} != set(plan["resources"])
            or len({x["owner"] for x in values}) != 1
            or any(not isinstance(x["owner"], str) or not x["owner"] or type(x["token"]) is not int for x in values)):
        raise FlowError("One real owner must hold exactly every member and shared-resource lease")
    return sorted(values, key=lambda x: x["resource"])


@contextmanager
def _controller_lock(store, oid):
    """Exclude reconciliation while an original controller can still launch."""
    _path_id(oid)
    root = store.root / "command-group-locks"
    root.mkdir(parents=True, exist_ok=True)
    with (root / (oid + ".lock")).open("a+b") as stream:
        if os.name == "nt":
            import msvcrt
            if stream.seek(0, os.SEEK_END) == 0:
                stream.write(b"\0"); stream.flush()
            stream.seek(0)
            acquire = lambda: msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            release = lambda: (stream.seek(0), msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1))
        else:
            import fcntl
            acquire = lambda: fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            release = lambda: fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
        try:
            acquire()
        except OSError as exc:
            raise FlowError("Original command-group controller is active; do not launch or reconcile concurrently") from exc
        try:
            yield
        finally:
            release()


def run_group(store, tid, operation_id, card, leases, *, assignment=None, owner=None, token=None):
    with _controller_lock(store, operation_id):
        return _run_group(store, tid, operation_id, card, leases, assignment=assignment, owner=owner, token=token)


def _run_group(store, tid, operation_id, card, leases, *, assignment=None, owner=None, token=None):
    from . import team
    from .flow import guard_execution, get_flow, blockers
    if not assignment and (owner is not None or token is not None):
        raise FlowError("Owner/token require an assignment")
    guard_execution(store, tid, allow_parallel=assignment is not None)
    task = store.task(tid)
    if "execute" not in task["spec"].get("permissions", []) or task["state"] in {"completed", "cancelled", "paused", "blocked", "failed"}:
        raise FlowError("Task is not active or lacks execute permission")
    safe_id(operation_id)
    plan = group_plan(card)
    leases = _leases(leases, plan)
    identity = {"kind": "distributed-command-group", "plan": plan, "context": task["context"], "context_epoch": task["context_epoch"]}
    if assignment:
        identity.update(assignment=assignment, owner=owner, token=token)
        if leases[0]["owner"] != owner:
            raise FlowError("Assignment owner must hold all group leases")
    request = fingerprint(identity)
    with store.db() as db:
        db.execute("BEGIN IMMEDIATE")
        for lease in leases:
            store.check_lease(db, **lease)
        current = db.execute("SELECT context,state FROM tasks WHERE id=?", (tid,)).fetchone()
        if (current["context"] != task["context"] or context_epoch(db, tid) != task["context_epoch"]
                or current["state"] in {"completed", "cancelled", "paused", "blocked", "failed"}):
            raise FlowError("Task context/state changed before group execution")
        flow = get_flow(db, tid)
        if flow and blockers(db, tid, task, flow):
            raise FlowError("New guidance/context needs attention before execution")
        prior = db.execute("SELECT * FROM operations WHERE id=?", (operation_id,)).fetchone()
        if prior:
            if prior["task"] != tid or prior["request_hash"] != request:
                raise FlowError("Operation ID belongs to a different request")
            if prior["status"] in {"complete", "failed"}:
                return json.loads(prior["result"])
            raise FlowError("Group outcome unknown; reconcile every original member before another launch")
        if db.execute("SELECT 1 FROM operations WHERE lower(id)=lower(?)", (operation_id,)).fetchone():
            raise FlowError("Group operation ID collides with an existing identifier on case-insensitive filesystems")
        assigned = None
        for lease in leases:
            if assignment:
                assigned = team.check_execution(db, tid, assignment, owner, token, lease["resource"])
            for reservation in team.active_reservations(db):
                if (reservation["id"] != assignment and reservation["spec"].get("resource_scope", "assignment") == "assignment"
                        and lease["resource"] in reservation["spec"]["resources"]):
                    raise FlowError("Group resource is reserved by another assignment")
            occupied = db.execute("SELECT o.id FROM operations o JOIN events e ON json_extract(e.payload,'$.operation')=o.id "
                                  "WHERE e.kind='operation-started' AND json_extract(e.payload,'$.lease.resource')=? "
                                  "AND o.status IN ('started','unknown')", (lease["resource"],)).fetchone()
            if occupied:
                raise FlowError("Group resource has an unresolved execution, including in another task")
        history = db.execute("SELECT id,status,result FROM operations WHERE task=?", (tid,)).fetchall()
        _budget(db, history, task["spec"].get("budget", {}), plan["timeout_seconds"])
        for other in history:
            if other["status"] not in {"started", "unknown"}:
                continue
            linked = db.execute("SELECT assignment FROM assignment_operations WHERE operation=?", (other["id"],)).fetchone()
            if (not assigned or other["status"] == "unknown" or not team.active_operation(db, other["id"], tid)
                    or not linked or linked["assignment"] == assignment):
                raise FlowError("Prior execution outcome is unresolved; reconcile before another command group")
        if assigned:
            history = db.execute("SELECT o.id,o.status,o.result FROM operations o JOIN assignment_operations a ON o.id=a.operation WHERE a.assignment=?", (assignment,)).fetchall()
            _budget(db, history, assigned["spec"]["budget"], plan["timeout_seconds"])
        db.execute("INSERT INTO operations VALUES(?,?,?,'started',NULL,?)", (operation_id, tid, request, utc()))
        if assigned:
            db.execute("INSERT INTO assignment_operations VALUES(?,?,?)", (operation_id, assignment, token))
        # Existing core lease acquisition and sequential runners see every
        # resource without schema changes. These events do not add operations.
        for lease in leases:
            store.event(db, tid, "operation-started", {"operation": operation_id, "request": request,
                        "lease": lease, "timeout_seconds": plan["timeout_seconds"], "kind": "distributed-command-group"})
        store.event(db, tid, "command-group-intent", {"operation": operation_id, "request": request, **identity, "leases": leases})
    return _execute(store, tid, operation_id, request, plan, task)


def _budget(db, history, budget, timeout):
    if len(history) >= budget.get("max_operations", 100):
        raise FlowError("Operation budget exhausted")
    spent = sum(operation_budget_seconds(db, row["id"], json.loads(row["result"] or "{}"),
                                        reserve=row["status"] in {"started", "unknown"}) for row in history)
    if timeout > budget.get("max_seconds", float("inf")) - spent:
        raise FlowError("Group timeout exceeds remaining execution budget")


def _member_write(directory, state):
    write_json(directory / "state.json", state)


def _execute(store, tid, oid, request, plan, task):
    directory = store.root / "runs" / tid / oid
    directory.mkdir(parents=True, exist_ok=False)
    write_json(directory / "group-plan.json", plan)
    started = time.monotonic()
    states = {m["id"]: {"id": m["id"], "node": m["node"], "status": "not-started", "returncode": None,
                         "timed_out": False, "backend": m["plan"]["backend"]} for m in plan["members"]}
    processes, begins, logs = {}, {}, {}
    interrupted = None
    with ExitStack() as stack:
        try:
            for member in plan["members"]:
                mid, command = member["id"], member["plan"]
                if time.monotonic() - started >= plan["timeout_seconds"]:
                    states[mid].update(reason="group deadline reached before launch")
                    break
                destination = directory / mid
                destination.mkdir()
                write_json(destination / "plan.json", command)
                logs[mid] = [destination / "stdout.log", destination / "stderr.log"]
                stdout = stack.enter_context(logs[mid][0].open("wb"))
                stderr = stack.enter_context(logs[mid][1].open("wb"))
                state = states[mid]
                state.update(status="launching", launch_intent_at=utc())
                _member_write(destination, state)  # Durable before a possibly successful Popen.
                begins[mid] = time.monotonic()
                try:
                    proc = subprocess.Popen(command["argv"], cwd=command["cwd"], env={**os.environ, **command["env"]},
                                            stdout=stdout, stderr=stderr)
                except OSError as exc:
                    state.update(status="spawn-failed", error=type(exc).__name__ + ": " + str(exc), seconds=time.monotonic() - begins[mid])
                    stderr.write(state["error"].encode("utf-8"))
                    _member_write(destination, state)
                    break  # Do not dispatch remaining nodes after a known spawn failure.
                processes[mid] = proc
                state.update(status="started", local_transport_pid=proc.pid, launched_at=utc())
                write_json(destination / "process.json", {"operation": oid, "member": mid,
                           "pid": proc.pid, "request": request, "created_at": state["launched_at"],
                           "scope": "local transport child only; not remote training PID"})
                _member_write(destination, state)
            # Start all node transports before waiting for any one node. torchrun
            # rendezvous would deadlock if each node were awaited sequentially.
            while processes:
                now = time.monotonic()
                for member in plan["members"]:
                    mid = member["id"]
                    proc = processes.get(mid)
                    if proc is None:
                        continue
                    code = proc.poll()
                    expired = now - started >= plan["timeout_seconds"] or now - begins[mid] >= member["plan"]["timeout_seconds"]
                    if code is None and expired:
                        states[mid]["timed_out"] = True
                        states[mid]["timeout_basis"] = "group" if now - started >= plan["timeout_seconds"] else "member"
                        # Terminate only the Popen child transport we own. This
                        # proves nothing about remote ranks; their outcome stays unknown.
                        proc.kill()
                        code = proc.wait()
                    if code is not None:
                        states[mid].update(status="transport-exited", returncode=code,
                                           seconds=time.monotonic() - begins[mid], finished_at=utc())
                        _member_write(directory / mid, states[mid])
                        del processes[mid]
                if processes:
                    time.sleep(0.02)
        except BaseException as exc:
            interrupted = exc
            for mid, proc in processes.items():
                states[mid].update(status="unknown", reason="controller-interrupted; inspect original local transport and remote ranks")
                _member_write(directory / mid, states[mid])
        finally:
            for mid, state in states.items():
                (directory / mid).mkdir(exist_ok=True)
                _member_write(directory / mid, state)
    all_returned = all(s["status"] == "transport-exited" and not s["timed_out"] for s in states.values())
    good = all_returned and all(s["returncode"] == 0 for s in states.values()) and interrupted is None
    local_failed = all_returned and all(s["backend"] == "local" for s in states.values()) and interrupted is None
    status = "complete" if good else "failed" if local_failed else "unknown"
    evidence = [store.put(path.read_bytes()) for path in sorted(directory.rglob("*.json"))]
    evidence += [store.put(path.read_bytes()) for pair in logs.values() for path in pair]
    result = {"operation": oid, "kind": "distributed-command-group", "request": request, "status": status,
              "context": task["context"], "context_epoch": task["context_epoch"],
              "members": list(states.values()), "seconds": time.monotonic() - started, "evidence": evidence,
              "remote_outcome": "command-returned" if status != "unknown" else "all-members-reconcile-required",
              "validation": "unassessed; transport exit zero is not numerical/performance/checkpoint validation"}
    if interrupted:
        result["controller_error"] = type(interrupted).__name__ + ": " + str(interrupted)
    write_json(directory / "result.json", result)
    with store.db() as db:
        db.execute("UPDATE operations SET status=?,result=? WHERE id=?", (status, json.dumps(result), oid))
        store.event(db, tid, "operation-finished", result)
    if interrupted:
        raise interrupted
    return result


def _intent(db, oid):
    event = db.execute("SELECT payload FROM events WHERE kind='command-group-intent' AND json_extract(payload,'$.operation')=?", (oid,)).fetchone()
    if not event:
        raise FlowError("Operation is not a command group")
    return json.loads(event["payload"])


def group_status(store, oid):
    with store.db() as db:
        intent = _intent(db, oid)
        row = db.execute("SELECT * FROM operations WHERE id=?", (oid,)).fetchone()
    if row["result"]:
        return json.loads(row["result"])
    directory = store.root / "runs" / row["task"] / oid
    states = []
    for member in intent["plan"]["members"]:
        path = directory / member["id"] / "state.json"
        state = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {"id": member["id"], "status": "unknown"}
        states.append(state)
    return {"operation": oid, "status": "unknown", "recorded_status": row["status"], "request": intent["request"],
            "context": intent["context"], "members": states,
            "note": "Controller may still be running or may have crashed; do not infer process outcome from local receipts"}


def reconcile_group(store, oid, receipt):
    with _controller_lock(store, oid):
        return _reconcile_group(store, oid, receipt)


def _reconcile_group(store, oid, receipt):
    if (not isinstance(receipt, dict) or set(receipt) != {"request", "context", "status", "members", "note"}
            or receipt.get("status") not in {"complete", "failed"} or not isinstance(receipt.get("note"), str) or not receipt["note"].strip()
            or not isinstance(receipt.get("members"), list)):
        raise FlowError("Group reconciliation requires request/context/status, every member, and explanation")
    with store.db() as db:
        db.execute("BEGIN IMMEDIATE")
        intent = _intent(db, oid)
        row = db.execute("SELECT * FROM operations WHERE id=?", (oid,)).fetchone()
        if row["status"] not in {"started", "unknown"}:
            raise FlowError("Only an unresolved command group can be reconciled")
        if receipt["request"] != intent["request"] or receipt["context"] != intent["context"]:
            raise FlowError("Group reconciliation request/context differs")
        expected = {m["id"] for m in intent["plan"]["members"]}
        seen = set()
        for member in receipt["members"]:
            if (not isinstance(member, dict) or set(member) != {"id", "outcome", "processes_reconciled", "evidence", "note"}
                    or member["id"] not in expected or member["id"] in seen
                    or member["outcome"] not in {"complete", "failed", "not-started"}
                    or member["processes_reconciled"] is not True
                    or not isinstance(member["note"], str) or not member["note"].strip()
                    or not isinstance(member["evidence"], list) or not member["evidence"]):
                raise FlowError("Each original member needs terminal/no-launch evidence and explicit process reconciliation")
            for sha in member["evidence"]:
                store.artifact(sha)
            seen.add(member["id"])
        if seen != expected:
            raise FlowError("Reconciliation must cover the whole command group")
        if receipt["status"] == "complete" and any(m["outcome"] != "complete" for m in receipt["members"]):
            raise FlowError("Complete group requires every member completed")
        value = json.loads(row["result"] or "{}")
        value.update(operation=oid, kind="distributed-command-group", request=intent["request"], context=intent["context"],
                     context_epoch=intent["context_epoch"], remote_outcome="reconciled-by-evidence",
                     budget_seconds=operation_budget_seconds(db, oid, value, reserve=True),
                     budget_basis="One group wall-clock timeout reservation retained; not multiplied by nodes or leases",
                     status=receipt["status"], reconciliation=receipt)
        db.execute("UPDATE operations SET status=?,result=? WHERE id=?", (value["status"], json.dumps(value), oid))
        store.event(db, row["task"], "command-group-reconciled", value)
        # All resource intents reference this one row, so all clear atomically.
    return value
