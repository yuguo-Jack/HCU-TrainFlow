"""Opt-in retention for registered caches and explicitly retired temporary outputs.

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
TEMP_ROOT = Path("scratch/disposable")
TEMP_KINDS = {"temporary-checkpoint", "debug-output", "profiler-intermediate", "temporary-output"}
MAINTENANCE_TRIGGERS = {"periodic", "experiment-batch", "stage-transition", "recovery-reconciled", "task-close", "space-pressure"}
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


def _generation_path(store, relative, *, exists=True, temporary=False):
    path = _inside(store.root, relative, exists=exists)
    parts = PurePosixPath(relative).parts
    base = TEMP_ROOT if temporary else CACHE_ROOT
    if len(parts) != 4 or tuple(parts[:2]) != tuple(base.parts):
        raise FlowError(f"Only {base.as_posix()}/FAMILY/GENERATION can be registered")
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


def _tree(path, *, deadline=None, max_files=20000, max_bytes=10 * 1024**3,
          metadata_only=False, allow_checkpoint=False):
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
        protected = PROTECTED - {"checkpoint", "checkpoints"} if allow_checkpoint else PROTECTED
        suffixes = PROTECTED_SUFFIXES - {".pt", ".pth", ".ckpt", ".safetensors"} if allow_checkpoint else PROTECTED_SUFFIXES
        if (current.name.lower() in protected or current.suffix.lower() in suffixes
                or ".sqlite" in current.name.lower()):
            raise FlowError("Protected evidence/database/source/checkpoint found in cache")
        row = {"path": relative, "mode": before.st_mode, "dev": before.st_dev,
               "inode": before.st_ino, "mtime_ns": before.st_mtime_ns}
        if stat.S_ISDIR(before.st_mode):
            row["kind"] = "directory"
            rows.append(row)
            with os.scandir(current) as entries:
                children = []
                for entry in entries:
                    check_time()
                    children.append(entry.name)
                    if len(children) + len(rows) > max_files:
                        raise FlowError("Retention scan file count exceeded")
                children.sort()
            for name in children:
                visit(current / name, (relative + "/" if relative else "") + name)
            after = current.lstat()
            if (after.st_dev, after.st_ino, after.st_mtime_ns) != (before.st_dev, before.st_ino, before.st_mtime_ns) or _link(current, after):
                raise FlowError("Cache directory changed during scan")
        elif stat.S_ISREG(before.st_mode):
            if before.st_nlink != 1:
                raise FlowError("Hardlinked cache files are not disposable")
            total += before.st_size
            if (not metadata_only and total > max_bytes) or len(rows) >= max_files:
                raise FlowError("Retention scan size/count budget exceeded")
            if metadata_only:
                # Closed, explicitly retired outputs only. No payload reads or
                # integrity claim; writers/readers must participate in pins.
                row.update(kind="file", size=before.st_size, ctime_ns=before.st_ctime_ns)
                rows.append(row)
                return
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


def _entry_path(store, entry):
    return _generation_path(store, entry["path"], temporary=entry.get("category") == "temporary")


def _entry_tree(path, entry, deadline):
    temporary = entry.get("category") == "temporary"
    return _tree(path, deadline=deadline, metadata_only=temporary,
                 allow_checkpoint=temporary and entry["kind"] == "temporary-checkpoint")


def _retirement_evidence(store, evidence):
    # Retain a small disposition record which references original evidence,
    # never repeatedly load a multi-GB checkpoint/dump during maintenance.
    with store.db() as db:
        row = db.execute("SELECT size FROM artifacts WHERE id=?", (evidence,)).fetchone()
    if not row or not 0 < row["size"] <= 1024**2:
        raise FlowError("Retirement evidence must be a retained nonempty record <=1 MiB")
    if not store.artifact(evidence).strip():
        raise FlowError("Retirement evidence record must not be empty")


def register_temporary(store, relative, kind, owner, *, now=None):
    """Register an owned scratch generation, initially protected by its producer."""
    safe_id(owner)
    if kind not in TEMP_KINDS:
        raise FlowError("Unknown temporary output kind")
    now = time.time() if now is None else _number(now, "registration time")
    with _locked(store) as control:
        path = _generation_path(store, relative, temporary=True)
        identity = _root_identity(path)
        value = _registry(control)
        if relative in value["entries"]:
            raise FlowError("Generation already registered; use a new generation name")
        family, generation = PurePosixPath(relative).parts[-2:]
        entry = {"path": relative, "family": family, "generation": generation,
                 "category": "temporary", "kind": kind, "owner": owner,
                 "registered_at": now, "last_used_at": now, "pins": {owner: {"since": now}},
                 "state": "retained", "lifecycle": "active", "root_identity": identity}
        value["entries"][relative] = entry
        write_json(control / "cache-registry.json", value)
        return entry


def retire_temporary(store, relative, owner, reason, evidence, *, producer_stopped=False, now=None):
    """Attest closure and retained evidence; this does not stop or inspect processes."""
    safe_id(owner)
    now = time.time() if now is None else _number(now, "retirement time")
    if producer_stopped is not True or not isinstance(reason, str) or not reason.strip():
        raise FlowError("Retirement requires a reason and explicit producer-stopped attestation")
    if not isinstance(evidence, str):
        raise FlowError("Retain a nonempty retirement/evidence record in workspace objects first")
    _retirement_evidence(store, evidence)
    with _locked(store) as control:
        value = _registry(control); entry = value["entries"].get(relative)
        if (not entry or entry.get("category") != "temporary" or entry["state"] != "retained"
                or entry["lifecycle"] not in {"active", "retired"} or entry["owner"] != owner):
            raise FlowError("Only the registered owner may retire a retained temporary generation")
        if set(entry["pins"]) - {owner}:
            raise FlowError("Other consumers still pin this generation")
        if now < entry["last_used_at"]:
            raise FlowError("Retirement clock moved backwards")
        path = _entry_path(store, entry)
        if _root_identity(path) != entry["root_identity"]:
            raise FlowError("Temporary generation root changed since registration")
        tree = _entry_tree(path, entry, time.monotonic() + 60)
        if entry["lifecycle"] == "retired":
            entry.setdefault("retirement_history", []).append({"retired_at": entry["retired_at"],
                "retirement": entry["retirement"], "fingerprint": entry["retired_fingerprint"]})
        entry.update(lifecycle="retired", retired_at=now, last_used_at=now, pins={},
                     retirement={"reason": reason, "evidence": evidence, "producer_stopped": True},
                     retired_fingerprint=tree["fingerprint"])
        write_json(control / "cache-registry.json", value)
        return entry


def capacity_status(store, *, min_free_bytes=20 * 1024**3, min_free_percent=10):
    """Cheap filesystem capacity only; site/user quotas require a separate probe."""
    _number(min_free_bytes, "minimum free bytes")
    _number(min_free_percent, "minimum free percent")
    if min_free_percent > 100:
        raise FlowError("Minimum free percent must be <=100")
    usage = shutil.disk_usage(store.root)
    required = max(min_free_bytes, usage.total * min_free_percent / 100)
    return {"workspace": str(store.root), "total_bytes": usage.total, "free_bytes": usage.free,
            "required_free_bytes": math.ceil(required), "status": "low-space" if usage.free < required else "ok",
            "quota_checked": False}


def sweep_workspace(store, *, enabled=False, plan_options=None, capacity_options=None, now=None):
    """One explicit bounded sweep. Returned byte counts are logical, not disk blocks."""
    if type(enabled) is not bool:
        raise FlowError("Deletion opt-in must be an explicit boolean")
    capacity_options = capacity_options or {}
    before = capacity_status(store, **capacity_options)
    plan = plan_retention(store, **(plan_options or {}), now=now)
    candidates = [row for row in plan["entries"] if row["action"] == "remove"]
    result = {"status": "dry-run", "plan_hash": plan["plan_hash"],
              "remove_bytes": sum(row["tree"]["bytes"] for row in candidates),
              "entries": [{k: row[k] for k in ("path", "action", "reasons")} for row in plan["entries"]],
              "plan_path": str(store.root / CONTROL_ROOT / "plans" / (plan["plan_hash"] + ".json"))}
    if enabled and candidates:
        receipt = apply_retention(store, plan, plan["plan_hash"], enabled=True, now=now)
        result.update(receipt)
    result.update(capacity_before=before, capacity_after=capacity_status(store, **capacity_options))
    return result


def maintenance_tick(store, *, trigger="periodic", scan_interval_seconds=6 * 3600,
                     enabled=False, resume_after_review=False, plan_options=None, capacity_options=None, now=None):
    """Low-frequency hook; milestones have a one-hour floor, periodic scans six by default.

    No scheduler is installed. A single deployment owner calls this at its
    milestones or configured interval, independently of the human-input poll.
    """
    if trigger not in MAINTENANCE_TRIGGERS:
        raise FlowError("Unknown maintenance trigger")
    if type(enabled) is not bool or type(resume_after_review) is not bool:
        raise FlowError("Maintenance opt-in flags must be explicit booleans")
    _number(scan_interval_seconds, "maintenance scan interval", 3600)
    now = time.time() if now is None else _number(now, "maintenance time")
    control = _inside(store.root, CONTROL_ROOT.as_posix(), exists=False)
    with observer_lock(control, name="maintenance-tick.lock"):
        state_path = _inside(store.root, (CONTROL_ROOT / "tick-state.json").as_posix(), exists=False)
        state = read_json(state_path) if state_path.exists() else None
        capacity = capacity_status(store, **(capacity_options or {}))
        effective_trigger = "space-pressure" if capacity["status"] == "low-space" else trigger
        interval = scan_interval_seconds if effective_trigger == "periodic" else 3600
        if state:
            last = _number(state["attempted_at"], "last maintenance time")
            if now < last:
                raise FlowError("Maintenance clock moved backwards; inspect schedule state")
            if state["status"] != "complete" and not resume_after_review:
                raise FlowError("Previous maintenance incomplete; reconcile plan/quarantine before --resume-after-review")
            if now - last < interval and not resume_after_review:
                return {"status": "not-due", "trigger": effective_trigger, "next_eligible_at": last + interval,
                        "capacity_after": capacity, "reason": "scan-cooldown; no directory scan"}
        state = {"schema_version": 1, "attempted_at": now, "trigger": effective_trigger, "status": "started"}
        write_json(state_path, state)
        try:
            result = sweep_workspace(store, enabled=enabled, plan_options=plan_options,
                                     capacity_options=capacity_options, now=now)
        except BaseException:
            state["status"] = "attention"; write_json(state_path, state)
            raise
        state.update(status="complete", plan_hash=result["plan_hash"])
        write_json(state_path, state)
        result["trigger"] = effective_trigger
        return result


def pin_cache(store, relative, owner, *, release=False, now=None):
    """Pin before any consumer/writer opens this cache; release after reconciliation."""
    safe_id(owner)
    now = time.time() if now is None else _number(now, "cache use time")
    with _locked(store) as control:
        value = _registry(control); entry = value["entries"].get(relative)
        if not entry or entry["state"] != "retained":
            raise FlowError("Cache is not a retained registered generation")
        _entry_path(store, entry)
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


def plan_retention(store, *, keep_last=3, min_age_seconds=7 * 86400, max_scan_seconds=60,
                   temporary_min_age_seconds=3600, now=None):
    now = time.time() if now is None else _number(now, "plan time")
    policy = _policy(keep_last, min_age_seconds, max_scan_seconds)
    policy["temporary_min_age_seconds"] = _number(temporary_min_age_seconds, "temporary minimum age")
    with _locked(store) as control:
        registry = _registry(control)
        with store.db() as db:
            activity = _activity(db, now)
            retained = [v for v in registry["entries"].values() if v["state"] == "retained"]
            newest = set()
            caches = [v for v in retained if v.get("category") != "temporary"]
            for family in {v["family"] for v in caches}:
                newest.update(v["path"] for v in sorted((v for v in caches if v["family"] == family),
                    key=lambda v: (v["registered_at"], v["generation"]), reverse=True)[:keep_last])
            rows = []; deadline = time.monotonic() + max_scan_seconds
            for entry in sorted(retained, key=lambda v: v["path"]):
                if time.monotonic() > deadline:
                    raise FlowError("Retention scan time budget exceeded")
                path = _entry_path(store, entry)
                identity = _root_identity(path)
                reasons = _source_pins(db, store, entry["path"])
                temporary = entry.get("category") == "temporary"
                minimum_age = temporary_min_age_seconds if temporary else min_age_seconds
                if temporary and entry["lifecycle"] != "retired": reasons.append("not-explicitly-retired")
                if temporary and identity != entry["root_identity"]:
                    raise FlowError("Temporary generation root changed since registration")
                if entry["path"] in newest: reasons.append("newest-generations")
                if entry["pins"]: reasons.append("explicit-use-pins")
                last_use = max(entry["registered_at"], entry["last_used_at"])
                if now < last_use: reasons.append("clock-mismatch")
                elif now - last_use < minimum_age: reasons.append("younger-than-minimum-age")
                if activity["operations"] or activity["leases"]: reasons.append("workspace-active-or-unresolved")
                # Do not read gigabytes of active/recent caches just to keep
                # them. A later eligible plan performs a fresh deep scan.
                tree = None if reasons else _entry_tree(path, entry, deadline)
                if tree:
                    if temporary:
                        _retirement_evidence(store, entry["retirement"]["evidence"])
                        if tree["fingerprint"] != entry["retired_fingerprint"]:
                            reasons.append("changed-after-retirement")
                    last_use = max(last_use, tree["latest_mtime"])
                    if now < last_use: reasons.append("clock-mismatch")
                    elif now - last_use < minimum_age: reasons.append("younger-than-minimum-age")
                rows.append({"path": entry["path"], "root_identity": identity, "tree": tree,
                    "scan": ("metadata-only; explicitly retired" if temporary else "deep") if tree else "identity-only; already protected",
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
                entry = registry["entries"][row["path"]]
                path = _entry_path(store, entry)
                if _root_identity(path) != row["root_identity"]:
                    raise FlowError("Cache root identity changed after plan")
                if row["action"] == "remove":
                    if entry.get("category") == "temporary":
                        if entry["lifecycle"] != "retired" or entry["pins"]:
                            raise FlowError("Temporary generation is active or pinned")
                        _retirement_evidence(store, entry["retirement"]["evidence"])
                    if not row.get("tree") or _entry_tree(path, entry, deadline) != row["tree"]:
                        raise FlowError("Cache contents/identity changed after plan")
                if row["action"] == "remove" and _source_pins(db, store, row["path"]):
                    raise FlowError("Cache acquired a source reference after plan")
            receipt = {"schema_version": 1, "plan_hash": expected_hash, "status": "started", "started_at": utc(), "results": []}
            write_json(receipt_path, receipt)
            try:
                for row in plan["entries"]:
                    if row["action"] != "remove": continue
                    entry = registry["entries"][row["path"]]
                    path = _entry_path(store, entry)
                    if _entry_tree(path, entry, deadline) != row["tree"]:
                        raise FlowError("Concurrent cache mutation; no further deletion")
                    quarantine_relative = (CONTROL_ROOT / "quarantine" / uuid.uuid4().hex).as_posix()
                    quarantine = _inside(store.root, quarantine_relative, exists=False)
                    quarantine.parent.mkdir(parents=True, exist_ok=True)
                    result = {"path": row["path"], "quarantine": quarantine_relative, "status": "rename-intent", "bytes": row["tree"]["bytes"]}
                    receipt["results"].append(result); write_json(receipt_path, receipt)
                    os.rename(path, quarantine)
                    result["status"] = "quarantined"; write_json(receipt_path, receipt)
                    # Name changes do not alter the tree's relative identities.
                    if _entry_tree(quarantine, entry, deadline) != row["tree"]:
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
            receipt["removed_logical_bytes"] = sum(r["bytes"] for r in receipt["results"] if r["status"] == "removed")
            receipt["finished_at"] = utc(); write_json(receipt_path, receipt)
        return receipt
