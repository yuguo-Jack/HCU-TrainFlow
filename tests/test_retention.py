"""Real local temporary-directory deletion tests; no site/campaign data touched."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time

import pytest

from hcu_trainflow.core import FlowError, Store, fingerprint
from hcu_trainflow import retention as r


@pytest.fixture
def cache(tmp_path):
    store = Store(tmp_path / "workspace")
    base = time.time()
    store.create({"schema_version": 1, "task_id": "fixture", "mode": "analyze", "objective": "synthetic local retention",
                  "context": {"source": "fixture"}})
    for i in range(5):
        name = f"cache/recreatable/build/g{i}"
        path = store.root / name
        path.mkdir(parents=True)
        (path / "payload.bin").write_bytes(bytes([i]) * 17)
        r.register_cache(store, name, "Rebuild from fixed synthetic source fixture", now=base + i)
    return store, base + 10 * 86400


def test_default_dry_run_keeps_latest_three_and_unregistered(cache):
    store, now = cache
    extra = store.root / "cache/recreatable/build/unregistered"
    extra.mkdir(); (extra / "keep").write_text("not registered")
    plan = r.plan_retention(store, now=now)
    assert [x["path"].split("/")[-1] for x in plan["entries"] if x["action"] == "remove"] == ["g0", "g1"]
    assert all((store.root / x["path"]).is_dir() for x in plan["entries"])
    with pytest.raises(FlowError, match="opt-in"):
        r.apply_retention(store, plan, plan["plan_hash"], now=now)
    receipt = r.apply_retention(store, plan, plan["plan_hash"], enabled=True, now=now)
    assert receipt["status"] == "complete" and len(receipt["results"]) == 2
    assert not (store.root / "cache/recreatable/build/g0").exists()
    assert (store.root / "cache/recreatable/build/g4").exists() and (extra / "keep").exists()
    with pytest.raises(FlowError, match="already attempted"):
        r.apply_retention(store, plan, plan["plan_hash"], enabled=True, now=now)


@pytest.mark.parametrize("path", ["../outside", "/tmp/cache", "D:/temp/cache", "cache/recreatable/../evidence", "cache\\recreatable\\f\\g",
    "evidence/f/g", "objects/a/b", "checkouts/project/gen", "runtime/checkpoints/old", "cache/recreatable/build"])
def test_lexical_escapes_and_protected_roots_rejected(cache, path):
    with pytest.raises(FlowError): r.register_cache(cache[0], path, "rebuild")


@pytest.mark.parametrize("protected", ["state.sqlite3", "state.sqlite3-wal", "model.pt", "weights.safetensors", "trainflow-snapshot.json", "attempt.json", ".git"])
def test_protected_content_rejected(cache, protected):
    store, now = cache
    path = store.root / "cache/recreatable/new/g0"; path.mkdir(parents=True)
    (path / protected).write_text("must retain")
    with pytest.raises(FlowError, match="Protected"):
        r.register_cache(store, "cache/recreatable/new/g0", "rebuild", now=now)
    assert (path / protected).read_text() == "must retain"


def test_use_pin_and_recent_use_preserved(cache):
    store, now = cache; relative = "cache/recreatable/build/g0"
    r.pin_cache(store, relative, "reader", now=now)
    plan = r.plan_retention(store, now=now)
    row = next(x for x in plan["entries"] if x["path"] == relative)
    assert row["action"] == "keep" and "explicit-use-pins" in row["reasons"]
    r.pin_cache(store, relative, "reader", release=True, now=now)
    plan = r.plan_retention(store, now=now)
    assert next(x for x in plan["entries"] if x["path"] == relative)["action"] == "keep"


@pytest.mark.parametrize("status", ["started", "unknown", "unexpected-state"])
def test_unresolved_operation_pins_entire_workspace(cache, status):
    store, now = cache
    with store.db() as db:
        db.execute("INSERT INTO operations VALUES('operation','fixture','hash',?,NULL,'synthetic')", (status,))
    plan = r.plan_retention(store, now=now)
    assert all(x["action"] == "keep" for x in plan["entries"])
    with pytest.raises(FlowError, match="Active/unknown"):
        r.apply_retention(store, plan, plan["plan_hash"], enabled=True, now=now)


def test_operation_started_after_plan_is_not_deleted(cache):
    store, now = cache; plan = r.plan_retention(store, now=now)
    with store.db() as db:
        db.execute("INSERT INTO operations VALUES('operation','fixture','hash','unknown',NULL,'synthetic')")
    with pytest.raises(FlowError, match="Active/unknown"):
        r.apply_retention(store, plan, plan["plan_hash"], enabled=True, now=now)
    assert (store.root / "cache/recreatable/build/g0").exists()


def test_active_workspace_dry_run_does_not_read_cache_contents(cache, monkeypatch):
    store, now = cache
    with store.db() as db:
        db.execute("INSERT INTO operations VALUES('operation','fixture','hash','started',NULL,'synthetic')")
    monkeypatch.setattr(r, "_tree", lambda *a, **k: pytest.fail("Busy-cache dry-run must not deep scan"))
    plan = r.plan_retention(store, now=now)
    assert all(row["tree"] is None and row["action"] == "keep" for row in plan["entries"])


def test_only_deletion_candidates_are_deep_scanned(cache, monkeypatch):
    store, now = cache; original = r._tree; seen = []
    def scan(path, **kwargs):
        seen.append(path.name)
        return original(path, **kwargs)
    monkeypatch.setattr(r, "_tree", scan)
    plan = r.plan_retention(store, now=now)
    assert seen == ["g0", "g1"]
    assert all(row["tree"] is None for row in plan["entries"] if row["action"] == "keep")
    r.apply_retention(store, plan, plan["plan_hash"], enabled=True, now=now)
    assert not {"g2", "g3", "g4"} & set(seen)


def test_live_resource_lease_protects_even_without_operation(cache):
    store, now = cache
    with store.db() as db: db.execute("INSERT INTO leases VALUES('gpu','operator',1,?)", (now + 500,))
    plan = r.plan_retention(store, now=now)
    assert all("workspace-active-or-unresolved" in x["reasons"] for x in plan["entries"])


def test_source_reference_pins_generation(cache):
    store, now = cache; relative = "cache/recreatable/build/g0"
    store.create({"schema_version": 1, "task_id": "source-owner", "mode": "analyze", "objective": "source identity",
                  "context": {"source": str(store.root / relative)}})
    row = next(x for x in r.plan_retention(store, now=now)["entries"] if x["path"] == relative)
    assert row["action"] == "keep" and "task-source-reference:source-owner" in row["reasons"]


def test_source_reference_created_after_plan_protects(cache):
    store, now = cache; relative = "cache/recreatable/build/g0"
    plan = r.plan_retention(store, now=now)
    store.create({"schema_version": 1, "task_id": "new-owner", "mode": "analyze", "objective": "new source ref",
                  "context": {"source": str(store.root / relative)}})
    with pytest.raises(FlowError, match="source reference"):
        r.apply_retention(store, plan, plan["plan_hash"], enabled=True, now=now)
    assert (store.root / relative).is_dir()


def test_identical_bytes_replaced_file_identity_rejected(cache):
    store, now = cache; plan = r.plan_retention(store, now=now)
    path = store.root / "cache/recreatable/build/g0/payload.bin"
    old = path.stat(); new = path.with_name("new.bin"); new.write_bytes(path.read_bytes())
    os.utime(new, ns=(old.st_atime_ns, old.st_mtime_ns)); os.replace(new, path)
    with pytest.raises(FlowError, match="changed"):
        r.apply_retention(store, plan, plan["plan_hash"], enabled=True, now=now)
    assert path.exists()


@pytest.mark.parametrize("mutation", ["content", "missing", "pin", "plan"])
def test_recheck_rejects_changed_or_missing_evidence(cache, mutation):
    store, now = cache; plan = r.plan_retention(store, now=now)
    file = store.root / "cache/recreatable/build/g0/payload.bin"
    if mutation == "content": file.write_bytes(b"different content")
    elif mutation == "missing": file.unlink()
    elif mutation == "pin": r.pin_cache(store, "cache/recreatable/build/g0", "reader", now=now)
    else: plan["entries"][0]["tree"]["bytes"] += 1
    with pytest.raises(FlowError): r.apply_retention(store, plan, plan["plan_hash"], enabled=True, now=now)
    assert file.parent.exists()


@pytest.mark.parametrize("delta", [-1, 3601])
def test_stale_or_backwards_clock_rejected(cache, delta):
    store, now = cache; plan = r.plan_retention(store, now=now)
    with pytest.raises(FlowError, match="stale or clock"):
        r.apply_retention(store, plan, plan["plan_hash"], enabled=True, now=now+delta)


def test_old_plan_schema_requires_fresh_dry_run(cache):
    store, now = cache; plan = r.plan_retention(store, now=now)
    plan.pop("plan_hash"); plan["schema_version"] = 1; plan["plan_hash"] = fingerprint(plan)
    with pytest.raises(FlowError, match="plan hash/workspace mismatch"):
        r.apply_retention(store, plan, plan["plan_hash"], enabled=True, now=now)
    assert (store.root / "cache/recreatable/build/g0").exists()


def test_age_and_keep_floor(cache):
    store, now = cache
    with pytest.raises(FlowError): r.plan_retention(store, keep_last=2, now=now)
    with pytest.raises(FlowError): r.plan_retention(store, min_age_seconds=0, now=now)
    plan = r.plan_retention(store, now=now-10*86400)
    assert all(x["action"] == "keep" for x in plan["entries"])


def test_real_symlink_or_windows_junction_is_rejected(cache, tmp_path):
    store, now = cache; outside = tmp_path / "outside"; outside.mkdir(); (outside / "secret").write_text("preserve")
    link = store.root / "cache/recreatable/build/g0/link"
    if sys.platform == "win32":
        result = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(outside)], capture_output=True)
        assert result.returncode == 0, result.stderr
    else: link.symlink_to(outside, target_is_directory=True)
    try:
        with pytest.raises(FlowError, match="link|junction"):
            r.plan_retention(store, now=now)
        assert (outside / "secret").read_text() == "preserve"
    finally:
        if sys.platform == "win32": os.rmdir(link)
        else: link.unlink()


def test_hardlink_cache_rejected(cache, tmp_path):
    store, now = cache; outside = tmp_path / "keep"; outside.write_text("retained")
    os.link(outside, store.root / "cache/recreatable/build/g0/shared")
    with pytest.raises(FlowError, match="Hardlinked"):
        r.plan_retention(store, now=now)
    assert outside.read_text() == "retained"


def test_partial_delete_receipt_keeps_quarantine_and_refuses_retry(cache, monkeypatch):
    store, now = cache; plan = r.plan_retention(store, now=now); original = r.shutil.rmtree
    calls = []
    def delete(path):
        calls.append(path)
        if len(calls) == 2: raise OSError("synthetic open-file conflict")
        return original(path)
    monkeypatch.setattr(r.shutil, "rmtree", delete)
    with pytest.raises(OSError, match="synthetic"):
        r.apply_retention(store, plan, plan["plan_hash"], enabled=True, now=now)
    receipt = json.loads((store.root / ".maintenance/receipts" / (plan["plan_hash"] + ".json")).read_text())
    assert receipt["status"] == "attention"
    assert [x["status"] for x in receipt["results"]] == ["removed", "quarantined"]
    assert (store.root / receipt["results"][1]["quarantine"] / "payload.bin").exists()
    with pytest.raises(FlowError, match="already attempted"):
        r.apply_retention(store, plan, plan["plan_hash"], enabled=True, now=now)


def test_mutation_between_preflight_and_rename_is_rejected(cache, monkeypatch):
    store, now = cache; plan = r.plan_retention(store, now=now); original = r._tree
    calls = []
    def scan(path, **kwargs):
        if path.name == "g0":
            calls.append(path)
            if len(calls) == 2: (path / "payload.bin").write_bytes(b"concurrent writer")
        return original(path, **kwargs)
    monkeypatch.setattr(r, "_tree", scan)
    with pytest.raises(FlowError, match="Concurrent"):
        r.apply_retention(store, plan, plan["plan_hash"], enabled=True, now=now)
    assert (store.root / "cache/recreatable/build/g0/payload.bin").read_bytes() == b"concurrent writer"


def test_cli_defaults_to_no_deletion(cache):
    store, _ = cache
    script = Path(__file__).parents[1] / "scripts/maintain_workspace.py"
    result = subprocess.run([sys.executable, "-B", str(script), "--workspace", str(store.root)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["results"][0]["status"] == "dry-run"
    assert all((store.root / f"cache/recreatable/build/g{i}").exists() for i in range(5))


def test_cross_process_maintenance_lock_blocks_pin(cache):
    store, _ = cache
    code = "from hcu_trainflow.core import Store,FlowError; from hcu_trainflow.retention import pin_cache; import sys\ntry: pin_cache(Store(sys.argv[1]),'cache/recreatable/build/g0','other')\nexcept FlowError: raise SystemExit(7)"
    with r._locked(store):
        result = subprocess.run([sys.executable, "-B", "-c", code, str(store.root)], capture_output=True)
    assert result.returncode == 7, result.stderr
