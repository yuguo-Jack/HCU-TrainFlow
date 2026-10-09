"""Durable Megatron text-log adapter; observation only, never process control."""
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sqlite3
import time

from .core import FlowError, Store, atomic_write, fingerprint, read_json, safe_id


class _ObserverLease:
    def __init__(self, root):
        self.root, self.pid, self.active = root, os.getpid(), True


@contextmanager
def observer_lock(state_dir, *, name="observer.lock"):
    """One writer across API, CLI and daemon, including NDJSON export/monitor.

    Never unlink the lock file: a new inode would allow two independent locks.
    POSIX flock and Windows byte locks are local runtime mechanisms; deployment
    must verify the filesystem's locking semantics before shared-disk use.
    """
    root = Path(state_dir).resolve()
    root.mkdir(parents=True, exist_ok=True)
    with (root / name).open("a+b") as stream:
        if os.name == "nt":
            import msvcrt
            if stream.seek(0, os.SEEK_END) == 0:
                stream.write(b"\0")
                stream.flush()
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
            raise FlowError("Another observer owns this state directory; do not remove the lock file") from exc
        lease = _ObserverLease(root)
        try:
            yield lease
        finally:
            lease.active = False
            release()


def _check_lease(lease, state_dir):
    if (not isinstance(lease, _ObserverLease) or not lease.active or lease.pid != os.getpid()
            or lease.root != Path(state_dir).resolve()):
        raise FlowError("Observer lease is expired, foreign, or belongs to another state directory")


def observe_once(workspace, task, manifest_path, policy_path, state_dir, exit_path=None, lease=None):
    """Normalize one increment and evaluate it in the matching task context."""
    if lease is None:
        with observer_lock(state_dir) as owned:
            return observe_once(workspace, task, manifest_path, policy_path, state_dir, exit_path, owned)
    _check_lease(lease, state_dir)
    from .monitor import check_policy, poll_log
    store = Store(workspace)
    current = store.task(task)
    manifest = validate_manifest(read_json(manifest_path))
    if current["context"] != manifest["context"]:
        raise FlowError("Attempt manifest and remote task context differ")
    policy = read_json(policy_path)
    check_policy(policy)
    if "startup_timeout_seconds" not in policy:
        raise FlowError("Raw training observer requires explicit startup_timeout_seconds")
    receipt = read_json(exit_path) if exit_path and Path(exit_path).exists() else None
    adapted = collect_training_log(state_dir, manifest, exit_receipt=receipt, lease=lease)
    heartbeat = poll_log(store, task, adapted["normalized_log"], policy)
    return {"adapter": adapted, "monitor": heartbeat, "status": heartbeat["status"]}


_NUMBER = r"[+-]?(?:nan|inf(?:inity)?|(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)"
_ITERATION = re.compile(r"\biteration\s+(\d+)\s*/\s*(\d+)\s*\|", re.I)
_CLOCK = re.compile(r"\[(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d(?:\.\d+)?)\]")
_RANK = re.compile(r"\[rank\s*(\d+)\]", re.I)


def _finite(value, name, minimum=0):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < minimum:
        raise FlowError("Invalid " + name)
    return value


def _zone(value):
    if value == "UTC":
        return timezone.utc
    match = re.fullmatch(r"([+-])(\d\d):(\d\d)", value or "")
    if not match or int(match[2]) > 23 or int(match[3]) > 59:
        raise FlowError("log_timezone must be UTC or an explicit offset such as +08:00")
    return timezone((1 if match[1] == "+" else -1) * timedelta(hours=int(match[2]), minutes=int(match[3])))


def validate_manifest(value):
    if not isinstance(value, dict) or type(value.get("schema_version")) is not int or value["schema_version"] != 1:
        raise FlowError("Training attempt manifest requires schema_version=1")
    safe_id(value.get("attempt_id"))
    if not isinstance(value.get("context"), str) or not value["context"]:
        raise FlowError("Attempt context is required")
    if not isinstance(value.get("log_path"), str) or not Path(value["log_path"]).is_absolute():
        raise FlowError("Attempt log_path must be absolute in the observer's namespace")
    for name in ("expected_final_step", "start_step", "log_start_offset"):
        if type(value.get(name)) is not int or value[name] < 0:
            raise FlowError("Attempt requires nonnegative integer " + name)
    if value["expected_final_step"] <= value["start_step"]:
        raise FlowError("Expected final step must exceed the checkpoint/start step")
    _finite(value.get("started_at"), "attempt started_at")
    _zone(value.get("log_timezone"))
    identity = value.get("process")
    if (not isinstance(identity, dict) or type(identity.get("pid")) is not int or identity["pid"] <= 0
            or not isinstance(identity.get("start_ticks"), str) or not identity["start_ticks"].isdecimal()
            or not isinstance(identity.get("boot_id"), str) or not identity["boot_id"]
            or not isinstance(identity.get("pid_namespace"), str) or not identity["pid_namespace"]):
        raise FlowError("Process identity requires pid, decimal start_ticks, boot_id and pid_namespace")
    return value


def process_identity(pid, proc_root=Path("/proc")):
    """Linux PID identity, robust to PID reuse and names containing parentheses."""
    root = Path(proc_root)
    if type(pid) is not int or pid <= 0:
        raise FlowError("PID must be a positive integer")
    try:
        record = (root / str(pid) / "stat").read_text()
        fields = record.rsplit(")", 1)[1].split()
        if not fields[19].isdecimal():
            raise ValueError("Invalid process start ticks")
        identity = {"pid": pid, "start_ticks": fields[19],
                    "boot_id": (root / "sys/kernel/random/boot_id").read_text().strip(),
                    "pid_namespace": os.readlink(root / str(pid) / "ns/pid")}
        return {"status": "exited" if fields[0] in {"Z", "X"} else "alive", "identity": identity,
                "process_state": fields[0]}
    except FileNotFoundError:
        return ({"status": "unknown", "reason": "process-exists-but-identity-metadata-missing"}
                if (root / str(pid)).exists() else {"status": "exited", "reason": "pid-absent"})
    except (OSError, IndexError, ValueError) as exc:
        return {"status": "unknown", "reason": type(exc).__name__ + ": " + str(exc)}


def _numeric(text):
    if re.fullmatch(r"[+-]?\d+", text):
        return int(text)
    value = float(text)
    return value if math.isfinite(value) else str(value)


def parse_megatron_line(line, *, log_timezone="UTC", observed_at=None):
    """Parse verified stdout shapes; unmatched text is not training progress."""
    observed_at = time.time() if observed_at is None else observed_at
    parsed = {"timestamp": observed_at, "timestamp_basis": "first-observed-no-source-clock"}
    clock = _CLOCK.search(line)
    if clock:
        parsed.update(timestamp=datetime.fromisoformat(clock[1]).replace(tzinfo=_zone(log_timezone)).timestamp(),
                      timestamp_basis="source-log-clock")
    fields = {}
    for section in line.split("|"):
        match = re.search(r"([^|:]+):\s*(" + _NUMBER + r")\s*$", section.strip(), re.I)
        if match:
            fields[match[1].strip().lower()] = _numeric(match[2])
    iteration = _ITERATION.search(line)
    if iteration:
        parsed.update(kind="iteration", step=int(iteration[1]), total_steps=int(iteration[2]), metrics=fields)
        losses = {key: val for key, val in fields.items() if "loss" in key and key != "loss scale"}
        parsed["losses"] = losses
        if losses:
            parsed["loss"] = losses.get("lm loss", next(iter(losses.values())))
        if any(isinstance(value, str) for value in losses.values()) or fields.get("number of nan iterations", 0) != 0:
            parsed["loss"] = "nan"
            parsed["nonfinite"] = True
        if "grad norm" in fields:
            parsed["grad_norm"] = fields["grad norm"]
            if isinstance(parsed["grad_norm"], str):
                parsed["nonfinite"] = True
        if "elapsed time per iteration (ms)" in fields:
            duration = fields["elapsed time per iteration (ms)"]
            if not isinstance(duration, (int, float)) or duration <= 0:
                parsed["warning"] = "invalid-reported-iteration-duration"
            else:
                parsed["step_seconds_reported"] = duration / 1000.0
        else:
            parsed["warning"] = "iteration-duration-missing"
        return parsed
    if "memory (MB)" in line:
        rank = _RANK.search(line)
        memory = {}
        for label, key in (("allocated", "allocator_allocated_bytes"), ("max allocated", "allocator_peak_allocated_bytes"),
                           ("reserved", "allocator_reserved_bytes"), ("max reserved", "allocator_peak_reserved_bytes"),
                           ("total device memory used", "device_memory_bytes")):
            if label in fields and isinstance(fields[label], (int, float)) and fields[label] >= 0:
                memory[key] = round(fields[label] * 1024 * 1024)
        if not memory:
            return {**parsed, "kind": "warning", "warning": "unparsed-memory-report"}
        return {**parsed, "kind": "memory", "rank": rank[1] if rank else "unknown", "memory": memory,
                "memory_source_unit": "MiB (source prints MB; divisor is 1024**2)"}
    # PyTorch HIP can report torch.AcceleratorError with "CUDA error" in its
    # message. Capture the qualified exception line, without classifying prose
    # mentioning an Error type as a new fatal event.
    exception_line = re.match(r"^(?:\[rank\s*\d+\]:\s*)?(?:[A-Za-z_]\w*\.)*[A-Za-z_]\w*(?:Error|Exception):", line.strip(), re.I)
    if exception_line or re.search(r"(?:RuntimeError|AssertionError|OutOfMemoryError|ChildFailedError):|Segmentation fault|Traceback \(most recent call last\):", line, re.I):
        return {**parsed, "kind": "fatal", "fatal": line.strip()[:4000]}
    if re.search(r"\biteration\s+\d+\s*/", line, re.I):
        return {**parsed, "kind": "warning", "warning": "unparsed-iteration-record"}
    return None


def _exit_status(receipt, manifest, now):
    if receipt is None:
        return None, []
    required = {"attempt_id": manifest["attempt_id"], "context": manifest["context"], "process": manifest["process"]}
    if (not isinstance(receipt, dict) or any(receipt.get(key) != val for key, val in required.items())
            or type(receipt.get("exit_code")) is not int):
        return None, ["exit-receipt-identity-mismatch"]
    finished = receipt.get("finished_at")
    if (isinstance(finished, bool) or not isinstance(finished, (int, float)) or not math.isfinite(finished)
            or not manifest["started_at"] <= finished <= now):
        return None, ["exit-receipt-time-invalid"]
    return receipt, []


def _verify_log_seal(receipt, manifest, state, db):
    """Bind late-read, clockless iterations to bytes sealed by their launcher."""
    seal = receipt.get("log_evidence") if receipt else None
    if seal is None:
        return False, []
    if state.get("completed") and state.get("verified_log_receipt") == fingerprint(receipt):
        return True, []  # Already verified immutable receipt; do not reread a reused path.
    if (not isinstance(seal, dict) or seal.get("path") != manifest["log_path"]
            or type(seal.get("bytes")) is not int or seal["bytes"] < manifest["log_start_offset"]
            or not isinstance(seal.get("sha256"), str) or not re.fullmatch(r"[0-9a-f]{64}", seal["sha256"])):
        return False, ["exit-log-seal-invalid"]
    try:
        with Path(manifest["log_path"]).open("rb") as stream:
            before = os.fstat(stream.fileno())
            sha = hashlib.sha256()
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                sha.update(chunk)
            # A rotated/replaced path can have the same length while old
            # clockless samples refer to different bytes at those offsets.
            # Bind each such progress observation to its actual sealed line.
            for row in db.execute("SELECT payload FROM samples WHERE json_extract(payload,'$.attempt_id')=? "
                                  "AND json_extract(payload,'$.progress_observed')=1 "
                                  "AND COALESCE(json_extract(payload,'$.timestamp_basis'),'')!='source-log-clock' ORDER BY seq",
                                  (manifest["attempt_id"],)):
                source = json.loads(row["payload"])["source"]
                if source["path"] != seal["path"] or source["offset"] + source["bytes"] > seal["bytes"]:
                    return False, ["exit-log-seal-does-not-cover-clockless-progress"]
                stream.seek(source["offset"])
                if hashlib.sha256(stream.read(source["bytes"])).hexdigest() != source["sha256"]:
                    return False, ["exit-log-seal-does-not-cover-clockless-progress"]
            after = os.fstat(stream.fileno())
        if (before.st_size, before.st_mtime_ns, before.st_ino) != (after.st_size, after.st_mtime_ns, after.st_ino):
            return False, ["exit-log-seal-file-changed"]
        if after.st_size != seal["bytes"] or sha.hexdigest() != seal["sha256"]:
            return False, ["exit-log-seal-hash-or-size-mismatch"]
    except OSError:
        return False, ["exit-log-seal-file-unavailable"]
    if state["offset"] != seal["bytes"] or state.get("backlog"):
        return False, ["exit-log-seal-not-fully-consumed"]
    state["verified_log_receipt"] = fingerprint(receipt)
    return True, []


def _base(manifest, state, now, kind, *, progress=False):
    sample = {"context": manifest["context"], "attempt_id": manifest["attempt_id"],
              "attempt_started_at": manifest["started_at"], "timestamp": now, "observed_at": now, "step": state["step"],
              "expected_final_step": manifest["expected_final_step"], "process_identity": manifest["process"],
              "start_step": manifest["start_step"],
              "observation_kind": kind, "progress_observed": progress, "phase": state["phase"],
              "adapter_warnings": list(state["warnings"]), "fatal_errors": list(state["fatal_errors"]),
              "completed": state.get("completed", False), "memory_by_rank": state.get("memory_by_rank", {})}
    for key in ("loss", "grad_norm", "losses", "metrics", "step_seconds_reported"):
        if key in state:
            sample[key] = state[key]
    physical = [v["device_memory_bytes"] for v in sample["memory_by_rank"].values() if "device_memory_bytes" in v]
    if physical:
        sample["device_memory_bytes"] = max(physical)
        sample["memory_coverage"] = "maximum physical usage among reporting ranks only; not full cluster coverage"
    return sample


def _add(db, sample, key):
    db.execute("INSERT OR IGNORE INTO samples(event_id,payload) VALUES(?,?)",
               (key, json.dumps(sample, sort_keys=True, ensure_ascii=False, allow_nan=False)))


def _export(db, output):
    """Append immutable samples; rebuild only if an interrupted export disagrees."""
    prior = db.execute("SELECT value FROM meta WHERE key='export'").fetchone()
    cursor = json.loads(prior[0]) if prior else {"seq": 0, "size": 0, "tail": ""}
    valid = output.exists() and output.stat().st_size == cursor["size"]
    if valid and cursor["size"]:
        with output.open("rb") as stream:
            stream.seek(max(0, cursor["size"] - 512))
            valid = hashlib.sha256(stream.read()).hexdigest() == cursor["tail"]
    if not valid:
        content = b"".join((row["payload"] + "\n").encode("utf-8") for row in db.execute("SELECT payload FROM samples ORDER BY seq"))
        atomic_write(output, content)
        sequence = db.execute("SELECT COALESCE(MAX(seq),0) FROM samples").fetchone()[0]
    else:
        sequence = cursor["seq"]
        with output.open("ab") as stream:
            for row in db.execute("SELECT seq,payload FROM samples WHERE seq>? ORDER BY seq", (sequence,)):
                stream.write((row["payload"] + "\n").encode("utf-8"))
                sequence = row["seq"]
            stream.flush()
            os.fsync(stream.fileno())
    size = output.stat().st_size
    with output.open("rb") as stream:
        stream.seek(max(0, size - 512))
        tail = hashlib.sha256(stream.read()).hexdigest()
    db.execute("INSERT OR REPLACE INTO meta VALUES('export',?)", (json.dumps({"seq": sequence, "size": size, "tail": tail}),))


def collect_training_log(state_dir, manifest, *, now=None, process_status=None, exit_receipt=None, lease=None):
    """One bounded, crash-recoverable poll; no process launch, kill or restart.

    PID identity and receipts refer to the same observer namespace. A new
    attempt ID is mandatory after restart; state never infers a restart from a
    PID or line counter. ``process_status`` is an injection seam for site
    adapters/tests, and must contain an independently verified process identity.
    """
    if lease is None:
        with observer_lock(state_dir) as owned:
            return collect_training_log(state_dir, manifest, now=now, process_status=process_status,
                                        exit_receipt=exit_receipt, lease=owned)
    _check_lease(lease, state_dir)
    validate_manifest(manifest)
    now = time.time() if now is None else _finite(now, "observation time")
    root = Path(state_dir).resolve()
    root.mkdir(parents=True, exist_ok=True)
    output = root / "normalized.jsonl"
    db = sqlite3.connect(root / "training-log.sqlite3", timeout=30)
    db.row_factory = sqlite3.Row
    try:
        db.executescript("CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);"
                         "CREATE TABLE IF NOT EXISTS samples(seq INTEGER PRIMARY KEY AUTOINCREMENT,event_id TEXT UNIQUE,payload TEXT NOT NULL);"
                         "CREATE TABLE IF NOT EXISTS raw_lines(attempt TEXT,hash TEXT,content BLOB,PRIMARY KEY(attempt,hash));")
        db.execute("BEGIN IMMEDIATE")
        context = db.execute("SELECT value FROM meta WHERE key='context'").fetchone()
        if context and context[0] != manifest["context"]:
            raise FlowError("Observer context changed; use a new state directory")
        db.execute("INSERT OR IGNORE INTO meta VALUES('context',?)", (manifest["context"],))
        key = "attempt:" + manifest["attempt_id"]
        existing = db.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
        state = json.loads(existing[0]) if existing else {"manifest_hash": fingerprint(manifest), "offset": manifest["log_start_offset"],
                    "step": manifest["start_step"], "max_step": manifest["start_step"], "phase": "startup", "started_at": manifest["started_at"],
                    "warnings": [], "fatal_errors": [], "memory_by_rank": {}, "iterations": 0}
        if state["manifest_hash"] != fingerprint(manifest):
            raise FlowError("Attempt manifest changed; establish a new attempt ID")
        active = db.execute("SELECT value FROM meta WHERE key='active_attempt'").fetchone()
        if active and active[0] != manifest["attempt_id"] and existing:
            raise FlowError("Cannot reactivate an old attempt after a newer attempt")
        if active and active[0] != manifest["attempt_id"]:
            old = db.execute("SELECT value FROM meta WHERE key=?", ("attempt:" + active[0],)).fetchone()
            if old and manifest["started_at"] < json.loads(old[0]).get("started_at", 0):
                raise FlowError("New attempt starts before the previously observed attempt")
        db.execute("INSERT OR REPLACE INTO meta VALUES('active_attempt',?)", (manifest["attempt_id"],))
        original_count = db.execute("SELECT count(*) FROM samples").fetchone()[0]
        current_process = process_status if process_status is not None else process_identity(manifest["process"]["pid"])
        receipt, receipt_warnings = _exit_status(exit_receipt, manifest, now)
        warnings = list(receipt_warnings)
        if receipt is None and state.get("exit_receipt"):
            receipt, prior_warnings = _exit_status(state["exit_receipt"], manifest, now)
            warnings.extend(prior_warnings)
        if receipt is not None and state.get("exit_receipt") and state["exit_receipt"] != receipt:
            state["fatal_errors"].append("exit-receipt-changed-after-observation")
            state["completed"] = False
        if receipt is not None:
            state["exit_receipt"] = receipt
        matched_identity = current_process.get("identity") == manifest["process"]
        if current_process.get("status") == "alive" and not matched_identity:
            warnings.append("pid-reused-or-observer-namespace-mismatch")
        elif current_process.get("status") == "unknown":
            warnings.append("process-liveness-unknown")
        may_read = ((current_process.get("status") == "alive" and matched_identity) or receipt is not None
                    or current_process.get("status") == "exited")
        # A valid exit receipt belongs to the frozen attempt. Do not keep reading
        # a reused path after terminal completion on subsequent polls.
        if not state.get("completed") and may_read:
            try:
                with Path(manifest["log_path"]).open("rb") as stream:
                    stat_value = os.fstat(stream.fileno())
                    file_id = [stat_value.st_dev, stat_value.st_ino]
                    prefix = stream.read(min(stat_value.st_size, 128))
                    prior_length = state.get("prefix_length", 0)
                    changed = (stat_value.st_size < state["offset"] or (state.get("file_id") and state["file_id"] != file_id)
                               or (state.get("prefix_hash") and hashlib.sha256(prefix[:prior_length]).hexdigest() != state["prefix_hash"]))
                    if changed:
                        warnings.append("raw-log-rotated-or-truncated; continuity-requires-review")
                        state["offset"] = 0
                    state.update(file_id=file_id, prefix_length=len(prefix), prefix_hash=hashlib.sha256(prefix).hexdigest())
                    stream.seek(state["offset"])
                    # Limit one poll to 16 MiB; a huge historical log must not
                    # prevent liveness polling indefinitely.
                    read_bytes = 0
                    while read_bytes < 16 * 1024**2:
                        position = stream.tell()
                        raw = stream.readline(1024**2)
                        if not raw:
                            break
                        if not raw.endswith(b"\n") and not (receipt is not None and len(raw) < 1024**2):
                            if len(raw) == 1024**2:
                                warnings.append("raw-line-exceeds-1MiB; requires-explicit-log-repair")
                            break
                        read_bytes += len(raw)
                        state["offset"] = stream.tell()
                        raw_hash = hashlib.sha256(raw).hexdigest()
                        cursor = db.execute("INSERT OR IGNORE INTO raw_lines VALUES(?,?,?)", (manifest["attempt_id"], raw_hash, raw))
                        if not cursor.rowcount:
                            continue
                        try:
                            parsed = parse_megatron_line(raw.decode("utf-8"), log_timezone=manifest["log_timezone"], observed_at=now)
                        except (UnicodeError, ValueError):
                            warnings.append("raw-record-decoding-or-timestamp-error")
                            continue
                        if parsed is None:
                            continue
                        if parsed["timestamp"] < manifest["started_at"] or parsed["timestamp"] > now + 30:
                            warnings.append("source-log-clock-outside-attempt-window")
                            parsed["timestamp"] = now
                            parsed["timestamp_basis"] = "collector-clock-source-time-invalid"
                        if parsed.get("warning"):
                            warnings.append(parsed["warning"])
                        kind = parsed["kind"]
                        if kind == "iteration":
                            if parsed["timestamp_basis"] != "source-log-clock":
                                warnings.append("iteration-time-is-collector-time; wall-clock-performance-unverified")
                            if parsed["total_steps"] != manifest["expected_final_step"]:
                                state["fatal_errors"].append("iteration-total-does-not-match-attempt-contract")
                            if not manifest["start_step"] <= parsed["step"] <= parsed["total_steps"]:
                                state["fatal_errors"].append("iteration-step-outside-attempt-contract")
                            if parsed["step"] < state["step"]:
                                state["fatal_errors"].append("step-regressed-without-new-attempt")
                            state.update(step=parsed["step"], max_step=max(state["max_step"], parsed["step"]))
                            if parsed["step"] > manifest["start_step"]:
                                state["phase"] = "training"
                            state["iterations"] += 1
                            for field in ("loss", "grad_norm", "losses", "metrics", "step_seconds_reported"):
                                if field in parsed:
                                    state[field] = parsed[field]
                            if parsed.get("nonfinite"):
                                state["fatal_errors"].append("nonfinite-training-numerics-observed")
                        elif kind == "memory":
                            state["memory_by_rank"][parsed["rank"]] = {**parsed["memory"], "observed_at": now,
                                                                       "source_unit": parsed["memory_source_unit"]}
                        elif kind == "fatal":
                            state["fatal_errors"].append(parsed["fatal"])
                        state["fatal_errors"] = list(dict.fromkeys(state["fatal_errors"]))
                        sample = _base(manifest, state, parsed["timestamp"], kind if kind in {"iteration", "memory"} else "lifecycle",
                                       progress=kind == "iteration" and parsed["step"] > manifest["start_step"])
                        sample.update(observed_at=now, source_record_kind=kind, timestamp_basis=parsed["timestamp_basis"], source={"path": manifest["log_path"], "offset": position,
                                      "bytes": len(raw), "sha256": raw_hash})
                        _add(db, sample, manifest["attempt_id"] + ":raw:" + raw_hash)
                    state["backlog"] = state["offset"] < stat_value.st_size
            except OSError as exc:
                warnings.append("raw-log-unavailable:" + type(exc).__name__)
        transient = ("raw-log-unavailable:", "process-liveness-unknown", "exit-receipt-")
        state["warnings"] = list(dict.fromkeys(state["warnings"] + [value for value in warnings if not value.startswith(transient)]))
        if receipt:
            sealed, seal_warnings = _verify_log_seal(receipt, manifest, state, db)
            warnings.extend(seal_warnings)
            state["log_seal_verified"] = sealed
            if any(warning != "exit-log-seal-not-fully-consumed" for warning in seal_warnings):
                state["fatal_errors"] = list(dict.fromkeys(state["fatal_errors"] + seal_warnings))
        if receipt and not state.get("backlog"):
            if receipt["exit_code"] == 0 and state["max_step"] >= manifest["expected_final_step"] and not state["fatal_errors"]:
                state.update(completed=True, phase="finished")
            else:
                state.update(completed=False, phase="failed")
                reason = "training-exit-code-nonzero" if receipt["exit_code"] else "expected-final-step-not-observed-or-numerical-failure"
                state["fatal_errors"] = list(dict.fromkeys(state["fatal_errors"] + [reason]))
        elif current_process.get("status") in {"exited", "unknown"} or not matched_identity:
            if not state.get("completed"):
                state["phase"] = "unknown"
        heartbeat = _base(manifest, state, now, "heartbeat")
        heartbeat["adapter_warnings"] = list(dict.fromkeys(heartbeat["adapter_warnings"] + warnings))
        heartbeat["process_observation"] = current_process
        if current_process.get("status") == "alive" and matched_identity:
            heartbeat["job_alive"] = True
        elif current_process.get("status") in {"alive", "exited"}:
            heartbeat["job_alive"] = False
        if receipt:
            heartbeat["exit_receipt"] = receipt
            heartbeat["log_seal_verified"] = state.get("log_seal_verified", False)
        _add(db, heartbeat, manifest["attempt_id"] + ":heartbeat:" + fingerprint(heartbeat))
        db.execute("INSERT OR REPLACE INTO meta VALUES(?,?)", (key, json.dumps(state, allow_nan=False)))
        db.commit()  # Raw cursor + immutable samples must survive an export crash.
        db.execute("BEGIN IMMEDIATE")
        _export(db, output)
        db.commit()
        return {"normalized_log": str(output), "samples_written": db.execute("SELECT count(*) FROM samples").fetchone()[0] - original_count,
                "last_observation": heartbeat, "raw_offset": state["offset"], "backlog": state.get("backlog", False),
                "recovery_action": "none; observation adapter never controls training"}
    except BaseException:
        db.rollback()
        raise
    finally:
        db.close()
