"""Managed updates use real local Git graphs; no network transport is exercised."""
import hashlib
from pathlib import Path
import subprocess

import pytest

from hcu_trainflow import dependencies
from hcu_trainflow.core import write_json


def git(path, *args):
    result = subprocess.run(['git', '-C', str(path), *args], capture_output=True,
                            text=True, encoding='utf-8', errors='replace', timeout=20)
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


def commit(path, value):
    (path / 'file.txt').write_text(value, encoding='utf-8')
    git(path, 'add', 'file.txt')
    git(path, '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid',
        '-c', 'commit.gpgsign=false', 'commit', '-m', value)
    return git(path, 'rev-parse', 'HEAD')


@pytest.fixture
def source(tmp_path, monkeypatch):
    seed = tmp_path / 'seed'
    seed.mkdir()
    git(seed, 'init')
    commits = [commit(seed, str(i)) for i in range(3)]
    root = tmp_path / 'project'
    item = {'id': 'tool', 'path': 'thirdparty/tool',
            'url': 'https://github.com/example/tool.git', 'commit': commits[-1]}
    calls = []
    real_git = dependencies.git
    transport = {'path': seed}

    def local_transport(path, *args, **kwargs):
        calls.append(args)
        if args[0] == 'fetch':
            # Keep the registered origin/manifest checks real, replacing only
            # the transport endpoint so tests cannot contact GitHub.
            assert args[-2] == 'origin'
            args = (*args[:-2], transport['path'].as_uri(), args[-1])
        return real_git(path, *args, **kwargs)

    monkeypatch.setattr(dependencies, 'git', local_transport)

    def save(target=None):
        if target:
            item['commit'] = target
        write_json(root / 'thirdparty/manifest.json',
                   {'schema_version': 1, 'dependencies': [item]})

    def checkout(shallow=False):
        dest = root / item['path']
        dest.parent.mkdir(parents=True, exist_ok=True)
        args = ['git', 'clone', *(['--depth', '1'] if shallow else []),
                seed.as_uri(), str(dest)]
        result = subprocess.run(args, capture_output=True, text=True, timeout=20)
        assert result.returncode == 0, result.stderr
        git(dest, 'remote', 'set-url', 'origin', item['url'])
        return dest

    save()
    return root, item, seed, commits, calls, transport, save, checkout


def test_newer_managed_head_is_not_downgraded(source):
    root, item, _, commits, calls, _, save, checkout = source
    path = checkout()
    save(commits[0])
    result = dependencies.sync_dependencies(root)
    row = result['dependencies'][0]
    assert result['status'] == 'incomplete' and row['status'] == 'revision-mismatch'
    assert 'newer than the locked commit' in row['action']
    assert git(path, 'rev-parse', 'HEAD') == commits[-1]
    assert (path / 'file.txt').read_text() == '2'
    assert not any(c[0] in {'fetch', 'checkout', 'reset', 'clean'} for c in calls)


def test_diverged_managed_head_is_preserved_after_fetch(source):
    root, _, seed, _, calls, _, save, checkout = source
    path = checkout()
    local_head = commit(path, 'local branch')
    target = commit(seed, 'remote branch')
    save(target)
    row = dependencies.sync_dependencies(root)['dependencies'][0]
    assert row['status'] == 'revision-mismatch' and 'divergent history' in row['action']
    assert git(path, 'rev-parse', 'HEAD') == local_head
    assert (path / 'file.txt').read_text() == 'local branch'
    assert any(c[0] == 'fetch' for c in calls)
    assert not any(c[0] in {'checkout', 'reset', 'clean'} for c in calls)


@pytest.mark.parametrize('shallow', [False, True])
def test_forward_update_fetches_history_without_cutting_target_to_depth_one(source, shallow):
    root, _, seed, commits, calls, _, save, checkout = source
    path = checkout(shallow)
    assert git(path, 'rev-parse', '--is-shallow-repository') == str(shallow).lower()
    commit(seed, 'new parent')
    target = commit(seed, 'new target')
    save(target)
    assert dependencies.sync_dependencies(root)['status'] == 'ready'
    assert git(path, 'rev-parse', 'HEAD') == target
    assert (path / 'file.txt').read_text() == 'new target'
    assert git(path, 'merge-base', '--is-ancestor', commits[-1], target) == ''
    fetches = [c for c in calls if c[0] == 'fetch']
    assert len(fetches) == 1 and '--depth' not in fetches[0]
    assert f'--deepen={dependencies.FORWARD_HISTORY_DEEPEN}' in fetches[0]
    # An existing full history must not become shallow while proving the update.
    if not shallow:
        assert git(path, 'rev-parse', '--is-shallow-repository') == 'false'


def test_already_available_forward_proof_does_not_fetch(source):
    root, item, _, commits, calls, _, _, checkout = source
    path = checkout()
    git(path, 'checkout', '--detach', commits[0])
    assert dependencies.sync_dependencies(root)['status'] == 'ready'
    assert git(path, 'rev-parse', 'HEAD') == item['commit']
    assert not any(c[0] == 'fetch' for c in calls)


def test_missing_checkout_still_installs_the_exact_pin(source):
    root, item, _, _, calls, _, _, _ = source
    assert dependencies.sync_dependencies(root)['status'] == 'ready'
    path = root / item['path']
    assert git(path, 'rev-parse', 'HEAD') == item['commit']
    assert git(path, 'remote', 'get-url', 'origin') == item['url']
    assert ('fetch', '--depth', '1', 'origin', item['commit']) in calls


def test_status_only_leaves_head_worktree_and_fetch_state_unchanged(source):
    root, _, seed, commits, calls, _, save, checkout = source
    path = checkout(shallow=True)
    save(commit(seed, 'not fetched'))
    before = {p.relative_to(path): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in path.rglob('*') if p.is_file() and '.git' not in p.relative_to(path).parts}
    shallow_before = (path / '.git/shallow').read_bytes()
    row = dependencies.sync_dependencies(root, status_only=True)['dependencies'][0]
    assert row['status'] == 'revision-mismatch'
    assert git(path, 'rev-parse', 'HEAD') == commits[-1]
    assert before == {p.relative_to(path): hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in path.rglob('*') if p.is_file() and '.git' not in p.relative_to(path).parts}
    assert (path / '.git/shallow').read_bytes() == shallow_before
    assert not (path / '.git/FETCH_HEAD').exists()
    assert all(c[0] in {'rev-parse', 'remote', 'status'} for c in calls)


def test_incomplete_remote_history_cannot_authorize_checkout(source, tmp_path):
    root, _, seed, commits, calls, transport, save, checkout = source
    path = checkout(shallow=True)
    commit(seed, 'parent absent from shallow remote')
    target = commit(seed, 'remote shallow tip')
    shallow_remote = tmp_path / 'shallow-remote'
    result = subprocess.run(['git', 'clone', '--depth', '1', seed.as_uri(), str(shallow_remote)],
                            capture_output=True, text=True, timeout=20)
    assert result.returncode == 0, result.stderr
    transport['path'] = shallow_remote
    save(target)
    row = dependencies.sync_dependencies(root)['dependencies'][0]
    assert row['status'] == 'revision-mismatch' and 'Cannot prove a forward update' in row['action']
    assert git(path, 'rev-parse', 'HEAD') == commits[-1]
    assert (path / 'file.txt').read_text() == '2'
    assert len([c for c in calls if c[0] == 'fetch']) == 1
    assert not any(c[0] == 'checkout' for c in calls)


def test_unavailable_history_preserves_mismatch_instead_of_installing(source):
    root, _, seed, commits, calls, transport, save, checkout = source
    path = checkout()
    save(commit(seed, 'unavailable target'))
    transport['path'] = seed / 'not-a-repository'
    row = dependencies.sync_dependencies(root)['dependencies'][0]
    assert row['status'] == 'revision-mismatch' and 'fetch was unavailable' in row['action']
    assert git(path, 'rev-parse', 'HEAD') == commits[-1]
    assert not any(c[0] == 'checkout' for c in calls)


def test_concurrent_edits_during_history_fetch_are_preserved(source, monkeypatch):
    root, _, seed, commits, _, _, save, checkout = source
    path = checkout()
    save(commit(seed, 'new target'))
    local_transport = dependencies.git

    def edit_during_fetch(where, *args, **kwargs):
        result = local_transport(where, *args, **kwargs)
        if args[0] == 'fetch':
            (path / 'file.txt').write_text('concurrent edit', encoding='utf-8')
        return result

    monkeypatch.setattr(dependencies, 'git', edit_during_fetch)
    row = dependencies.sync_dependencies(root)['dependencies'][0]
    assert row['status'] == 'dirty'
    assert git(path, 'rev-parse', 'HEAD') == commits[-1]
    assert (path / 'file.txt').read_text() == 'concurrent edit'


@pytest.mark.parametrize('condition', ['dirty', 'origin'])
def test_existing_identity_and_dirty_guards_run_before_history_fetch(source, condition):
    root, _, seed, commits, calls, _, save, checkout = source
    path = checkout()
    save(commit(seed, 'new target'))
    if condition == 'dirty':
        (path / 'file.txt').write_text('user edit', encoding='utf-8')
    else:
        git(path, 'remote', 'set-url', 'origin', 'https://github.com/other/tool.git')
    row = dependencies.sync_dependencies(root)['dependencies'][0]
    assert row['status'] == ('dirty' if condition == 'dirty' else 'origin-mismatch')
    assert git(path, 'rev-parse', 'HEAD') == commits[-1]
    assert not any(c[0] in {'fetch', 'checkout', 'reset', 'clean'} for c in calls)
