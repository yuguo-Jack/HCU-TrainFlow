"""Explicit command plans and replay-safe execution intents; no implicit shell."""
import json
import math
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import time

from .core import FlowError, atomic_write, child, context_epoch, fingerprint, safe_id, utc, write_json


def operation_budget_seconds(db, operation_id, result, *, reserve=False):
    """Count interrupted runs conservatively without inventing measured runtime."""
    values = [result[key] for key in ("seconds", "budget_seconds")
              if isinstance(result.get(key), (int, float)) and not isinstance(result[key], bool)
              and math.isfinite(result[key]) and result[key] >= 0]
    if reserve or not values:
        event = db.execute("SELECT payload FROM events WHERE kind='operation-started' "
                           "AND json_extract(payload,'$.operation')=? ORDER BY seq LIMIT 1", (operation_id,)).fetchone()
        timeout = json.loads(event["payload"]).get("timeout_seconds") if event else None
        # Legacy incomplete records may have no start receipt. Charge the maximum
        # permitted command duration until their accounting is explicitly repaired.
        values.append(timeout if isinstance(timeout, (int, float)) and not isinstance(timeout, bool)
                      and math.isfinite(timeout) and timeout > 0 else 86400)
    return max(values)


def command_plan(card):
    allowed = {"schema_version", "argv", "cwd", "env", "timeout_seconds", "backend", "ssh_target", "ssh_jump", "ssh_known_hosts", "container", "namespace", "pod", "allocation", "activation", "basis"}
    if not isinstance(card, dict) or set(card) - allowed or type(card.get("schema_version")) is not int or card.get("schema_version") != 1:
        raise FlowError("Unknown command-card fields or version")
    argv = card.get("argv")
    if not isinstance(argv, list) or not argv or any(not isinstance(x, str) or "\x00" in x for x in argv) or not argv[0]:
        raise FlowError("argv must be a nonempty string array")
    env = card.get("env", {})
    if not isinstance(env, dict) or any(not isinstance(k, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", k) or not isinstance(v, str) or "\x00" in v for k, v in env.items()):
        raise FlowError("Invalid environment mapping")
    if (not isinstance(card.get("basis"), str) or not card["basis"].strip()
            or not isinstance(card.get("cwd"), str) or not card["cwd"] or "\x00" in card["cwd"]):
        raise FlowError("Commands require a reviewed basis and explicit working directory")
    timeout = card.get("timeout_seconds", 600)
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not 0 < timeout <= 86400:
        raise FlowError("timeout_seconds must be in (0,86400]")
    backend = card.get("backend", "local")
    if not isinstance(backend, str):
        raise FlowError("Unsupported execution backend")
    activation = card.get("activation")
    # env -- preserves an executable/argument beginning with '-' as data. All
    # user-provided arguments remain individual words across every shell hop.
    inner = "exec " + shlex.join(["env", "--"] + [k + "=" + v for k, v in env.items()] + argv)
    remote_command = "cd -- " + shlex.quote(card["cwd"]) + " && " + inner
    if activation is not None:
        if not isinstance(activation, str) or not activation.startswith("/") or "\x00" in activation:
            raise FlowError("Activation must be a verified absolute POSIX script path")
        # Activation scripts may themselves change directory. Establish the
        # requested cwd after activation, then apply the card's explicit env.
        remote_command = ". " + shlex.quote(activation) + " && " + remote_command
    ssh_jump = card.get("ssh_jump")
    if (ssh_jump is not None or card.get("ssh_known_hosts") is not None) and backend not in {"ssh", "ssh-docker", "ssh-slurm"}:
        raise FlowError("SSH transport settings are only valid for SSH execution backends")
    result = {"backend": backend, "cwd": card["cwd"], "env": env, "timeout_seconds": timeout, "card_hash": fingerprint(card), "basis": card["basis"]}
    if backend == "local":
        if activation:
            raise FlowError("Local activation is not implicit; use an explicit interpreter in argv")
        result["argv"] = argv
    elif backend in {"ssh", "ssh-docker", "ssh-slurm"}:
        target = _ssh_target(card.get("ssh_target"))
        if backend == "ssh-docker":
            container = card.get("container", "")
            safe_id(container)
            remote_command = shlex.join(["docker", "exec", container, "bash", "-lc", remote_command])
        elif backend == "ssh-slurm":
            allocation = str(card.get("allocation", ""))
            if not allocation.isdecimal():
                raise FlowError("Slurm execution requires an existing numeric allocation; this does not submit a new job")
            remote_command = shlex.join(["srun", "--jobid", allocation, "bash", "-lc", remote_command])
        else:
            remote_command = shlex.join(["bash", "-lc", remote_command])
        known_hosts = card.get("ssh_known_hosts")
        if ssh_jump is not None and known_hosts is not None and (not isinstance(known_hosts, str) or not known_hosts.startswith("/")):
            raise FlowError("Nested SSH known-hosts file must be an absolute POSIX path on the jump host")
        transport = _ssh_argv(target, remote_command, known_hosts)
        if ssh_jump is not None:
            if (not isinstance(ssh_jump, dict) or set(ssh_jump) - {"mode", "target", "known_hosts"}
                    or ssh_jump.get("mode") != "exec"):
                raise FlowError("ssh_jump requires mode='exec', target, and optional known_hosts")
            jump = _ssh_target(ssh_jump.get("target"))
            if jump == target:
                raise FlowError("Jump host and final target must differ")
            # Unlike ProxyJump, this SSH client runs on the jump host and uses
            # its existing credentials. Never copy keys or forward an agent.
            transport = _ssh_argv(jump, "exec " + shlex.join(transport), ssh_jump.get("known_hosts"))
        result.update(argv=transport, cwd=None, env={})
    elif backend == "k8s":
        for key in ("pod", "namespace", "container"):
            safe_id(card.get(key))
        result.update(argv=["kubectl", "exec", "-n", card["namespace"], card["pod"], "-c", card["container"], "--", "bash", "-lc", remote_command], cwd=None, env={})
    else:
        raise FlowError("Unsupported execution backend")
    return result


def _ssh_target(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_.@-]*", value):
        raise FlowError("Use an explicit trusted SSH config alias or user@host")
    return value


def _ssh_argv(target, command, known_hosts=None):
    # Known hosts must be enrolled through the site's normal verification
    # procedure; a command-card execution must never prompt or trust a new key.
    arguments = ["ssh", "-T", "-o", "BatchMode=yes", "-o", "ForwardAgent=no",
                 "-o", "StrictHostKeyChecking=yes", "-o", "ConnectTimeout=15"]
    if known_hosts is not None:
        if (not isinstance(known_hosts, str) or not known_hosts
                or any(ord(x) < 32 for x in known_hosts) or any(x in known_hosts for x in ("%", "$"))
                or not (known_hosts.startswith("/") or re.match(r"^[A-Za-z]:[/\\]", known_hosts))
                or known_hosts.lower().replace("\\", "/").rstrip("/") in {"/dev/null", "nul"}):
            raise FlowError("SSH known-hosts file must be an explicit absolute path, without expansion tokens")
        if re.match(r"^[A-Za-z]:[/\\]", known_hosts):
            known_hosts = known_hosts.replace("\\", "/")
        # OpenSSH parses -o as config syntax after argv parsing. Quote again so
        # spaces denote one filename, not multiple user-known-hosts files.
        quoted = '"' + known_hosts.replace("\\", "\\\\").replace('"', '\\"') + '"'
        arguments += ["-o", "UserKnownHostsFile=" + quoted]
    return arguments + [target, command]


def run_command(store, tid, operation_id, card, lease, *, control_plane=False, assignment=None, owner=None, token=None,
                expected_context=None, expected_context_epoch=None):
    # Use the existing group lock domain for every operation ID. Reconciliation
    # cannot declare "no process" while this controller can still launch one,
    # and a single/group API race cannot dispatch the same ID twice.
    from .command_group import _controller_lock
    with _controller_lock(store, operation_id):
        return _run_command(store, tid, operation_id, card, lease, control_plane=control_plane,
                            assignment=assignment, owner=owner, token=token,
                            expected_context=expected_context, expected_context_epoch=expected_context_epoch)


def _run_command(store, tid, operation_id, card, lease, *, control_plane=False, assignment=None, owner=None, token=None,
                 expected_context=None, expected_context_epoch=None):
    from . import team
    bound_context = expected_context is not None or expected_context_epoch is not None
    if bound_context and (not isinstance(expected_context, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_context)
                          or type(expected_context_epoch) is not int or expected_context_epoch < 0):
        raise FlowError("Execution context binding requires a context hash and nonnegative epoch")
    if control_plane and assignment:
        raise FlowError('A local delivery bridge is not an assignment experiment')
    if not assignment and (owner is not None or token is not None):
        raise FlowError('Owner/token require an assignment')
    if not control_plane:
        from .flow import guard_execution
        guard_execution(store, tid, allow_parallel=assignment is not None)
    task = store.task(tid)
    if "execute" not in task["spec"].get("permissions", []):
        raise FlowError("Task has no execute permission")
    if control_plane and "agent-dispatch" not in task["spec"].get("permissions", []):
        raise FlowError("A control-plane bridge requires explicit agent-dispatch permission")
    if task["state"] in {"completed", "cancelled", "paused", "blocked", "failed"}:
        raise FlowError("Task is not active")
    safe_id(operation_id)
    plan = command_plan(card)
    if control_plane and plan["backend"] != "local":
        raise FlowError("A control-plane bridge must use the local controller backend")
    identity = {"plan": plan, "context": task["context"]}
    if task['context_epoch']:
        # Preserve IDs from the initial context while distinguishing A -> B -> A.
        identity['context_epoch'] = task['context_epoch']
    if assignment:
        identity.update(assignment=assignment, owner=owner, token=token)
    request = fingerprint(identity)
    with store.db() as db:
        db.execute("BEGIN IMMEDIATE")
        store.check_lease(db, **lease)
        current = db.execute('SELECT context,state FROM tasks WHERE id=?', (tid,)).fetchone()
        current_epoch = context_epoch(db, tid)
        if bound_context and (current['context'] != expected_context or current_epoch != expected_context_epoch):
            raise FlowError('Bound execution context/epoch changed before admission; inspect the original event')
        if (current['context'] != task['context'] or current_epoch != task['context_epoch']
                or current['state'] in {'completed', 'cancelled', 'paused', 'blocked', 'failed'}):
            raise FlowError('Task context/state changed before execution')
        if not control_plane:
            from .flow import get_flow, blockers
            current_flow = get_flow(db, tid)
            if current_flow and blockers(db, tid, task, current_flow):
                raise FlowError('New guidance/context needs attention before execution')
        prior = db.execute("SELECT * FROM operations WHERE id=?", (operation_id,)).fetchone()
        if prior:
            if prior["task"] != tid or prior["request_hash"] != request:
                raise FlowError("Operation ID belongs to a different request")
            if prior["status"] in {"complete", "failed"}:
                return json.loads(prior["result"])
            raise FlowError("Outcome unknown; reconcile original execution before creating another operation")
        if db.execute("SELECT 1 FROM operations WHERE lower(id)=lower(?)", (operation_id,)).fetchone():
            raise FlowError("Operation ID collides with an existing identifier on case-insensitive filesystems")
        assigned=team.check_execution(db,tid,assignment,owner,token,lease['resource']) if assignment else None
        for reservation in team.active_reservations(db):
            if (reservation['id'] != assignment and reservation['spec'].get('resource_scope', 'assignment') == 'assignment'
                    and lease['resource'] in reservation['spec']['resources']):
                raise FlowError('Resource is reserved by a claimed assignment; execute with its owner/token or release its scope')
        occupied = db.execute("SELECT o.id FROM operations o JOIN events e ON json_extract(e.payload,'$.operation')=o.id WHERE e.kind='operation-started' AND json_extract(e.payload,'$.lease.resource')=? AND o.status IN ('started','unknown')", (lease["resource"],)).fetchone()
        if occupied:
            raise FlowError("Resource already has an unresolved execution, including in another task")
        count = db.execute("SELECT count(*) FROM operations WHERE task=?", (tid,)).fetchone()[0]
        if count >= task["spec"].get("budget", {}).get("max_operations", 100):
            raise FlowError("Operation budget exhausted")
        spent = sum(operation_budget_seconds(db, row["id"], json.loads(row["result"] or "{}"),
                                            reserve=row["status"] in {"started", "unknown"})
                    for row in db.execute("SELECT id,status,result FROM operations WHERE task=?", (tid,)))
        remaining = task["spec"].get("budget", {}).get("max_seconds", float("inf")) - spent
        if plan["timeout_seconds"] > remaining:
            raise FlowError("Command timeout exceeds remaining execution budget")
        uncertain = db.execute("SELECT id,status FROM operations WHERE task=? AND status IN ('started','unknown')", (tid,)).fetchall()
        for other in uncertain:
            # The authorized short local bridge must deliver questions/incidents
            # while workers run, including to wake reconciliation of an unknown job.
            # It still needs its own lease/budget and cannot reuse an occupied resource.
            if control_plane:
                continue
            linked=db.execute('SELECT assignment FROM assignment_operations WHERE operation=?',(other['id'],)).fetchone()
            if not assigned or other['status']=='unknown' or not team.active_operation(db,other['id'],tid) or linked['assignment']==assignment:
                raise FlowError("Prior execution outcome is unresolved; reconcile before another command")
        if assigned:
            history=db.execute('SELECT o.id,o.status,o.result FROM operations o JOIN assignment_operations a ON o.id=a.operation WHERE a.assignment=?',(assignment,)).fetchall()
            budget=assigned['spec']['budget']
            seconds=sum(operation_budget_seconds(db, r['id'], json.loads(r['result'] or '{}'),
                                                 reserve=r['status'] in {'started', 'unknown'}) for r in history)
            if len(history)>=budget.get('max_operations',100) or plan['timeout_seconds']>budget.get('max_seconds',float('inf'))-seconds:
                raise FlowError('Assignment execution budget exhausted')
        db.execute("INSERT INTO operations VALUES(?,?,?,'started',NULL,?)", (operation_id, tid, request, utc()))
        if assigned:db.execute('INSERT INTO assignment_operations VALUES(?,?,?)',(operation_id,assignment,token))
        store.event(db, tid, "operation-started", {"operation": operation_id, "request": request, "lease": lease,
                                                "timeout_seconds": plan['timeout_seconds']})
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
              "context": task["context"], "context_epoch": task['context_epoch'], "evidence": artifacts,
              "status": "unknown" if timed_out or (plan["backend"] != "local" and code != 0) else ("complete" if code == 0 else "failed"),
              "validation": "unassessed; exit zero does not establish numerical or performance correctness",
              "remote_outcome": "reconcile-required" if plan["backend"] != "local" and (timed_out or code != 0) else "command-returned"}
    write_json(output / "result.json", result)
    with store.db() as db:
        # Record facts even if the lease expired; no subsequent action is authorized by this record.
        db.execute("UPDATE operations SET status=?,result=? WHERE id=?", (result["status"], json.dumps(result), operation_id))
        store.event(db, tid, "operation-finished", result)
    return result


def _source_name(name):
    """Reject path aliases before platform-dependent Path normalization."""
    from pathlib import PurePosixPath
    if (not isinstance(name, str) or not name or "\\" in name or ":" in name or "\x00" in name
            or name.startswith("/") or any(part in {"", ".", ".."} for part in name.split("/"))):
        raise FlowError("Source paths must be unambiguous relative POSIX paths")
    if name.split("/", 1)[0].casefold() == "trainflow-snapshot.json":
        raise FlowError("Source path collides with reserved trainflow-snapshot.json receipt")
    if os.name == "nt" and any(part.endswith((".", " ")) or PurePosixPath(part).stem.upper() in
                              {"CON", "PRN", "AUX", "NUL", *[f"COM{i}" for i in range(1, 10)],
                               *[f"LPT{i}" for i in range(1, 10)]} for part in name.split("/")):
        raise FlowError("Source path is not representable safely on Windows")
    return name


def _validate_manifest(manifest, snapshot_id):
    if not isinstance(snapshot_id, str) or not re.fullmatch(r"[0-9a-f]{64}", snapshot_id):
        raise FlowError("Invalid snapshot ID")
    if (not isinstance(manifest, dict) or type(manifest.get("schema_version")) is not int
            or manifest["schema_version"] != 1 or not isinstance(manifest.get("files"), dict) or not manifest["files"]):
        raise FlowError("Invalid source manifest")
    if fingerprint(manifest) != snapshot_id:
        raise FlowError("Snapshot manifest hash mismatch")
    names = set()
    for name, info in manifest["files"].items():
        _source_name(name)
        normalized = os.path.normcase(name)
        if normalized in names:
            raise FlowError("Source paths collide on the target filesystem")
        names.add(normalized)
        if (not isinstance(info, dict) or not isinstance(info.get("sha256"), str)
                or not re.fullmatch(r"[0-9a-f]{64}", info["sha256"])
                or type(info.get("size")) is not int or info["size"] < 0 or type(info.get("executable")) is not bool):
            raise FlowError("Invalid source file metadata")
        if "source_path" in info:
            _source_name(info["source_path"])
    for name in names:
        # normcase uses backslashes on Windows; normalize just for this prefix check.
        parts = name.replace("\\", "/").split("/")
        if any(os.path.normcase("/".join(parts[:i])) in names for i in range(1, len(parts))):
            raise FlowError("Source file conflicts with a parent directory")
    links = manifest.get("resolved_links", {})
    if not isinstance(links, dict):
        raise FlowError("Invalid source link evidence")
    for name, link in links.items():
        from .core import digest
        _source_name(name)
        if not isinstance(link, dict):
            raise FlowError("Invalid source link evidence")
        target = link.get("target")
        if (not isinstance(target, str) or not target or target.startswith("/") or "\\" in target or ":" in target
                or any(ord(char) < 32 for char in target) or digest(target.encode("utf-8")) != link.get("target_sha256")
                or link.get("kind") not in {"file", "directory"}
                or link.get("representation") not in {"filesystem-symlink", "git-index-placeholder"}):
            raise FlowError("Invalid source link evidence")
        _source_name(link.get("resolved_source"))
    return manifest


def _git_modes(repo):
    metadata = Path(repo) / ".git"
    if metadata.is_symlink() and not metadata.exists():
        # Git may silently discover an enclosing repository through a dangling
        # child .git link. Its successful exit does not establish child modes.
        raise FlowError("Cannot read dangling Git source metadata: " + str(repo))
    result = subprocess.run(["git", "-C", str(repo), "ls-files", "--stage", "-z"], capture_output=True)
    if result.returncode:
        if (Path(repo) / ".git").exists() or (Path(repo) / ".git").is_symlink():
            raise FlowError("Cannot read Git source modes: " + str(repo))
        return {}
    modes = {}
    for row in result.stdout.split(b"\0"):
        if not row:
            continue
        metadata, name = row.split(b"\t", 1)
        mode, _, stage = metadata.split(b" ")
        name = name.decode("utf-8", errors="surrogateescape")
        modes[name] = mode.decode("ascii") if stage == b"0" else "unmerged"
    return modes


def _executable_metadata(candidate, name, modes, *, windows=None):
    if modes.get(name) == "120000":
        raise FlowError("Git symlink source requires explicit external dependency handling")
    if modes.get(name) == "unmerged":
        raise FlowError("Unmerged Git source requires conflict resolution before snapshot")
    windows = os.name == "nt" if windows is None else windows
    if windows:
        # Windows stat reports suffix-based execute bits, not the Git mode.
        # Untracked files have no POSIX execution contract; use bash/python
        # explicitly or git add/update-index --chmod=+x before snapshotting.
        return {"executable": modes.get(name) == "100755",
                "executable_source": "git-index" if name in modes else "windows-untracked-default-nonexecutable"}
    return {"executable": bool(candidate.stat().st_mode & 0o111), "executable_source": "posix-working-tree"}


def _new_transfer_destination(destination):
    destination = Path(destination).resolve()
    if destination.exists():
        raise FlowError("Snapshot destination must be new; never overwrite a running worktree")
    staging = destination.with_name(destination.name + ".partial")
    if staging.exists() or staging.is_symlink():
        raise FlowError("An unfinished transfer exists; inspect it before retry")
    return destination, staging


def _excluded_source(name):
    parts = name.split("/")
    return any(part in {".git", ".private", ".work", "__pycache__"} or part.startswith(".env") for part in parts)


def _resolve_source(repo, name, modes, links, chain=(), mode_roots=None):
    """Resolve components in order, including Git's Windows text placeholders.

    Do not normpath before following a link: link/.. is relative to the link's
    resolved directory, not necessarily the directory containing the link.
    """
    from .core import digest
    mode_roots = {repo} if mode_roots is None else mode_roots
    parts, todo = [], name.split("/")
    while todo:
        part = todo.pop(0)
        if part in {"", "."}:
            continue
        if part == "..":
            if not parts:
                raise FlowError("Source link escapes repository")
            parts.pop()
            continue
        current = "/".join([*parts, part])
        candidate = repo.joinpath(*parts, part)
        physical_link = candidate.is_symlink()
        if (os.name == "nt" and not physical_link and candidate.exists()
                and candidate.resolve().name != part):
            raise FlowError("Select source paths with their exact filesystem spelling")
        if physical_link or modes.get(current) == "120000":
            if current in chain or len(chain) >= 64:
                raise FlowError("Source link cycle or excessive link depth")
            if physical_link:
                target = os.readlink(candidate)
                raw = target.encode("utf-8")
                representation = "filesystem-symlink"
            else:
                if not candidate.is_file():
                    raise FlowError("Git source link placeholder is missing")
                raw = candidate.read_bytes()
                try:
                    target = raw.decode("utf-8")
                except UnicodeError as exc:
                    raise FlowError("Invalid Git source link placeholder") from exc
                representation = "git-index-placeholder"
            if (not target or target.startswith("/") or "\\" in target or ":" in target
                    or any(ord(char) < 32 for char in target)):
                raise FlowError("Source links must contain a relative POSIX target")
            resolved = _resolve_source(repo, "/".join([*parts, target]), modes, links, (*chain, current), mode_roots)
            resolved_name = resolved.relative_to(repo).as_posix()
            if _excluded_source(resolved_name):
                raise FlowError("Source link targets an excluded private/generated path")
            evidence = {"target": target, "target_sha256": digest(raw), "resolved_source": resolved_name,
                        "kind": "directory" if resolved.is_dir() else "file", "representation": representation}
            if current in links and links[current] != evidence:
                raise FlowError("Source link changed during snapshot")
            links[current] = evidence
            parts = list(resolved.relative_to(repo).parts)
            candidate = resolved
        else:
            if getattr(candidate, "is_junction", lambda: False)():
                raise FlowError("Source junctions require explicit external dependency handling")
            if not candidate.exists():
                raise FlowError("Source or link target does not exist: " + current)
            if not candidate.resolve().is_relative_to(repo):
                raise FlowError("Source escaped repository")
            parts.append(part)
        if candidate.is_dir() and candidate not in mode_roots and ((candidate / ".git").exists() or (candidate / ".git").is_symlink()):
            # The outer index contains only the gitlink for a submodule.
            # Load its index before interpreting any contained placeholder,
            # even when the selected path names a file inside that checkout.
            prefix = candidate.relative_to(repo).as_posix() + "/"
            modes.update({prefix + child: mode for child, mode in _git_modes(candidate).items()})
            mode_roots.add(candidate)
        if todo and not candidate.is_dir():
            raise FlowError("Source link path traverses a non-directory")
    resolved = repo.joinpath(*parts)
    if not resolved.exists():
        raise FlowError("Source or link target does not exist")
    return resolved


def snapshot(store, repository, paths):
    repo = Path(repository).resolve()
    if not paths:
        raise FlowError("Choose explicit source paths to snapshot")
    files, selected_files, links = {}, {}, {}
    modes = _git_modes(repo)
    mode_roots = {repo}
    def select(source_name, output_name, ancestors=()):
        if _excluded_source(source_name) or _excluded_source(output_name):
            return
        _source_name(output_name)
        candidate = _resolve_source(repo, source_name, modes, links, mode_roots=mode_roots)
        if candidate.is_dir():
            if candidate in ancestors:
                raise FlowError("Source directory link cycle")
            for entry in sorted(candidate.iterdir()):
                select(entry.relative_to(repo).as_posix(), output_name + "/" + entry.name, (*ancestors, candidate))
        elif candidate.is_file():
            selected_files[output_name] = candidate
        else:
            raise FlowError("Unsupported source file type")
    for relative in paths:
        relative = str(relative).replace("\\", "/") if os.name == "nt" else str(relative)
        _source_name(relative)
        select(relative, relative)
    if not selected_files:
        raise FlowError("Empty source snapshot")
    def contents():
        from .core import digest
        for name, candidate in sorted(selected_files.items()):
            if candidate.is_symlink() or not candidate.resolve().is_relative_to(repo):
                raise FlowError("Source changed to a symlink or escaped repository during snapshot")
            before = candidate.stat()
            content = candidate.read_bytes()
            after = candidate.stat()
            if (before.st_size, before.st_mtime_ns, before.st_ino) != (after.st_size, after.st_mtime_ns, after.st_ino):
                raise FlowError("Source changed while being read; stop edits before taking a snapshot")
            original = candidate.relative_to(repo).as_posix()
            files[name] = {"sha256": digest(content), "size": len(content), **_executable_metadata(candidate, original, modes)}
            if original != name:
                files[name]["source_path"] = original
            yield content
        # Resolve again before the batch becomes registered. Replacement of a
        # link with a regular file must not silently retain stale provenance.
        for link_name, evidence in list(links.items()):
            if not (repo / link_name).is_symlink() and modes.get(link_name) != "120000":
                raise FlowError("Source link changed during snapshot")
            resolved = _resolve_source(repo, link_name, modes, links, mode_roots=mode_roots)
            if resolved.relative_to(repo).as_posix() != evidence["resolved_source"]:
                raise FlowError("Source link changed during snapshot")
    store.put_many(contents())
    head = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True)
    manifest = {"schema_version": 1, "files": files, "git_head": head.stdout.strip() if head.returncode == 0 else None,
                "meaning": "Exact selected working-tree bytes, including uncommitted modifications; repository HEAD alone is insufficient"}
    if links:
        manifest["resolved_links"] = links
        manifest["meaning"] += "; contained relative links dereferenced into immutable ordinary files, with resolution evidence; writable alias semantics are not retained"
    sid = fingerprint(manifest)
    _validate_manifest(manifest, sid)
    write_json(store.root / "snapshots" / (sid + ".json"), manifest)
    return {"snapshot_id": sid, **manifest}


def materialize(store, snapshot_id, destination):
    from .core import read_json, digest
    if not isinstance(snapshot_id, str) or not re.fullmatch(r"[0-9a-f]{64}", snapshot_id):
        raise FlowError("Invalid snapshot ID")
    manifest = read_json(store.root / "snapshots" / (snapshot_id + ".json"))
    _validate_manifest(manifest, snapshot_id)
    destination, staging = _new_transfer_destination(destination)
    staging.mkdir(parents=True)
    import contextlib
    with contextlib.closing(store.iter_artifacts(info["sha256"] for info in manifest["files"].values())) as objects:
        for (name, info), (_, content) in zip(manifest["files"].items(), objects):
            if len(content) != info["size"]:
                raise FlowError("Source manifest size mismatch")
            path = child(staging, name)
            atomic_write(path, content)
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
    if not isinstance(snapshot_id, str) or not re.fullmatch(r"[0-9a-f]{64}", snapshot_id):
        raise FlowError("Invalid snapshot ID")
    manifest = read_json(store.root / "snapshots" / (snapshot_id + ".json"))
    _validate_manifest(manifest, snapshot_id)
    destination, staging = _new_transfer_destination(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    import contextlib
    with zipfile.ZipFile(staging, "x", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("manifest.json", json.dumps({"snapshot_id": snapshot_id, "manifest": manifest}))
        with contextlib.closing(store.iter_artifacts(info["sha256"] for info in manifest["files"].values())) as objects:
            for (name, record), (_, content) in zip(manifest["files"].items(), objects):
                if len(content) != record["size"]:
                    raise FlowError("Source manifest size mismatch")
                archive.writestr("files/" + name, content)
    with staging.open("r+b") as stream:
        os.fsync(stream.fileno())
    staging.rename(destination)
    return {"snapshot_id": snapshot_id, "bundle": str(destination), "visibility": "private"}


def receive(store, archive_path, destination, max_bytes=4 * 1024**3):
    import zipfile
    from .core import digest
    if type(max_bytes) is not int or max_bytes <= 0:
        raise FlowError("Transfer maximum bytes must be a positive integer")
    _new_transfer_destination(destination)
    with zipfile.ZipFile(archive_path) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)) or sum(x.file_size for x in archive.infolist()) > max_bytes:
            raise FlowError("Duplicate archive member or bundle too large")
        def unique_pairs(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise FlowError("Duplicate manifest JSON key")
                result[key] = value
            return result
        record = json.loads(archive.read("manifest.json"), object_pairs_hook=unique_pairs)
        if not isinstance(record, dict) or not {"manifest", "snapshot_id"} <= record.keys():
            raise FlowError("Invalid transferred snapshot record")
        manifest, sid = record["manifest"], record["snapshot_id"]
        _validate_manifest(manifest, sid)
        if set(names) != {"manifest.json"} | {"files/" + x for x in manifest["files"]}:
            raise FlowError("Bundle file set differs from manifest")
        for name, info in manifest["files"].items():
            member = archive.getinfo("files/" + name)
            if member.is_dir() or (member.external_attr >> 16) & 0o170000 == 0o120000 or member.file_size != info["size"]:
                raise FlowError("Transferred source member type/size mismatch")
            child(destination, name)
        def contents():
            for name, info in manifest["files"].items():
                content = archive.read("files/" + name)
                if len(content) != info["size"] or digest(content) != info["sha256"]:
                    raise FlowError("Transferred source hash/size mismatch")
                yield content
        store.put_many(contents())
    write_json(store.root / "snapshots" / (sid + ".json"), manifest)
    return materialize(store, sid, destination)
