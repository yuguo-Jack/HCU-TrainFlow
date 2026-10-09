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
    cmd('flow-start', 'task', 'file')
    q = cmd('flow-replan', 'task', 'file'); q.add_argument('--reason', required=True)
    cmd('flow-next', 'task')
    cmd('flow-submit', 'task', 'file')
    cmd('flow-review', 'task', 'file')
    q = cmd('flow-review-failed', 'task', 'round'); q.add_argument('--reason', required=True)
    cmd('flow-advance', 'task')
    cmd('flow-board', 'task')
    q = cmd('flow-watch', 'task'); q.add_argument('--once', action='store_true')
    q = cmd('flow-guidance-ack', 'task', 'hash'); q.add_argument('--decision', choices=['applied','queued','needs-human','not-applicable'], required=True); q.add_argument('--note', required=True)
    cmd('flow-question', 'task', 'file')
    q = cmd('flow-question-close', 'task', 'question'); q.add_argument('--guidance', required=True); q.add_argument('--note', required=True)
    cmd("artifact-add", "file")
    cmd("artifact-read", "sha", "destination")
    cmd("report-add", "task", "kind", "file")
    q = cmd("lease-acquire", "resource", "owner"); q.add_argument("--ttl", type=float, default=300)
    q = cmd("lease-renew", "file"); q.add_argument("--ttl", type=float, default=300)
    cmd("lease-release", "file")
    cmd("command-plan", "card")
    q = cmd("command-run", "task", "operation", "card", "lease_file"); q.add_argument('--assignment'); q.add_argument('--owner'); q.add_argument('--token',type=int)
    cmd("operation-reconcile", "operation", "file")
    cmd("assignment-add", "task", "file")
    q = cmd("assignment-return", "assignment", "owner", "report"); q.add_argument('--token',type=int,required=True)
    cmd('team-plan', 'task', 'file')
    cmd('team-next', 'task')
    cmd('assignment-claim', 'assignment', 'owner')
    q = cmd('assignment-bind', 'assignment', 'owner', 'session'); q.add_argument('--token',type=int,required=True)
    cmd('assignment-review', 'assignment', 'file')
    cmd('assignment-cancel', 'assignment', 'file')
    q = cmd('assignment-yield', 'assignment', 'owner', 'file'); q.add_argument('--token',type=int,required=True)
    cmd('agent-send', 'task', 'file')
    q = cmd('agent-inbox', 'task'); q.add_argument('--recipient')
    cmd('agent-ack', 'message', 'owner', 'file')
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
    q = cmd('tracelens-report', 'trace'); q.add_argument('--project', default=os.environ.get('TRAINFLOW_PROJECT', '.')); q.add_argument('--rank', type=int); q.add_argument('--gpu-arch-json'); q.add_argument('--timeout', type=int, default=1800)
    q = cmd('tracelens-collective', 'trace_pattern'); q.add_argument('--project', default=os.environ.get('TRAINFLOW_PROJECT', '.')); q.add_argument('--world-size', type=int, required=True); q.add_argument('--timeout', type=int, default=1800)
    q = cmd("watch", "task", "log", "policy"); q.add_argument("--once", action="store_true"); q.add_argument("--interval", type=float, default=10)
    q = cmd("heartbeat-check", "file"); q.add_argument("--max-age", type=float, required=True)
    q = cmd("events-export", "destination"); q.add_argument("--after", type=int, default=0)
    cmd("events-import", "peer", "file")
    q = cmd("inbox"); q.add_argument("--action", choices=["list", "claim", "complete", "retry"], default="list"); q.add_argument("--event"); q.add_argument("--owner")
    cmd("monitor-report", "task", "output")
    cmd("public-export", "source", "destination", "manifest")
    cmd('experience-record','task','file')
    cmd('experience-index')
    q=cmd('experience-sync'); q.add_argument('task',nargs='?')
    cmd('experience-read','id')
    cmd('experience-compare','left','right')
    q=cmd('experience-search','query'); q.add_argument('--limit',type=int,default=10)
    q.add_argument('--model'); q.add_argument('--environment'); q.add_argument('--kind'); q.add_argument('--context')
    cmd("wiki-index", "project")
    q=cmd('wiki-read','id'); select=q.add_mutually_exclusive_group()
    select.add_argument('--generation'); select.add_argument('--project')
    cmd('wiki-catalog','project')
    q = cmd("wiki-search", "query"); q.add_argument("--limit", type=int, default=10); q.add_argument("--engine"); q.add_argument("--stage")
    q.add_argument('--kind',choices=['authored','source-pr','source-map','source-document'])
    q.add_argument('--project', default=os.environ.get('TRAINFLOW_PROJECT','.')); q.add_argument('--online-pr',choices=['auto','always','off'],default='auto')
    q.add_argument('--pr-query'); q.add_argument('--repo',action='append',default=[]); q.add_argument('--source')
    q = cmd('wiki-search-pr', 'query'); q.add_argument('--project',default=os.environ.get('TRAINFLOW_PROJECT','.'))
    q.add_argument('--engine'); q.add_argument('--source'); q.add_argument('--repo',action='append',default=[])
    q.add_argument('--limit',type=int,default=10); q.add_argument('--state',choices=['all','open','closed','merged'],default='all'); q.add_argument('--branch'); q.add_argument('--page',type=int,default=1)
    q = cmd('wiki-code','repository','commit','path'); q.add_argument('--max-chars',type=int,default=24000)
    q = cmd('wiki-inventory','project','source'); q.add_argument('--retain',action='store_true')
    cmd('wiki-triage','project','source','decisions')
    q = cmd('wiki-sync-prs','project','source'); q.add_argument('--max-prs',type=int,default=10); q.add_argument('--since')
    q = cmd('wiki-sync-docs','project','source'); q.add_argument('--max-documents',type=int,default=40)
    q = cmd('wiki-update','project','source'); q.add_argument('--max-prs',type=int,default=10); q.add_argument('--max-documents',type=int,default=40); q.add_argument('--since')
    cmd('wiki-apply','project','stage')
    cmd("wiki-refresh", "project", "source")
    q = cmd("wiki-pr", "repository", "number"); q.add_argument("--output"); q.add_argument('--retain-project'); q.add_argument('--engine',default='unspecified'); q.add_argument('--max-pages',type=int,default=20)
    cmd('wiki-review-pr','project','id','decisions')
    q = cmd("wiki-review", "project", "stage", "decisions"); q.add_argument('--defer-workflows',metavar='REASON')
    cmd("demo", "destination")
    cmd('collaboration-demo', 'destination')
    return p


def execute(a):
    from . import analysis, coordination, delivery, environment, execution, flow, monitor, quality, team, wiki, official, experience
    store = Store(a.workspace)
    c = a.command
    if c == "init": return {"workspace": str(store.root), "schema_version": 1, "version": __version__}
    if c == "task-create": return store.create(read_json(a.spec))
    if c == "task-show": return store.task(a.task)
    if c == "task-context": return store.change_context(a.task, read_json(a.context_file))
    if c == "task-transition": return store.transition(a.task, a.state, a.reason)
    if c in {'flow-start', 'flow-replan'}: return flow.start(store, a.task, read_json(a.file), getattr(a, 'reason', None))
    if c == 'flow-next': return flow.next_step(store, a.task)
    if c == 'flow-submit': return flow.submit(store, a.task, read_json(a.file))
    if c == 'flow-review': return flow.review(store, a.task, read_json(a.file))
    if c == 'flow-review-failed': return flow.review_failure(store, a.task, int(a.round), a.reason)
    if c == 'flow-advance': return flow.advance(store, a.task)
    if c == 'flow-guidance-ack': return flow.acknowledge(store, a.task, a.hash, a.decision, a.note)
    if c == 'flow-question': return flow.question(store, a.task, read_json(a.file))
    if c == 'flow-question-close': return flow.close_question(store, a.task, a.question, a.guidance, a.note)
    if c in {'flow-board', 'flow-watch'}:
        while True:
            change = flow.sync_guidance(store, a.task, force=c == 'flow-board' or a.once)
            result = {**flow.render_board(store, a.task), **change}
            if c == 'flow-board' or a.once: return result
            if change['new']: print(json.dumps(result, ensure_ascii=False), flush=True)
            with store.db() as db: interval = flow.get_flow(db, a.task)['plan']['poll_seconds']
            time.sleep(interval)
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
    if c == "command-run": return execution.run_command(store, a.task, a.operation, read_json(a.card), read_json(a.lease_file),assignment=a.assignment,owner=a.owner,token=a.token)
    if c == "operation-reconcile": return coordination.reconcile_operation(store, a.operation, **read_json(a.file))
    if c == "assignment-add": return coordination.assign(store, a.task, read_json(a.file))
    if c == "assignment-return": return coordination.finish_assignment(store, a.assignment, a.owner, a.report, a.token)
    if c == 'team-plan': return team.plan(store,a.task,read_json(a.file))
    if c == 'team-next': return team.schedule(store,a.task)
    if c == 'assignment-claim': return team.claim(store,a.assignment,a.owner)
    if c == 'assignment-bind': return team.bind(store,a.assignment,a.owner,a.token,a.session)
    if c == 'assignment-review': return team.review(store,a.assignment,read_json(a.file))
    if c == 'assignment-cancel': return team.cancel(store,a.assignment,read_json(a.file))
    if c == 'assignment-yield': return team.yield_assignment(store,a.assignment,a.owner,a.token,read_json(a.file))
    if c == 'agent-send': return team.send(store,a.task,read_json(a.file))
    if c == 'agent-inbox': return {'messages':team.messages(store,a.task,a.recipient)}
    if c == 'agent-ack': return team.acknowledge(store,a.message,a.owner,read_json(a.file))
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
    if c in {'tracelens-report', 'tracelens-collective'}:
        from .tracelens import run_report
        if c == 'tracelens-report':
            return run_report(store, a.project, trace=a.trace, rank=a.rank, gpu_arch_json=a.gpu_arch_json, timeout=a.timeout)
        return run_report(store, a.project, trace_pattern=a.trace_pattern, world_size=a.world_size, timeout=a.timeout)
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
    if c == 'experience-record': return experience.record(store,a.task,read_json(a.file))
    if c == 'experience-index': return experience.rebuild(store)
    if c == 'experience-sync': return experience.sync(store,a.task)
    if c == 'experience-read': return experience.get(store,a.id)
    if c == 'experience-compare': return experience.compare(store,a.left,a.right)
    if c == 'experience-search': return experience.search(store,a.query,a.limit,a.model,a.environment,a.kind,a.context)
    if c == "wiki-index": return wiki.index_wiki(store, a.project)
    if c == 'wiki-read':
        generation=wiki.index_wiki(store,a.project)['generation'] if a.project else a.generation
        return wiki.read_page(store,a.id,generation)
    if c == 'wiki-catalog': return official.catalog(a.project)
    if c == 'wiki-search-pr':
        return official.annotate_prs(a.project,official.search_prs(store,a.query,official.engine_repos(a.project,a.engine,a.source,a.repo),
                                   limit=a.limit,state=a.state,branch=a.branch,page=a.page))
    if c == 'wiki-code': return official.read_code(store,a.repository,a.commit,a.path,max_chars=a.max_chars)
    if c == 'wiki-inventory': return official.inventory(store,a.project,a.source,retain=a.retain)
    if c == 'wiki-triage': return official.triage_inventory(store,a.project,a.source,read_json(a.decisions))
    if c == 'wiki-sync-prs': return official.sync_prs(store,a.project,a.source,max_prs=a.max_prs,since=a.since)
    if c == 'wiki-sync-docs': return official.sync_documents(store,a.project,a.source,max_documents=a.max_documents)
    if c == 'wiki-update': return official.update_source(store,a.project,a.source,max_prs=a.max_prs,max_documents=a.max_documents,since=a.since)
    if c == 'wiki-apply': return official.apply_refresh(store,a.project,a.stage)
    if c == "wiki-search":
        index=wiki.index_wiki(store,a.project)
        result=wiki.search_wiki(store,a.query,a.limit,a.engine,a.stage,a.kind,index=index)
        if a.online_pr == 'always' or a.online_pr=='auto' and not result['results']:
            result['online_pr']=official.annotate_prs(a.project,official.search_prs(store,a.pr_query or a.query,official.engine_repos(a.project,a.engine,a.source,a.repo),limit=a.limit))
            if result['online_pr'].get('status') == 'partial':
                result['status']='partial'
        result['followup']='If local candidates are insufficient, wiki-search-pr -> wiki-pr -> wiki-code at exact head/base; no HCU-Knowledge update.'
        return result
    if c == "wiki-refresh": return wiki.refresh_source(store, a.project, a.source, os.environ.get("GITHUB_TOKEN"))
    if c == "wiki-pr":
        result = official.read_pr(store, a.repository, int(a.number), max_pages=a.max_pages)
        if a.retain_project: result['retained']=official.retain_pr(store,a.retain_project,result,a.engine)
        if a.output: write_json(a.output, result)
        return result
    if c == "wiki-review":
        decisions = read_json(a.decisions)
        return wiki.review_refresh(store, a.stage, decisions["pages"], a.project, decisions.get("workflows"),a.defer_workflows)
    if c == 'wiki-review-pr': return official.review_pr(store,a.project,a.id,read_json(a.decisions))
    if c == "demo":
        from .demo import run_demo
        return run_demo(a.destination)
    if c == 'collaboration-demo':
        from .collaboration_demo import run_demo
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
