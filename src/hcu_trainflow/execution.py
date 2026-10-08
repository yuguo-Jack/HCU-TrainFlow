"""Explicit command plans and replay-safe execution intents; no implicit shell."""
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import time

from .core import FlowError, atomic_write, child, fingerprint, safe_id, utc, write_json


def command_plan(card):
    allowed = {"schema_version", "argv", "cwd", "env", "timeout_seconds", "backend", "ssh_target", "container", "namespace", "pod", "allocation", "activation", "basis"}
    if set(card) - allowed or card.get("schema_version") != 1:
        raise FlowError("Unknown command-card fields or version")
    argv = card.get("argv")
    if not isinstance(argv, list) or not argv or any(not isinstance(x, str) or "\x00" in x for x in argv) or not argv[0]:
        raise FlowError("argv must be a nonempty string array")
    env = card.get("env", {})
    if not isinstance(env, dict) or any(not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", k) or not isinstance(v, str) or "\x00" in v for k, v in env.items()):
        raise FlowError("Invalid environment mapping")
    if not card.get("basis") or not card.get("cwd"):
        raise FlowError("Commands require a reviewed basis and explicit working directory")
    timeout = card.get("timeout_seconds", 600)
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not 0 < timeout <= 86400:
        raise FlowError("timeout_seconds must be in (0,86400]")
    backend = card.get("backend", "local")
    activation = card.get("activation")
    inner = "exec " + shlex.join(["env"] + [k + "=" + v for k, v in env.items()] + argv)
    if activation:
        if not isinstance(activation, str) or not activation.startswith("/") or "\x00" in activation:
            raise FlowError("Activation must be a verified absolute POSIX script path")
        inner = ". " + shlex.quote(activation) + " && " + inner
    remote_command = "cd " + shlex.quote(card["cwd"]) + " && " + inner
    result = {"backend": backend, "cwd": card["cwd"], "env": env, "timeout_seconds": timeout, "card_hash": fingerprint(card), "basis": card["basis"]}
    if backend == "local":
        if activation:
            raise FlowError("Local activation is not implicit; use an explicit interpreter in argv")
        result["argv"] = argv
    elif backend in {"ssh", "ssh-docker", "ssh-slurm"}:
        target = card.get("ssh_target", "")
        if not re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_.@-]*", target):
            raise FlowError("Use an explicit trusted SSH config alias or user@host")
        if backend == "ssh-docker":
            container = card.get("container", "")
            safe_id(container)
            remote_command = shlex.join(["docker", "exec", container, "bash", "-lc", remote_command])
        elif backend == "ssh-slurm":
            allocation = str(card.get("allocation", ""))
            if not allocation.isdecimal():
                raise FlowError("Slurm execution requires an existing numeric allocation; this does not submit a new job")
            remote_command = shlex.join(["srun", "--jobid", allocation, "bash", "-lc", remote_command])
        result.update(argv=["ssh", "-o", "BatchMode=yes", target, remote_command], cwd=None, env={})
    elif backend == "k8s":
        for key in ("pod", "namespace", "container"):
            safe_id(card.get(key))
        result.update(argv=["kubectl", "exec", "-n", card["namespace"], card["pod"], "-c", card["container"], "--", "bash", "-lc", remote_command], cwd=None, env={})
    else:
        raise FlowError("Unsupported execution backend")
    return result


def run_command(store, tid, operation_id, card, lease):
    task = store.task(tid)
    if "execute" not in task["spec"].get("permissions", []):
        raise FlowError("Task has no execute permission")
    if task["state"] in {"completed", "cancelled", "paused", "blocked", "failed"}:
        raise FlowError("Task is not active")
    safe_id(operation_id)
    plan = command_plan(card)
    request = fingerprint({"plan": plan, "context": task["context"]})
    with store.db() as db:
        db.execute("BEGIN IMMEDIATE")
        store.check_lease(db, **lease)
        prior = db.execute("SELECT * FROM operations WHERE id=?", (operation_id,)).fetchone()
        if prior:
            if prior["task"] != tid or prior["request_hash"] != request:
                raise FlowError("Operation ID belongs to a different request")
            if prior["status"] in {"complete", "failed"}:
                return json.loads(prior["result"])
            raise FlowError("Outcome unknown; reconcile original execution before creating another operation")
        count = db.execute("SELECT count(*) FROM operations WHERE task=?", (tid,)).fetchone()[0]
        if count >= task["spec"].get("budget", {}).get("max_operations", 100):
            raise FlowError("Operation budget exhausted")
        spent = sum(json.loads(x[0]).get("seconds", 0) for x in db.execute("SELECT result FROM operations WHERE task=? AND result IS NOT NULL", (tid,)))
        remaining = task["spec"].get("budget", {}).get("max_seconds", float("inf")) - spent
        if plan["timeout_seconds"] > remaining:
            raise FlowError("Command timeout exceeds remaining execution budget")
        uncertain = db.execute("SELECT id FROM operations WHERE task=? AND status IN ('started','unknown')", (tid,)).fetchall()
        if uncertain:
            raise FlowError("Prior execution outcome is unresolved; reconcile before another command")
        db.execute("INSERT INTO operations VALUES(?,?,?,'started',NULL,?)", (operation_id, tid, request, utc()))
        store.event(db, tid, "operation-started", {"operation": operation_id, "request": request, "lease": lease})
    output = store.root / "runs" / tid / operation_id
    output.mkdir(parents=True, exist_ok=False)
    write_json(output / "plan.json", plan)
    started = time.monotonic()
    timed_out = False
    # Files, rather than in-memory pipes, retain large logs and survive controller crashes.
    with (output / "stdout.log").open("wb") as stdout, (output / "stderr.log").open("wb") as stderr:
        try:
            proc = subprocess.Popen(plan["argv"], cwd=plan["cwd"], env={**os.environ, **plan["env"]}, stdout=stdout, stderr=stderr)
            write_json(output / "process.json", {"pid": proc.pid, "created_at": utc(), "operation": operation_id})
            try:
                code = proc.wait(timeout=plan["timeout_seconds"])
            except subprocess.TimeoutExpired:
                timed_out = True
                proc.kill()
                code = proc.wait()
        except OSError as exc:
            code = -1
            stderr.write(str(exc).encode("utf-8"))
    artifacts = [store.put((output / x).read_bytes()) for x in ("stdout.log", "stderr.log", "plan.json")]
    result = {"operation": operation_id, "returncode": code, "timed_out": timed_out, "seconds": time.monotonic() - started,
              "context": task["context"], "evidence": artifacts,
              "status": "unknown" if timed_out or (plan["backend"] != "local" and code != 0) else ("complete" if code == 0 else "failed"),
              "validation": "unassessed; exit zero does not establish numerical or performance correctness",
              "remote_outcome": "reconcile-required" if plan["backend"] != "local" and (timed_out or code != 0) else "command-returned"}
    write_json(output / "result.json", result)
    with store.db() as db:
        # Record facts even if the lease expired; no subsequent action is authorized by this record.
        db.execute("UPDATE operations SET status=?,result=? WHERE id=?", (result["status"], json.dumps(result), operation_id))
        store.event(db, tid, "operation-finished", result)
    return result


def snapshot(store, repository, paths):
    repo = Path(repository).resolve()
    if not paths:
        raise FlowError("Choose explicit source paths to snapshot")
    files = {}
    for relative in paths:
        if (repo / relative).is_symlink():
            raise FlowError("Selected source is a symlink")
        path = child(repo, relative)
        if not path.exists():
            raise FlowError("Selected source does not exist: " + relative)
        selected = [path] if path.is_file() else sorted(path.rglob("*"))
        for candidate in selected:
            if candidate.is_symlink():
                raise FlowError("Snapshot symlinks require explicit external dependency handling")
            if not candidate.is_file():
                continue
            name = candidate.relative_to(repo).as_posix()
            if any(part in {".git", ".private", ".work", "__pycache__"} for part in candidate.relative_to(repo).parts) or candidate.name.startswith(".env"):
                continue
            if not candidate.resolve().is_relative_to(repo):
                raise FlowError("Source escaped repository")
            content = candidate.read_bytes()
            files[name] = {"sha256": store.put(content), "size": len(content), "executable": bool(candidate.stat().st_mode & 0o111)}
    if not files:
        raise FlowError("Empty source snapshot")
    head = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True)
    manifest = {"schema_version": 1, "files": files, "git_head": head.stdout.strip() if head.returncode == 0 else None,
                "meaning": "Exact selected working-tree bytes, including uncommitted modifications; repository HEAD alone is insufficient"}
    sid = fingerprint(manifest)
    write_json(store.root / "snapshots" / (sid + ".json"), manifest)
    return {"snapshot_id": sid, **manifest}


def materialize(store, snapshot_id, destination):
    from .core import read_json, digest
    if not re.fullmatch(r"[0-9a-f]{64}", snapshot_id):
        raise FlowError("Invalid snapshot ID")
    manifest = read_json(store.root / "snapshots" / (snapshot_id + ".json"))
    if fingerprint(manifest) != snapshot_id:
        raise FlowError("Snapshot manifest hash mismatch")
    destination = Path(destination).resolve()
    if destination.exists():
        raise FlowError("Snapshot destination must be new; never overwrite a running worktree")
    staging = destination.with_name(destination.name + ".partial")
    if staging.exists():
        raise FlowError("An unfinished transfer exists; inspect it before retry")
    staging.mkdir(parents=True)
    for name, info in manifest["files"].items():
        path = child(staging, name)
        atomic_write(path, store.artifact(info["sha256"]))
        if digest(path.read_bytes()) != info["sha256"]:
            raise FlowError("Materialized snapshot hash mismatch")
        if info["executable"] and os.name != "nt":
            path.chmod(0o755)
    write_json(staging / "trainflow-snapshot.json", {"snapshot_id": snapshot_id, **manifest})
    staging.rename(destination)
    return {"snapshot_id": snapshot_id, "destination": str(destination), "verified": True}


def bundle(store, snapshot_id, destination):
    """Portable exact-byte bundle; copy it with the site's approved SSH/transfer tool."""
    import zipfile
    from .core import read_json
    if not re.fullmatch(r"[0-9a-f]{64}", snapshot_id):
        raise FlowError("Invalid snapshot ID")
    manifest = read_json(store.root / "snapshots" / (snapshot_id + ".json"))
    if fingerprint(manifest) != snapshot_id:
        raise FlowError("Snapshot manifest changed")
    with zipfile.ZipFile(destination, "x", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("manifest.json", json.dumps({"snapshot_id": snapshot_id, "manifest": manifest}))
        for name, record in manifest["files"].items():
            archive.writestr("files/" + name, store.artifact(record["sha256"]))
    return {"snapshot_id": snapshot_id, "bundle": str(Path(destination).resolve()), "visibility": "private"}


def receive(store, archive_path, destination, max_bytes=4 * 1024**3):
    import zipfile
    from .core import digest
    with zipfile.ZipFile(archive_path) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)) or sum(x.file_size for x in archive.infolist()) > max_bytes:
            raise FlowError("Duplicate archive member or bundle too large")
        record = json.loads(archive.read("manifest.json"))
        manifest, sid = record["manifest"], record["snapshot_id"]
        if fingerprint(manifest) != sid:
            raise FlowError("Transferred manifest failed integrity check")
        if set(names) != {"manifest.json"} | {"files/" + x for x in manifest["files"]}:
            raise FlowError("Bundle file set differs from manifest")
        for name, info in manifest["files"].items():
            child(destination, name)
            content = archive.read("files/" + name)
            if len(content) != info["size"] or digest(content) != info["sha256"]:
                raise FlowError("Transferred source hash/size mismatch")
            store.put(content)
    write_json(store.root / "snapshots" / (sid + ".json"), manifest)
    return materialize(store, sid, destination)
