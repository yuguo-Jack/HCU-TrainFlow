"""Rebuildable local Wiki search and staged public-source refresh.

Source acquisition never silently edits authored conclusions or advances a live
task's source lock. Failed pagination is visible, and review is per affected page.
"""
import hashlib
import contextlib
import json
from pathlib import Path
import re
import sqlite3
import urllib.error
import urllib.parse
import urllib.request

import yaml

from .core import FlowError, atomic_write, child, digest, fingerprint, read_json, safe_id, utc, write_json


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise FlowError("Redirect rejected before forwarding credentials; register canonical repository")


def parse_page(path):
    text = Path(path).read_text(encoding="utf-8-sig")
    if text.startswith("---\n"):
        _, front, body = text.split("---", 2)
        meta = yaml.safe_load(front) or {}
    else:
        meta, body = {}, text
    return meta, body.strip()


def terms(text):
    result = []
    for word in re.findall(r"[A-Za-z_][A-Za-z0-9_.:-]*|[\u3400-\u9fff]+|[0-9]+", text.lower()):
        if re.search(r"[\u3400-\u9fff]", word):
            result.extend(word[i:i+2] for i in range(max(1, len(word)-1)))
        else:
            result.extend([word] + [x for x in re.split(r"[_.:-]", word) if x != word])
    return list(dict.fromkeys(result))


def index_wiki(store, project):
    root = Path(project).resolve() / "knowledge"
    if not root.is_dir():
        raise FlowError("Project knowledge directory not found")
    records = []
    for path in sorted(root.rglob("*.md")):
        meta, body = parse_page(path)
        if meta.get("visibility", "public") != "public":
            continue
        records.append((path, meta, body))
    identities = [m.get("id", p.relative_to(root).as_posix()) for p, m, _ in records]
    if len(identities) != len(set(identities)):
        raise FlowError("Duplicate Wiki page ID")
    generation = fingerprint({"root": str(root), "pages": {p.relative_to(root).as_posix(): digest(p.read_bytes()) for p, _, _ in records}})
    destination = store.root / "wiki" / (generation + ".sqlite3")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists():
        temp = destination.with_suffix(".building")
        if temp.exists():
            raise FlowError("Interrupted Wiki build exists; inspect it before retry")
        with contextlib.closing(sqlite3.connect(temp)) as db, db:
            db.execute("CREATE TABLE pages(id TEXT PRIMARY KEY,title TEXT,path TEXT,body TEXT,metadata TEXT,sha256 TEXT)")
            db.execute("CREATE VIRTUAL TABLE fts USING fts5(title,body)")
            for path, meta, body in records:
                pid = meta.get("id", path.relative_to(root).as_posix())
                title = meta.get("title", next((x[2:] for x in body.splitlines() if x.startswith("# ")), path.stem))
                cursor = db.execute("INSERT INTO pages VALUES(?,?,?,?,?,?)", (pid, title, str(path), body, json.dumps(meta, ensure_ascii=False), digest(path.read_bytes())))
                db.execute("INSERT INTO fts(rowid,title,body) VALUES(?,?,?)", (cursor.lastrowid, " ".join(terms(title)), " ".join(terms(body))))
        temp.rename(destination)
    write_json(store.root / "wiki/active.json", {"generation": generation, "path": str(destination), "root": str(root), "pages": len(records), "created_at": utc()})
    return {"generation": generation, "pages": len(records)}


def search_wiki(store, query, limit=10, engine=None, stage=None):
    if not isinstance(limit, int) or not 1 <= limit <= 100:
        raise FlowError("Search limit must be in [1,100]")
    active = store.root / "wiki/active.json"
    if not active.exists():
        raise FlowError("Run wiki index first; no upstream refresh is needed for local indexing")
    state = read_json(active)
    tokens = terms(query)
    if not tokens:
        return {"results": [], "generation": state["generation"]}
    expression = " OR ".join('"' + x.replace('"', '""') + '"' for x in tokens[:50])
    conditions, args = ["fts MATCH ?"], [expression]
    if engine:
        conditions.append("json_extract(metadata,'$.engine')=?")
        args.append(engine)
    if stage:
        conditions.append("EXISTS(SELECT 1 FROM json_each(json_extract(metadata,'$.stages')) WHERE value=?)")
        args.append(stage)
    with contextlib.closing(sqlite3.connect(Path(state["path"]).as_uri() + "?mode=ro", uri=True)) as db:
        db.row_factory = sqlite3.Row
        rows = db.execute("SELECT pages.*,bm25(fts,4,1) score FROM fts JOIN pages ON pages.rowid=fts.rowid WHERE " + " AND ".join(conditions) + " ORDER BY score LIMIT ?", args + [limit]).fetchall()
    results = []
    for row in rows:
        value = dict(row)
        value["metadata"] = json.loads(value["metadata"])
        path = Path(value["path"])
        value["review_state"] = "indexed-snapshot" if path.exists() and digest(path.read_bytes()) == value["sha256"] else "local-page-changed; reindex"
        value["excerpt"] = value.pop("body")[:1600]
        results.append(value)
    return {"results": results, "generation": state["generation"], "instruction": "Read full page and pinned source before relying on a conclusion; retrieval does not refresh sources."}


def _get_json(url, token=None):
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname != "api.github.com" or parsed.username or parsed.password:
        raise FlowError("Public GitHub adapter only accepts api.github.com HTTPS URLs")
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "HCU-TrainFlow"}
    if token:
        headers["Authorization"] = "Bearer " + token
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.build_opener(NoRedirect()).open(request, timeout=60) as response:
            if urllib.parse.urlsplit(response.url).hostname != "api.github.com":
                raise FlowError("Unexpected API redirect")
            return json.load(response), response.headers.get("Link", "")
    except urllib.error.HTTPError as exc:
        raise FlowError(f"GitHub HTTP {exc.code}; check permission/rate limit separately") from None


def pages(url, token=None, max_pages=100):
    rows, seen = [], set()
    while url:
        if url in seen or len(seen) >= max_pages:
            raise FlowError("Pagination incomplete; cursor not advanced")
        seen.add(url)
        body, links = _get_json(url, token)
        if not isinstance(body, list):
            raise FlowError("Expected paginated array")
        rows.extend(body)
        match = re.search(r'<([^>]+)>; rel="next"', links)
        url = match.group(1) if match else None
    return rows


def refresh_source(store, project, source_id, token=None):
    safe_id(source_id)
    registry = read_json(Path(project) / "knowledge/sources.json")
    source = next((x for x in registry if x["id"] == source_id), None)
    if not source:
        raise FlowError("Source is not registered")
    repo = source["repository"]
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo):
        raise FlowError("Invalid public repository identity")
    ref = source["ref"]
    commit, _ = _get_json(f"https://api.github.com/repos/{repo}/commits/{urllib.parse.quote(ref, safe='')}", token)
    sha = commit["sha"]
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise FlowError("Unexpected commit SHA")
    cursor_path = store.root / "wiki/sources" / (source_id + ".json")
    previous = read_json(cursor_path) if cursor_path.exists() else {"files": {}}
    files, failures = {}, []
    for name in source["paths"]:
        if name.startswith("/") or ".." in Path(name).parts:
            raise FlowError("Invalid registered source path")
        url = f"https://raw.githubusercontent.com/{repo}/{sha}/" + urllib.parse.quote(name)
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "HCU-TrainFlow"}), timeout=60) as response:
                data = response.read(16 * 1024 * 1024 + 1)
            if len(data) > 16 * 1024 * 1024:
                raise FlowError("Source exceeds acquisition size limit")
            files[name] = {"sha256": store.put(data, "public"), "url": f"https://github.com/{repo}/blob/{sha}/{name}"}
        except (OSError, FlowError):
            failures.append({"path": name, "status": "unavailable"})
    reviewed_path = store.root / "wiki/reviewed-sources" / (source_id + ".json")
    reviewed = read_json(reviewed_path) if reviewed_path.exists() else {"files": source.get("baseline_files", {})}
    changes = sorted(name for name in files.keys() | reviewed["files"].keys() if files.get(name, {}).get("sha256") != reviewed["files"].get(name, {}).get("sha256"))
    affected = []
    for path in (Path(project) / "knowledge").rglob("*.md"):
        meta, _ = parse_page(path)
        refs = [x for x in meta.get("sources", []) if x.get("source") == source_id]
        if refs and any(x.get("path") in changes for x in refs):
            affected.append({"page": path.relative_to(project).as_posix(), "page_sha256": digest(path.read_bytes()), "status": "pending-content-review"})
    maintenance = []
    maintenance_path = Path(project) / "knowledge/maintenance.json"
    if maintenance_path.exists():
        for rule in read_json(maintenance_path):
            if rule["source"] == source_id and any(name in changes for name in rule["paths"]):
                maintenance.extend(rule["targets"])
    result = {"source": source_id, "repository": repo, "ref": ref, "commit": sha, "files": files, "changed_paths": changes,
              "affected_pages": affected, "affected_workflows": sorted(set(maintenance)), "failures": failures, "observed_at": utc(), "status": "partial" if failures else "collected-not-reviewed"}
    stage_id = fingerprint(result)
    write_json(store.root / "wiki/staging" / (stage_id + ".json"), result)
    if not failures:
        write_json(cursor_path, result)
    return {"stage_id": stage_id, **result}


def collect_pr(store, repository, number, token=None):
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository) or number <= 0:
        raise FlowError("Invalid public PR identity")
    base = f"https://api.github.com/repos/{repository}"
    detail, _ = _get_json(f"{base}/pulls/{number}", token)
    data = {"repository": repository, "number": number, "detail": detail,
            "issue_comments": pages(f"{base}/issues/{number}/comments?per_page=100", token),
            "inline_comments": pages(f"{base}/pulls/{number}/comments?per_page=100", token),
            "reviews": pages(f"{base}/pulls/{number}/reviews?per_page=100", token),
            "files": pages(f"{base}/pulls/{number}/files?per_page=100", token)}
    missing_patches = [x["filename"] for x in data["files"] if not x.get("patch")]
    data["coverage"] = {"discussion_pagination": "complete", "diff": "partial" if missing_patches or detail.get("changed_files", 0) != len(data["files"]) else "api-files", "missing_patches": missing_patches,
                        "limit": "GitHub file APIs can truncate large diffs; inspect exact head/base source before conclusions"}
    sha = store.put(json.dumps(data, ensure_ascii=False).encode(), "public")
    return {"artifact": sha, "coverage": data["coverage"], "reviews": len(data["reviews"]), "status": "collected-not-reviewed"}


def review_refresh(store, stage_id, decisions, project, workflow_decisions=None):
    if not re.fullmatch(r"[0-9a-f]{64}", stage_id):
        raise FlowError("Invalid stage ID")
    stage = read_json(store.root / "wiki/staging" / (stage_id + ".json"))
    if stage["failures"]:
        raise FlowError("Partial source refresh cannot be marked reviewed")
    expected = {x["page"] for x in stage["affected_pages"]}
    if set(decisions) != expected:
        raise FlowError("Every affected overview/topic/case needs an explicit content decision")
    workflow_decisions = workflow_decisions or {}
    if set(workflow_decisions) != set(stage.get("affected_workflows", [])):
        raise FlowError("Affected Skills/adapters need review as well as Wiki pages")
    for path, decision in {**decisions, **workflow_decisions}.items():
        if decision.get("decision") not in {"updated", "still-applicable", "historical"} or not decision.get("note"):
            raise FlowError("Review requires a substantive per-page conclusion")
        current = child(project, path)
        if digest(current.read_bytes()) != decision.get("page_sha256"):
            raise FlowError("Reviewed page changed; renew its review")
        if decision.get("source_commit") != stage["commit"]:
            raise FlowError("Review must address the newly observed source commit")
    latest_path = store.root / "wiki/sources" / (stage["source"] + ".json")
    if latest_path.exists() and read_json(latest_path)["commit"] != stage["commit"]:
        raise FlowError("A newer source was observed; review that stage instead")
    receipt = {"stage_id": stage_id, "decisions": decisions, "workflow_decisions": workflow_decisions, "reviewed_at": utc(), "status": "content-reviewed", "runtime_validated": False}
    write_json(store.root / "wiki/reviews" / (stage_id + ".json"), receipt)
    write_json(store.root / "wiki/reviewed-sources" / (stage["source"] + ".json"), stage)
    return receipt
