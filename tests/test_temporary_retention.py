"""Temporary-output lifecycle and capacity tests; only disposable local fixtures."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from types import SimpleNamespace

import pytest

from hcu_trainflow.core import FlowError, Store
from hcu_trainflow import retention as r


@pytest.fixture
def temporary(tmp_path):
    store = Store(tmp_path / "workspace")
    store.create({"schema_version": 1, "task_id": "fixture", "mode": "analyze",
                  "objective": "temporary maintenance fixture", "context": {"source": "fixture"}})
    relative = "scratch/disposable/save/failed-001"
    path = store.root / relative
    path.mkdir(parents=True)
    (path / "shard.pt").write_bytes(b"incomplete synthetic checkpoint")
    now = time.time()
    r.register_temporary(store, relative, "temporary-checkpoint", "writer", now=now)
    evidence = store.put(b"Synthetic writer exited; checkpoint invalid; original error retained. No recovery consumer.")
    return store, relative, evidence, now


def retire(fixture):
    store, relative, evidence, now = fixture
    return r.retire_temporary(store, relative, "writer", "Incomplete save after reconciled failure", evidence,
                              producer_stopped=True, now=now)


def test_explicit_retirement_required_even_after_producer_pin_released(temporary):
    store, relative, _, now = temporary
    r.pin_cache(store, relative, "writer", release=True, now=now)
    row = r.plan_retention(store, now=now + 100000)["entries"][0]
    assert row["action"] == "keep" and "not-explicitly-retired" in row["reasons"]
    assert row["tree"] is None


def test_retired_checkpoint_deletes_after_grace_and_keeps_originals(temporary):
    store, relative, evidence, now = temporary
    originals = store.root / "checkpoints/latest-valid"
    originals.mkdir(parents=True); (originals / "shard.pt").write_bytes(b"keep")
    unregistered = store.root / "scratch/disposable/save/unregistered"
    unregistered.mkdir(); (unregistered / "shard.pt").write_bytes(b"keep")
    retire(temporary)
    assert r.plan_retention(store, now=now + 1800)["entries"][0]["action"] == "keep"
    plan = r.plan_retention(store, now=now + 3601)
    assert plan["entries"][0]["action"] == "remove"
    assert "metadata-only" in plan["entries"][0]["scan"]
    assert (store.root / relative).exists()  # plan remains dry-run
    receipt = r.apply_retention(store, plan, plan["plan_hash"], enabled=True, now=now + 3601)
    assert receipt["status"] == "complete" and receipt["removed_logical_bytes"] > 0
    assert not (store.root / relative).exists()
    assert (originals / "shard.pt").read_bytes() == b"keep"
    assert (unregistered / "shard.pt").read_bytes() == b"keep" and store.artifact(evidence)


@pytest.mark.parametrize("mutation", ["owner", "running", "empty-reason", "unknown-evidence", "empty-evidence", "reader"])
def test_retirement_requires_owner_closure_and_evidence(temporary, mutation):
    store, relative, evidence, now = temporary
    owner = "writer"; stopped = True; reason = "Discard unused failed save"
    if mutation == "owner": owner = "someone-else"
    if mutation == "running": stopped = False
    if mutation == "empty-reason": reason = " "
    if mutation == "unknown-evidence": evidence = "0" * 64
    if mutation == "empty-evidence": evidence = store.put(b"")
    if mutation == "reader": r.pin_cache(store, relative, "reader", now=now)
    with pytest.raises(FlowError):
        r.retire_temporary(store, relative, owner, reason, evidence, producer_stopped=stopped, now=now)
    assert r.plan_retention(store, now=now + 100000)["entries"][0]["action"] == "keep"


@pytest.mark.parametrize("relative", ["../outside", "checkpoints/old/a/b", "cache/recreatable/save/g0",
                                      "scratch/disposable/../save/g0", "scratch/disposable/save"])
def test_temporary_cannot_adopt_normal_checkpoint_or_other_roots(temporary, relative):
    with pytest.raises(FlowError):
        r.register_temporary(temporary[0], relative, "temporary-checkpoint", "writer")


@pytest.mark.parametrize("mutation", ["file", "late-pin", "operation", "lease", "evidence"])
def test_recheck_prevents_deletion_after_change(temporary, mutation):
    store, relative, evidence, now = temporary
    retire(temporary)
    plan = r.plan_retention(store, now=now + 3601)
    if mutation == "file": (store.root / relative / "shard.pt").write_bytes(b"new output")
    if mutation == "late-pin": r.pin_cache(store, relative, "recovery", now=now + 3601)
    if mutation == "operation":
        with store.db() as db:
            db.execute("INSERT INTO operations VALUES('operation','fixture','hash','unknown',NULL,'fixture')")
    if mutation == "lease":
        with store.db() as db: db.execute("INSERT INTO leases VALUES('gpu','operator',1,?)", (now + 7200,))
    if mutation == "evidence": (store.root / "objects" / evidence[:2] / evidence).unlink()
    with pytest.raises((FlowError, OSError)):
        r.apply_retention(store, plan, plan["plan_hash"], enabled=True, now=now + 3601)
    assert (store.root / relative).exists()


def test_changed_retired_output_does_not_become_eligible_by_waiting(temporary):
    store, relative, _, now = temporary
    retire(temporary)
    (store.root / relative / "shard.pt").write_bytes(b"unexpected writer")
    row = r.plan_retention(store, now=now + 100000)["entries"][0]
    assert row["action"] == "keep" and "changed-after-retirement" in row["reasons"]


def test_retirement_refuses_replaced_generation(temporary):
    store, relative, _, _ = temporary
    path = store.root / relative
    path.rename(path.with_name("retained-old")); path.mkdir()
    with pytest.raises(FlowError, match="root changed"):
        retire(temporary)


@pytest.mark.parametrize("protected", ["state.sqlite3", ".git", "evidence", "attempt.json"])
def test_checkpoint_exception_does_not_allow_evidence_or_database_deletion(temporary, protected):
    store, relative, _, _ = temporary
    (store.root / relative / protected).write_bytes(b"retain")
    with pytest.raises(FlowError, match="Protected"):
        retire(temporary)


def test_noncheckpoint_temporary_kind_cannot_discard_weights(temporary):
    store, _, evidence, now = temporary
    relative = "scratch/disposable/debug/g0"
    path = store.root / relative; path.mkdir(parents=True)
    (path / "model.pt").write_bytes(b"weights")
    r.register_temporary(store, relative, "debug-output", "debugger", now=now)
    with pytest.raises(FlowError, match="Protected"):
        r.retire_temporary(store, relative, "debugger", "no longer used", evidence,
                           producer_stopped=True, now=now)


def test_retired_large_file_uses_metadata_not_payload_reads(tmp_path, monkeypatch):
    path = tmp_path / "large"; path.mkdir(); file = path / "core.dump"; file.write_bytes(b"fixture")
    real_stat = Path.lstat
    def fake_size(self, *args, **kwargs):
        info = real_stat(self, *args, **kwargs)
        if self == file:
            fields = {k: getattr(info, k) for k in dir(info) if k.startswith("st_")}
            fields["st_size"] = 64 * 1024**3
            return SimpleNamespace(**fields)
        return info
    monkeypatch.setattr(Path, "lstat", fake_size)
    monkeypatch.setattr(r.os, "open", lambda *a, **kw: pytest.fail("No large payload reads"))
    tree = r._tree(path, metadata_only=True)
    assert tree["bytes"] == 64 * 1024**3
    assert all("sha256" not in row for row in tree["rows"])


def test_checkpoint_hardlink_refused(temporary, tmp_path):
    store, relative, _, _ = temporary
    other = tmp_path / "valid.pt"; other.write_bytes(b"keep")
    os.link(other, store.root / relative / "shared.pt")
    with pytest.raises(FlowError, match="Hardlinked"):
        retire(temporary)
    assert other.read_bytes() == b"keep"


def test_interrupted_temporary_delete_retains_receipt_and_evidence(temporary, monkeypatch):
    store, relative, evidence, now = temporary
    retire(temporary); plan = r.plan_retention(store, now=now + 3601)
    def fail(path): raise OSError("synthetic busy file")
    monkeypatch.setattr(r.shutil, "rmtree", fail)
    with pytest.raises(OSError, match="synthetic"):
        r.apply_retention(store, plan, plan["plan_hash"], enabled=True, now=now + 3601)
    receipt = json.loads((store.root / ".maintenance/receipts" / (plan["plan_hash"] + ".json")).read_text())
    assert receipt["status"] == "attention" and receipt["results"][0]["status"] == "quarantined"
    assert (store.root / receipt["results"][0]["quarantine"] / "shard.pt").exists()
    assert store.artifact(evidence)


def test_capacity_has_no_tree_scan_and_reports_pressure(temporary, monkeypatch):
    store = temporary[0]
    monkeypatch.setattr(r.shutil, "disk_usage", lambda p: SimpleNamespace(total=1000, used=950, free=50))
    monkeypatch.setattr(r, "_tree", lambda *a, **kw: pytest.fail("capacity must not scan"))
    result = r.capacity_status(store, min_free_bytes=0, min_free_percent=10)
    assert result["status"] == "low-space" and result["required_free_bytes"] == 100
    assert result["quota_checked"] is False
    assert r.capacity_status(store, min_free_bytes=50, min_free_percent=0)["status"] == "ok"


@pytest.mark.parametrize("kwargs", [{"min_free_bytes": -1}, {"min_free_percent": 101},
                                    {"min_free_bytes": float("nan")}, {"min_free_percent": True}])
def test_invalid_capacity_policy_rejected(temporary, kwargs):
    with pytest.raises(FlowError): r.capacity_status(temporary[0], **kwargs)


def test_cli_capacity_pressure_returns_two(temporary):
    store = temporary[0]
    script = Path(__file__).parents[1] / "scripts/maintain_workspace.py"
    result = subprocess.run([sys.executable, "-B", str(script), "--workspace", str(store.root),
                             "--min-free-gib", "1000000000", "capacity"], capture_output=True, text=True)
    assert result.returncode == 2, result.stderr
    assert json.loads(result.stdout)["results"][0]["status"] == "low-space"


def test_cli_retirement_and_tick_are_separate(temporary):
    store, relative, evidence, _ = temporary
    script = Path(__file__).parents[1] / "scripts/maintain_workspace.py"
    base = [sys.executable, "-B", str(script), "--workspace", str(store.root)]
    result = subprocess.run(base + ["retire", relative, "--owner", "writer", "--reason", "failed save",
                                     "--evidence", evidence, "--producer-stopped"], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["results"][0]["lifecycle"] == "retired"
    result = subprocess.run(base + ["--min-free-gib", "0", "--min-free-percent", "0", "tick", "--enable-delete"],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    row = json.loads(result.stdout)["results"][0]["entries"][0]
    assert row["action"] == "keep" and "younger-than-minimum-age" in row["reasons"]
    assert (store.root / relative).exists()


def test_periodic_tick_skips_scan_for_six_hours_and_milestones_have_floor(temporary, monkeypatch):
    store, _, _, now = temporary
    options = {"capacity_options": {"min_free_bytes": 0, "min_free_percent": 0}}
    first = r.maintenance_tick(store, now=now, **options)
    assert first["status"] == "dry-run"
    original = r.sweep_workspace
    monkeypatch.setattr(r, "sweep_workspace", lambda *a, **kw: pytest.fail("Repeated sweep during cooldown"))
    assert r.maintenance_tick(store, now=now + 5 * 3600, **options)["status"] == "not-due"
    assert r.maintenance_tick(store, trigger="experiment-batch", now=now + 300, **options)["status"] == "not-due"
    monkeypatch.setattr(r, "sweep_workspace", original)
    assert r.maintenance_tick(store, trigger="stage-transition", now=now + 3600, **options)["status"] == "dry-run"
    assert r.maintenance_tick(store, now=now + 7 * 3600, **options)["status"] == "dry-run"


def test_incomplete_tick_needs_reconciliation_not_automatic_retry(temporary, monkeypatch):
    store, _, _, now = temporary
    options = {"capacity_options": {"min_free_bytes": 0, "min_free_percent": 0}}
    original = r.sweep_workspace
    def failed(*a, **kw): raise OSError("fixture interruption")
    monkeypatch.setattr(r, "sweep_workspace", failed)
    with pytest.raises(OSError): r.maintenance_tick(store, now=now, **options)
    monkeypatch.setattr(r, "sweep_workspace", original)
    with pytest.raises(FlowError, match="Previous maintenance incomplete"):
        r.maintenance_tick(store, now=now + 10 * 3600, **options)
    assert r.maintenance_tick(store, resume_after_review=True, now=now + 10 * 3600, **options)["status"] == "dry-run"


def test_low_space_can_advance_periodic_sweep_but_not_spam_scans(temporary, monkeypatch):
    store, _, _, now = temporary
    monkeypatch.setattr(r.shutil, "disk_usage", lambda p: SimpleNamespace(total=1000, used=990, free=10))
    options = {"capacity_options": {"min_free_bytes": 100, "min_free_percent": 0}}
    r.maintenance_tick(store, now=now, **options)
    assert r.maintenance_tick(store, now=now + 300, **options)["status"] == "not-due"
    result = r.maintenance_tick(store, now=now + 3600, **options)
    assert result["status"] == "dry-run" and result["trigger"] == "space-pressure"


def test_temporary_age_floor_and_schedule_clock(temporary):
    store, _, _, now = temporary
    with pytest.raises(FlowError): r.plan_retention(store, temporary_min_age_seconds=-1)
    with pytest.raises(FlowError): r.maintenance_tick(store, scan_interval_seconds=300)
    r.maintenance_tick(store, now=now)
    with pytest.raises(FlowError, match="clock moved backwards"):
        r.maintenance_tick(store, now=now - 1)


def test_oversized_retirement_record_is_rejected_without_reading_payload(temporary, monkeypatch):
    store, relative, _, now = temporary
    record = store.put(b"x" * (1024**2 + 1))
    monkeypatch.setattr(store, "artifact", lambda *a: pytest.fail("Do not read oversized record"))
    with pytest.raises(FlowError, match="<=1 MiB"):
        r.retire_temporary(store, relative, "writer", "failed save", record, producer_stopped=True, now=now)


def test_string_false_cannot_enable_automatic_deletion(temporary):
    with pytest.raises(FlowError, match="boolean"):
        r.sweep_workspace(temporary[0], enabled="false")
    with pytest.raises(FlowError, match="boolean"):
        r.maintenance_tick(temporary[0], resume_after_review="false")


def test_explicit_reretirement_preserves_history_and_restarts_grace(temporary):
    store, relative, evidence, now = temporary
    retire(temporary)
    (store.root / relative / "shard.pt").write_bytes(b"previous reader changed output; now reconciled")
    entry = r.retire_temporary(store, relative, "writer", "Rechecked writer closure after modification", evidence,
                               producer_stopped=True, now=now + 4000)
    assert len(entry["retirement_history"]) == 1
    assert entry["retirement_history"][0]["retired_at"] == now
    assert r.plan_retention(store, now=now + 4001)["entries"][0]["action"] == "keep"
    assert r.plan_retention(store, now=now + 8000)["entries"][0]["action"] == "remove"


def test_task_close_can_explicitly_set_zero_grace_without_bypassing_lifecycle(temporary):
    store, relative, _, now = temporary
    assert r.plan_retention(store, temporary_min_age_seconds=0, now=now)["entries"][0]["action"] == "keep"
    retire(temporary)
    result = r.maintenance_tick(store, trigger="task-close", enabled=True, now=now + 1,
        plan_options={"temporary_min_age_seconds": 0},
        capacity_options={"min_free_bytes": 0, "min_free_percent": 0})
    assert result["status"] == "complete" and not (store.root / relative).exists()
