"""Explicit public export and retained, private monitoring reports."""
import html
import json
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


def monitor_report(store, tid, output):
    store.task(tid)
    samples = [x["payload"] for x in store.events() if x["task"] == tid and x["kind"] == "observation"]
    incidents = [x for x in store.events() if x["task"] == tid and x["kind"].startswith("incident-")]
    if not samples:
        raise FlowError("No observations available for charts")
    charts = []
    for field in ("step", "loss", "grad_norm", "device_memory_bytes"):
        valid = [x for x in samples if isinstance(x.get(field), (int, float))]
        if not valid:
            continue
        xmin, xmax = min(x["timestamp"] for x in valid), max(x["timestamp"] for x in valid)
        ymin, ymax = min(x[field] for x in valid), max(x[field] for x in valid)
        # Separate attempts to avoid drawing a false continuity through a restart.
        attempts = list(dict.fromkeys(x["attempt_id"] for x in valid))
        lines = []
        for attempt in attempts:
            points = " ".join(f'{40+720*(x["timestamp"]-xmin)/max(1,xmax-xmin):.2f},{210-170*(x[field]-ymin)/max(1e-12,ymax-ymin):.2f}' for x in valid if x["attempt_id"] == attempt)
            lines.append('<polyline fill="none" stroke="#167d9a" stroke-width="2" points="' + points + '"/>')
        charts.append(f'<h2>{html.escape(field)}</h2><p>range {ymin:g} – {ymax:g}; UTC epoch {xmin:g} – {xmax:g}</p><svg viewBox="0 0 800 240" role="img" aria-label="{field} over time"><path d="M40 30 V210 H770" fill="none" stroke="#888"/>{"".join(lines)}</svg>')
    body = '<!doctype html><meta charset="utf-8"><title>Training observations</title><style>body{max-width:960px;margin:40px auto;font:16px system-ui}svg{width:100%;background:#f3f6f8}pre{white-space:pre-wrap}</style>'
    body += '<h1>' + html.escape(tid) + '</h1><p>Private observed telemetry. Curves alone do not establish convergence or full device coverage.</p>' + "".join(charts)
    body += '<h2>Incidents</h2><pre>' + html.escape(json.dumps(incidents, ensure_ascii=False, indent=2)) + '</pre>'
    atomic_write(output, body)
    return {"status": "complete", "path": str(Path(output).resolve()), "observations": len(samples), "incidents": len(incidents), "visibility": "private"}
