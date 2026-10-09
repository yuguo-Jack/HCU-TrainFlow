import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import sys

import pytest

from hcu_trainflow import dependencies
from hcu_trainflow.core import FlowError, write_json

ROOT = Path(__file__).resolve().parents[1]


def script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT/'scripts'/f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_real_manifest_requires_knowledge_by_default(tmp_path, monkeypatch):
    root, items = dependencies.load_manifest(ROOT)
    kb = next(x for x in items if x['id'] == 'hcu-knowledge')
    assert not kb['optional']
    write_json(tmp_path/'thirdparty/manifest.json', {'schema_version': 1, 'dependencies': items})
    monkeypatch.setattr(dependencies, 'git', lambda *a, **k: pytest.fail('Status must not fetch'))
    result = dependencies.sync_dependencies(tmp_path, status_only=True)
    assert {x['id'] for x in result['dependencies']} == {x['id'] for x in items}
    assert result['status'] == 'incomplete'


def setup_fakes(monkeypatch, tmp_path, external=True):
    module = script('setup_trainflow')
    paths = {'hcu-knowledge': tmp_path/'kb', 'tracelens': tmp_path/'lens'}
    monkeypatch.setattr(module, 'sync_dependencies', lambda p: {'status': 'ready', 'dependencies': [
        {'id': 'hcu-knowledge', 'status': 'ready', 'external': external}]})
    monkeypatch.setattr(module, 'require_checkout', lambda p, name: (paths[name], {}))
    return module


@pytest.mark.parametrize('external', [True, False])
def test_full_setup_order_and_no_upstream_refresh(tmp_path, monkeypatch, external):
    module = setup_fakes(monkeypatch, tmp_path, external)
    commands = []
    def run(argv, **kw):
        commands.append(argv)
        return SimpleNamespace(returncode=0)
    result = module.setup(tmp_path, tmp_path/'skills', run=run)
    assert result['status'] == 'ready'
    if external:
        assert all(x[0] != 'git' for x in commands)
    else:
        assert ['git', 'lfs', 'install', '--local'] in commands
        assert ['git', 'lfs', 'pull'] in commands
    assert all('update' not in x and 'fetch' not in x for x in commands)
    stages = result['completed_stages']
    assert stages.index('knowledge-bootstrap') < stages.index('knowledge-doctor') < stages.index('skills')
    assert '--workflow-only' not in commands[-1]


def test_missing_private_access_prevents_installation(tmp_path, monkeypatch):
    module = script('setup_trainflow')
    monkeypatch.setattr(module, 'sync_dependencies', lambda p: {'status': 'incomplete', 'dependencies': [
        {'id': 'hcu-knowledge', 'status': 'unavailable'}]})
    with pytest.raises(FlowError, match='hcu-knowledge'):
        module.setup(tmp_path, tmp_path/'skills', run=lambda *a, **kw: pytest.fail('Must stop before pip/Skills'))
    assert json.loads((tmp_path/'.work/setup/status.json').read_text())['status'] == 'incomplete'


def test_index_failure_blocks_skills_and_replaces_old_success(tmp_path, monkeypatch):
    module = setup_fakes(monkeypatch, tmp_path)
    write_json(tmp_path/'.work/setup/status.json', {'status': 'ready'})
    commands = []
    def run(argv, **kw):
        commands.append(argv)
        return SimpleNamespace(returncode=2 if 'bootstrap' in argv else 0)
    with pytest.raises(FlowError, match='knowledge-bootstrap'):
        module.setup(tmp_path, tmp_path/'skills', run=run)
    state = json.loads((tmp_path/'.work/setup/status.json').read_text())
    assert state['status'] == 'incomplete' and state['failed_stage'] == 'knowledge-bootstrap'
    assert not any('install_skills.py' in str(x) for x in commands)


def test_default_installer_copies_eleven_and_binds_knowledge(tmp_path, monkeypatch):
    module = script('install_skills')
    module.ROOT = tmp_path
    kernel, kb = tmp_path/'kernel', tmp_path/'kb'
    for names, parent in [(module.NAMES, tmp_path), (module.KERNEL_NAMES, kernel), (module.KNOWLEDGE_NAMES, kb)]:
        for name in names:
            path = parent/'skills'/name
            path.mkdir(parents=True)
            (path/'SKILL.md').write_text(name)
            (path/'helper.py').write_text('# source\n')
    monkeypatch.setattr(module, 'require_checkout', lambda p, name: (kb if name == 'hcu-knowledge' else kernel, {}))
    monkeypatch.setattr(module.subprocess, 'run', lambda *a, **kw: SimpleNamespace(returncode=0, stdout='{"local_ready": true}'))
    target = tmp_path/'installed'
    monkeypatch.setattr(sys, 'argv', ['install_skills.py', '--target', str(target)])
    module.main()
    assert len(list(target.glob('*/SKILL.md'))) == 11
    for name in module.KNOWLEDGE_NAMES:
        assert json.loads((target/name/'workspace.json').read_text())['root'] == str(kb)
        assert (target/name/'helper.py').is_file()
    module.main()  # Bound workspace files must not make an idempotent install differ.
    (target/module.NAMES[0]/'SKILL.md').write_text('user edits')
    with pytest.raises(SystemExit): module.main()
    assert (target/module.NAMES[0]/'SKILL.md').read_text() == 'user edits'


def test_external_binding_never_fetches_or_resets(tmp_path, monkeypatch):
    item = dict(id='hcu-knowledge', path='thirdparty/HCU-Knowledge', url='https://github.com/example/kb.git', commit='a'*40, optional=False)
    write_json(tmp_path/'thirdparty/manifest.json', {'schema_version': 1, 'dependencies': [item]})
    kb = tmp_path/'existing'; kb.mkdir()
    write_json(tmp_path/'thirdparty.local.json', {'hcu_knowledge_root': str(kb)})
    def git(path, *args, **kw):
        assert args[0] in {'rev-parse', 'remote', 'status'}
        value = str(kb) if '--show-toplevel' in args else item['url'] if args[0] == 'remote' else 'b'*40 if args[0] == 'rev-parse' else ' M local-note.md'
        return SimpleNamespace(returncode=0, stdout=value)
    monkeypatch.setattr(dependencies, 'git', git)
    result = dependencies.sync_dependencies(tmp_path)
    assert result['status'] == 'ready'
    assert result['dependencies'][0]['commit'] == 'b'*40
    assert result['dependencies'][0]['dirty']


def test_unready_knowledge_cannot_install_any_skills(tmp_path, monkeypatch):
    module = script('install_skills')
    monkeypatch.setattr(module, 'require_checkout', lambda *a: (tmp_path/'kb', {}))
    monkeypatch.setattr(module.subprocess, 'run', lambda *a, **kw: SimpleNamespace(returncode=2, stdout='{"local_ready": false}'))
    target = tmp_path/'skills'
    monkeypatch.setattr(sys, 'argv', ['install_skills.py', '--target', str(target)])
    with pytest.raises(SystemExit): module.main()
    assert not target.exists()


def test_interrupted_setup_does_not_leave_ready_record(tmp_path, monkeypatch):
    module = setup_fakes(monkeypatch, tmp_path)
    def run(*a, **kw): raise KeyboardInterrupt()
    with pytest.raises(KeyboardInterrupt): module.setup(tmp_path, tmp_path/'skills', run=run)
    assert json.loads((tmp_path/'.work/setup/status.json').read_text())['status'] == 'interrupted'


@pytest.mark.parametrize('current,rollback', [(True, False), (False, False), (True, True)])
def test_reuse_only_current_external_index(tmp_path, monkeypatch, current, rollback):
    module = setup_fakes(monkeypatch, tmp_path)
    commands = []
    def run(argv, **kw):
        commands.append(argv)
        return SimpleNamespace(returncode=0, stdout=json.dumps({'local_ready': True, 'index_current': current, 'snapshot_mode': 'rollback' if rollback else 'current'}))
    result = module.setup(tmp_path, tmp_path/'skills', run=run)
    reused = current and not rollback
    assert ('knowledge-bootstrap-reused' in result['completed_stages']) == reused
    assert any('bootstrap' in x for x in commands) != reused
