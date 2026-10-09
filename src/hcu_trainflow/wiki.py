"""Rebuildable local Wiki search and staged public-source refresh.

Source acquisition never silently edits authored conclusions or advances a live
task's source lock. Failed pagination is visible, and review is per affected page.
"""
import hashlib
import contextlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sqlite3
import functools
import os
import subprocess
import tempfile
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
    return parse_text(text)


def parse_text(text):
    text = text.replace('\r\n', '\n').replace('\r', '\n')
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
        raw = path.read_bytes()
        meta, body = parse_text(raw.decode('utf-8-sig'))
        if meta.get("visibility", "public") != "public":
            continue
        records.append((path, meta, body, digest(raw)))
    identities = [m.get("id", p.relative_to(root).as_posix()) for p, m, _, _ in records]
    if len(identities) != len(set(identities)):
        raise FlowError("Duplicate Wiki page ID")
    generation = fingerprint({"root": str(root), "pages": {p.relative_to(root).as_posix(): sha for p, _, _, sha in records}})
    destination = store.root / "wiki" / (generation + ".sqlite3")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists():
        fd, name = tempfile.mkstemp(prefix=generation+'-', suffix='.building', dir=destination.parent)
        os.close(fd)
        temp = Path(name)
        try:
            with contextlib.closing(sqlite3.connect(temp)) as db, db:
                db.execute("CREATE TABLE pages(id TEXT PRIMARY KEY,title TEXT,path TEXT,body TEXT,metadata TEXT,sha256 TEXT)")
                db.execute("CREATE VIRTUAL TABLE fts USING fts5(title,body)")
                for path, meta, body, sha in records:
                    pid = meta.get("id", path.relative_to(root).as_posix())
                    title = meta.get("title", next((x[2:] for x in body.splitlines() if x.startswith("# ")), path.stem))
                    cursor = db.execute("INSERT INTO pages VALUES(?,?,?,?,?,?)", (pid, title, str(path), body, json.dumps(meta, ensure_ascii=False), sha))
                    db.execute("INSERT INTO fts(rowid,title,body) VALUES(?,?,?)", (cursor.lastrowid, " ".join(terms(title)), " ".join(terms(body))))
            if not destination.exists():
                try:
                    temp.rename(destination)
                except FileExistsError:
                    pass  # A concurrent reader built the same immutable generation.
        finally:
            temp.unlink(missing_ok=True)
    state = {"generation": generation, "path": str(destination), "root": str(root), "pages": len(records), "created_at": utc()}
    write_json(store.root / "wiki/active.json", state)
    return state


def search_wiki(store, query, limit=10, engine=None, stage=None, kind=None, index=None):
    if not isinstance(limit, int) or not 1 <= limit <= 100:
        raise FlowError("Search limit must be in [1,100]")
    active = store.root / "wiki/active.json"
    if index is None and not active.exists():
        raise FlowError("Run wiki index first; no upstream refresh is needed for local indexing")
    state = index or read_json(active)
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
    if kind:
        conditions.append("coalesce(json_extract(metadata,'$.kind'),'authored')=?")
        args.append(kind)
    with contextlib.closing(sqlite3.connect(Path(state["path"]).as_uri() + "?mode=ro", uri=True)) as db:
        db.row_factory = sqlite3.Row
        rows = db.execute("SELECT pages.*,bm25(fts,4,1) * CASE json_extract(metadata,'$.kind') WHEN 'source-map' THEN 0.05 WHEN 'source-document' THEN 0.6 WHEN 'source-pr' THEN 0.8 ELSE 1 END score FROM fts JOIN pages ON pages.rowid=fts.rowid WHERE " + " AND ".join(conditions) + " ORDER BY score LIMIT ?", args + [limit]).fetchall()
    results = []
    for row in rows:
        value = dict(row)
        value["metadata"] = json.loads(value["metadata"])
        path = Path(value["path"])
        value["review_state"] = "indexed-snapshot" if path.exists() and digest(path.read_bytes()) == value["sha256"] else "local-page-changed; reindex"
        value["excerpt"] = value.pop("body")[:1600]
        results.append(value)
    return {"results": results, "generation": state["generation"], "instruction": "Read full page and pinned source before relying on a conclusion; retrieval does not refresh sources."}


def read_page(store, identity, generation=None):
    if generation is not None:
        if not re.fullmatch(r'[0-9a-f]{64}', generation):
            raise FlowError('Invalid Wiki generation')
        state={'generation':generation, 'path':str(store.root/'wiki'/f'{generation}.sqlite3')}
    else:
        state=read_json(store.root/'wiki/active.json')
    with contextlib.closing(sqlite3.connect(Path(state['path']).as_uri()+'?mode=ro',uri=True)) as db:
        db.row_factory=sqlite3.Row
        row=db.execute('SELECT * FROM pages WHERE id=?',(identity,)).fetchone()
    if not row:raise FlowError('Unknown Wiki page ID; index the current project first')
    value=dict(row);value['metadata']=json.loads(value['metadata'])
    value['generation']=state['generation']
    path=Path(value['path'])
    value['review_state']='indexed-snapshot' if path.is_file() and digest(path.read_bytes())==value['sha256'] else 'local-page-changed; reindex'
    return value


@functools.lru_cache(maxsize=1)
def github_token():
    token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
    if token:
        return token
    try:
        proc = subprocess.run(['git', '-c', 'credential.interactive=false', 'credential', 'fill'],
                              input=b'protocol=https\nhost=github.com\n\n', capture_output=True, timeout=10,
                              env={**os.environ,'GIT_TERMINAL_PROMPT':'0','GCM_INTERACTIVE':'Never'})
        fields = dict(line.split('=',1) for line in proc.stdout.decode().splitlines() if '=' in line)
        return fields.get('password')
    except (OSError, subprocess.TimeoutExpired, UnicodeError):
        return None


def _get_json(url, token=None):
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname != "api.github.com" or parsed.username or parsed.password:
        raise FlowError("Public GitHub adapter only accepts api.github.com HTTPS URLs")
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "HCU-TrainFlow"}
    token = token or github_token()
    if token:
        headers["Authorization"] = "Bearer " + token
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.build_opener(NoRedirect()).open(request, timeout=60) as response:
            if urllib.parse.urlsplit(response.url).hostname != "api.github.com":
                raise FlowError("Unexpected API redirect")
            return json.load(response), response.headers.get("Link", "")
    except urllib.error.HTTPError as exc:
        reason = 'authentication' if exc.code == 401 else 'permission or rate limit' if exc.code in {403,429} else 'resource unavailable or permission' if exc.code == 404 else 'request failed'
        raise FlowError(f"GitHub HTTP {exc.code}: {reason}; no empty-result inference") from None


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
    if source.get('kind') == 'web':
        sha, files, failures = collect_web_documents(store, source)
        ref = 'registered-official-pages'
    else:
        sha, files, failures = collect_git_files(store, source, token)
        ref = source['ref']
    return stage_source_refresh(store, project, source, sha, files, failures, ref)


def collect_git_files(store, source, token=None):
    repo = source['repository']
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo):
        raise FlowError("Invalid public repository identity")
    ref = source["ref"]
    commit, _ = _get_json(f"https://api.github.com/repos/{repo}/commits/{urllib.parse.quote(ref, safe='')}", token)
    sha = commit["sha"]
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise FlowError("Unexpected commit SHA")
    files, failures = {}, []
    inventory_path=store.root/'wiki/inventory'/(source['id']+'.json')
    known_tree=None
    if inventory_path.exists():
        inventory=read_json(inventory_path)
        if inventory['commit']==sha:
            known_tree=json.loads(store.artifact(inventory['artifact']))['entries']
    for name in source["paths"]:
        if name.startswith("/") or ".." in Path(name).parts:
            raise FlowError("Invalid registered source path")
        if known_tree is not None and name not in known_tree:
            continue  # Complete tree at this exact SHA proves removal; stage diff requires review.
        url = f"https://raw.githubusercontent.com/{repo}/{sha}/" + urllib.parse.quote(name)
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "HCU-TrainFlow"}), timeout=60) as response:
                data = response.read(16 * 1024 * 1024 + 1)
            if len(data) > 16 * 1024 * 1024:
                raise FlowError("Source exceeds acquisition size limit")
            files[name] = {"sha256": store.put(data, "public"), "url": f"https://github.com/{repo}/blob/{sha}/{name}"}
        except (OSError, FlowError) as exc:
            # The raw host can fail independently of the GitHub content API.
            # Both paths stay pinned to the same full SHA; never substitute HEAD.
            try:
                from .official import read_code
                code=read_code(store,repo,sha,name,token,max_chars=1)
                files[name]={'sha256':code['artifact'],'url':code['url']}
            except (OSError,ValueError) as fallback:
                failures.append({"path":name,"status":"unavailable","error":str(fallback)[:240],"raw_error":type(exc).__name__})
    return sha, files, failures


class DocumentText(HTMLParser):
    """Readable tutorial text; raw HTML remains separately available as evidence."""
    def __init__(self):
        super().__init__()
        self.skip = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in {'script', 'style', 'nav', 'footer', 'header'}:
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in {'script', 'style', 'nav', 'footer', 'header'} and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip and data.strip():
            self.parts.append(' '.join(data.split()))


def collect_web_documents(store, source):
    files, failures = {}, []
    for name in source['paths']:
        url = source['documents'][name]
        parsed = urllib.parse.urlsplit(url)
        if parsed.scheme != 'https' or parsed.hostname != 'docs.nvidia.com' or parsed.username or parsed.password or parsed.port not in (None, 443):
            raise FlowError('Official document adapter requires canonical docs.nvidia.com HTTPS URLs')
        try:
            # No token and no redirects: a moved document must be explicitly re-registered.
            opener = urllib.request.build_opener(NoRedirect)
            request = urllib.request.Request(url, headers={'User-Agent': 'HCU-TrainFlow'})
            with opener.open(request, timeout=60) as response:
                data = response.read(8 * 1024 * 1024 + 1)
                mime = response.headers.get('Content-Type', '')
            if len(data) > 8 * 1024 * 1024 or 'text/html' not in mime.lower():
                raise FlowError('Expected bounded HTML document')
            parser = DocumentText(); parser.feed(data.decode('utf-8'))
            text = '\n'.join(parser.parts).encode('utf-8')
            if len(text) < 200:
                raise FlowError('Document body is empty or incomplete')
            files[name] = {'sha256': store.put(text, 'public'), 'raw_sha256': store.put(data, 'public'), 'url': url}
        except (OSError, ValueError, FlowError):
            failures.append({'path': name, 'status': 'unavailable', 'url': url})
    # A web revision is a content fingerprint, never a fabricated Git SHA.
    revision = fingerprint({name: {'sha256': row['sha256'], 'url': row['url']} for name, row in files.items()})
    return revision, files, failures


def source_page_hashes(project, source_id):
    result = {}
    for path in (Path(project) / 'knowledge').rglob('*.md'):
        meta, _ = parse_page(path)
        if any(ref.get('source') == source_id for ref in meta.get('sources', [])):
            result[path.relative_to(project).as_posix()] = digest(path.read_bytes())
    return result


def stage_source_refresh(store, project, source, sha, files, failures, ref):
    source_id, repo = source['id'], source['repository']
    cursor_path = store.root / 'wiki/sources' / (source_id + '.json')
    reviewed_path = store.root / "wiki/reviewed-sources" / (source_id + ".json")
    reviewed = read_json(reviewed_path) if reviewed_path.exists() else {"files": source.get("baseline_files", {})}
    changes = sorted(name for name in files.keys() | reviewed["files"].keys()
                     if files.get(name, {}).get("sha256") != reviewed["files"].get(name, {}).get("sha256")
                     or (source.get('kind') == 'web' and files.get(name, {}).get('url') != reviewed['files'].get(name, {}).get('url')))
    page_hashes = source_page_hashes(project, source_id)
    reviewed_hashes = reviewed.get('page_hashes', {p['page']: p['page_sha256'] for p in reviewed.get('affected_pages', [])})
    # Removing a citation does not by itself review the surviving prose.
    for name in reviewed_hashes.keys() - page_hashes.keys():
        path = child(project, name)
        if path.is_file():
            page_hashes[name] = digest(path.read_bytes())
    # An unchanged upstream must not erase a review invalidated by local edits/new topics.
    affected = [{'page': name, 'page_sha256': sha256, 'status': 'pending-content-review'}
                for name, sha256 in page_hashes.items()
                if changes or (reviewed_path.exists() and reviewed_hashes.get(name) != sha256)]
    maintenance = []
    maintenance_path = Path(project) / "knowledge/maintenance.json"
    if maintenance_path.exists():
        for rule in read_json(maintenance_path):
            if rule["source"] == source_id and any(name in changes for name in rule["paths"]):
                maintenance.extend(rule["targets"])
    pending_path=store.root/'wiki/workflow-pending'/(source_id+'.json')
    if pending_path.exists():
        maintenance.extend(read_json(pending_path).get('targets',[]))
    reviewed_workflows = reviewed.get('workflow_hashes', {})
    for name, sha256 in reviewed_workflows.items():
        path = child(project, name)
        if not path.is_file() or digest(path.read_bytes()) != sha256:
            maintenance.append(name)
    result = {"source": source_id, "repository": repo, "ref": ref, "commit": sha, "files": files, "changed_paths": changes,
              "affected_pages": affected, "affected_workflows": sorted(set(maintenance)), "failures": failures, "observed_at": utc(), "status": "partial" if failures else "collected-not-reviewed"}
    result['page_inventory'] = page_hashes
    result['workflow_hashes'] = reviewed_workflows
    result['revision_kind'] = 'web-content-fingerprint' if source.get('kind') == 'web' else 'git-commit'
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


def review_refresh(store, stage_id, decisions, project, workflow_decisions=None, defer_workflows=None):
    if not re.fullmatch(r"[0-9a-f]{64}", stage_id):
        raise FlowError("Invalid stage ID")
    stage = read_json(store.root / "wiki/staging" / (stage_id + ".json"))
    if stage["failures"]:
        raise FlowError("Partial source refresh cannot be marked reviewed")
    expected = {x["page"] for x in stage["affected_pages"]}
    if set(decisions) != expected:
        raise FlowError("Every affected overview/topic/case needs an explicit content decision")
    workflow_decisions = workflow_decisions or {}
    required_workflows = set(stage.get("affected_workflows", []))
    if set(workflow_decisions) - required_workflows or (not defer_workflows and set(workflow_decisions) != required_workflows):
        raise FlowError("Affected Skills/adapters need review as well as Wiki pages")
    if defer_workflows is not None and not str(defer_workflows).strip():
        raise FlowError('Deferred workflow review requires a reason and remains pending')
    for path, decision in {**decisions, **workflow_decisions}.items():
        if decision.get("decision") not in {"updated", "still-applicable", "historical"} or not decision.get("note"):
            raise FlowError("Review requires a substantive per-page conclusion")
        current = child(project, path)
        if digest(current.read_bytes()) != decision.get("page_sha256"):
            raise FlowError("Reviewed page changed; renew its review")
        if decision.get("source_commit") != stage["commit"]:
            raise FlowError("Review must address the newly observed source commit")
    current_hashes = source_page_hashes(project, stage['source'])
    staged_hashes = stage.get('page_inventory', {p['page']: p['page_sha256'] for p in stage['affected_pages']})
    bound_hashes = dict(current_hashes)
    for path in staged_hashes.keys() - bound_hashes.keys():
        current = child(project, path)
        bound_hashes[path] = digest(current.read_bytes()) if current.is_file() else None
    if any(path not in decisions and staged_hashes.get(path) != sha for path, sha in bound_hashes.items()):
        raise FlowError('Related pages changed or were added after staging; refresh and review again')
    latest_path = store.root / "wiki/sources" / (stage["source"] + ".json")
    if latest_path.exists() and read_json(latest_path)["commit"] != stage["commit"]:
        raise FlowError("A newer source was observed; review that stage instead")
    receipt = {"stage_id": stage_id, "decisions": decisions, "workflow_decisions": workflow_decisions, "reviewed_at": utc(), "status": "content-reviewed", "runtime_validated": False}
    deferred = sorted(required_workflows-set(workflow_decisions))
    receipt.update(workflow_deferred=deferred, workflow_deferral_reason=defer_workflows,
                   workflow_status='pending-site-review' if deferred else 'reviewed')
    receipt['page_hashes'] = current_hashes
    receipt['content_hashes'] = bound_hashes
    receipt['workflow_hashes'] = {**stage.get('workflow_hashes', {}), **{p: d['page_sha256'] for p, d in workflow_decisions.items()}}
    for path in deferred:
        receipt['workflow_hashes'].pop(path, None)
    write_json(store.root/'wiki/workflow-pending'/(stage['source']+'.json'), {'targets':deferred,'reason':defer_workflows,'stage_id':stage_id})
    write_json(store.root / "wiki/reviews" / (stage_id + ".json"), receipt)
    write_json(store.root / "wiki/reviewed-sources" / (stage["source"] + ".json"),
               {**stage, 'page_hashes': current_hashes, 'workflow_hashes': receipt['workflow_hashes']})
    return receipt
