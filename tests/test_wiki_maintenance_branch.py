"""Maintenance targets are checked before private Store or network side effects."""
from argparse import Namespace
from pathlib import Path
import subprocess

import pytest

from hcu_trainflow import cli, maintenance_branch as branch
from hcu_trainflow.core import FlowError, write_json


def git(root, *args):
    result = subprocess.run(['git', *args], cwd=root, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


def project(tmp_path, name='project', configured=True):
    root = tmp_path/name
    (root/'knowledge').mkdir(parents=True)
    write_json(root/'knowledge/sources.json', [])
    if configured:
        write_json(root/'knowledge/storage.json', {'profile':'discovery-first', 'maintenance_branch':'lite'})
    return root


def repository(tmp_path):
    root = project(tmp_path)
    git(root, 'init', '-b', 'lite')
    git(root, '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid',
        'commit', '--allow-empty', '-m', 'fixture')
    return root


def test_actual_lite_checkout_passes_and_foreign_or_detached_keeps_changes(tmp_path):
    root = repository(tmp_path)
    marker = root/'unrelated.txt'
    marker.write_bytes(b'user changes')
    assert branch.check(root)['branch'] == 'lite'
    git(root, 'switch', '-c', 'main')
    with pytest.raises(FlowError, match='requires lite'):
        branch.check(root)
    assert git(root, 'branch', '--show-current') == 'main'
    git(root, 'checkout', '--detach')
    with pytest.raises(FlowError, match='detached'):
        branch.check(root)
    assert marker.read_bytes() == b'user changes'


def test_worktree_git_file_and_nested_standalone_project(tmp_path):
    root = repository(tmp_path)
    linked = tmp_path/'linked'
    git(root, 'worktree', 'add', '-b', 'other', str(linked))
    # Metadata must be present in this untracked-fixture worktree too.
    (linked/'knowledge').mkdir()
    write_json(linked/'knowledge/sources.json', [])
    write_json(linked/'knowledge/storage.json', {'maintenance_branch':'other'})
    assert (linked/'.git').is_file()
    assert branch.check(linked)['branch'] == 'other'
    nested = project(root, 'standalone')
    assert branch.check(nested)['status'] == 'non-git-project'


def test_legacy_and_invalid_or_cross_project_targets(tmp_path):
    legacy = project(tmp_path, configured=False)
    assert branch.check(legacy)['status'] == 'legacy-unconfigured'
    foreign = tmp_path/'knowledge-base'
    foreign.mkdir()
    with pytest.raises(FlowError, match='TrainFlow project'):
        branch.check(foreign)
    write_json(legacy/'knowledge/storage.json', [])
    with pytest.raises(FlowError, match='mapping'):
        branch.check(legacy)


def test_unicode_checkout_uses_explicit_git_output_encoding(tmp_path, monkeypatch):
    parent = tmp_path/'训练工程'
    parent.mkdir()
    root = repository(parent)
    native = branch.subprocess.run
    encodings = []
    def run(*args, **kwargs):
        encodings.append(kwargs.get('encoding'))
        return native(*args, **kwargs)
    monkeypatch.setattr(branch.subprocess, 'run', run)
    assert branch.check(root)['branch'] == 'lite'
    assert encodings == ['utf-8', 'utf-8']


def test_mismatched_git_toplevel_is_rejected(tmp_path, monkeypatch):
    root = repository(tmp_path)
    monkeypatch.setattr(branch.subprocess, 'run', lambda *args, **kwargs:
        subprocess.CompletedProcess(args, 0, str(tmp_path), ''))
    with pytest.raises(FlowError, match='actual Git checkout root'):
        branch.check(root)


def test_cli_guard_precedes_store_and_uses_actual_retention_target(tmp_path, monkeypatch):
    root = repository(tmp_path)
    git(root, 'switch', '-c', 'main')
    monkeypatch.setattr(cli, 'Store', lambda *args: pytest.fail('Store created before branch check'))
    args = cli.parser().parse_args(['--workspace', str(tmp_path/'private'), 'wiki-update', str(root), 'engine'])
    with pytest.raises(FlowError, match='requires lite'):
        cli.execute(args)
    assert not (tmp_path/'private').exists()
    calls = []
    monkeypatch.setattr(branch, 'check', lambda path: calls.append(path))
    for command in ['wiki-search', 'wiki-read', 'wiki-index', 'wiki-code']:
        branch.guard_cli(Namespace(command=command, project='unrelated'))
    branch.guard_cli(Namespace(command='wiki-pr', project='unrelated', retain_project='selected'))
    branch.guard_cli(Namespace(command='wiki-inventory', project='selected', retain=False))
    branch.guard_cli(Namespace(command='wiki-inventory', project='inventory', retain=True))
    assert calls == ['selected', 'inventory']
