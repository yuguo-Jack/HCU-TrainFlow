"""Project-owned Wiki paths and read-only routing to external knowledge.

Page IDs identify knowledge independently of its directory. Migration aliases
resolve live maintenance records, never certify an old content-review receipt.
"""
from pathlib import Path
from functools import lru_cache
import fnmatch
import os
import re

from .core import FlowError, child, read_json


def external_routes(project):
    path = Path(project) / 'knowledge/catalog/external-knowledge.json'
    return read_json(path).get('routes', []) if path.is_file() else []


def external_route(project, identity):
    value = identity.removeprefix('https://github.com/').removesuffix('.git').rstrip('/').lower()
    return next((row for row in external_routes(project)
                 if value in {row['id'].lower(), row.get('repository', '').lower()}), None)


def require_local_owner(project, identity):
    route = external_route(project, identity)
    value = identity.removeprefix('https://github.com/').lower()
    if route or value.startswith('hygon-ai/'):
        owner = route.get('owner', 'HCU-Knowledge') if route else 'HCU-Knowledge'
        raise FlowError(f'{identity}: knowledge is maintained by {owner}; consult '
                        'knowledge/catalog/external-knowledge.json and hcu-knowledge-search. '
                        'Do not retain another HCU repository Wiki here. Temporary source reads remain available.')


def project_id(project, source=None, repository=None):
    """Registry assignment wins; unregistered public PRs get one isolated project."""
    registry_path = Path(project) / 'knowledge/sources.json'
    registry = read_json(registry_path) if registry_path.is_file() else []
    row = next((r for r in registry if (source and r['id'] == source) or
                (repository and r.get('repository', '').lower() == repository.lower())), None)
    if row:
        identity = row.get('knowledge_project', row['id'])
    else:
        identity = source or (repository or '').replace('/', '--').lower()
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', identity) or identity in {'.', '..'}:
        raise FlowError('Invalid knowledge project identity')
    return identity


def upstream_root(project, source=None, repository=None):
    return child(project, f'knowledge/projects/{project_id(project, source, repository)}/knowledgebase/upstream')


def source_map(project, source):
    return upstream_root(project, source=source) / 'source-map' / (source + '.md')


def document_root(project, source):
    return upstream_root(project, source=source) / 'docs' / source


def pr_root(project, repository):
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository) or any(
            part in {'.', '..'} for part in repository.split('/')):
        raise FlowError('Invalid PR repository identity')
    return upstream_root(project, repository=repository) / 'prs' / repository.replace('/', '--')


@lru_cache(maxsize=8)
def _path_aliases(path, modified_ns):
    return read_json(Path(path))


def current_path(project, name):
    """Map old repo-relative paths; a changed body still needs a new review."""
    aliases = Path(project) / 'knowledge/catalog/path-migrations.json'
    mapping = _path_aliases(str(aliases.resolve()), aliases.stat().st_mtime_ns) if aliases.is_file() else {}
    result = mapping.get('paths', {}).get(name, name)
    if result == name:
        for old, new in sorted(mapping.get('prefixes', {}).items(), key=lambda pair: len(pair[0]), reverse=True):
            if name.startswith(old):
                result = new + name[len(old):]
                break
    child(project, result)  # Reject unsafe persisted paths.
    return result


def current_hashes(project, hashes):
    return {current_path(project, name): sha for name, sha in hashes.items()}


def review_page_candidates(project):
    """Read live authored/experience routes without traversing generated sources.

    The canonical upstream subtree contains acquisition copies, not conclusions.
    Do not cache the remaining inventory: new pages and removed citations must
    invalidate reviews even when acquisition is a long-running batch.
    """
    root = Path(project) / 'knowledge'
    for directory, children, files in os.walk(root):
        parts = Path(directory).relative_to(root).parts
        if len(parts) == 4 and parts[0] == 'projects' and parts[2:] == ('knowledgebase', 'upstream'):
            children.clear()
            continue
        for name in files:
            if fnmatch.fnmatch(name, '*.md'):
                yield Path(directory) / name
