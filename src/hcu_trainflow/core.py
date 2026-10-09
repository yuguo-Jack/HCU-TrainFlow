"""Transactional task state, immutable artifacts and fenced resource ownership."""
from __future__ import annotations

import contextlib
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import tempfile
import time
import uuid


class FlowError(ValueError):
    pass


def utc():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def fingerprint(value):
    return digest(json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False).encode())


def read_json(path):
    with open(path, encoding="utf-8-sig") as stream:
        return json.load(stream, parse_constant=lambda value: (_ for _ in ()).throw(FlowError("Non-finite JSON: " + value)))


def atomic_write(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not isinstance(data, bytes):
        data = data.encode("utf-8")
    fd, name = tempfile.mkstemp(prefix=".write-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def write_json(path, value):
    atomic_write(path, json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n")


def safe_id(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,99}", value):
        raise FlowError("Invalid identifier")
    return value


def child(root, relative):
    root = Path(root).resolve()
    path = (root / relative).resolve()
    if path == root or not path.is_relative_to(root):
        raise FlowError("Path must stay inside its managed root")
    return path


MODES = {"environment", "adapt", "analyze", "optimize", "diagnose", "operate", "full"}
PIPELINE = ["draft", "prepared", "environment_checked", "baseline_validated", "profiling", "optimizing", "scale_ready", "training", "completed"]
GATES = {"environment_checked": ["environment"], "baseline_validated": ["baseline"],
         "profiling": ["baseline"], "optimizing": ["analysis"], "scale_ready": ["stage-quality", "performance"],
         "training": ["environment", "stage-quality", "scale"], "completed": ["completion"]}


def validate_spec(spec):
    allowed = {"schema_version", "task_id", "mode", "objective", "context", "permissions", "recovery_owner", "budget", "external_job"}
    if set(spec) - allowed or spec.get("schema_version") != 1:
        raise FlowError("Unsupported TaskSpec version or unknown fields")
    safe_id(spec.get("task_id"))
    if spec.get("mode") not in MODES or not isinstance(spec.get("objective"), str) or not spec["objective"].strip():
        raise FlowError("Task requires a supported mode and objective")
    if not isinstance(spec.get("context"), dict) or not spec["context"]:
        raise FlowError("Context must identify the evidence/model/environment scope")
    permissions = spec.get("permissions", [])
    if not isinstance(permissions, list) or set(permissions) - {"execute", "sync", "notify", "agent-dispatch"}:
        raise FlowError("Unknown permissions; training recovery belongs to the configured external owner")
    if "budget" in spec and (not isinstance(spec["budget"], dict) or set(spec["budget"]) - {"max_operations", "max_seconds"}):
        raise FlowError("Invalid budget")
    for value in spec.get("budget", {}).values():
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 < value < float("inf"):
            raise FlowError("Budgets must be positive finite numbers")
    return spec


class Store:
    def __init__(self, root):
        self.root = Path(root).expanduser().resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.db_path = self.root / "state.sqlite3"
        with self.db() as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS tasks(id TEXT PRIMARY KEY,spec TEXT NOT NULL,state TEXT NOT NULL,context TEXT NOT NULL,revision INTEGER NOT NULL DEFAULT 0,created TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS artifacts(id TEXT PRIMARY KEY,path TEXT NOT NULL,size INTEGER NOT NULL,visibility TEXT NOT NULL,created TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS reports(task TEXT,kind TEXT,context TEXT,artifact TEXT,result TEXT,created TEXT,PRIMARY KEY(task,kind,context));
            CREATE TABLE IF NOT EXISTS events(seq INTEGER PRIMARY KEY AUTOINCREMENT,event_id TEXT UNIQUE,task TEXT,kind TEXT,payload TEXT,created TEXT);
            CREATE TABLE IF NOT EXISTS outbox(event_id TEXT PRIMARY KEY,channel TEXT,status TEXT,attempts INTEGER DEFAULT 0,detail TEXT);
            CREATE TABLE IF NOT EXISTS leases(resource TEXT PRIMARY KEY,owner TEXT,token INTEGER,expires REAL);
            CREATE TABLE IF NOT EXISTS operations(id TEXT PRIMARY KEY,task TEXT,request_hash TEXT,status TEXT,result TEXT,created TEXT);
            CREATE TABLE IF NOT EXISTS cursors(peer TEXT PRIMARY KEY,seq INTEGER NOT NULL);
            CREATE TABLE IF NOT EXISTS assignments(id TEXT PRIMARY KEY,task TEXT,payload TEXT,status TEXT);
            CREATE TABLE IF NOT EXISTS flows(task TEXT PRIMARY KEY,plan TEXT,goal TEXT,context TEXT);
            CREATE TABLE IF NOT EXISTS flow_rounds(task TEXT,number INTEGER,context TEXT,revision INTEGER,goal TEXT,candidate TEXT,review TEXT,status TEXT,failures INTEGER DEFAULT 0,PRIMARY KEY(task,number));
            CREATE TABLE IF NOT EXISTS flow_guidance(task TEXT,id TEXT,context TEXT,status TEXT,note TEXT,created TEXT,PRIMARY KEY(task,id));
            CREATE TABLE IF NOT EXISTS flow_guidance_cursor(task TEXT PRIMARY KEY,hash TEXT);
            CREATE TABLE IF NOT EXISTS flow_questions(task TEXT,id TEXT,payload TEXT,status TEXT,resolution TEXT,PRIMARY KEY(task,id));
            """)
            row = db.execute("SELECT value FROM meta WHERE key='schema'").fetchone()
            if row and row[0] != "1":
                raise FlowError("Unsupported workspace schema; do not overwrite it")
            db.execute("INSERT OR IGNORE INTO meta VALUES('schema','1')")

    @contextlib.contextmanager
    def db(self):
        db = sqlite3.connect(self.db_path, timeout=30)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA journal_mode=WAL")
        db.execute("PRAGMA foreign_keys=ON")
        try:
            with db:
                yield db
        finally:
            db.close()

    def event(self, db, task, kind, payload, event_id=None, channel=None):
        eid = event_id or uuid.uuid4().hex
        existing = db.execute("SELECT * FROM events WHERE event_id=?", (eid,)).fetchone()
        body = json.dumps(payload, sort_keys=True, ensure_ascii=False, allow_nan=False)
        if existing:
            if (existing["task"], existing["kind"], existing["payload"]) != (task, kind, body):
                raise FlowError("An event ID cannot be reused for different content")
            return eid
        db.execute("INSERT INTO events(event_id,task,kind,payload,created) VALUES(?,?,?,?,?)", (eid, task, kind, body, utc()))
        if channel:
            db.execute("INSERT INTO outbox(event_id,channel,status) VALUES(?,?,'pending')", (eid, channel))
        return eid

    def create(self, spec):
        validate_spec(spec)
        with self.db() as db:
            db.execute("INSERT INTO tasks(id,spec,state,context,created) VALUES(?,?,'draft',?,?)", (spec["task_id"], json.dumps(spec), fingerprint(spec["context"]), utc()))
            self.event(db, spec["task_id"], "task-created", {"mode": spec["mode"]})
        return self.task(spec["task_id"])

    def task(self, tid):
        with self.db() as db:
            row = db.execute("SELECT * FROM tasks WHERE id=?", (tid,)).fetchone()
        if not row:
            raise FlowError("Unknown task: " + tid)
        result = dict(row)
        result["spec"] = json.loads(result["spec"])
        return result

    def put(self, data, visibility="private"):
        if visibility not in {"private", "public"}:
            raise FlowError("Invalid visibility")
        sha = digest(data)
        path = self.root / "objects" / sha[:2] / sha
        if path.exists():
            if digest(path.read_bytes()) != sha:
                raise FlowError("Corrupted existing artifact")
        else:
            atomic_write(path, data)
        with self.db() as db:
            old = db.execute("SELECT visibility FROM artifacts WHERE id=?", (sha,)).fetchone()
            # Identical private bytes never silently become public through re-import.
            effective = "private" if old and old[0] == "private" else visibility
            db.execute("INSERT INTO artifacts VALUES(?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET visibility=?", (sha, path.relative_to(self.root).as_posix(), len(data), effective, utc(), effective))
        return sha

    def artifact(self, sha):
        with self.db() as db:
            row = db.execute("SELECT * FROM artifacts WHERE id=?", (sha,)).fetchone()
        if not row:
            raise FlowError("Unknown artifact")
        data = child(self.root, row["path"]).read_bytes()
        if digest(data) != sha:
            raise FlowError("Artifact hash mismatch")
        return data

    def report(self, tid, kind, value):
        task = self.task(tid)
        if value.get("context") != task["context"]:
            raise FlowError("Report belongs to another environment/model/source context")
        if value.get("status") not in {"pass", "fail", "incomplete", "complete"}:
            raise FlowError("Report needs an explicit status")
        if not value.get("evidence") or not isinstance(value["evidence"], list):
            raise FlowError("Report requires retained evidence IDs")
        for sha in value["evidence"]:
            self.artifact(sha)
        if value["status"] == "pass" and (value.get("executed", 0) <= 0 or value.get("failures", 0) or value.get("required_missing")):
            raise FlowError("PASS requires actual execution, no failures and required coverage")
        data = json.dumps(value, ensure_ascii=False, allow_nan=False).encode()
        sha = self.put(data)
        with self.db() as db:
            db.execute("INSERT OR REPLACE INTO reports VALUES(?,?,?,?,?,?)", (tid, kind, task["context"], sha, value["status"], utc()))
            self.event(db, tid, "report-recorded", {"kind": kind, "artifact": sha, "status": value["status"]})
        return {"artifact": sha, "status": value["status"]}

    def change_context(self, tid, context):
        if not isinstance(context, dict) or not context:
            raise FlowError("A nonempty context is required")
        with self.db() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT * FROM tasks WHERE id=?", (tid,)).fetchone()
            if not row:
                raise FlowError("Unknown task")
            if row["state"] in {"completed", "cancelled"}:
                raise FlowError("Terminal task; create a new task for a new context")
            spec = json.loads(row["spec"])
            spec["context"] = context
            db.execute("UPDATE tasks SET spec=?,context=?,state='prepared',revision=revision+1 WHERE id=?", (json.dumps(spec), fingerprint(context), tid))
            self.event(db, tid, "context-changed", {"old": row["context"], "new": fingerprint(context), "evidence": "requires-revalidation"})
        return self.task(tid)

    def transition(self, tid, state, reason=None):
        from .flow import sync_guidance, guard_transition
        sync_guidance(self, tid)
        with self.db() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT * FROM tasks WHERE id=?", (tid,)).fetchone()
            if not row:
                raise FlowError("Unknown task")
            spec = json.loads(row["spec"])
            if row["state"] in {"completed", "cancelled"}:
                raise FlowError("Terminal task; create a new task")
            guard_transition(self, db, dict(row), state)
            if state in {"paused", "blocked", "failed", "cancelled"}:
                if not reason:
                    raise FlowError("A reason is required")
            else:
                modes = {"environment": "environment", "adapt": "baseline", "analyze": "analysis", "diagnose": "diagnosis", "optimize": "stage-quality", "operate": "operations"}
                reports = {x["kind"]: x for x in db.execute("SELECT * FROM reports WHERE task=? AND context=?", (tid, row["context"]))}
                if state == "completed" and spec["mode"] in modes:
                    kind = modes[spec["mode"]]
                    if kind not in reports:
                        raise FlowError("Missing requested deliverable: " + kind)
                    if spec["mode"] in {"adapt", "optimize"} and reports[kind]["result"] != "pass":
                        raise FlowError("The requested validated result has not passed")
                elif state == "prepared":
                    if row["state"] not in {"draft", "paused", "blocked", "failed"}:
                        raise FlowError("Cannot reset an active task without a context change")
                else:
                    if state not in PIPELINE or row["state"] not in PIPELINE or PIPELINE.index(state) != PIPELINE.index(row["state"]) + 1:
                        raise FlowError("Invalid state transition")
                    for kind in GATES.get(state, []):
                        accepted = {"pass", "complete"} if kind == "analysis" else {"pass"}
                        if kind not in reports or reports[kind]["result"] not in accepted:
                            raise FlowError("Missing passing current evidence: " + kind)
            db.execute("UPDATE tasks SET state=?,revision=revision+1 WHERE id=?", (state, tid))
            self.event(db, tid, "state-changed", {"from": row["state"], "to": state, "reason": reason})
        return self.task(tid)

    def lease(self, resource, owner, ttl=300):
        if ttl <= 0 or ttl > 86400:
            raise FlowError("Lease TTL must be in (0,86400]")
        with self.db() as db:
            db.execute("BEGIN IMMEDIATE")
            running = db.execute("SELECT o.id FROM operations o JOIN events e ON json_extract(e.payload,'$.operation')=o.id WHERE e.kind='operation-started' AND json_extract(e.payload,'$.lease.resource')=? AND o.status IN ('started','unknown')", (resource,)).fetchone()
            if running:
                raise FlowError("Resource has an unresolved execution; reconcile before acquiring it")
            row = db.execute("SELECT * FROM leases WHERE resource=?", (resource,)).fetchone()
            if row and row["expires"] > time.time():
                raise FlowError("Resource is already leased; renew with its fencing token")
            token = row["token"] + 1 if row else 1
            db.execute("INSERT OR REPLACE INTO leases VALUES(?,?,?,?)", (resource, owner, token, time.time() + ttl))
        return {"resource": resource, "owner": owner, "token": token}

    def check_lease(self, db, resource, owner, token):
        row = db.execute("SELECT * FROM leases WHERE resource=?", (resource,)).fetchone()
        if not row or row["owner"] != owner or row["token"] != token or row["expires"] <= time.time():
            raise FlowError("Expired lease or stale fencing token")

    def renew(self, lease, ttl=300):
        if not 0 < ttl <= 86400:
            raise FlowError("Invalid lease duration")
        with self.db() as db:
            db.execute("BEGIN IMMEDIATE")
            self.check_lease(db, **lease)
            db.execute("UPDATE leases SET expires=? WHERE resource=?", (time.time() + ttl, lease["resource"]))
        return lease

    def events(self, after=0):
        with self.db() as db:
            return [{**dict(x), "payload": json.loads(x["payload"])} for x in db.execute("SELECT * FROM events WHERE seq>? ORDER BY seq", (after,))]

    def release(self, lease):
        with self.db() as db:
            db.execute("BEGIN IMMEDIATE")
            self.check_lease(db, **lease)
            db.execute("UPDATE leases SET expires=0 WHERE resource=?", (lease["resource"],))
        return {**lease, "released": True}
