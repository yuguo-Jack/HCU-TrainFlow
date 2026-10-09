"""Opt-in retention for explicitly registered, reproducible private caches.

This never discovers disposable data by filename across a workspace. Writers
must pin generations before use and cooperate with the maintenance lock.
"""
import contextlib
import math
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import time
import uuid

from .core import FlowError, fingerprint, read_json, safe_id, utc, write_json
from .training_logs import observer_lock

CACHE_ROOT = Path("cache/recreatable")
CONTROL_ROOT = Path(".maintenance")
PROTECTED = {".git", ".svn", "objects", "evidence", "materials", "checkpoints", "checkpoint",
             "source", "sources", "checkouts", "knowledgebase", "wiki", "experience", "snapshots",
             "training-logs", "watch", "state", "trainflow-snapshot.json", "attempt.json", "exit.json"}
PROTECTED_SUFFIXES = {".sqlite", ".sqlite3", ".db", ".pt", ".pth", ".ckpt", ".safetensors"}


def _number(value, name, minimum=0):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < minimum:
        raise FlowError("Invalid " + name)
    return value


def _link(path, st=None):
    st = path.lstat() if st is None else st
    return (stat.S_ISLNK(st.st_mode) or bool(getattr(st, "st_file_attributes", 0) & 0x400)
            or getattr(path, "is_junction", lambda: False)())


def _inside(root, relative, *, exists=True):
    """Check lexical components before resolve; never bless a resolved junction."""
    if not isinstance(relative, str) or "\\" in relative or ":" in relative:
        raise FlowError("Use a relative POSIX cache path")
    parts = PurePosixPath(relative).parts
    if not parts or relative.startswith("/") or any(x in {"", ".", ".."} for x in relative.split("/")):
        raise FlowError("Cache path must stay inside workspace")
    path = root
    if _link(root):
        raise FlowError("Workspace is a link or reparse point")
    for part in parts:
        path = path / part
        if path.exists() or path.is_symlink():
            if _link(path) or os.path.ismount(path):
                raise FlowError("Links, junctions and mount points cannot be retained automatically")
        elif exists:
            raise FlowError("Registered cache is missing")
    if not path.resolve().is_relative_to(root) or path.resolve() == root:
        raise FlowError("Cache resolved outside workspace")
    return path


def _generation_path(store, relative, *, exists=True):
    path = _inside(store.root, relative, exists=exists)
    parts = PurePosixPath(relative).parts
    if len(parts) != 4 or tuple(parts[:2]) != tuple(CACHE_ROOT.parts):
        raise FlowError("Only cache/recreatable/FAMILY/GENERATION can be registered")
    safe_id(parts[2]); safe_id(parts[3])
    return path


@contextlib.contextmanager
def _locked(store):
    control = _inside(store.root, CONTROL_ROOT.as_posix(), exists=False)
    with observer_lock(control, name="retention.lock"):
        yield control


def _registry(control):
    path = control / "cache-registry.json"
    if path.exists() and _link(path):
        raise FlowError("Cache registry must not be a link/reparse point")
    value = read_json(path) if path.exists() else {"schema_version": 1, "entries": {}}
    if value.get("schema_version") != 1 or not isinstance(value.get("entries"), dict):
        raise FlowError("Invalid cache registry; preserve for inspection")
    return value


def _tree(path, *, deadline=None, max_files=20000, max_bytes=10 * 1024**3):
    from hashlib import sha256
    rows = []; total = 0
    device = path.lstat().st_dev
    def check_time():
        if deadline is not None and time.monotonic() > deadline:
            raise FlowError("Retention scan time budget exceeded; nothing further removed")
    def visit(current, relative):
        nonlocal total
        check_time()
        before = current.lstat()
        if _link(current, before) or before.st_dev != device or (relative and os.path.ismount(current)):
            raise FlowError("Cache contains link, junction or mount point")
        if (current.name.lower() in PROTECTED or current.suffix.lower() in PROTECTED_SUFFIXES
                or ".sqlite" in current.name.lower()):
            raise FlowError("Protected evidence/database/source/checkpoint found in cache")
        row = {"path": relative, "mode": before.st_mode, "dev": before.st_dev,
               "inode": before.st_ino, "mtime_ns": before.st_mtime_ns}
        if stat.S_ISDIR(before.st_mode):
            row["kind"] = "directory"
            rows.append(row)
            with os.scandir(current) as entries:
                children = sorted((e.name for e in entries))
            for name in children:
                visit(current / name, (relative + "/" if relative else "") + name)
            after = current.lstat()
            if (after.st_dev, after.st_ino, after.st_mtime_ns) != (before.st_dev, before.st_ino, before.st_mtime_ns) or _link(current, after):
                raise FlowError("Cache directory changed during scan")
        elif stat.S_ISREG(before.st_mode):
            if before.st_nlink != 1:
                raise FlowError("Hardlinked cache files are not disposable")
            total += before.st_size
            if total > max_bytes or len(rows) >= max_files:
                raise FlowError("Retention scan size/count budget exceeded")
            digest = sha256()
            # O_NOFOLLOW adds another protection on hosts that support it.
            fd = os.open(current, os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0))
            with os.fdopen(fd, "rb") as stream:
                opened = os.fstat(stream.fileno())
                if (opened.st_dev, opened.st_ino, opened.st_size, opened.st_mtime_ns) != (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns):
                    raise FlowError("Cache changed while opening")
                while chunk := stream.read(1024 * 1024):
                    check_time(); digest.update(chunk)
            after = current.lstat()
            if (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns) != (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) or _link(current, after):
                raise FlowError("Cache changed during scan")
            row.update(kind="file", size=before.st_size, sha256=digest.hexdigest())
            rows.append(row)
        else:
            raise FlowError("Special files cannot be disposable caches")
        if len(rows) > max_files:
            raise FlowError("Retention scan file count exceeded")
    visit(path, "")
    return {"rows": rows, "bytes": total, "fingerprint": fingerprint(rows),
            "latest_mtime": max(r["mtime_ns"] for r in rows) / 1e9}


def register_cache(store, relative, rebuild, *, now=None):
    """Registration is an explicit attestation that this generation is reproducible."""
    now = time.time() if now is None else _number(now, "registration time")
    if not isinstance(rebuild, str) or not rebuild.strip():
        raise FlowError("Record a substantive rebuild/source recipe; it will not be executed")
    with _locked(store) as control:
        path = _generation_path(store, relative)
        if not path.is_dir():
            raise FlowError("Register a standalone generation directory")
        tree = _tree(path, deadline=time.monotonic() + 60)
        value = _registry(control)
        if relative in value["entries"]:
            raise FlowError("Cache already registered; touch/pin it rather than overwrite its identity")
        family, generation = PurePosixPath(relative).parts[-2:]
        value["entries"][relative] = {"path": relative, "family": family, "generation": generation,
            "rebuild": rebuild, "registered_at": now, "last_used_at": now, "pins": {}, "state": "retained",
            "registration_fingerprint": tree["fingerprint"]}
        write_json(control / "cache-registry.json", value)
        return value["entries"][relative]


def pin_cache(store, relative, owner, *, release=False, now=None):
    """Pin before any consumer/writer opens this cache; release after reconciliation."""
    safe_id(owner)
    now = time.time() if now is None else _number(now, "cache use time")
    with _locked(store) as control:
        _generation_path(store, relative)
        value = _registry(control); entry = value["entries"].get(relative)
        if not entry or entry["state"] != "retained":
            raise FlowError("Cache is not a retained registered generation")
        if now < entry["last_used_at"]:
            raise FlowError("Cache use clock moved backwards")
        if release:
            if owner not in entry["pins"]:
                raise FlowError("Only an existing owner's pin can be released")
            del entry["pins"][owner]
        else:
            entry["pins"][owner] = {"since": now}
        entry["last_used_at"] = now
        write_json(control / "cache-registry.json", value)
        return entry


def _activity(db, now):
    # Fail closed even if the cache-to-command mapping is incomplete. Expired
    # leases never override an unresolved remote operation.
    return {"operations": [dict(r) for r in db.execute("SELECT id,status FROM operations WHERE status NOT IN ('complete','failed') ORDER BY id")],
            "leases": [dict(r) for r in db.execute("SELECT resource,owner,token,expires FROM leases WHERE expires>? OR expires IS NULL ORDER BY resource", (now,))]}


def _source_pins(db, store, relative):
    candidates = [relative, str(store.root / relative), (store.root / relative).as_posix()]
    pins = []
    for row in db.execute("SELECT id,spec FROM tasks"):
        if any(s.replace("\\", "/").lower() in row["spec"].replace("\\\\", "/").lower() for s in candidates):
            pins.append("task-source-reference:" + row["id"])
    return pins


def _policy(keep_last, min_age_seconds, max_scan_seconds):
    if type(keep_last) is not int or keep_last < 3:
        raise FlowError("Retain at least the newest 3 generations per family")
    _number(min_age_seconds, "minimum age", 3600)
    _number(max_scan_seconds, "scan seconds", 1)
    if max_scan_seconds > 300:
        raise FlowError("Retention scan must be bounded to <=300 seconds")
    return {"keep_last": keep_last, "min_age_seconds": min_age_seconds, "max_scan_seconds": max_scan_seconds}


def _root_identity(path):
    info = path.lstat()
    if not stat.S_ISDIR(info.st_mode) or _link(path, info):
        raise FlowError("Registered generation is no longer a regular directory")
    return {"dev": info.st_dev, "inode": info.st_ino, "mode": info.st_mode}


def plan_retention(store, *, keep_last=3, min_age_seconds=7 * 86400, max_scan_seconds=60, now=None):
    now = time.time() if now is None else _number(now, "plan time")
    policy = _policy(keep_last, min_age_seconds, max_scan_seconds)
    with _locked(store) as control:
        registry = _registry(control)
        with store.db() as db:
            activity = _activity(db, now)
            retained = [v for v in registry["entries"].values() if v["state"] == "retained"]
            newest = set()
            for family in {v["family"] for v in retained}:
                newest.update(v["path"] for v in sorted((v for v in retained if v["family"] == family),
                    key=lambda v: (v["registered_at"], v["generation"]), reverse=True)[:keep_last])
            rows = []; deadline = time.monotonic() + max_scan_seconds
            for entry in sorted(retained, key=lambda v: v["path"]):
                path = _generation_path(store, entry["path"])
                identity = _root_identity(path)
                reasons = _source_pins(db, store, entry["path"])
                if entry["path"] in newest: reasons.append("newest-generations")
                if entry["pins"]: reasons.append("explicit-use-pins")
                last_use = max(entry["registered_at"], entry["last_used_at"])
                if now < last_use: reasons.append("clock-mismatch")
                elif now - last_use < min_age_seconds: reasons.append("younger-than-minimum-age")
                if activity["operations"] or activity["leases"]: reasons.append("workspace-active-or-unresolved")
                # Do not read gigabytes of active/recent caches just to keep
                # them. A later eligible plan performs a fresh deep scan.
                tree = None if reasons else _tree(path, deadline=deadline)
                if tree:
                    last_use = max(last_use, tree["latest_mtime"])
                    if now < last_use: reasons.append("clock-mismatch")
                    elif now - last_use < min_age_seconds: reasons.append("younger-than-minimum-age")
                rows.append({"path": entry["path"], "root_identity": identity, "tree": tree,
                    "scan": "deep" if tree else "identity-only; already protected",
                    "action": "keep" if reasons else "remove", "reasons": reasons})
        plan = {"schema_version": 2, "workspace": str(store.root), "created_at": now,
                "registry_hash": fingerprint(registry), "policy": policy, "activity": activity, "entries": rows,
                "default": "dry-run; apply needs explicit plan hash and opt-in"}
        plan["plan_hash"] = fingerprint(plan)
        write_json(_inside(store.root, (CONTROL_ROOT / "plans" / (plan["plan_hash"] + ".json")).as_posix(), exists=False), plan)
        return plan


def apply_retention(store, plan, expected_hash, *, enabled=False, now=None):
    """Recheck all candidates, quarantine atomically, then delete only that tree.

    An interruption or failed recheck keeps quarantine and a durable receipt.
    No unreviewed automatic retry of a partial plan is supported.
    """
    if enabled is not True:
        raise FlowError("Deletion is opt-in; use dry-run until explicitly enabled")
    now = time.time() if now is None else _number(now, "apply time")
    body = {k: v for k, v in plan.items() if k != "plan_hash"}
    if (expected_hash != plan.get("plan_hash") or fingerprint(body) != expected_hash
            or plan.get("schema_version") != 2 or plan.get("workspace") != str(store.root)):
        raise FlowError("Retention plan hash/workspace mismatch")
    if now < plan["created_at"] or now - plan["created_at"] > 3600:
        raise FlowError("Retention plan is stale or clock changed; generate a new dry-run")
    with _locked(store) as control:
        retained_plan = _inside(store.root, (CONTROL_ROOT / "plans" / (expected_hash + ".json")).as_posix())
        if not retained_plan.is_file() or read_json(retained_plan) != plan:
            raise FlowError("Plan was not created by this workspace")
        receipt_path = _inside(store.root, (CONTROL_ROOT / "receipts" / (expected_hash + ".json")).as_posix(), exists=False)
        if receipt_path.exists():
            raise FlowError("Plan already attempted; inspect its receipt before replanning")
        registry = _registry(control)
        if fingerprint(registry) != plan["registry_hash"]:
            raise FlowError("Cache registration/pins changed after plan")
        deadline = time.monotonic() + plan["policy"]["max_scan_seconds"]
        with store.db() as db:
            # Blocks new TrainFlow operations/leases until this bounded sweep
            # finishes. Unregistered external consumers must obey the pin API.
            db.execute("BEGIN IMMEDIATE")
            activity = _activity(db, now)
            if activity["operations"] or activity["leases"]:
                raise FlowError("Active/unknown operations or live resource leases protect workspace caches")
            if activity != plan["activity"]:
                raise FlowError("Workspace activity changed after plan")
            for row in plan["entries"]:
                path = _generation_path(store, row["path"])
                if _root_identity(path) != row["root_identity"]:
                    raise FlowError("Cache root identity changed after plan")
                if row["action"] == "remove":
                    if not row.get("tree") or _tree(path, deadline=deadline) != row["tree"]:
                        raise FlowError("Cache contents/identity changed after plan")
                if row["action"] == "remove" and _source_pins(db, store, row["path"]):
                    raise FlowError("Cache acquired a source reference after plan")
            receipt = {"schema_version": 1, "plan_hash": expected_hash, "status": "started", "started_at": utc(), "results": []}
            write_json(receipt_path, receipt)
            try:
                for row in plan["entries"]:
                    if row["action"] != "remove": continue
                    path = _generation_path(store, row["path"])
                    if _tree(path, deadline=deadline) != row["tree"]:
                        raise FlowError("Concurrent cache mutation; no further deletion")
                    quarantine_relative = (CONTROL_ROOT / "quarantine" / uuid.uuid4().hex).as_posix()
                    quarantine = _inside(store.root, quarantine_relative, exists=False)
                    quarantine.parent.mkdir(parents=True, exist_ok=True)
                    result = {"path": row["path"], "quarantine": quarantine_relative, "status": "rename-intent", "bytes": row["tree"]["bytes"]}
                    receipt["results"].append(result); write_json(receipt_path, receipt)
                    os.rename(path, quarantine)
                    result["status"] = "quarantined"; write_json(receipt_path, receipt)
                    # Name changes do not alter the tree's relative identities.
                    if _tree(quarantine, deadline=deadline) != row["tree"]:
                        raise FlowError("Quarantine changed; preserve for manual reconciliation")
                    _inside(store.root, quarantine_relative)
                    shutil.rmtree(quarantine)
                    result["status"] = "removed"
                    registry["entries"][row["path"]]["state"] = "removed"
                    registry["entries"][row["path"]]["removal_plan"] = expected_hash
                    write_json(control / "cache-registry.json", registry)
                    write_json(receipt_path, receipt)
                receipt["status"] = "complete"
            except BaseException as exc:
                receipt.update(status="attention", error=type(exc).__name__ + ": " + str(exc))
                write_json(receipt_path, receipt)
                raise
            receipt["finished_at"] = utc(); write_json(receipt_path, receipt)
        return receipt
