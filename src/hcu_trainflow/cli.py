"""JSON CLI for agents and humans. Inputs are explicit; no site discovery side effects."""
import argparse
import json
import os
from pathlib import Path
import sqlite3
import sys
import time

from . import __version__
from .core import FlowError, Store, read_json, write_json


def parser():
    p = argparse.ArgumentParser(prog="hcu-trainflow", description="Local-centred HCU training workflow and evidence tools")
    p.add_argument("--version", action="version", version=__version__)
    p.add_argument("--workspace", default=os.environ.get("TRAINFLOW_WORKSPACE", ".work"), help="Private mutable state, never a public repository data directory")
    sub = p.add_subparsers(dest="command", required=True)
    def cmd(name, *fields):
        q = sub.add_parser(name)
        for field in fields:
            q.add_argument(field)
        return q
    cmd("init")
    cmd("task-create", "spec")
    cmd("task-show", "task")
    cmd("task-context", "task", "context_file")
    q = cmd("task-transition", "task", "state"); q.add_argument("--reason")
    cmd("artifact-add", "file")
    cmd("artifact-read", "sha", "destination")
    cmd("report-add", "task", "kind", "file")
    q = cmd("lease-acquire", "resource", "owner"); q.add_argument("--ttl", type=float, default=300)
    q = cmd("lease-renew", "file"); q.add_argument("--ttl", type=float, default=300)
    cmd("lease-release", "file")
    cmd("command-plan", "card")
    cmd("command-run", "task", "operation", "card", "lease_file")
    cmd("operation-reconcile", "operation", "file")
    cmd("assignment-add", "task", "file")
    cmd("assignment-return", "assignment", "owner", "report")
    cmd("inbox-dispatch", "event", "owner", "card", "lease_file")
    q = cmd("source-snapshot", "repository"); q.add_argument("paths", nargs="+")
    cmd("source-materialize", "snapshot", "destination")
    cmd("source-bundle", "snapshot", "destination")
    cmd("source-receive", "archive", "destination")
    cmd("environment-check", "contract", "observations")
    cmd("proxy-check", "full", "candidate")
    cmd("quality-check", "contract", "baseline", "candidate")
    cmd("iteration-check", "file")
    cmd("profile-plan", "file")
    q = cmd("profile-analyze", "trace", "window"); q.add_argument("--models"); q.add_argument("--output"); q.add_argument("--groups")
    q = cmd("watch", "task", "log", "policy"); q.add_argument("--once", action="store_true"); q.add_argument("--interval", type=float, default=10)
    q = cmd("heartbeat-check", "file"); q.add_argument("--max-age", type=float, required=True)
    q = cmd("events-export", "destination"); q.add_argument("--after", type=int, default=0)
    cmd("events-import", "peer", "file")
    q = cmd("inbox"); q.add_argument("--action", choices=["list", "claim", "complete", "retry"], default="list"); q.add_argument("--event"); q.add_argument("--owner")
    cmd("monitor-report", "task", "output")
    cmd("public-export", "source", "destination", "manifest")
    cmd("wiki-index", "project")
    q = cmd("wiki-search", "query"); q.add_argument("--limit", type=int, default=10); q.add_argument("--engine"); q.add_argument("--stage")
    cmd("wiki-refresh", "project", "source")
    q = cmd("wiki-pr", "repository", "number"); q.add_argument("--output")
    cmd("wiki-review", "project", "stage", "decisions")
    cmd("demo", "destination")
    return p


def execute(a):
    from . import analysis, coordination, delivery, environment, execution, monitor, quality, wiki
    store = Store(a.workspace)
    c = a.command
    if c == "init": return {"workspace": str(store.root), "schema_version": 1, "version": __version__}
    if c == "task-create": return store.create(read_json(a.spec))
    if c == "task-show": return store.task(a.task)
    if c == "task-context": return store.change_context(a.task, read_json(a.context_file))
    if c == "task-transition": return store.transition(a.task, a.state, a.reason)
    if c == "artifact-add": return {"artifact": store.put(Path(a.file).read_bytes()), "visibility": "private"}
    if c == "artifact-read":
        from .core import atomic_write
        if Path(a.destination).exists(): raise FlowError("Destination exists")
        atomic_write(a.destination, store.artifact(a.sha)); return {"destination": a.destination}
    if c == "report-add": return store.report(a.task, a.kind, read_json(a.file))
    if c == "lease-acquire": return store.lease(a.resource, a.owner, a.ttl)
    if c == "lease-renew": return store.renew(read_json(a.file), a.ttl)
    if c == "lease-release": return store.release(read_json(a.file))
    if c == "command-plan": return execution.command_plan(read_json(a.card))
    if c == "command-run": return execution.run_command(store, a.task, a.operation, read_json(a.card), read_json(a.lease_file))
    if c == "operation-reconcile": return coordination.reconcile_operation(store, a.operation, **read_json(a.file))
    if c == "assignment-add": return coordination.assign(store, a.task, read_json(a.file))
    if c == "assignment-return": return coordination.finish_assignment(store, a.assignment, a.owner, a.report)
    if c == "inbox-dispatch": return coordination.dispatch_inbox(store, a.event, a.owner, read_json(a.card), read_json(a.lease_file))
    if c == "source-snapshot": return execution.snapshot(store, a.repository, a.paths)
    if c == "source-materialize": return execution.materialize(store, a.snapshot, a.destination)
    if c == "source-bundle": return execution.bundle(store, a.snapshot, a.destination)
    if c == "source-receive": return execution.receive(store, a.archive, a.destination)
    if c == "environment-check": return environment.assess_health(read_json(a.contract), read_json(a.observations))
    if c == "proxy-check": return quality.proxy_contract(read_json(a.full), read_json(a.candidate))
    if c == "quality-check": return quality.compare_loss(read_json(a.contract), read_json(a.baseline), read_json(a.candidate))
    if c == "iteration-check": return quality.assess_iteration(**read_json(a.file))
    if c == "profile-plan":
        value = read_json(a.file); return analysis.profile_plan(value["groups"], value["available"])
    if c == "profile-analyze":
        result = analysis.analyze_trace(read_json(a.trace), read_json(a.window), read_json(a.models) if a.models else {})
        if a.groups:
            groups = read_json(a.groups)
            coverage = analysis.profile_plan(groups, [int(x) for x in result["ranks"] if x.isdecimal()])
            result["rank_coverage"] = coverage
            if coverage["status"] != "pass": result["status"] = "incomplete"
        else:
            result["rank_coverage"] = {"status": "unassessed", "reason": "Actual process groups were not supplied"}
            result["status"] = "incomplete"
        if a.output: write_json(a.output, result)
        return result
    if c == "watch":
        if not 0.1 <= a.interval <= 3600: raise FlowError("Watch interval must be in [0.1,3600]")
        policy = read_json(a.policy)
        if a.once: return monitor.poll_log(store, a.task, a.log, policy)
        while True:
            result = monitor.poll_log(store, a.task, a.log, policy)
            print(json.dumps(result, ensure_ascii=False, allow_nan=False), flush=True)
            time.sleep(a.interval)
    if c == "heartbeat-check": return monitor.check_heartbeat(a.file, a.max_age)
    if c == "events-export":
        events = store.events(a.after); write_json(a.destination, events)
        return {"events": len(events), "last_seq": events[-1]["seq"] if events else a.after}
    if c == "events-import": return monitor.import_events(store, a.peer, read_json(a.file))
    if c == "inbox": return monitor.inbox(store, a.action, a.event, a.owner)
    if c == "monitor-report": return delivery.monitor_report(store, a.task, a.output)
    if c == "public-export": return delivery.export_public(a.source, a.destination, read_json(a.manifest))
    if c == "wiki-index": return wiki.index_wiki(store, a.project)
    if c == "wiki-search": return wiki.search_wiki(store, a.query, a.limit, a.engine, a.stage)
    if c == "wiki-refresh": return wiki.refresh_source(store, a.project, a.source, os.environ.get("GITHUB_TOKEN"))
    if c == "wiki-pr":
        result = wiki.collect_pr(store, a.repository, int(a.number), os.environ.get("GITHUB_TOKEN"))
        if a.output: write_json(a.output, result)
        return result
    if c == "wiki-review":
        decisions = read_json(a.decisions)
        return wiki.review_refresh(store, a.stage, decisions["pages"], a.project, decisions.get("workflows"))
    if c == "demo":
        from .demo import run_demo
        return run_demo(a.destination)
    raise FlowError("Unsupported command")


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        result = execute(args)
        print(json.dumps(result, ensure_ascii=False, allow_nan=False, indent=2))
        status = result.get("status") if isinstance(result, dict) else None
        return 2 if status in {"fail", "failed", "incomplete", "partial", "rejected", "unknown", "attention"} else 0
    except KeyboardInterrupt:
        return 130
    except (FlowError, OSError, ValueError, KeyError, TypeError, sqlite3.Error) as exc:
        print(json.dumps({"status": "error", "message": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
