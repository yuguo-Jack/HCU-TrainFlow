"""A real local execution with synthetic training evidence, requiring no GPU."""
import json
from pathlib import Path
import sys

from .analysis import analyze_trace, profile_plan
from .core import FlowError, Store, atomic_write, write_json
from .delivery import monitor_report
from .environment import assess_health
from .execution import materialize, run_command, snapshot
from .monitor import import_events, inbox, poll_log
from .quality import compare_loss


def run_demo(destination):
    root = Path(destination).resolve()
    if root.exists():
        raise FlowError("Demo destination must be new")
    store = Store(root / "controller")
    task = store.create({"schema_version": 1, "task_id": "synthetic", "mode": "analyze", "objective": "Exercise orchestration with synthetic evidence", "context": {"model": "synthetic", "source": "fixture-v1", "environment": "local-cpu"}, "permissions": ["execute"], "recovery_owner": "external-demo-owner"})
    ctx = task["context"]
    source = root / "source"
    atomic_write(source / "check.py", "print('local fixture executed; no HCU benchmark')\n")
    snap = snapshot(store, source, ["check.py"])
    materialize(store, snap["snapshot_id"], root / "execution")
    lease = store.lease("demo-local-cpu", "controller")
    execution = run_command(store, "synthetic", "check-v1", {"schema_version": 1, "backend": "local", "argv": [sys.executable, "check.py"], "cwd": str(root / "execution"), "basis": "Bundled CPU-only demonstration", "timeout_seconds": 30}, lease)
    store.release(lease)
    evidence = execution["evidence"]
    health_contract = {"context": ctx, "required": [{"node": "synthetic-node", "device": "0", "check": "fixture", "conditions": {"fixture": True}}]}
    health = assess_health(health_contract, [{"node": "synthetic-node", "device": "0", "check": "fixture", "conditions": {"fixture": True}, "context": ctx, "status": "pass", "executed": 1, "evidence": evidence}])
    trace = {"traceEvents": [{"ph": "X", "cat": "kernel", "name": "fixture_gemm", "ts": 0, "dur": 95, "args": {"rank": rank, "shape": [8, 8, 8], "dtype": "float32", "phase": "forward"}} for rank in (0, 1)]}
    analysis = analyze_trace(trace, {"start_us": 0, "end_us": 100}, {"fixture_gemm": {"kind": "gemm", "m": 8, "n": 8, "k": 8, "peak_flops_s": 20e6, "basis": "Synthetic peak for testing only", "efficiency_target": 0.4}})
    coverage = profile_plan([{"domain": "dp", "ranks": [0, 1]}], [0, 1])
    contract = {"context": ctx, "sample_fingerprint": "synthetic-samples", "aggregation": "fixed-token-mean", "min_steps": 3, "atol": 0.001, "rtol": 0, "tolerance_basis": "Synthetic regression fixture"}
    record = {"context": ctx, "sample_fingerprint": contract["sample_fingerprint"], "aggregation": contract["aggregation"], "executed": 3, "evidence": evidence, "candidate_path_exercised": True, "steps": [1, 2, 3], "loss": [2.0, 1.9, 1.8]}
    quality = compare_loss(contract, record, {**record, "loss": [2.0001, 1.9001, 1.8001]})
    remote = Store(root / "remote-watcher")
    remote.create(task["spec"])
    log = root / "normalized.jsonl"
    samples = [{"attempt_id": "attempt-1", "timestamp": 1000 + step * 10, "step": step, "loss": 2 - step * 0.1, "grad_norm": 1.1, "device_memory_bytes": 1024 + step * 10} for step in range(3)]
    atomic_write(log, "".join(json.dumps(x) + "\n" for x in samples))
    policy = {"stall_seconds": 30, "telemetry_seconds": 45, "recovery_seconds": 60, "min_progress_samples": 2}
    good = poll_log(remote, "synthetic", log, policy, now=1021)
    stalled = poll_log(remote, "synthetic", log, policy, now=1100)
    imported = import_events(store, "demo-remote", remote.events())
    messages = inbox(store)
    for event in messages:
        inbox(store, "claim", event["event_id"], "demo-controller")
        inbox(store, "complete", event["event_id"], "demo-controller")
    monitor_report(store, "synthetic", root / "observations.html")
    report_evidence = store.put(json.dumps({"trace": trace, "analysis": analysis, "rank_coverage": coverage}).encode())
    store.report("synthetic", "analysis", {**analysis, "context": ctx, "evidence": [report_evidence]})
    store.transition("synthetic", "completed")
    result = {"status": "complete", "demo_kind": "Synthetic telemetry and CPU subprocess; no HCU performance or loss claim", "snapshot": snap["snapshot_id"], "command": execution["status"], "health": health["status"], "analysis": analysis["status"], "loss_fixture": quality["status"], "healthy_watch": good["status"], "stalled_watch": stalled["status"], "replayed_events": imported["imported"], "claimed_incidents": len(messages), "report": str(root / "observations.html")}
    write_json(root / "demo-result.json", result)
    return result
