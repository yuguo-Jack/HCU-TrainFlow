"""Explicit public export and retained, private monitoring reports."""
import html
import json
import math
from datetime import datetime, timezone
from pathlib import Path
import re

from .core import FlowError, atomic_write, child, digest, utc, write_json


def export_public(source, destination, manifest):
    source, destination = Path(source).resolve(), Path(destination).resolve()
    if destination.exists() or destination == source or destination.is_relative_to(source):
        raise FlowError("Export to a new directory outside the source tree")
    if not manifest.get("reviewed_by") or not manifest.get("files"):
        raise FlowError("Public export needs an explicit reviewed file allowlist")
    approved = []
    for entry in manifest["files"]:
        path = child(source, entry["path"])
        if (source / entry["path"]).is_symlink() or path.suffix.lower() not in {".md", ".json", ".yaml", ".yml", ".py", ".toml", ".txt", ".svg"}:
            raise FlowError("Export accepts reviewed text files only")
        if any(x in {".private", ".work", ".git", "objects", "runs", "materials", "experience"} for x in (*Path(entry["path"]).parts, *path.relative_to(source).parts)):
            raise FlowError("Private evidence/cache cannot be exported")
        data = path.read_bytes()
        if digest(data) != entry.get("sha256"):
            raise FlowError("Export file changed after review")
        text = data.decode("utf-8-sig")
        patterns = [r"gh[pousr]_[A-Za-z0-9]{20,}", r"github_pat_[A-Za-z0-9_]{20,}", r"-----BEGIN .*PRIVATE KEY-----",
                    r"(?i)authorization\s*[:=]\s*bearer\s+\S+", r"https?://[^\s/]+\.feishu\.cn/", r"https?://(?:10\.|192\.168\.|127\.)\d"]
        if any(re.search(pattern, text) for pattern in patterns):
            raise FlowError("Sensitive-looking content requires redaction before export: " + entry["path"])
        approved.append((entry, data))
    destination.mkdir(parents=True)
    for entry, data in approved:
        atomic_write(child(destination, entry["path"]), data)
    write_json(destination / "export-receipt.json", {**manifest, "exported_at": utc(), "limit": "Allowlist and scan do not replace human content review"})
    return {"status": "complete", "files": len(approved), "destination": str(destination)}


def _number(value):
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def _clock(value):
    if not _number(value) or not 0 <= value <= 253402300799:
        return False
    try:
        datetime.fromtimestamp(value, timezone.utc)
    except (ValueError, OSError, OverflowError):
        return False
    return True


def monitor_series(samples, *, diagnostics=None):
    """Chart measurements with explicit clocks; never extend heartbeat values.

    The public return shape remains label -> (context, attempt) -> (time,value).
    Collector-fallback measurements use separate labelled series. Optional
    diagnostics retain omitted values and clock/contract gaps for the report.
    """
    series, seen, last_time, contracts = {}, set(), {}, {}
    info = diagnostics if diagnostics is not None else {}
    info.update(skipped={}, duplicates=0, warnings=[], clock_bases={})

    def skip(reason):
        info["skipped"][reason] = info["skipped"].get(reason, 0) + 1

    def add(label, group, timestamp, value, identity=None, *, nonnegative=False):
        if value is None:
            return
        if not _number(value) or nonnegative and value < 0:
            skip("invalid-numeric:" + label)
            return
        if not _clock(timestamp):
            skip("invalid-clock:" + label)
            return
        key = (label, group, timestamp, value, identity)
        if key in seen:
            info["duplicates"] += 1
            return
        seen.add(key)
        clock_key = (label, group)
        if timestamp < last_time.get(clock_key, timestamp):
            warning = "Clock moved backwards in " + label + " / " + group[1] + "; points preserve values, not a verified chronological trajectory"
            if warning not in info["warnings"]:
                info["warnings"].append(warning)
        last_time[clock_key] = max(timestamp, last_time.get(clock_key, timestamp))
        series.setdefault(label, {}).setdefault(group, []).append((timestamp, value))

    for sample in samples:
        if not isinstance(sample, dict) or not isinstance(sample.get("attempt_id"), str) or not sample["attempt_id"]:
            skip("missing-attempt-identity")
            continue
        context = sample.get("context", "legacy-context-unspecified")
        if not isinstance(context, str) or not context:
            skip("invalid-context")
            continue
        attempt = sample["attempt_id"]
        contract = json.dumps(_json_safe({key: sample.get(key) for key in ("attempt_started_at", "process_identity", "_report_epoch")}), sort_keys=True)
        scopes = contracts.setdefault((context, attempt), [])
        if contract not in scopes:
            scopes.append(contract)
            if len(scopes) > 1:
                info["warnings"].append("Attempt identity/epoch changed without a distinct ID: " + attempt + "; separated display segments")
        segment = scopes.index(contract)
        group = (context, attempt if segment == 0 else attempt + " [scope " + str(segment + 1) + "]")
        kind = sample.get("observation_kind")
        legacy = not any(key in sample for key in ("observation_kind", "progress_observed", "phase"))
        progress = legacy or kind == "iteration" and sample.get("progress_observed") is True
        if sample.get("progress_observed") is True and kind != "iteration":
            skip("progress-on-noniteration-record")
        if progress:
            basis = sample.get("timestamp_basis", "legacy-normalized-clock" if legacy else "unknown-clock")
            if not isinstance(basis, str):
                basis = "unknown-clock"
            info["clock_bases"][basis] = info["clock_bases"].get(basis, 0) + 1
            if basis in {"source-log-clock", "legacy-normalized-clock"}:
                suffix = ""
            elif basis in {"first-observed-no-source-clock", "collector-clock-source-time-invalid"}:
                suffix = " [collector clock; event time unverified]"
            else:
                suffix = " [unknown clock; event time unverified]"
            source = sample.get("source")
            identity = (str(source.get("path")), str(source.get("offset")), str(source.get("sha256"))) if isinstance(source, dict) else ("step", str(sample.get("step")))
            for field in ("step", "loss", "grad_norm", "step_seconds_reported", "tokens_per_second"):
                value = sample.get(field)
                if field == "step" and value is not None and type(value) is not int:
                    skip("invalid-numeric:step")
                    continue
                add(field + suffix, group, sample.get("timestamp"), value, identity, nonnegative=field != "loss")
        # Top-level physical usage has no independent memory timestamp. A
        # modern iteration/heartbeat may merely carry it; only memory records
        # (or legacy explicitly normalized measurements) establish a new point.
        physical = sample.get("device_memory_bytes")
        if (kind == "memory" or legacy) and physical is not None:
            if _number(physical) and physical >= 0:
                add("physical device memory (GiB)", group, sample.get("observed_at", sample.get("timestamp")), physical / 2**30)
            else:
                skip("invalid-numeric:physical device memory")
        memories = sample.get("memory_by_rank", {})
        if not isinstance(memories, dict):
            skip("invalid-memory-map")
            continue
        for rank, memory in memories.items():
            if not isinstance(memory, dict):
                skip("invalid-rank-memory")
                continue
            timestamp = memory.get("observed_at")
            received = sample.get("observed_at")
            if _clock(received) and _number(timestamp) and timestamp > received:
                skip("rank-memory-from-future")
                continue
            for field in ("allocator_allocated_bytes", "allocator_reserved_bytes", "allocator_peak_allocated_bytes", "allocator_peak_reserved_bytes", "device_memory_bytes"):
                value = memory.get(field)
                if value is None:
                    continue
                if not _number(value) or value < 0:
                    skip("invalid-numeric:" + field)
                    continue
                # The measurement's own clock deduplicates carried snapshots.
                add(f"rank {rank} / {field} (GiB)", group, timestamp, value / 2**30)
    for groups in series.values():
        for points in groups.values():
            points.sort()
    return series


def _json_safe(value):
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return value


def _fraction(value, lower, upper):
    if lower == upper:
        return 0.5
    # Two finite opposite-sign extrema may have an infinite subtraction span.
    span = upper - lower
    return (value / 2 - lower / 2) / (upper / 2 - lower / 2) if not math.isfinite(span) else (value - lower) / span


def monitor_report(store, tid, output, *, attempt=None, context=None):
    store.task(tid)
    events = [x for x in store.events() if x["task"] == tid]
    samples, selected_events = [], []
    epochs = {}
    for event in events:
        # Imported event IDs carry a peer prefix; local/imported context reset
        # streams must not reset one another's chart segments.
        origin = event.get("event_id", "").rsplit(":", 1)[0] if ":" in event.get("event_id", "") else "local"
        if event["kind"] == "context-changed":
            epochs[origin] = epochs.get(origin, 0) + 1
        if event["kind"] != "observation":
            continue
        sample = event["payload"]
        if not isinstance(sample, dict):
            continue
        if attempt is not None and sample.get("attempt_id") != attempt or context is not None and sample.get("context") != context:
            continue
        samples.append({**sample, "_report_epoch": epochs.get(origin, 0)})
        selected_events.append(event)
    if not samples:
        raise FlowError("No observations available for the requested chart scope")
    opened = {x["payload"].get("incident_id") for x in events if x["kind"].startswith("incident-")
              and isinstance(x["payload"], dict) and x["payload"].get("incident_id") is not None
              and (attempt is None or x["payload"].get("attempt_id") == attempt)
              and (context is None or x["payload"].get("context") == context)}
    incidents = [x for x in events if x["kind"].startswith("incident-") and isinstance(x["payload"], dict)
                 and (context is None or x["payload"].get("context") == context)
                 and (attempt is None or x["payload"].get("attempt_id") == attempt or x["payload"].get("incident_id") in opened)]
    diagnostics = {}
    series = monitor_series(samples, diagnostics=diagnostics)
    counts = {label: sum(len(points) for points in groups.values()) for label, groups in series.items()}
    missing = [name for name in ("loss", "grad_norm", "step_seconds_reported", "tokens_per_second") if not any(label == name or label.startswith(name + " [") for label in series)]
    if not any("device memory" in name or "/ device_memory_bytes" in name for name in series):
        missing.append("physical device memory")
    data = {"schema_version": 1, "visibility": "private", "task": tid, "selection": {"attempt": attempt, "context": context},
            "observations": len(samples), "measurement_counts": counts, "missing_metrics": missing,
            "diagnostics": diagnostics, "events": _json_safe(selected_events), "incidents": _json_safe(incidents),
            "series": [{"metric": label, "context": scope, "attempt": aid, "points": points}
                       for label, groups in series.items() for (scope, aid), points in groups.items()]}
    raw = json.dumps(data, sort_keys=True, ensure_ascii=False, indent=2, allow_nan=False).encode("utf-8")
    data_hash = digest(raw)
    data_path = Path(output).with_suffix(".data.json")
    if Path(output).resolve() == data_path.resolve():
        raise FlowError("Report HTML and data sidecar paths must differ")
    atomic_write(data_path, raw)
    charts = []
    palette = ("#167d9a", "#8b5cf6", "#dc6803", "#00875a", "#b42318")
    for label, groups in series.items():
        values = [point for points in groups.values() for point in points]
        xmin, xmax = min(p[0] for p in values), max(p[0] for p in values)
        ymin, ymax = min(p[1] for p in values), max(p[1] for p in values)
        lines, legend = [], []
        for index, ((scope, aid), points) in enumerate(groups.items()):
            color = palette[index % len(palette)]
            xy = [(55 + 690 * _fraction(t, xmin, xmax), 210 - 170 * _fraction(v, ymin, ymax)) for t, v in points]
            coordinates = " ".join(f"{x:.2f},{y:.2f}" for x, y in xy)
            # Memory and fallback clocks are collected snapshots. Dots avoid
            # implying a continuously measured or interpolated trajectory.
            if "(GiB)" not in label and "event time unverified" not in label and not diagnostics["warnings"]:
                lines.append(f'<polyline fill="none" stroke="{color}" stroke-width="2" points="{coordinates}"/>')
            for (x, y), (timestamp, value) in zip(xy, points):
                title = html.escape(f"{aid}: {value:g} at {datetime.fromtimestamp(timestamp, timezone.utc).isoformat()}")
                lines.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="4" fill="{color}"><title>{title}</title></circle>')
            legend.append(f'<li style="color:{color}">{html.escape(aid)} · context {html.escape(scope[:12])} · {len(points)} measurements</li>')
        start, end = (datetime.fromtimestamp(value, timezone.utc).isoformat() for value in (xmin, xmax))
        charts.append(f'<section><h2>{html.escape(label)}</h2><p>range {ymin:g} – {ymax:g}; UTC {start} – {end}</p><svg viewBox="0 0 800 250" role="img" aria-label="{html.escape(label)} over time"><path d="M55 30 V210 H770" fill="none" stroke="#888"/>{"".join(lines)}</svg><ul>{"".join(legend)}</ul></section>')
    body = '<!doctype html><meta charset="utf-8"><title>Training observations</title><style>body{max-width:1100px;margin:40px auto;padding:0 20px;font:16px system-ui;color:#183044;background:#fff}section{border:1px solid #dde5ed;border-radius:12px;padding:18px;margin:18px 0}svg{width:100%;background:#f3f6f8}pre{white-space:pre-wrap;overflow-wrap:anywhere}code{overflow-wrap:anywhere}summary{cursor:pointer}table{border-collapse:collapse}td,th{padding:7px 14px;border:1px solid #dde5ed}</style>'
    body += '<h1>' + html.escape(tid) + '</h1><p>Private observed telemetry. Attempts and contexts are separate lines. Heartbeats do not create new training measurements. Rank allocator memory is distinct from physical device use; peaks are allocator high-water marks. Memory clocks are collection times. Collector fallback iteration clocks are labelled separately; legacy normalized clocks have unspecified origin. No missing values are interpolated. Curves alone do not establish convergence, performance benefit or full device coverage.</p>'
    body += '<p>Selection: <code>' + html.escape(json.dumps(data["selection"], ensure_ascii=False)) + '</code></p><p>Data sidecar SHA256: <code>' + data_hash + '</code> · ' + html.escape(data_path.name) + '</p>'
    body += '<h2>Coverage</h2><p>' + str(len(samples)) + ' observations; ' + str(sum(counts.values())) + ' metric measurements (different metrics may share one source record).</p><p>Not observed: ' + html.escape(', '.join(missing) or 'none among the standard summary fields') + '</p>'
    body += '<table><tr><th>Metric</th><th>Measured points</th></tr>' + ''.join('<tr><td>' + html.escape(label) + '</td><td>' + str(count) + '</td></tr>' for label, count in counts.items()) + '</table>'
    body += ''.join(charts)
    body += '<h2>Data quality and clocks</h2><pre>' + html.escape(json.dumps(diagnostics, ensure_ascii=False, indent=2)) + '</pre>'
    body += '<h2>Incidents</h2><pre>' + html.escape(json.dumps(_json_safe(incidents), ensure_ascii=False, indent=2)) + '</pre>'
    body += '<details><summary>Original selected event projection</summary><pre>' + html.escape(json.dumps(_json_safe(selected_events), ensure_ascii=False, indent=2)) + '</pre></details>'
    atomic_write(output, body)
    return {"status": "complete" if series else "incomplete", "path": str(Path(output).resolve()),
            "data_path": str(data_path.resolve()), "data_sha256": data_hash, "observations": len(samples),
            "series": len(series), "measurement_counts": counts, "missing_metrics": missing,
            "diagnostics": diagnostics, "incidents": len(incidents), "visibility": "private"}
