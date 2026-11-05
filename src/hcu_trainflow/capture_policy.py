"""Small source policies; discovery is not an obligation to mirror discussions."""
import json
from pathlib import Path
import re

from .core import digest, read_json


def is_discovery(source):
    policy = source.get('capture_policy', {})
    return isinstance(policy, dict) and policy.get('changes') == 'discover'


def discovery_project(project, repository=None):
    root = Path(project)
    storage = root / 'knowledge/storage.json'
    settings = read_json(storage) if storage.is_file() else {}
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
