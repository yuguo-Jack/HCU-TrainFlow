"""Durable normalized-log watcher, incidents and reconnectable agent inbox."""
import json
import math
import os
from pathlib import Path
import time

from .core import FlowError, fingerprint, read_json, utc, write_json


_PHASES = {"startup", "training", "finished", "failed", "unknown"}
_KINDS = {"iteration", "memory", "heartbeat", "lifecycle"}
_PROGRESS_VERSION = 3


def _finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _modern(sample):
    return any(key in sample for key in ("phase", "observation_kind", "progress_observed"))


def _iteration(sample):
    # Legacy normalized rows represented iterations. Explicit modern heartbeats
    # and memory reports must never advance or regress the iteration clock.
    return not _modern(sample) or (sample.get("observation_kind") == "iteration"
                                   and sample.get("progress_observed") is True)


def _event_time_known(sample):
    # Legacy normalized input has its own event-time contract. A raw adapter
    # must explicitly distinguish event time from collector fallback time.
    return sample.get("timestamp_basis") in {None, "source-log-clock"}


def _validate_contract(sample):
    if _modern(sample):
        if sample.get("phase") not in _PHASES or sample.get("observation_kind") not in _KINDS:
            raise ValueError("invalid observation phase/kind")
        if type(sample.get("progress_observed")) is not bool:
            raise ValueError("progress_observed boolean required")
        if sample["progress_observed"] and sample["observation_kind"] != "iteration":
            raise ValueError("only iteration observations may report progress")
        started = sample.get("attempt_started_at")
        if not _finite(started) or started > sample["timestamp"]:
            raise ValueError("attempt_started_at must be finite and no later than observation")
    for key in ("adapter_warnings", "fatal_errors"):
        if key in sample and (not isinstance(sample[key], list) or any(not isinstance(x, str) for x in sample[key])):
            raise ValueError(key + " must be a list of strings")


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
        if key in policy and (not _finite(policy[key]) or policy[key] < 0):
            raise FlowError("Invalid optional threshold: " + key)
    if "startup_timeout_seconds" in policy and (not _finite(policy["startup_timeout_seconds"]) or policy["startup_timeout_seconds"] <= 0):
        raise FlowError("Invalid startup_timeout_seconds")
    if type(policy.get("performance_window", 5)) is not int or policy.get("performance_window", 5) < 2:
        raise FlowError("performance_window must be an integer >=2")


def _record_progress(progress, sample):
    """Keep attempt clocks and monotonic progress independent of sample retention."""
    attempt = progress.get(sample["attempt_id"])
    iteration = _iteration(sample)
    if attempt is None:
        attempt = progress[sample["attempt_id"]] = {
            "started_at": sample.get("attempt_started_at", sample["timestamp"]),
            "last_progress_at": sample.get("attempt_started_at", sample["timestamp"]),
            "last_observation_at": sample["timestamp"], "max_step": -1, "last_step": None,
            "progress_samples": 0, "regressed": False, "clock_regressed": False,
            "clocks": {},
            "training_seen": False, "modern": _modern(sample), "contract_changed": False,
            "contract": {key: sample.get(key) for key in ("attempt_started_at", "expected_final_step", "process_identity")},
            "fatal_errors": [], "nonfinite": [],
            "last_source_progress_at": None, "clockless_ranges": {}, "clockless_source_invalid": False,
        }
    elif attempt["modern"] != _modern(sample) or attempt["contract"] != {
            key: sample.get(key) for key in ("attempt_started_at", "expected_final_step", "process_identity")}:
        attempt["contract_changed"] = True
    # Source-log iterations may arrive after a newer collector heartbeat. They
    # must be monotonic relative to other iterations, not heartbeat wall time.
    # Keep source-clock memory records separate from collector lifecycle rows.
    clock = (("iteration-source" if _event_time_known(sample) else "iteration-collected") if iteration else "source-other"
             if sample.get("timestamp_basis") == "source-log-clock" else "collector")
    previous_time = attempt["clocks"].get(clock, sample["timestamp"])
    time_regressed = sample["timestamp"] < previous_time
    attempt["clocks"][clock] = max(previous_time, sample["timestamp"])
    attempt["clock_regressed"] |= time_regressed
    attempt["last_observation_at"] = max(attempt["last_observation_at"], sample["timestamp"])
    attempt["training_seen"] |= iteration or sample.get("phase") == "training"
    if iteration:
        if attempt["last_step"] is not None and sample["step"] < attempt["last_step"]:
            attempt["regressed"] = True
        if sample["step"] > attempt["max_step"]:
            if not time_regressed:
                attempt["last_progress_at"] = max(attempt["last_progress_at"], sample["timestamp"])
                attempt["progress_samples"] += 1
            attempt["max_step"] = sample["step"]
            if _event_time_known(sample):
                attempt["last_source_progress_at"] = sample["timestamp"]
            else:
                source = sample.get("source")
                if (not isinstance(source, dict) or not isinstance(source.get("path"), str)
                        or type(source.get("offset")) is not int or source["offset"] < 0
                        or type(source.get("bytes")) is not int or source["bytes"] <= 0):
                    attempt["clockless_source_invalid"] = True
                else:
                    ranges = attempt["clockless_ranges"]
                    ranges[source["path"]] = max(ranges.get(source["path"], 0), source["offset"] + source["bytes"])
        attempt["last_step"] = sample["step"]
    for error in sample.get("fatal_errors", []):
        if error not in attempt["fatal_errors"]:
            attempt["fatal_errors"].append(error)
    for name in ("loss", "grad_norm"):
        if sample.get(name) is not None and not _finite(sample[name]) and name not in attempt["nonfinite"]:
            attempt["nonfinite"].append(name)


def _completion_verified(sample, attempt, now):
    """A terminal label is a claim; independently bind it to observed progress."""
    if sample.get("completed") is not True or sample.get("phase", "finished") != "finished":
        return False
    expected = sample.get("expected_final_step")
    receipt, identity = sample.get("exit_receipt"), sample.get("process_identity")
    if (type(expected) is not int or expected <= 0 or attempt["max_step"] < expected
            or attempt["progress_samples"] < 1 or not isinstance(receipt, dict) or not isinstance(identity, dict)):
        return False
    if (type(identity.get("pid")) is not int or identity["pid"] <= 0
            or not isinstance(identity.get("start_ticks"), str) or not identity["start_ticks"].isdecimal()
            or not isinstance(identity.get("boot_id"), str) or not identity["boot_id"]
            or not isinstance(identity.get("pid_namespace"), str) or not identity["pid_namespace"]):
        return False
    finished = receipt.get("finished_at")
    if attempt["clockless_source_invalid"]:
        return False
    if attempt["clockless_ranges"]:
        seal = receipt.get("log_evidence")
        if sample.get("log_seal_verified") is not True or not isinstance(seal, dict) or type(seal.get("bytes")) is not int:
            return False
        sha = seal.get("sha256")
        if not isinstance(sha, str) or len(sha) != 64 or set(sha) - set("0123456789abcdef"):
            return False
        for source_path, end in attempt["clockless_ranges"].items():
            if source_path != seal.get("path") or end > seal["bytes"]:
                return False
    last_source = attempt["last_source_progress_at"]
    return (receipt.get("attempt_id") == sample["attempt_id"]
            and bool(sample.get("context")) and receipt.get("context") == sample["context"]
            and receipt.get("process") == identity and type(receipt.get("exit_code")) is int and receipt["exit_code"] == 0
            and _finite(finished) and attempt["started_at"] <= finished <= min(now, sample["timestamp"])
            and (last_source is None or last_source <= finished)
            and not any(attempt[key] for key in ("regressed", "clock_regressed", "contract_changed", "fatal_errors", "nonfinite")))


def observation_issues(samples, policy, now=None, *, progress=None):
    check_policy(policy)
    now = time.time() if now is None else now
    if not _finite(now):
        raise FlowError("Watcher time must be finite")
    if not samples:
        return [{"kind": "telemetry-missing", "severity": "warning", "detail": "No valid observations"}]
    latest = samples[-1]
    for sample in samples:
        _validate_contract(sample)
    if _modern(latest) and "startup_timeout_seconds" not in policy:
        raise FlowError("Phase-aware monitoring requires an independent startup_timeout_seconds")
    current = [x for x in samples if x["attempt_id"] == latest["attempt_id"]]
    if progress is None:
        progress = {}
        for sample in current:
            _record_progress(progress, sample)
    attempt = progress[latest["attempt_id"]]
    completed = _completion_verified(latest, attempt, now)
    issues = []
    age = now - latest["timestamp"]
    if age < -30:
        issues.append({"kind": "clock-mismatch", "severity": "warning", "detail": "Observation timestamp is ahead of watcher"})
    if age > policy["telemetry_seconds"] and not completed:
        issues.append({"kind": "telemetry-stale", "severity": "critical", "detail": "Collector/log path may have stopped; training state unknown"})
    if latest.get("job_alive") is False and not completed:
        issues.append({"kind": "job-exited", "severity": "critical", "detail": "Check scheduler and recovery owner"})
    advancing = []
    for sample in current:
        if _iteration(sample) and (not advancing or sample["step"] > advancing[-1]["step"]):
            advancing.append(sample)
    if attempt["regressed"]:
        issues.append({"kind": "step-regressed", "severity": "critical", "detail": "Step went backwards without a new attempt"})
    if attempt["clock_regressed"]:
        issues.append({"kind": "observation-time-regressed", "severity": "critical", "detail": "Observation time moved backwards; verify clocks and log ordering"})
    if attempt["contract_changed"]:
        issues.append({"kind": "attempt-contract-changed", "severity": "critical", "detail": "Start time, process or expected final step changed without a new attempt"})
    if not completed:
        if not attempt["training_seen"] and attempt["modern"]:
            if now - attempt["started_at"] > policy["startup_timeout_seconds"]:
                issues.append({"kind": "startup-timeout", "severity": "critical", "detail": "Startup/compilation has not produced a training iteration within the configured startup allowance"})
        elif now - attempt["last_progress_at"] > policy["stall_seconds"]:
            issues.append({"kind": "training-stalled", "severity": "critical", "detail": "Liveness alone does not prove training progress"})
    if (latest.get("completed") or latest.get("phase") == "finished") and not completed:
        issues.append({"kind": "completion-unverified", "severity": "critical", "detail": "Need matching process exit receipt, successful exit and observed expected final step"})
    if latest.get("phase") == "failed":
        issues.append({"kind": "training-failed", "severity": "critical", "detail": "Adapter reports training failure; preserve attempt evidence"})
    if latest.get("phase") == "unknown":
        issues.append({"kind": "training-state-unknown", "severity": "warning", "detail": "Training liveness/phase is unverified; reconcile the current attempt"})
    if latest.get("adapter_warnings"):
        issues.append({"kind": "adapter-warning", "severity": "warning", "detail": latest["adapter_warnings"]})
    if attempt["fatal_errors"]:
        issues.append({"kind": "training-fatal-error", "severity": "critical", "detail": attempt["fatal_errors"]})
    if latest.get("recovery_state") in {"restarting", "recovering", "restored"}:
        recovered = (attempt["progress_samples"] >= policy["min_progress_samples"] and latest.get("checkpoint_verified") is True
                     and not any(attempt[key] for key in ("regressed", "clock_regressed", "contract_changed", "fatal_errors", "nonfinite")))
        if not recovered and now - attempt["started_at"] > policy["recovery_seconds"]:
            issues.append({"kind": "recovery-timeout", "severity": "critical", "detail": "Restart has not produced verified checkpoint and advancing steps"})
    for name in attempt["nonfinite"]:
        issues.append({"kind": "nonfinite-" + name, "severity": "critical", "detail": "Preserve numerical evidence before recovery"})
    limit = policy.get("memory_limit_bytes")
    if limit and latest.get("device_memory_bytes") is not None:
        reserve = policy.get("required_headroom_bytes", 0)
        if limit - latest["device_memory_bytes"] < reserve:
            issues.append({"kind": "memory-headroom", "severity": "warning", "detail": "Device memory leaves less than the stage's configured reserve"})
    reference = policy.get("reference_step_seconds")
    if reference and not attempt["clock_regressed"] and len(advancing) >= policy.get("performance_window", 5):
        subset = advancing[-policy.get("performance_window", 5):]
        delta = subset[-1]["step"] - subset[0]["step"]
        # Collector scheduling/backlog is not training step latency. Preserve
        # the adapter warning instead of classifying it as measured slowdown.
        ratio = ((subset[-1]["timestamp"] - subset[0]["timestamp"]) / delta / reference
                 if delta and all(_event_time_known(row) for row in subset) else None)
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
    if progress is None or previous.get("progress_version") != _PROGRESS_VERSION:
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
                _validate_contract(sample)
                if _modern(sample) and "startup_timeout_seconds" not in policy:
                    raise FlowError("Phase-aware monitoring requires an independent startup_timeout_seconds")
                # Non-finite numerical samples become incidents, but JSON artifacts remain valid.
                for name in ("loss", "grad_norm"):
                    if isinstance(sample.get(name), float) and not math.isfinite(sample[name]):
                        sample[name] = str(sample[name])
                if "device_memory_bytes" in sample and (not _finite(sample["device_memory_bytes"]) or sample["device_memory_bytes"] < 0):
                    raise ValueError("invalid device memory")
                for flag in ("job_alive", "completed", "checkpoint_verified"):
                    if flag in sample and not isinstance(sample[flag], bool):
                        raise ValueError("invalid boolean: " + flag)
                event_id = "observation-" + fingerprint({"task": tid, "sample": sample})
                existed = db.execute("SELECT 1 FROM events WHERE event_id=?", (event_id,)).fetchone()
                store.event(db, tid, "observation", sample, event_id)
                if not existed:
                    previous["samples"].append(sample)
                    _record_progress(progress, sample)
            except FlowError:
                raise
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
                 "completion_verified": bool(samples and _completion_verified(samples[-1], progress[samples[-1]["attempt_id"]], time.time() if now is None else now)),
                 "recovery_action": "none; external owner retains control"}
    db.execute("INSERT OR REPLACE INTO meta VALUES(?,?)", (key, json.dumps({"offset": offset, "prefix": prefix_hash,
               "prefix_length": prefix_length, "file_id": file_id, "progress": progress, "progress_version": _PROGRESS_VERSION, "samples": samples,
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
