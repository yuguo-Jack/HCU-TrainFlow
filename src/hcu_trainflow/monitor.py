"""Durable normalized-log watcher, incidents and reconnectable agent inbox."""
import json
import math
import os
from pathlib import Path
import time

from .core import FlowError, fingerprint, read_json, utc, write_json


def check_policy(policy):
    required = {"stall_seconds", "telemetry_seconds", "recovery_seconds", "min_progress_samples"}
    if required - policy.keys():
        raise FlowError("Monitoring thresholds must be configured for the task")
    for key in required:
        value = policy[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
            raise FlowError("Invalid monitor threshold: " + key)
    if not isinstance(policy["min_progress_samples"], int) or policy["min_progress_samples"] < 2:
        raise FlowError("Recovery needs at least two advancing progress observations")
    for key in ("memory_limit_bytes", "required_headroom_bytes", "reference_step_seconds", "slowdown_ratio"):
        if key in policy and (not isinstance(policy[key], (int, float)) or not math.isfinite(policy[key]) or policy[key] < 0):
            raise FlowError("Invalid optional threshold: " + key)
    if not isinstance(policy.get("performance_window", 5), int) or policy.get("performance_window", 5) < 2:
        raise FlowError("performance_window must be an integer >=2")


def _record_progress(progress, sample):
    """Keep attempt clocks and monotonic progress independent of sample retention."""
    attempt = progress.get(sample["attempt_id"])
    if attempt is None:
        progress[sample["attempt_id"]] = {
            "started_at": sample["timestamp"], "last_progress_at": sample["timestamp"],
            "max_step": sample["step"], "last_step": sample["step"],
            "progress_samples": 1, "regressed": False,
        }
        return
    attempt["started_at"] = min(attempt["started_at"], sample["timestamp"])
    if sample["step"] < attempt["last_step"]:
        attempt["regressed"] = True
    if sample["step"] > attempt["max_step"]:
        attempt["last_progress_at"] = max(attempt["last_progress_at"], sample["timestamp"])
        attempt["max_step"] = sample["step"]
        attempt["progress_samples"] += 1
    attempt["last_step"] = sample["step"]


def observation_issues(samples, policy, now=None, *, progress=None):
    check_policy(policy)
    now = time.time() if now is None else now
    if not samples:
        return [{"kind": "telemetry-missing", "severity": "warning", "detail": "No valid observations"}]
    latest = samples[-1]
    issues = []
    age = now - latest["timestamp"]
    if age < -30:
        issues.append({"kind": "clock-mismatch", "severity": "warning", "detail": "Observation timestamp is ahead of watcher"})
    if age > policy["telemetry_seconds"] and not latest.get("completed", False):
        issues.append({"kind": "telemetry-stale", "severity": "critical", "detail": "Collector/log path may have stopped; training state unknown"})
    if latest.get("job_alive") is False and not latest.get("completed", False):
        issues.append({"kind": "job-exited", "severity": "critical", "detail": "Check scheduler and recovery owner"})
    current = [x for x in samples if x["attempt_id"] == latest["attempt_id"]]
    if progress is None:
        progress = {}
        for sample in current:
            _record_progress(progress, sample)
    attempt = progress[latest["attempt_id"]]
    advancing = [current[0]]
    for sample in current[1:]:
        if sample["step"] > advancing[-1]["step"]:
            advancing.append(sample)
    if attempt["regressed"]:
        issues.append({"kind": "step-regressed", "severity": "critical", "detail": "Step went backwards without a new attempt"})
    if now - attempt["last_progress_at"] > policy["stall_seconds"] and not latest.get("completed", False):
        issues.append({"kind": "training-stalled", "severity": "critical", "detail": "Liveness alone does not prove training progress"})
    if latest.get("recovery_state") in {"restarting", "recovering", "restored"}:
        recovered = attempt["progress_samples"] >= policy["min_progress_samples"] and latest.get("checkpoint_verified") is True
        if not recovered and now - attempt["started_at"] > policy["recovery_seconds"]:
            issues.append({"kind": "recovery-timeout", "severity": "critical", "detail": "Restart has not produced verified checkpoint and advancing steps"})
    for name in ("loss", "grad_norm"):
        value = latest.get(name)
        if value is not None and (not isinstance(value, (int, float)) or not math.isfinite(value)):
            issues.append({"kind": "nonfinite-" + name, "severity": "critical", "detail": "Preserve numerical evidence before recovery"})
    limit = policy.get("memory_limit_bytes")
    if limit and latest.get("device_memory_bytes") is not None:
        reserve = policy.get("required_headroom_bytes", 0)
        if limit - latest["device_memory_bytes"] < reserve:
            issues.append({"kind": "memory-headroom", "severity": "warning", "detail": "Device memory leaves less than the stage's configured reserve"})
    reference = policy.get("reference_step_seconds")
    if reference and len(advancing) >= policy.get("performance_window", 5):
        subset = advancing[-policy.get("performance_window", 5):]
        delta = subset[-1]["step"] - subset[0]["step"]
        ratio = (subset[-1]["timestamp"] - subset[0]["timestamp"]) / delta / reference if delta else None
        if ratio and ratio > policy.get("slowdown_ratio", 1.2):
            issues.append({"kind": "sustained-slowdown", "severity": "warning", "detail": {"step_time_ratio": ratio}})
    return issues


def poll_log(store, tid, logfile, policy, now=None):
    """Cursor, deduplication, observations and incident transitions commit together."""
    check_policy(policy)
    with store.db() as db:
        db.execute("BEGIN IMMEDIATE")
        heartbeat = _poll_transaction(store, db, tid, logfile, policy, now)
    # Heartbeat is a derived receipt. A crash here cannot lose the durable cursor.
    write_json(store.root / "watch" / (tid + "-heartbeat.json"), heartbeat)
    return heartbeat


def _poll_transaction(store, db, tid, logfile, policy, now):
    task = store.task(tid)
    path = Path(logfile).resolve()
    key = "watch:" + tid
    row = db.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
    previous = json.loads(row[0]) if row else {"offset": 0, "samples": [], "active_incidents": {}, "path": str(path),
                                             "context_epoch": task['context_epoch']}
    if previous.get("context", task["context"]) != task["context"]:
        raise FlowError("Watcher context changed; establish a new task/watch scope")
    if previous.get('context_epoch', 0) != task['context_epoch']:
        raise FlowError("Watcher context epoch changed or legacy scope is ambiguous; establish a new task/watch scope")
    if previous["path"] != str(path):
        raise FlowError("Watcher log path changed; use an explicit new watcher workspace")
    progress = previous.get("progress")
    if progress is None:
        # Older cursors retained only 1000 samples. Recover their clocks from the
        # transactionally retained observations rather than resetting on upgrade.
        progress = {}
        for event in db.execute("SELECT payload FROM events WHERE task=? AND kind='observation' "
                                "AND json_extract(payload,'$.context')=? AND seq>? ORDER BY seq",
                                (tid, task["context"], task['context_epoch'])):
            _record_progress(progress, json.loads(event["payload"]))
        if not progress:
            for sample in previous["samples"]:
                _record_progress(progress, sample)
    errors, offset = [], previous["offset"]
    import io
    available = path.exists()
    if not available:
        errors.append("log-unavailable")
    with (path.open("rb") if available else io.BytesIO()) as stream:
        stat = os.fstat(stream.fileno()) if available else None
        size = stat.st_size if stat else 0
        file_id = [stat.st_dev, stat.st_ino] if stat and stat.st_ino else None
        prefix = stream.read(min(size, 128))
        prefix_length = len(prefix)
        prefix_hash = fingerprint(list(prefix))
        old_length = previous.get("prefix_length", 128 if previous.get("prefix") else 0)
        rotated = (size < offset
                   or (previous.get("file_id") and file_id and previous["file_id"] != file_id)
                   or (previous.get("prefix") and previous["prefix"] != fingerprint(list(prefix[:old_length]))))
        if rotated:
            offset = 0
            errors.append("log-rotated-or-truncated; prior observations retained")
        elif offset and "prefix_length" not in previous and not previous.get("prefix"):
            # Legacy short-file cursors had no prefix proof. Re-read once;
            # observation IDs prevent replay from counting as fresh progress.
            offset = 0
            errors.append("watch-cursor-upgraded; replaying unverified short-file prefix")
        stream.seek(offset)
        for raw in stream:
            if not raw.endswith(b"\n"):
                break  # Do not consume a partially written JSON record.
            offset += len(raw)
            try:
                sample = json.loads(raw)
                if not isinstance(sample, dict):
                    raise ValueError("observation must be an object")
                if sample.get("context", task["context"]) != task["context"]:
                    raise ValueError("observation belongs to another context")
                sample["context"] = task["context"]
                if not isinstance(sample.get("attempt_id"), str) or not sample["attempt_id"]:
                    raise ValueError("attempt_id required")
                if not isinstance(sample.get("step"), int) or isinstance(sample["step"], bool) or sample["step"] < 0:
                    raise ValueError("nonnegative integer step required")
                timestamp = sample.get("timestamp")
                if isinstance(timestamp, bool) or not isinstance(timestamp, (int, float)) or not math.isfinite(timestamp):
                    raise ValueError("finite UTC epoch timestamp required")
                # Non-finite numerical samples become incidents, but JSON artifacts remain valid.
                for name in ("loss", "grad_norm"):
                    if isinstance(sample.get(name), float) and not math.isfinite(sample[name]):
                        sample[name] = str(sample[name])
                if "device_memory_bytes" in sample and (not isinstance(sample["device_memory_bytes"], (int, float)) or not math.isfinite(sample["device_memory_bytes"])):
                    raise ValueError("invalid device memory")
                for flag in ("job_alive", "completed", "checkpoint_verified"):
                    if flag in sample and not isinstance(sample[flag], bool):
                        raise ValueError("invalid boolean: " + flag)
                event_id = "observation-" + fingerprint({"task": tid, "sample": sample})
                existed = db.execute("SELECT 1 FROM events WHERE event_id=?", (event_id,)).fetchone()
                store.event(db, tid, "observation", sample, event_id)
                if not existed:
                    if previous["samples"] and timestamp < previous["samples"][-1]["timestamp"]:
                        errors.append("observation-time-regressed")
                    previous["samples"].append(sample)
                    _record_progress(progress, sample)
            except (ValueError, TypeError, KeyError) as exc:
                errors.append("invalid-log-record:" + str(exc))
    samples = previous["samples"][-1000:]
    issues = observation_issues(samples, policy, now, progress=progress)
    if errors:
        issues.append({"kind": "collector-input-warning", "severity": "warning", "detail": errors})
    active = previous["active_incidents"]
    next_active = {}
    for issue in issues:
        issue_key = issue["kind"]
        incident = active.get(issue_key)
        if not incident:
            import uuid
            incident = uuid.uuid4().hex
            store.event(db, tid, "incident-opened", {"incident_id": incident, "context": task["context"], "attempt_id": samples[-1]["attempt_id"] if samples else None,
                        "recovery_owner": task["spec"].get("recovery_owner", "unassigned"), **issue}, channel="agent")
        next_active[issue_key] = incident
    for issue_key in active.keys() - next_active.keys():
        store.event(db, tid, "incident-cleared", {"incident_id": active[issue_key], "context": task["context"], "kind": issue_key}, channel="agent")
    heartbeat = {"schema_version": 1, "task_id": tid, "checked_at": time.time() if now is None else now,
                 "status": "attention" if issues else "healthy-observed", "issues": issues,
                 "last_observation": samples[-1] if samples else None, "context": task["context"],
                 "context_epoch": task['context_epoch'],
                 "recovery_action": "none; external owner retains control"}
    db.execute("INSERT OR REPLACE INTO meta VALUES(?,?)", (key, json.dumps({"offset": offset, "prefix": prefix_hash,
               "prefix_length": prefix_length, "file_id": file_id, "progress": progress, "samples": samples,
               "active_incidents": next_active, "path": str(path), "context": task["context"],
               "context_epoch": task['context_epoch']}, allow_nan=False)))
    return heartbeat


def check_heartbeat(path, max_age, now=None):
    value = read_json(path)
    age = (time.time() if now is None else now) - value["checked_at"]
    return {"status": "pass" if 0 <= age <= max_age else "fail", "age_seconds": age,
            "reason": "This observer must be hosted independently of the watched daemon"}


def import_events(store, peer, records):
    if not records:
        return {"imported": 0}
    with store.db() as db:
        db.execute("BEGIN IMMEDIATE")
        row = db.execute("SELECT seq FROM cursors WHERE peer=?", (peer,)).fetchone()
        cursor = row[0] if row else 0
        count = 0
        for record in records:
            if record["seq"] <= cursor:
                continue
            if record["seq"] != cursor + 1:
                raise FlowError("Event gap: retrieve the missing remote sequence before proceeding")
            store.event(db, record["task"], record["kind"], record["payload"], peer + ":" + record["event_id"],
                        "agent" if record["kind"].startswith("incident-") else None)
            cursor = record["seq"]
            count += 1
        db.execute("INSERT OR REPLACE INTO cursors VALUES(?,?)", (peer, cursor))
    return {"imported": count, "cursor": cursor, "next": "Reconcile current attempt/job/checkpoint before any control action"}


def inbox(store, action="list", event_id=None, owner=None):
    with store.db() as db:
        if action == "list":
            return [dict(row) for row in db.execute("SELECT o.*,e.task,e.kind,e.payload FROM outbox o JOIN events e USING(event_id) ORDER BY e.seq")]
        if action not in {"claim", "complete", "retry"} or not owner:
            raise FlowError("Inbox action requires an explicit consumer")
        db.execute("BEGIN IMMEDIATE")
        row = db.execute("SELECT * FROM outbox WHERE event_id=?", (event_id,)).fetchone()
        if not row:
            raise FlowError("Unknown inbox event")
        detail = json.loads(row["detail"] or "{}")
        if action == "claim":
            if row["status"] not in {"pending", "retry"}:
                raise FlowError("Event already claimed/completed; inspect before retry")
            detail = {"owner": owner, "claimed_at": utc()}
            status = "claimed"
        else:
            if row["status"] != "claimed" or detail.get("owner") != owner:
                raise FlowError("Only the claiming owner can acknowledge or retry")
            status = "completed" if action == "complete" else "retry"
        db.execute("UPDATE outbox SET status=?,detail=?,attempts=attempts+? WHERE event_id=?", (status, json.dumps(detail), int(action == "claim"), event_id))
    return {"event_id": event_id, "status": status, **detail}
