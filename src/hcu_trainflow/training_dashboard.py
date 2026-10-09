"""Offline, single-attempt evidence charts. Standard library only; no gates or control."""
import hashlib
import html
import json
import math
import os
from pathlib import Path

from .core import FlowError


MODES = ("unspecified", "performance", "profile", "stage-quality-audit", "functional", "monitor-drill")
MEMORY_FIELDS = ("allocator_allocated_bytes", "allocator_reserved_bytes",
                 "allocator_peak_allocated_bytes", "allocator_peak_reserved_bytes", "device_memory_bytes")
MAX_BYTES = 256 * 1024**2


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _finite(value):
    try:
        return type(value) in (int, float) and math.isfinite(value)
    except OverflowError:
        return False


def _snapshot(path):
    """Bound the read at its initial size and verify that prefix on the same handle."""
    path = Path(path).resolve()
    with path.open("rb", buffering=0) as stream:
        before = os.fstat(stream.fileno())
        if before.st_size > MAX_BYTES:
            raise FlowError("Input exceeds the 256 MiB offline snapshot limit")
        raw = stream.read(before.st_size)
        stream.seek(0)
        verified = stream.read(before.st_size)
        after = os.fstat(stream.fileno())
    if len(raw) != before.st_size or raw != verified or after.st_size < before.st_size:
        raise FlowError("Input changed within the captured prefix; copy a stable log and retry")
    current = path.stat()
    return raw, {"path": str(path), "bytes": len(raw), "sha256": _sha(raw),
                 "size_at_open": before.st_size, "size_after_read": after.st_size,
                 "appended_during_read": after.st_size > before.st_size,
                 "path_replaced_during_read": (before.st_dev, before.st_ino) != (current.st_dev, current.st_ino),
                 "consistency": "bounded prefix read twice on one handle; not a live file lock"}


def _constant(value):
    raise ValueError("Non-standard JSON numeric constant: " + value)


def _parse(raw, allow_partial_final_line):
    consumed = len(raw)
    tail = None
    if raw and not raw.endswith(b"\n"):
        if not allow_partial_final_line:
            raise FlowError("Unterminated final NDJSON line; retry after export or explicitly allow a partial final line")
        consumed = raw.rfind(b"\n") + 1
        tail = {"bytes": len(raw) - consumed, "sha256": _sha(raw[consumed:]),
                "reason": "explicitly excluded unterminated final line; original bytes preserved"}
    records = []
    for number, line in enumerate(raw[:consumed].splitlines(), 1):
        try:
            record = json.loads(line.decode("utf8"), parse_constant=_constant)
        except (UnicodeError, ValueError) as exc:
            raise FlowError(f"Invalid complete NDJSON line {number}: {exc}") from exc
        if not isinstance(record, dict):
            raise FlowError(f"NDJSON line {number} is not an object")
        record = dict(record)
        record["_line"] = number
        records.append(record)
    if not records:
        raise FlowError("No complete normalized observation records")
    return records, consumed, tail


def _identity(records, expected_attempt, expected_context):
    first = records[0]
    identity = {key: first.get(key) for key in ("context", "attempt_id", "process_identity")}
    if (not all(isinstance(identity[k], str) and identity[k] for k in ("context", "attempt_id"))
            or not isinstance(identity["process_identity"], dict) or not identity["process_identity"]):
        raise FlowError("Normalized log needs context, attempt_id and process_identity")
    if expected_attempt is not None and identity["attempt_id"] != expected_attempt:
        raise FlowError("Attempt differs from expected identity")
    if expected_context is not None and identity["context"] != expected_context:
        raise FlowError("Context differs from expected identity")
    for r in records:
        if any(r.get(k) != v for k, v in identity.items()):
            raise FlowError(f"Mixed context, attempt or process identity at line {r['_line']}; split attempts first")
        if r.get("observation_kind") not in ("iteration", "memory", "heartbeat", "lifecycle"):
            raise FlowError(f"Unknown observation_kind at line {r['_line']}")
        if type(r.get("step")) is not int or r["step"] < 0 or not _finite(r.get("timestamp")):
            raise FlowError(f"Invalid step/timestamp at line {r['_line']}")
    return identity


def _select(records, attempt_id, context):
    if (attempt_id is None) != (context is None):
        raise FlowError("Explicit selection requires both --attempt-id and --context")
    counts = {}
    for r in records:
        pair = (r.get("context"), r.get("attempt_id"))
        if not all(isinstance(v, str) and v for v in pair):
            raise FlowError(f"Missing context/attempt identity at line {r['_line']}")
        counts[pair] = counts.get(pair, 0) + 1
    selected = records if attempt_id is None else [r for r in records if (r["context"], r["attempt_id"]) == (context, attempt_id)]
    if not selected:
        raise FlowError("No records match the explicitly selected attempt and context")
    return selected, {"explicit": attempt_id is not None, "selected_records": len(selected),
                      "excluded_records": len(records) - len(selected),
                      "identities_in_snapshot": [{"context": c, "attempt_id": a, "records": n}
                                                 for (c, a), n in sorted(counts.items())]}


def _series(iterations, field, *, divisor=1, positive=False):
    points = []
    for r in iterations:
        metrics = r.get("metrics", {})
        if not isinstance(metrics, dict):
            raise FlowError(f"Invalid iteration metrics at line {r['_line']}")
        value = metrics.get(field)
        reason = None
        if field not in metrics:
            reason = "missing"
        elif not _finite(value):
            reason = "nonfinite-or-nonnumeric"
        elif positive and value <= 0:
            reason = "nonpositive-duration"
        points.append({"x": r["step"], "value": None if reason else value / divisor,
                       "reason": reason, "line": r["_line"]})
    return points


def _memory(records):
    result, previous, ambiguous = {}, {}, []
    for r in records:
        states = r.get("memory_by_rank", {})
        if not isinstance(states, dict):
            raise FlowError(f"Invalid memory_by_rank at line {r['_line']}")
        if r["observation_kind"] == "memory":
            changed = [rank for rank, values in states.items() if previous.get(rank) != values]
            if not changed and len(states) == 1:
                changed = list(states)  # A real memory event with one possible rank, even if its value is unchanged.
            if not changed and len(states) > 1:
                ambiguous.append(r["_line"])
            for rank, values in states.items():
                if not isinstance(values, dict):
                    raise FlowError(f"Invalid rank memory at line {r['_line']}")
                if rank not in changed:
                    continue  # Other ranks' carried snapshots are not new measurements.
                for key in MEMORY_FIELDS:
                    if key in values or f"rank {rank}: {key}" in result:
                        value = values.get(key)
                        reason = ("missing" if key not in values else
                                  None if _finite(value) and value >= 0 else "invalid-memory-value")
                        result.setdefault(f"rank {rank}: {key}", []).append({
                            "x": r["_line"], "value": None if reason else value / 1024**3,
                            "reason": reason, "line": r["_line"], "progress_step": r["step"],
                            "observed_at": values.get("observed_at"), "rank": rank})
        previous = states
    return result, ambiguous


def _source_records(records, raw_log):
    references, seen = [], set()
    for r in records:
        source = r.get("source")
        if source is None:
            continue
        if (not isinstance(source, dict) or not isinstance(source.get("path"), str)
                or type(source.get("offset")) is not int or source["offset"] < 0
                or type(source.get("bytes")) is not int or source["bytes"] <= 0
                or not isinstance(source.get("sha256"), str)
                or len(source["sha256"]) != 64
                or any(c not in "0123456789abcdef" for c in source["sha256"])):
            raise FlowError(f"Invalid raw source reference at line {r['_line']}")
        key = (source["path"], source["offset"], source["bytes"], source["sha256"])
        if key not in seen:
            references.append(dict(source)); seen.add(key)
    if len({r["path"] for r in references}) > 1:
        raise FlowError("Multiple raw log paths in one attempt; split streams before rendering")
    raw_bytes, raw_metadata = (None, None) if raw_log is None else _snapshot(raw_log)
    if raw_bytes is not None:
        if not references:
            raise FlowError("Cannot verify raw log without normalized source references")
        for ref in references:
            start, size = ref["offset"], ref["bytes"]
            if start + size > len(raw_bytes) or _sha(raw_bytes[start:start + size]) != ref["sha256"]:
                raise FlowError(f"Raw source bytes/hash mismatch at offset {start}")
    return references, raw_bytes, raw_metadata


def _esc(value):
    return html.escape(str(value), quote=True)


def _svg(title, unit, series, x_label):
    """Separate polylines at missing/nonfinite points; never interpolate across a gap."""
    colors = ("#2563eb", "#0d9488", "#ea580c", "#7c3aed", "#be185d", "#475569")
    points = [p for values in series.values() for p in values if p["value"] is not None]
    width, height = 960, 410 + 22 * len(series)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img">',
           f'<title>{_esc(title)}</title><rect width="100%" height="100%" fill="white"/>',
           '<g font-family="sans-serif" fill="#172b4d">', f'<text x="80" y="30" font-size="20">{_esc(title)}</text>']
    if not points:
        out += ['<text x="80" y="95">No observed numeric samples; missing is not zero.</text>', '</g></svg>']
        return "\n".join(out)
    all_x = [p["x"] for values in series.values() for p in values]
    xmin, xmax = min(all_x), max(all_x)
    magnitude = max(abs(p["value"]) for p in points)
    # Normalize BEFORE range/padding arithmetic: (+max_float)-(-max_float)
    # overflows despite both observations being finite. For extreme magnitudes,
    # label finite normalized ticks with an explicit multiplier instead of
    # multiplying padded ticks back into an unrepresentable float.
    scale = magnitude if magnitude and (magnitude > 1e6 or magnitude < 1e-6) else 1.0
    ymin, ymax = min(p["value"] / scale for p in points), max(p["value"] / scale for p in points)
    xspan = xmax - xmin or 1
    pad = (ymax - ymin) * .08 or max(abs(ymin) * .05, .05)
    ymin, ymax = ymin - pad, ymax + pad
    def xy(point):
        x = 80 + (point["x"] - xmin) / xspan * 840
        y = 340 - (point["value"] / scale - ymin) / (ymax - ymin) * 270
        if not (math.isfinite(x) and math.isfinite(y)):
            raise FlowError("Cannot represent a finite chart coordinate")
        return x, y
    for i in range(6):
        y = 70 + i * 54
        value = ymax - i / 5 * (ymax - ymin)
        out += [f'<path d="M80 {y} H920" stroke="#e2e8f0"/>', f'<text x="72" y="{y+4}" text-anchor="end" font-size="11">{value:.5g}</text>']
    for value in sorted({xmin + (i * (xmax - xmin) + 2) // 5 for i in range(6)}):
        x = 80 + (value - xmin) / xspan * 840
        out += [f'<text x="{x}" y="364" text-anchor="middle" font-size="11">{value}</text>']
    axis_unit = f"{unit} (tick × {scale:.6g})" if scale != 1 else unit
    out += [f'<text x="80" y="54" font-size="12">{_esc(axis_unit)}</text>', f'<text x="500" y="390" text-anchor="middle" font-size="12">{_esc(x_label)}</text>']
    for index, (label, values) in enumerate(series.items()):
        color, segment = colors[index % len(colors)], []
        for point in values + [{"value": None}]:
            if point["value"] is None:
                if segment:
                    out.append(f'<polyline points="{" ".join(segment)}" fill="none" stroke="{color}" stroke-width="1.7"/>')
                    segment = []
                continue
            x, y = xy(point); segment.append(f'{x:.2f},{y:.2f}')
            out.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="2.3" fill="{color}"><title>{_esc(label)}; x={point["x"]}; value={point["value"]:.9g}; line={point["line"]}</title></circle>')
        absent = sum(p["value"] is None for p in values)
        out.append(f'<text x="80" y="{418+22*index}" fill="{color}" font-size="12">{_esc(label[:100])} (missing/invalid: {absent})</text>')
    return "\n".join(out + ['</g></svg>'])


def render_dashboard(normalized_log, output_dir, *, measurement_mode="unspecified", attempt_id=None,
                     context=None, allow_partial_final_line=False, raw_log=None,
                     throughput_metric=None, throughput_unit=None, title="Training observation snapshot"):
    """Render exactly one identity. Output must be new/empty; no input is modified."""
    if measurement_mode not in MODES:
        raise FlowError("Unknown measurement mode")
    if bool(throughput_metric) != bool(throughput_unit):
        raise FlowError("Throughput requires both an exact numeric metric name and its declared unit")
    output = Path(output_dir).resolve()
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        raise FlowError("Use a new or empty output directory; earlier snapshots are immutable")
    raw, source = _snapshot(normalized_log)
    records, consumed, tail = _parse(raw, allow_partial_final_line)
    total_records = len(records)
    records, selection = _select(records, attempt_id, context)
    identity = _identity(records, attempt_id, context)
    iterations = [r for r in records if r["observation_kind"] == "iteration"]
    if any(not isinstance(r.get("metrics", {}), dict) for r in iterations):
        raise FlowError("Iteration metrics must be an object")
    steps = [r["step"] for r in iterations]
    if steps != sorted(set(steps)):
        raise FlowError("Duplicate or regressing iteration steps; do not combine ranks/restarts")
    losses = sorted({k for r in iterations for k in r.get("metrics", {}) if "loss" in k.lower() and k.lower() != "loss scale"})
    if len(losses) > 32:
        raise FlowError("Too many loss series for a readable single-attempt chart")
    memory_series, ambiguous_memory = _memory(records)
    charts = [dict(file="loss.svg", title="Reported training losses", unit="reported loss", x_label="training step",
                   series={key: _series(iterations, key) for key in losses}),
              dict(file="step-time.svg", title="Reported iteration time (all steps; no warmup exclusion)", unit="seconds", x_label="training step",
                   series={"reported duration": _series(iterations, "elapsed time per iteration (ms)", divisor=1000, positive=True)}),
              dict(file="memory.svg", title="Observed memory snapshots by rank", unit="GiB", x_label="normalized record ordinal (not time)", series=memory_series)]
    if throughput_metric:
        charts.append(dict(file="throughput.svg", title="Explicit reported throughput", unit=throughput_unit, x_label="training step",
                           series={throughput_metric: _series(iterations, throughput_metric)}))
    refs, raw_bytes, raw_metadata = _source_records(records, raw_log)
    for r in records:
        if any(not isinstance(r.get(name, []), list) for name in ("adapter_warnings", "fatal_errors")):
            raise FlowError(f"Invalid observer issue list at line {r['_line']}")
    issues = sorted({str(v) for r in records for name in ("adapter_warnings", "fatal_errors") for v in r.get(name, [])})
    gaps = []
    if not iterations: gaps.append("No iteration observations")
    if not losses: gaps.append("No fresh iteration loss fields in metrics; carried heartbeat loss is not plotted")
    if not charts[2]["series"]: gaps.append("No fresh memory observations; no whole-device memory inference")
    if ambiguous_memory: gaps.append(f"{len(ambiguous_memory)} memory events have unchanged multiple-rank snapshots; rank cannot be identified, so no new points are invented")
    if not throughput_metric: gaps.append("No explicit throughput field/unit selected; no throughput is inferred")
    if not refs: gaps.append("No raw source references in this stream")
    if tail: gaps.append("An unterminated final line was explicitly excluded and preserved in the snapshot")
    report = {"schema_version": 1, "identity": identity, "measurement_mode": measurement_mode,
              "measurement_mode_basis": "caller declaration; not independently certified by the plotter",
              "source": source, "parsed_bytes": consumed, "excluded_final_line": tail,
              "records": len(records), "snapshot_records": total_records, "selection": selection,
              "iterations": len(iterations), "raw_source_references": refs,
              "raw_log_snapshot": raw_metadata, "raw_references_verified": raw_bytes is not None,
              "charts": charts, "gaps": gaps, "observer_issues": issues,
              "ambiguous_memory_record_lines": ambiguous_memory,
              "gate_decision": "none", "limits": ["One attempt and context only; no comparison or quality gate",
              "All steps included, including cold compilation and warmup; no performance pass or summary inferred",
              "Missing/nonfinite values break lines, never become zero; source values remain in input snapshot",
              "Memory state copies on heartbeats are not new samples; allocator memory is not whole-device usage",
              "Original source hashes are references only unless --raw-log verifies the corresponding bytes"]}
    output.mkdir(parents=True, exist_ok=True)
    (output / "normalized.snapshot.jsonl").write_bytes(raw)
    if raw_bytes is not None: (output / "raw.snapshot.log").write_bytes(raw_bytes)
    for chart in charts:
        (output / chart["file"]).write_text(_svg(chart["title"], chart["unit"], chart["series"], chart["x_label"]), encoding="utf8")
    (output / "dashboard.json").write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf8")
    details = "\n".join(f"<li>{_esc(x)}</li>" for x in [f"Selected {len(records)} of {total_records} records; {selection['excluded_records']} other-attempt/context records excluded explicitly"] + gaps + issues + report["limits"])
    panels = "\n".join(f'<section><h2>{_esc(c["title"])}</h2><a href="{c["file"]}">Open SVG</a><img src="{c["file"]}" alt="{_esc(c["title"])}"/></section>' for c in charts)
    page = f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{_esc(title)}</title><style>body{{font-family:system-ui,sans-serif;background:#f5f7fb;color:#172b4d;max-width:1100px;margin:32px auto;padding:0 20px}}section{{background:white;border:1px solid #dce3ec;border-radius:12px;padding:18px;margin:22px 0}}img{{width:100%}}code{{overflow-wrap:anywhere}}li{{margin:8px 0}}a{{color:#2563eb}}</style>
<h1>{_esc(title)}</h1><p>Attempt: <code>{_esc(identity['attempt_id'])}</code><br>Context: <code>{_esc(identity['context'])}</code><br>Mode: <strong>{_esc(measurement_mode)}</strong> (caller declared)<br>Normalized snapshot SHA256: <code>{source['sha256']}</code></p>
<p>Offline observation only. No quality, convergence, performance or recovery gate is decided here.</p><ul>{details}</ul>{panels}
<p><a href="dashboard.json">Metrics and provenance</a> · <a href="normalized.snapshot.jsonl">Exact captured normalized bytes</a></p></html>'''
    (output / "index.html").write_text(page, encoding="utf8")
    return {"index": str(output / "index.html"), "data": str(output / "dashboard.json"),
            "identity": identity, "source_sha256": source["sha256"], "charts": len(charts),
            "iterations": len(iterations), "gaps": gaps, "gate_decision": "none"}
