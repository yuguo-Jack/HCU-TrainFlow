import json
from pathlib import Path
from types import SimpleNamespace
import sys

import pytest

from hcu_trainflow.core import FlowError
from hcu_trainflow import dependencies
from test_full_setup import ROOT, script, setup_fakes


def kernelwiki_fixture(tmp_path, monkeypatch):
    installer = script('install_skills')
    installer.ROOT = tmp_path/'project'
    source = installer.ROOT/'thirdparty/KernelWiki'
    for name, text in {
        'SKILL.md': '---\nname: KernelWiki\ndescription: Reference\n---\n',
        'scripts/query.py': '# query entry\n', 'wiki/topic.md': 'knowledge',
        'artifacts/kernel.cu': '// fixed source evidence', 'LICENSE': 'MIT',
        '.git/config': 'must not enter installation',
        '__pycache__/cached.pyc': 'cache', '.pytest_cache/state': 'cache',
    }.items():
        path = source/name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')
    def checkout(root, name):
        assert name == 'kernelwiki', 'Standalone installation must not inspect other dependencies'
        return source, {}
    monkeypatch.setattr(installer, 'require_checkout', checkout)
    monkeypatch.setattr(installer.subprocess, 'run', lambda *a, **kw: pytest.fail('No pip/knowledge doctor'))
    target = tmp_path/'skills'
    argv = ['install_skills.py', '--kernelwiki-only', '--target', str(target)]
    monkeypatch.setattr(sys, 'argv', argv)
    return installer, source, target, argv


def test_standalone_kernelwiki_install_preserves_resources_and_other_skills(tmp_path, monkeypatch):
    installer, source, target, argv = kernelwiki_fixture(tmp_path, monkeypatch)
    old = target/'hcu-train-environment-check-and-adapt/SKILL.md'
    old.parent.mkdir(parents=True)
    old.write_text('unrelated older installation')
    installer.main()
    assert installer.tree_hash(source) == installer.tree_hash(target/'KernelWiki')
    assert (target/'KernelWiki/artifacts/kernel.cu').is_file()
    assert not (target/'KernelWiki/.git').exists()
    assert not (target/'KernelWiki/.pytest_cache').exists()
    assert not (target/'KernelWiki/workspace.json').exists()
    assert old.read_text() == 'unrelated older installation'
    installer.main()  # Idempotent, including the ignored checkout metadata.
    monkeypatch.setattr(sys, 'argv', [*argv, '--check'])
    installer.main()


def test_optional_replacement_preserves_edits_until_explicit_and_verified(tmp_path, monkeypatch):
    installer, source, target, argv = kernelwiki_fixture(tmp_path, monkeypatch)
    installer.main()
    installed = target/'KernelWiki/SKILL.md'
    installed.write_text('local changes')
    with pytest.raises(SystemExit):
        installer.main()
    assert installed.read_text() == 'local changes'
    monkeypatch.setattr(sys, 'argv', [*argv, '--check'])
    with pytest.raises(SystemExit):
        installer.main()
    assert installed.read_text() == 'local changes'
    monkeypatch.setattr(sys, 'argv', [*argv, '--replace'])
    installer.main()
    assert installed.read_bytes() == (source/'SKILL.md').read_bytes()
    assert not list((tmp_path/'trainflow-skill-backups').rglob('SKILL.md'))


def test_optional_replacement_never_discards_independent_git_history(tmp_path, monkeypatch):
    installer, source, target, argv = kernelwiki_fixture(tmp_path, monkeypatch)
    installer.main()
    installed = target/'KernelWiki'
    (installed/'.git').mkdir()
    (installed/'.git/local-history').write_text('keep')
    (installed/'SKILL.md').write_text('independently updated')
    monkeypatch.setattr(sys, 'argv', [*argv, '--replace'])
    with pytest.raises(SystemExit):
        installer.main()
    assert (installed/'.git/local-history').read_text() == 'keep'
    assert (installed/'SKILL.md').read_text() == 'independently updated'


@pytest.mark.parametrize('optional_status', ['ready', 'unavailable'])
def test_complete_setup_only_selects_kernelwiki_when_requested(tmp_path, monkeypatch, optional_status):
    setup = setup_fakes(monkeypatch, tmp_path)
    selected = []
    def sync(project, only=None):
        selected.append(only)
        if only:
            assert only == ['kernelwiki']
            return {'status': 'ready' if optional_status == 'ready' else 'incomplete',
                    'dependencies': [{'id': 'kernelwiki', 'status': optional_status, 'optional': True}]}
        return {'status': 'ready', 'dependencies': [{'id': 'hcu-knowledge', 'status': 'ready', 'external': True}]}
    monkeypatch.setattr(setup, 'sync_dependencies', sync)
    commands = []
    def run(argv, **kwargs):
        commands.append(argv)
        return SimpleNamespace(returncode=0)
    if optional_status == 'unavailable':
        with pytest.raises(FlowError, match='kernelwiki'):
            setup.setup(tmp_path, tmp_path/'skills', run=run, with_kernelwiki=True)
        assert not commands
        assert json.loads((tmp_path/'.work/setup/status.json').read_text())['status'] == 'incomplete'
    else:
        result = setup.setup(tmp_path, tmp_path/'skills', run=run, with_kernelwiki=True)
        assert result['optional_skills'] == ['KernelWiki']
        assert '--with-kernelwiki' in commands[-1]
        assert '12 Skills' in result['note']
    assert selected == [None, ['kernelwiki']]


def test_default_dependency_status_skips_optional_but_explicit_selection_includes_it(tmp_path, monkeypatch):
    _, items = dependencies.load_manifest(ROOT)
    (tmp_path/'thirdparty').mkdir()
    (tmp_path/'thirdparty/manifest.json').write_text(json.dumps({'schema_version': 1, 'dependencies': items}))
    monkeypatch.setattr(dependencies, 'git', lambda *a, **kw: pytest.fail('Read-only missing checkout check'))
    default = dependencies.sync_dependencies(tmp_path, status_only=True)
    assert 'kernelwiki' not in {row['id'] for row in default['dependencies']}
    selected = dependencies.sync_dependencies(tmp_path, only=['kernelwiki'], status_only=True)
    assert [row['id'] for row in selected['dependencies']] == ['kernelwiki']


def test_legacy_include_knowledge_does_not_opt_into_kernelwiki(monkeypatch):
    bootstrap = script('bootstrap_thirdparty')
    def sync(project, only, include_optional, status_only, migrate_origin):
        assert include_optional is False and status_only is True
        return {'status': 'ready', 'dependencies': []}
    monkeypatch.setattr(bootstrap, 'sync_dependencies', sync)
    monkeypatch.setattr(sys, 'argv', ['bootstrap_thirdparty.py', '--include-knowledge', '--status'])
    assert bootstrap.main() == 0
