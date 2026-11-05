"""Enforce a configured knowledge-maintenance branch without switching it."""
import os
from pathlib import Path
import re
import subprocess

from .core import FlowError, read_json

MUTATIONS = {'wiki-catalog', 'wiki-triage', 'wiki-sync-prs', 'wiki-sync-docs',
             'wiki-update', 'wiki-apply', 'wiki-refresh', 'wiki-review', 'wiki-review-pr'}


def check(project):
    root = Path(project).resolve()
    if not (root / 'knowledge/sources.json').is_file():
        raise FlowError('Knowledge maintenance requires an existing TrainFlow project with knowledge/sources.json')
    settings = root / 'knowledge/storage.json'
    policy = read_json(settings) if settings.is_file() else {}
    if not isinstance(policy, dict):
        raise FlowError('knowledge/storage.json must be a mapping')
    expected = policy.get('maintenance_branch')
    if expected is None:
        return {'status': 'legacy-unconfigured'}
    if not isinstance(expected, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._/-]*', expected):
        raise FlowError('Invalid knowledge maintenance branch')
    if not (root / '.git').exists():
        # Do not accidentally use an ancestor repository for a standalone data
        # fixture or an explicitly chosen non-Git project directory.
        return {'status': 'non-git-project', 'expected_branch': expected}
    def git(*args):
        try:
            return subprocess.run(['git', *args], cwd=root,
                env={**os.environ, 'GIT_OPTIONAL_LOCKS': '0'}, capture_output=True,
                text=True, encoding='utf-8', timeout=20)
        except (OSError, UnicodeError, subprocess.TimeoutExpired) as exc:
            raise FlowError('Cannot verify the knowledge maintenance checkout') from exc
    location = git('rev-parse', '--show-toplevel')
    if location.returncode or Path(location.stdout.strip()).resolve() != root:
        raise FlowError('Knowledge maintenance target must be the actual Git checkout root')
    result = git('branch', '--show-current')
    if result.returncode or result.stdout.strip() != expected:
        actual = result.stdout.strip() or 'detached/unavailable'
        raise FlowError(f'Knowledge maintenance requires {expected}; actual checkout is {actual}. '
                        'Preserve existing changes and select the intended checkout; no automatic switch/reset was performed.')
    return {'status': 'current', 'branch': expected}


def guard_cli(args):
    command = args.command
    project = getattr(args, 'project', None) if command in MUTATIONS else None
    if command == 'wiki-pr':
        project = getattr(args, 'retain_project', None)
    elif command == 'wiki-inventory' and getattr(args, 'retain', False):
        project = args.project
    if project:
        return check(project)
    return None
