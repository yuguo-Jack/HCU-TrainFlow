"""Actual local concurrency and failure tests; no remote connection or GPU use."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import time

import pytest

from hcu_trainflow.core import FlowError, Store
from hcu_trainflow import command_group as groups
from hcu_trainflow.coordination import reconcile_operation
from hcu_trainflow.execution import command_plan, run_command


@pytest.fixture
def store(tmp_path):
    result = Store(tmp_path / "store")
    result.create({"schema_version": 1, "task_id": "t", "mode": "optimize", "objective": "local distributed group fixture",
                   "permissions": ["execute"], "context": {"source": "synthetic, no remote launch"},
                   "budget": {"max_operations": 100, "max_seconds": 600}})
    return result


def card(tmp_path, programs=None, timeout=10):
    programs = programs or ["print('a')", "print('b')"]
    return {"schema_version": 1, "basis": "local fixture for one distributed job", "timeout_seconds": timeout,
            "shared_resources": ["network-domain"], "members": [
                {"id": "rank-" + str(i), "node": "node-" + str(i), "resources": ["gpu-domain-" + str(i)],
                 "card": {"schema_version": 1, "backend": "local", "argv": [sys.executable, "-c", program],
                          "cwd": str(tmp_path), "timeout_seconds": timeout, "basis": "local rank fixture"}}
                for i, program in enumerate(programs)]}


def leases(store, spec):
    return [store.lease(resource, "coordinator", ttl=30) for resource in groups.group_plan(spec)["resources"]]


def reconciliation(store, result):
    proof = store.put(b"synthetic explicit process/job reconciliation proof")
    return {"request": result["request"], "context": result["context"], "status": "failed", "note": "every fixture process checked",
            "members": [{"id": m["id"], "outcome": "failed", "processes_reconciled": True,
                         "evidence": [proof], "note": "fixture ended; no residual process"} for m in result["members"]]}


def local_remote_transport(monkeypatch):
    def plan(value):
        result = command_plan(value)
        result.update(argv=value["argv"], cwd=value["cwd"], env=value.get("env", {}))
        return result
    monkeypatch.setattr(groups, "command_plan", plan)


def test_two_actual_children_rendezvous_concurrently_and_replay_once(store, tmp_path):
    # A sequential wait would time out: each child must see the other start.
    program = "import pathlib,time; p=pathlib.Path({name!r}); p.write_text('ready'); deadline=time.monotonic()+5\nwhile not pathlib.Path({other!r}).exists():\n assert time.monotonic()<deadline, 'peer was not launched concurrently'\n time.sleep(.01)\nwith p.open('a') as f: f.write('-finished')\n"
    spec = card(tmp_path, [program.format(name="r0", other="r1"), program.format(name="r1", other="r0")])
    held = leases(store, spec)
    result = groups.run_group(store, "t", "group", spec, held)
    assert result["status"] == "complete"
    assert all(x["returncode"] == 0 for x in result["members"])
    assert groups.run_group(store, "t", "group", spec, held) == result
    assert (tmp_path / "r0").read_text() == "ready-finished"
    with store.db() as db:
        assert db.execute("SELECT count(*) FROM operations").fetchone()[0] == 1
        assert db.execute("SELECT count(*) FROM events WHERE kind='operation-started'").fetchone()[0] == 3
    for name in ("rank-0", "rank-1"):
        path = store.root / "runs/t/group" / name
        assert (path / "process.json").exists() and (path / "state.json").exists()


@pytest.mark.parametrize("mutation", ["duplicate-id", "case-collision", "device-name", "trailing-dot", "duplicate-node", "shared-member", "duplicate-gpu", "missing-shared", "member-timeout", "unknown-field"])
def test_invalid_group_contracts(tmp_path, mutation):
    spec = card(tmp_path)
    if mutation == "duplicate-id": spec["members"][1]["id"] = spec["members"][0]["id"]
    elif mutation == "case-collision": spec["members"][1]["id"] = spec["members"][0]["id"].upper()
    elif mutation == "device-name": spec["members"][0]["id"] = "CON"
    elif mutation == "trailing-dot": spec["members"][0]["id"] = "node."
    elif mutation == "duplicate-node": spec["members"][1]["node"] = spec["members"][0]["node"]
    elif mutation == "shared-member": spec["members"][0]["resources"] = spec["shared_resources"]
    elif mutation == "duplicate-gpu": spec["members"][1]["resources"] = spec["members"][0]["resources"]
    elif mutation == "missing-shared": spec["shared_resources"] = []
    elif mutation == "member-timeout": spec["members"][0]["card"]["timeout_seconds"] = 11
    else: spec["parallel_anything"] = True
    with pytest.raises(FlowError): groups.group_plan(spec)


def test_ssh_docker_and_other_backends_use_existing_quoting(tmp_path):
    spec = card(tmp_path)
    one = spec["members"][0]["card"]
    one.update(backend="ssh-docker", ssh_target="node-a", container="task", cwd="/work/it's task",
               argv=["python", "file name.py", "$(do-not-execute)", ""], ssh_jump={"mode": "exec", "target": "jump"})
    two = spec["members"][1]["card"]
    two.update(backend="k8s", namespace="ns", pod="pod-b", container="train", cwd="/work")
    plan = groups.group_plan(spec)
    assert plan["members"][0]["plan"] == command_plan(one)
    assert plan["members"][1]["plan"] == command_plan(two)


def test_plan_is_frozen_from_mutable_python_input(tmp_path):
    spec = card(tmp_path)
    plan = groups.group_plan(spec)
    spec["members"][0]["card"]["argv"][0] = "wrong-executable"
    spec["shared_resources"].append("new-resource")
    assert plan["members"][0]["plan"]["argv"][0] == sys.executable
    assert plan["shared_resources"] == ["network-domain"]


@pytest.mark.parametrize("fault", ["stale", "missing", "extra", "different-owner"])
def test_all_leases_are_validated_before_any_launch(store, tmp_path, monkeypatch, fault):
    spec = card(tmp_path)
    held = leases(store, spec)
    if fault == "stale": held[-1]["token"] += 1
    elif fault == "missing": held.pop()
    elif fault == "extra": held.append(store.lease("unneeded", "coordinator"))
    else: held[-1]["owner"] = "fake-agent"
    monkeypatch.setattr(groups.subprocess, "Popen", lambda *a, **k: pytest.fail("must not launch before all leases pass"))
    with pytest.raises(FlowError): groups.run_group(store, "t", "group", spec, held)
    with store.db() as db:
        assert db.execute("SELECT count(*) FROM operations").fetchone()[0] == 0


def test_remote_failure_holds_all_resources_until_whole_group_reconciliation(store, tmp_path, monkeypatch):
    # An authorized local bridge must still respect the group's resource locks.
    with store.db() as db:
        task = store.task("t")["spec"]
        task["permissions"].append("agent-dispatch")
        db.execute("UPDATE tasks SET spec=? WHERE id='t'", (json.dumps(task),))
    spec = card(tmp_path, ["raise SystemExit(7)", "print('peer exited')"])
    for member in spec["members"]:
        member["card"].update(backend="ssh", ssh_target=member["node"])
    local_remote_transport(monkeypatch)
    held = leases(store, spec)
    result = groups.run_group(store, "t", "group", spec, held)
    assert result["status"] == "unknown" and sorted(x["returncode"] for x in result["members"]) == [0, 7]
    with pytest.raises(FlowError, match="unknown"):
        groups.run_group(store, "t", "group", spec, held)
    with pytest.raises(FlowError, match="covering every"):
        reconcile_operation(store, "group", "failed", [store.put(b"only one rank checked")], "insufficient old API")
    receipt = reconciliation(store, result)
    partial = deepcopy(receipt); partial["members"].pop()
    with pytest.raises(FlowError, match="whole command group"):
        groups.reconcile_group(store, "group", partial)
    for lease in held:
        with pytest.raises(FlowError, match="unresolved"):
            run_command(store, "t", "bypass-" + lease["resource"], card(tmp_path)["members"][0]["card"], lease, control_plane=True)
        store.release(lease)
        with pytest.raises(FlowError, match="unresolved"):
            store.lease(lease["resource"], "new-owner")
    final = groups.reconcile_group(store, "group", receipt)
    assert final["status"] == "failed" and final["budget_seconds"] >= 10
    assert final["remote_outcome"] == "reconciled-by-evidence"
    for lease in held:
        assert store.lease(lease["resource"], "new-owner")["token"] == 2


def test_partial_spawn_never_launches_remaining_nodes(store, tmp_path):
    spec = card(tmp_path, ["print('started')", "unused", "raise SystemExit('should not launch')"])
    spec["members"][1]["card"]["argv"] = [str(tmp_path / "nonexistent-executable")]
    result = groups.run_group(store, "t", "partial", spec, leases(store, spec))
    assert result["status"] == "unknown"
    assert [m["status"] for m in result["members"]] == ["transport-exited", "spawn-failed", "not-started"]
    assert (store.root / "runs/t/partial/rank-1/stderr.log").read_text(encoding="utf8")
    assert not (store.root / "runs/t/partial/rank-2/process.json").exists()


def test_group_budget_is_one_operation_and_wall_time_reservation(store, tmp_path):
    spec = card(tmp_path, ["import time;time.sleep(1)", "import time;time.sleep(1)"], timeout=.1)
    with store.db() as db:
        task = store.task("t")["spec"]
        task["budget"] = {"max_operations": 2, "max_seconds": .19}
        db.execute("UPDATE tasks SET spec=? WHERE id='t'", (json.dumps(task),))
    held = leases(store, spec)
    result = groups.run_group(store, "t", "reserved", spec, held)
    groups.reconcile_group(store, "reserved", reconciliation(store, result))
    with pytest.raises(FlowError, match="remaining execution budget"):
        groups.run_group(store, "t", "overspend", spec, held)
    with store.db() as db:
        assert db.execute("SELECT count(*) FROM operations").fetchone()[0] == 1


def test_different_task_cannot_bypass_any_group_resource(store, tmp_path):
    spec = card(tmp_path, ["import time;time.sleep(1)", "import time;time.sleep(1)"], timeout=.1)
    held = leases(store, spec)
    groups.run_group(store, "t", "pending", spec, held)
    store.create({"schema_version": 1, "task_id": "other", "mode": "analyze", "objective": "other fixture",
                  "context": {"other": True}, "permissions": ["execute"]})
    for lease in held:
        with pytest.raises(FlowError, match="unresolved"):
            run_command(store, "other", "bypass-" + lease["resource"], card(tmp_path)["members"][0]["card"], lease)
    with pytest.raises(FlowError, match="unresolved"):
        groups.run_group(store, "other", "bypass-group", spec, held)


def test_assignment_must_reserve_entire_group_including_network(store, tmp_path):
    from hcu_trainflow import team
    spec = card(tmp_path)
    resources = groups.group_plan(spec)["resources"]
    assignment = {"id": "worker", "owner": "coordinator", "goal": "one distributed experiment", "scope": "local fixture",
                  "allowed_paths": ["."], "acceptance": "retain both members", "mode": "read", "resources": resources,
                  "budget": {"max_operations": 1, "max_seconds": 15}, "context": store.task("t")["context"]}
    team.plan(store, "t", {"rationale": "single job fixture", "max_parallel": 1, "assignments": [assignment]})
    claim = team.claim(store, "worker", "coordinator")
    held = leases(store, spec)
    with pytest.raises(FlowError, match="reserved"):
        groups.run_group(store, "t", "unassigned", spec, held)
    with pytest.raises(FlowError):
        groups.run_group(store, "t", "wrong-token", spec, held, assignment="worker", owner="coordinator", token=claim["token"] + 1)
    result = groups.run_group(store, "t", "assigned", spec, held, assignment="worker", owner="coordinator", token=claim["token"])
    assert result["status"] == "complete"
    with pytest.raises(FlowError, match="budget"):
        groups.run_group(store, "t", "extra", spec, held, assignment="worker", owner="coordinator", token=claim["token"])


def test_context_reset_cannot_reuse_old_group_or_race_atomic_admission(store, tmp_path, monkeypatch):
    spec = card(tmp_path)
    held = leases(store, spec)
    groups.run_group(store, "t", "group", spec, held)
    original_context = store.task("t")["spec"]["context"]
    store.change_context("t", {"other": "fixture"})
    store.change_context("t", original_context)
    with pytest.raises(FlowError, match="different request"):
        groups.run_group(store, "t", "group", spec, held)
    original = groups.group_plan
    def change(value):
        result = original(value)
        store.change_context("t", {"raced": True})
        return result
    monkeypatch.setattr(groups, "group_plan", change)
    with pytest.raises(FlowError, match="context/state changed"):
        groups.run_group(store, "t", "race", spec, held)


def test_member_timeout_and_group_timeout_are_distinct(store, tmp_path):
    spec = card(tmp_path, ["import time;time.sleep(5)", "import time;time.sleep(5)"], timeout=0.3)
    spec["members"][0]["card"]["timeout_seconds"] = 0.1
    result = groups.run_group(store, "t", "timeout", spec, leases(store, spec))
    assert result["status"] == "unknown"
    assert [m["timeout_basis"] for m in result["members"]] == ["member", "group"]
    assert all(m["timed_out"] for m in result["members"])


def test_keyboard_interrupt_retains_unknown_and_does_not_relaunch(store, tmp_path, monkeypatch):
    spec = card(tmp_path, ["import time;time.sleep(.2)", "import time;time.sleep(.2)"])
    original = subprocess.Popen
    children = []
    def spawn(*args, **kwargs):
        proc = original(*args, **kwargs)
        children.append(proc)
        return type("Interrupted", (), {"pid": proc.pid, "poll": lambda self: (_ for _ in ()).throw(KeyboardInterrupt())})()
    monkeypatch.setattr(groups.subprocess, "Popen", spawn)
    held = leases(store, spec)
    with pytest.raises(KeyboardInterrupt): groups.run_group(store, "t", "interrupt", spec, held)
    for proc in children: proc.wait(timeout=5)
    result = groups.group_status(store, "interrupt")
    assert result["status"] == "unknown" and result["controller_error"].startswith("KeyboardInterrupt")
    with pytest.raises(FlowError): groups.run_group(store, "t", "interrupt-again", spec, held)


def test_hard_controller_crash_keeps_group_intent_and_resource_guards(store, tmp_path):
    spec = card(tmp_path, ["import time;time.sleep(1.5)", "import time;time.sleep(1.5)"])
    held = leases(store, spec)
    source = ("import json\nfrom hcu_trainflow.core import Store\nfrom hcu_trainflow.command_group import run_group\n"
              + "run_group(Store(" + repr(str(store.root)) + "),'t','crash',json.loads(" + repr(json.dumps(spec)) + "),json.loads(" + repr(json.dumps(held)) + "))")
    controller = subprocess.Popen([sys.executable, "-B", "-c", source], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        deadline = time.monotonic() + 5
        while not (store.root / "runs/t/crash/rank-1/process.json").exists():
            assert time.monotonic() < deadline and controller.poll() is None
            time.sleep(.02)
        with pytest.raises(FlowError, match="controller is active"):
            groups.reconcile_group(store, "crash", {})
        with pytest.raises(FlowError, match="controller is active"):
            groups.run_group(store, "t", "crash", spec, held)
        controller.kill(); controller.wait(timeout=5)
        result = groups.group_status(store, "crash")
        assert result["status"] == "unknown" and result["recorded_status"] == "started"
        assert len(result["members"]) == 2
        with pytest.raises(FlowError): groups.run_group(store, "t", "new-crash", spec, held)
        assert all((store.root / "runs/t/crash" / member["id"] / "stdout.log").exists() for member in spec["members"])
    finally:
        if controller.poll() is None: controller.kill(); controller.wait(timeout=5)
    time.sleep(1.6)  # Actual local fixture children end naturally; no remote signaling.


@pytest.mark.parametrize("fault", ["duplicate", "wrong-context", "wrong-request", "no-process-proof", "missing-evidence", "false-complete"])
def test_reconciliation_rejects_incomplete_or_unbound_claims(store, tmp_path, fault):
    spec = card(tmp_path, ["import time;time.sleep(1)", "import time;time.sleep(1)"], timeout=.1)
    result = groups.run_group(store, "t", "unresolved", spec, leases(store, spec))
    receipt = reconciliation(store, result)
    if fault == "duplicate": receipt["members"][1] = deepcopy(receipt["members"][0])
    elif fault == "wrong-context": receipt["context"] = "different"
    elif fault == "wrong-request": receipt["request"] = "different"
    elif fault == "no-process-proof": receipt["members"][0]["processes_reconciled"] = False
    elif fault == "missing-evidence": receipt["members"][0]["evidence"] = []
    else: receipt["status"] = "complete"
    with pytest.raises(FlowError): groups.reconcile_group(store, "unresolved", receipt)
    assert groups.group_status(store, "unresolved")["status"] == "unknown"
