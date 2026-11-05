"""Small source policies; discovery is not an obligation to mirror discussions."""
import json
from pathlib import Path
import re

from .core import FlowError, digest, read_json


def is_discovery(source, project=None):
    """The project profile is the default; a full capture must be explicit.

    Callers without project context retain legacy defaults. This preserves old
    standalone integrations without letting a new source in a lite project
    silently opt back into all-discussion retention.
    """
    policy = source.get('capture_policy', {})
    if not isinstance(policy, dict):
        raise FlowError('capture_policy must be a mapping')
    if 'mode' in policy and (not isinstance(policy['mode'],str) or policy['mode'] not in {
            'federated', 'selected_evidence', 'core_local', 'text_fallback', 'legacy_history'}):
        raise FlowError('Unknown capture_policy mode')
    if 'write_views' in policy and type(policy['write_views']) is not bool:
        raise FlowError('capture_policy.write_views must be boolean')
    changes = policy.get('changes')
    if 'changes' in policy:
        if not isinstance(changes,str) or changes not in {'discover', 'full'}:
            raise FlowError('capture_policy.changes must be discover or full')
        return changes == 'discover'
    return bool(project is not None and discovery_project(project))


def discovery_project(project, repository=None):
    root = Path(project)
    storage = root / 'knowledge/storage.json'
    settings = read_json(storage) if storage.is_file() else {}
    if not isinstance(settings,dict):
        raise FlowError('knowledge/storage.json must be a mapping')
    if settings.get('profile', settings.get('capture_profile')) == 'discovery-first':
        return True
    registry = root / 'knowledge/sources.json'
    return registry.is_file() and any(is_discovery(source) for source in read_json(registry)
                                     if source.get('repository', '').lower() == (repository or '').lower())


VOLATILE = {'observed_at', 'fetched_at', 'queried_at', 'updated_at', 'pushed_at',
            'stargazers_count', 'watchers_count', 'watchers', 'forks_count', 'forks',
            'open_issues_count', 'open_issues', 'size', 'network_count', 'subscribers_count',
            'reactions', 'avatar_url', 'gravatar_id'}
PR_COUNTERS = {'comments', 'review_comments', 'commits', 'additions', 'deletions'}


def semantic_pr_payload(data, requested=None):
    """Project old rich evidence onto the new explicitly requested scope.

    Raw originals stay untouched. Body, state, exact refs, requested discussion
    bodies/review states and files remain semantic; observation counters do not.
    """
    fields = ['repository', 'number', 'detail', 'refs']
    requested = requested or data.get('coverage', {})
    for key in ('issue_comments', 'inline_comments', 'reviews', 'files'):
        if requested.get(key, {}).get('requested', True):
            fields.append(key)
    def clean(value):
        if isinstance(value, dict):
            return {k: clean(v) for k, v in value.items() if k not in VOLATILE}
        if isinstance(value, list):
            return [clean(v) for v in value]
        return value
    result=clean({key: data.get(key) for key in fields})
    if isinstance(result.get('detail'),dict):
        result['detail']={k:v for k,v in result['detail'].items() if k not in PR_COUNTERS}
    return result


def semantic_pr_fingerprint(data, requested=None):
    return digest(json.dumps(semantic_pr_payload(data, requested), ensure_ascii=False, sort_keys=True).encode())


def public_query_risk(query):
    """Keep pasted private context local; callers can extract public terms."""
    return bool(re.search(r'[\r\n]|https?://|(?:\d{1,3}\.){3}\d{1,3}|[A-Za-z]:[\\/]|\\\\'
                          r'|\b[\w.-]+\.(?:internal|local)\b|\b(?:gh[pousr]_|github_pat_|sk-)[A-Za-z0-9_]+'
                          r'|\bBearer\s+\S+|(?:job_id|run_id|request_id|dataset|tenant|password|api_key|secret|authorization|access_token|refresh_token|token|credential|业务|数据集)\s*[:=]',query,re.I))
