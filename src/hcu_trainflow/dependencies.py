"""Selective, pinned thirdparty checkouts. Never publishes or resets their content."""
import os
from pathlib import Path
import re
import subprocess

from .core import FlowError, read_json, write_json


def dependency_path(root, item):
    binding = root / 'thirdparty.local.json'
    if item['id'] == 'hcu-knowledge' and binding.is_file():
        value = read_json(binding).get('hcu_knowledge_root')
        if not isinstance(value, str) or not Path(value).is_absolute():
            raise FlowError('HCU-Knowledge binding must be an absolute checkout path')
        return Path(value).resolve(), True
    return root / item['path'], False


def bind_knowledge(project, path):
    """Reuse an explicitly selected independent KB; never pull or reset it."""
    root, entries = load_manifest(project)
    item = next(x for x in entries if x['id'] == 'hcu-knowledge')
    path = Path(path).expanduser().resolve()
    if path == (root / item['path']).resolve():
        raise FlowError('Managed knowledge checkout needs no external binding')
    for name in ('kb.py', 'tools/setup_workspace.py', 'knowledge/INDEX.md',
                 'skills/hcu-knowledge-search/SKILL.md', 'skills/hcu-knowledge-update/SKILL.md'):
        if not (path / name).is_file():
            raise FlowError('Incomplete HCU-Knowledge checkout: ' + name)
    top = git(path, 'rev-parse', '--show-toplevel').stdout.strip()
    origin = git(path, 'remote', 'get-url', 'origin').stdout.strip()
    if Path(top).resolve() != path or origin.removesuffix('.git') != item['url'].removesuffix('.git'):
        raise FlowError('HCU-Knowledge checkout identity differs from the registered source')
    write_json(root / 'thirdparty.local.json', {'hcu_knowledge_root': str(path)})
    return path


def load_manifest(project):
    root = Path(project).resolve()
    manifest = read_json(root / 'thirdparty/manifest.json')
    if manifest.get('schema_version') != 1:
        raise FlowError('Unsupported thirdparty manifest')
    entries = manifest['dependencies']
    names, paths = set(), set()
    for item in entries:
        if not re.fullmatch(r'[a-z0-9-]+', item['id']) or item['id'] in names:
            raise FlowError('Invalid/duplicate dependency ID')
        relative = Path(item['path'])
        if relative.is_absolute() or len(relative.parts) != 2 or relative.parts[0] != 'thirdparty' or '..' in relative.parts:
            raise FlowError('Dependency checkout must be a direct child of thirdparty')
        path = root / relative
        if path.is_symlink() or not path.resolve().is_relative_to(root) or path.resolve().parent != (root / 'thirdparty').resolve():
            raise FlowError('Dependency checkout cannot escape thirdparty')
        if path in paths or not re.fullmatch(r'[0-9a-f]{40}', item['commit']):
            raise FlowError('Duplicate checkout or unpinned dependency')
        for url in [item['url']] + ([item['upstream_url']] if item.get('upstream_url') else []):
            if not re.fullmatch(r'https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\.git', url):
                raise FlowError('Expected credential-free GitHub HTTPS URL')
        if item.get('upstream_url') and not re.fullmatch(r'[0-9a-f]{40}', item.get('upstream_commit', '')):
            raise FlowError('Fork needs a pinned upstream baseline')
        for value in item.get('sparse_paths', []):
            if not re.fullmatch(r'[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*', value) or any(p in {'.', '..'} for p in value.split('/')):
                raise FlowError('Invalid sparse checkout directory')
        names.add(item['id']); paths.add(path)
    return root, entries


def git(path, *args, check=True):
    env = {**os.environ, 'GIT_TERMINAL_PROMPT': '0', 'GCM_INTERACTIVE': 'never', 'GIT_LFS_SKIP_SMUDGE': '1'}
    try:
        result = subprocess.run(['git', '-c', 'credential.interactive=never', '-C', str(path), *args],
                                capture_output=True, text=True, encoding='utf-8', errors='replace', env=env, timeout=300)
    except subprocess.TimeoutExpired as exc:
        raise FlowError('Git operation timed out; inspect the checkout and retry explicitly') from exc
    if check and result.returncode:
        # Git diagnostics may include credential-helper output. Keep only actionable context here.
        raise FlowError(f'Git {args[0]} failed (exit {result.returncode}); check network, repository access and Git credentials')
    return result


def inspect_checkout(root, item):
    path, external = dependency_path(root, item)
    result = {'id': item['id'], 'path': str(path), 'expected_commit': item['commit'], 'optional': item.get('optional', False), 'external': external}
    if not path.exists():
        return {**result, 'status': 'missing'}
    top = git(path, 'rev-parse', '--show-toplevel', check=False)
    if top.returncode or Path(top.stdout.strip()).resolve() != path.resolve():
        return {**result, 'status': 'invalid-checkout'}
    origin = git(path, 'remote', 'get-url', 'origin', check=False)
    if origin.returncode or origin.stdout.strip().removesuffix('.git') != item['url'].removesuffix('.git'):
        return {**result, 'status': 'origin-mismatch'}
    head = git(path, 'rev-parse', '--verify', 'HEAD', check=False)
    dirty = git(path, 'status', '--porcelain', '--untracked-files=normal').stdout.strip()
    revision = head.stdout.strip() if not head.returncode else None
    if external:
        return {**result, 'commit': revision, 'dirty': bool(dirty),
                'status': 'ready' if revision else 'invalid-checkout',
                'note': 'Independent knowledge revision preserved; setup must verify its local index and Skills'}
    return {**result, 'commit': revision, 'dirty': bool(dirty),
            'status': 'dirty' if dirty else 'ready' if revision == item['commit'] else 'revision-mismatch'}


def migrate_upstream_origin(root, item, state):
    """Explicitly migrate a clean, known upstream baseline to its registered fork."""
    path = root / item['path']
    origin = git(path, 'remote', 'get-url', 'origin').stdout.strip().removesuffix('.git')
    if not item.get('upstream_url') or origin != item['upstream_url'].removesuffix('.git'):
        return {**state, 'action': 'Only the manifest upstream origin can migrate; inspect this checkout manually'}
    if git(path, 'status', '--porcelain', '--untracked-files=normal').stdout.strip():
        return {**state, 'status': 'dirty', 'action': 'Preserve local changes before changing repository origin'}
    head = git(path, 'rev-parse', '--verify', 'HEAD', check=False)
    if head.returncode or head.stdout.strip() != item['upstream_commit']:
        return {**state, 'action': 'Unrecognized upstream revision; preserve local commits and migrate manually'}
    upstream = git(path, 'remote', 'get-url', 'upstream', check=False)
    if not upstream.returncode and upstream.stdout.strip().removesuffix('.git') != item['upstream_url'].removesuffix('.git'):
        return {**state, 'action': 'Existing upstream remote differs; preserve it and inspect manually'}
    if upstream.returncode:
        git(path, 'remote', 'add', 'upstream', item['upstream_url'])
    git(path, 'remote', 'set-url', 'origin', item['url'])
    return inspect_checkout(root, item)


def sync_dependencies(project, only=None, include_optional=False, status_only=False, migrate_origin=False):
    root, entries = load_manifest(project)
    requested = set(only or [])
    if requested - {x['id'] for x in entries}:
        raise FlowError('Unknown dependency ID')
    selected = [x for x in entries if x['id'] in requested] if requested else [x for x in entries if include_optional or not x.get('optional')]
    results = []
    for item in selected:
        try:
            state = inspect_checkout(root, item)
            if not status_only and migrate_origin and not state.get('external') and state['status'] == 'origin-mismatch':
                state = migrate_upstream_origin(root, item, state)
            if not status_only and not state.get('external') and state['status'] in {'missing', 'revision-mismatch'}:
                path = root / item['path']
                if state['status'] == 'missing':
                    path.mkdir(parents=True)
                    git(path, 'init')
                    git(path, 'remote', 'add', 'origin', item['url'])
                # No reset/clean: Git refuses collisions. Local changes are caught before fetching.
                filtering = ['--filter=blob:none'] if item.get('sparse_paths') else []
                git(path, 'fetch', '--depth', '1', *filtering, 'origin', item['commit'])
                if item.get('sparse_paths'):
                    git(path, 'sparse-checkout', 'set', '--cone', *item['sparse_paths'])
                git(path, 'checkout', '--detach', item['commit'])
                state = inspect_checkout(root, item)
            if state['status'] == 'dirty':
                state['action'] = 'Preserve local edits; use a separate development checkout or resolve them before sync'
            if state['status'] == 'origin-mismatch' and 'action' not in state:
                state['action'] = 'Inspect origin; use --migrate-origin only for the registered upstream baseline'
            if state['status'] == 'ready' and item.get('lfs'):
                state['materials'] = 'Checkout inspection does not verify LFS payloads or the search index; full setup runs knowledge bootstrap/doctor'
            results.append(state)
        except (FlowError, OSError) as exc:
            results.append({'id': item['id'], 'status': 'unavailable', 'message': str(exc),
                            'optional': item.get('optional', False), 'action': 'Authenticate Git for this repository or retry after network recovery'})
    return {'status': 'ready' if all(x['status'] == 'ready' for x in results) else 'incomplete', 'dependencies': results}


def require_checkout(project, dependency):
    root, entries = load_manifest(project)
    item = next((x for x in entries if x['id'] == dependency), None)
    if item is None:
        raise FlowError('Dependency is not registered')
    state = inspect_checkout(root, item)
    if state['status'] != 'ready':
        raise FlowError(f'{dependency}: {state["status"]}; run scripts/bootstrap_thirdparty.py --only {dependency}, preserving local changes')
    return dependency_path(root, item)[0], item
