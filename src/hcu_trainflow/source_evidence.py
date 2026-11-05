"""Read selected public evidence and retired originals from a fixed Git history.

No upstream refresh, automatic fetch, or duplicate historical mirror is created.
"""
import json
from pathlib import Path
import re
import subprocess

from .core import FlowError, atomic_write, child, digest, read_json as load_json


def policy(project):
    path = Path(project) / 'knowledge/storage.json'
    return load_json(path) if path.is_file() else {}


def retired(project, relative):
    child(project, relative)
    data = policy(project)
    return data.get('profile') == 'discovery-first' and bool(
        re.fullmatch(r'knowledge/evidence/prs/[^/]+/[^/]+\.json', relative)
        or re.fullmatch(r'knowledge/projects/[^/]+/knowledgebase/upstream/prs/[^/]+/PR-\d+\.md', relative))


def read_bytes(project, relative_ref, expected_sha=None):
    root = Path(project).resolve()
    path = child(root, relative_ref)
    ref = path.relative_to(root).as_posix()
    if path.is_file():
        raw = path.read_bytes()
    else:
        data = policy(root)
        commit = data.get('legacy_git', {}).get('commit', '')
        if not retired(root, ref) or not re.fullmatch(r'[0-9a-f]{40}', commit):
            raise FileNotFoundError(str(path))
        try:
            result = subprocess.run(['git', 'show', f'{commit}:{ref}'], cwd=root,
                                    capture_output=True, timeout=45)
        except FileNotFoundError as exc:
            raise FlowError('Git is required for an uncited historical original; open the fixed original page instead') from exc
        if result.returncode:
            raise FlowError('Original is in fixed Git history; fetch that commit in a shallow clone '
                            f'(git fetch --no-tags origin {commit}) or open its fixed GitHub page. '
                            'No source was refreshed and no missing evidence is treated as empty.')
        raw = result.stdout
    if raw.startswith(b'version https://git-lfs.github.com/spec/v1'):
        raise FlowError('Original is an unhydrated Git LFS pointer')
    named_sha = re.search(r'-([0-9a-f]{64})\.json$', ref)
    expected = expected_sha or (named_sha[1] if named_sha else None)
    if expected and digest(raw) != expected:
        raise FlowError('Source evidence SHA-256 mismatch')
    return raw


def read_json(project, relative_ref, default=None, expected_sha=None):
    try:
        return json.loads(read_bytes(project, relative_ref, expected_sha).decode('utf-8-sig'))
    except FileNotFoundError:
        return default


def exists(project, relative_ref):
    path = child(project, relative_ref)
    if path.is_file():
        return True
    if not retired(project, path.relative_to(Path(project).resolve()).as_posix()):
        return False
    commit = policy(project).get('legacy_git', {}).get('commit', '')
    if not re.fullmatch(r'[0-9a-f]{40}', commit):
        return False
    return subprocess.run(['git', 'cat-file', '-e', f'{commit}:{relative_ref}'], cwd=project,
                          capture_output=True, timeout=30).returncode == 0


def materialize(project, relative_ref, expected_sha=None):
    raw = read_bytes(project, relative_ref, expected_sha)
    path = child(project, relative_ref)
    if path.is_file():
        return path
    # Never overwrite a user's annotations in a previous viewing copy.
    target = child(project, f'.work/lite-reader-cache/{digest(raw)}/{path.name}')
    if target.exists() and digest(target.read_bytes()) != digest(raw):
        import uuid
        target = target.with_name(uuid.uuid4().hex + '-' + target.name)
    if not target.exists():
        atomic_write(target, raw)
    return target


def historical_page(project, identity):
    """Resolve old stable PR IDs or relative source paths without indexing them."""
    from . import wiki, knowledge_layout as layout
    root = Path(project).resolve()
    relative = identity
    match = re.fullmatch(r'pr-(.+)-(\d+)', identity)
    if match:
        rows = load_json(root / 'knowledge/sources.json')
        repo = next((r['repository'] for r in rows if r.get('repository', '').replace('/', '--').lower() == match[1]), None)
        if not repo:
            repo = match[1].replace('--', '/', 1)
        relative = (layout.pr_root(root, repo) / f'PR-{match[2]}.md').relative_to(root).as_posix()
    relative = layout.current_path(root, relative)
    if not retired(root, relative):
        raise FlowError('Unknown Wiki page ID')
    raw = read_bytes(root, relative)
    meta, body = wiki.parse_text(raw.decode('utf-8-sig'))
    if match and meta.get('id') != identity:
        raise FlowError('Historical PR page identity mismatch')
    return {'id': meta.get('id', relative), 'title': meta.get('title', Path(relative).name),
            'body': body, 'metadata': meta, 'sha256': digest(raw),
            'path': str(materialize(root, relative, digest(raw))), 'original_path': relative,
            'review_state': 'archived-fixed-source', 'source_commit': policy(root)['legacy_git']['commit']}
