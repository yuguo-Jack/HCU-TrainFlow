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
    assert {x['id'] for x in result['dependencies']} == {x['id'] for x in items if not x.get('optional')}
    assert next(x for x in items if x['id'] == 'kernelwiki')['optional'] is True
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


def test_relative_full_setup_target_matches_actual_install_from_other_cwd(tmp_path, monkeypatch):
    setup = setup_fakes(monkeypatch, tmp_path)
    installer = script('install_skills')
    project, caller, kernel, knowledge = [tmp_path/name for name in ('project', 'caller', 'kernel', 'kb')]
    caller.mkdir()
    for parent, names in [(project, installer.NAMES), (kernel, installer.KERNEL_NAMES), (knowledge, installer.KNOWLEDGE_NAMES)]:
        for name in names:
            source = parent/'skills'/name
            source.mkdir(parents=True)
            (source/'SKILL.md').write_text(name, encoding='utf-8')
    installer.ROOT = project
    monkeypatch.setattr(installer, 'require_checkout', lambda p, name: (knowledge if name == 'hcu-knowledge' else kernel, {}))
    ready = SimpleNamespace(returncode=0, stdout='{"local_ready": true, "index_current": true, "snapshot_mode": "current"}')
    monkeypatch.setattr(installer.subprocess, 'run', lambda *a, **kw: ready)
    def run(argv, cwd, **kwargs):
        for i, arg in enumerate(argv):
            if str(arg).endswith('install_skills.py'):
                with monkeypatch.context() as child:
                    child.chdir(cwd)
                    child.setattr(sys, 'argv', argv[i:])
                    installer.main()
        return ready
    monkeypatch.chdir(caller)
    state = setup.setup(project, Path('relative-skills'), run=run)
    expected = caller/'relative-skills'
    assert state['status'] == 'ready'
    assert Path(state['skills_dir']) == expected
    assert len(list(expected.glob('*/SKILL.md'))) == 11
    assert not (project/'relative-skills').exists()


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


def test_full_setup_blocks_install_on_broken_reading_resources(tmp_path, monkeypatch):
    module = setup_fakes(monkeypatch, tmp_path)
    commands = []
    def run(argv, **kwargs):
        commands.append(argv)
        return SimpleNamespace(returncode=1 if any('check_skill_resources.py' in str(a) for a in argv) else 0)
    with pytest.raises(FlowError, match='skill-resources'):
        module.setup(tmp_path, tmp_path/'skills', run=run)
    assert not any('pip' in c or any('install_skills.py' in str(a) for a in c) for c in commands)
    assert json.loads((tmp_path/'.work/setup/status.json').read_text())['failed_stage'] == 'skill-resources'


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
    monkeypatch.setattr(module.subprocess, 'run', lambda *a, **kw: SimpleNamespace(returncode=0, stdout='{"local_ready": true, "index_current": true, "snapshot_mode": "current"}'))
    target = tmp_path/'installed'
    monkeypatch.setattr(sys, 'argv', ['install_skills.py', '--target', str(target)])
    module.main()
    assert len(list(target.glob('*/SKILL.md'))) == 11
    for name in module.NAMES:
        assert json.loads((target/name/'workspace.json').read_text()) == {'project_root':str(tmp_path.resolve())}
        assert not (tmp_path/'skills'/name/'workspace.json').exists()
    for name in module.KNOWLEDGE_NAMES:
        assert json.loads((target/name/'workspace.json').read_text())['root'] == str(kb)
        assert (target/name/'helper.py').is_file()
    module.main()  # Bound workspace files must not make an idempotent install differ.
    (target/module.NAMES[0]/'SKILL.md').write_text('user edits')
    with pytest.raises(SystemExit): module.main()
    assert (target/module.NAMES[0]/'SKILL.md').read_text() == 'user edits'


def test_workflow_binding_from_other_directory_preserves_environment(tmp_path, monkeypatch):
    from hcu_trainflow.cli import execute, parser
    module = script('install_skills')
    project = tmp_path/'project'
    for name in module.NAMES:
        source = project/'skills'/name
        source.mkdir(parents=True)
        (source/'SKILL.md').write_text(name)
    (project/'knowledge').mkdir()
    (project/'knowledge/topic.md').write_text('---\nid: installation-binding\n---\n# Installed project discovery\n',encoding='utf-8')
    module.ROOT = project
    elsewhere = tmp_path/'elsewhere'; elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)
    monkeypatch.setenv('TRAINFLOW_PROJECT', str(tmp_path/'explicit-project'))
    monkeypatch.setenv('TRAINFLOW_WORKSPACE', str(tmp_path/'explicit-workspace'))
    target = tmp_path/'installed'
    monkeypatch.setattr(sys, 'argv', ['install_skills.py', '--workflow-only', '--target', str(target)])
    module.main()
    binding = json.loads((target/'hcu-trainflow/workspace.json').read_text())
    assert Path(binding['project_root']).is_absolute()
    result = execute(parser().parse_args(['--workspace',str(tmp_path/'search-state'),'wiki-search','discovery',
                                         '--project',binding['project_root'],'--online-pr','off']))
    assert result['results'][0]['id'] == 'installation-binding'
    import os
    assert os.environ['TRAINFLOW_PROJECT'] == str(tmp_path/'explicit-project')
    assert os.environ['TRAINFLOW_WORKSPACE'] == str(tmp_path/'explicit-workspace')


def test_workflow_relocation_requires_explicit_rebind_and_cleans_verified_backup(tmp_path, monkeypatch):
    import shutil
    module = script('install_skills')
    original, moved = tmp_path/'original', tmp_path/'moved'
    for name in module.NAMES:
        source = original/'skills'/name
        source.mkdir(parents=True)
        (source/'SKILL.md').write_text(name)
    target = tmp_path/'installed'
    module.ROOT = original
    argv = ['install_skills.py', '--workflow-only', '--target', str(target)]
    monkeypatch.setattr(sys, 'argv', argv)
    module.main()
    module.main()  # Generated bindings participate in idempotence.
    shutil.copytree(original, moved)
    module.ROOT = moved
    with pytest.raises(SystemExit): module.main()
    assert json.loads((target/'hcu-trainflow/workspace.json').read_text())['project_root'] == str(original.resolve())
    monkeypatch.setattr(sys, 'argv', [*argv,'--replace'])
    module.main()
    for name in module.NAMES:
        assert json.loads((target/name/'workspace.json').read_text())['project_root'] == str(moved.resolve())
        backups = list((tmp_path/'trainflow-skill-backups').glob('*/'+name+'/workspace.json'))
        assert not backups
        assert not (moved/'skills'/name/'workspace.json').exists()


@pytest.mark.parametrize('failure', ['copy', 'verify'])
def test_failed_skill_replacement_keeps_originals_and_obsolete_entry_backup(tmp_path, monkeypatch, failure):
    module = script('install_skills')
    module.ROOT = tmp_path/'project'
    target = tmp_path/'installed'
    for name in module.NAMES:
        source = module.ROOT/'skills'/name
        source.mkdir(parents=True)
        (source/'SKILL.md').write_text('new '+name)
    old_names = [module.NAMES[0], module.NAMES[1], 'hcu-train-operate']
    for name in old_names:
        dest = target/name
        dest.mkdir(parents=True)
        (dest/'SKILL.md').write_text('original '+name)
    real_copy = module.shutil.copytree
    def faulty_copy(source, dest, **kwargs):
        result = real_copy(source, dest, **kwargs)
        if failure == 'copy' and dest.name == module.NAMES[1]:
            raise OSError('synthetic copy failure')
        if failure == 'verify' and dest.name == module.NAMES[0]:
            (dest/'SKILL.md').write_text('corrupt installed content')
        return result
    monkeypatch.setattr(module.shutil, 'copytree', faulty_copy)
    monkeypatch.setattr(sys, 'argv', ['install_skills.py', '--target', str(target), '--workflow-only', '--replace'])
    with pytest.raises((OSError, FlowError)):
        module.main()
    for name in old_names:
        backups = list((tmp_path/'trainflow-skill-backups').glob('*/'+name+'/SKILL.md'))
        assert len(backups) == 1
        assert backups[0].read_text() == 'original '+name


def test_successful_install_only_cleans_its_own_backups(tmp_path, monkeypatch):
    module = script('install_skills')
    module.ROOT = tmp_path/'project'
    target = tmp_path/'installed'
    for name in module.NAMES:
        source = module.ROOT/'skills'/name
        source.mkdir(parents=True)
        (source/'SKILL.md').write_text('current '+name)
    old = target/module.NAMES[0]
    old.mkdir(parents=True)
    (old/'SKILL.md').write_text('old installed')
    history = tmp_path/'trainflow-skill-backups/previous-failed'/module.NAMES[0]/'SKILL.md'
    history.parent.mkdir(parents=True)
    history.write_text('unresolved previous backup')
    monkeypatch.setattr(sys, 'argv', ['install_skills.py', '--target', str(target), '--workflow-only', '--replace'])
    module.main()
    assert history.read_text() == 'unresolved previous backup'
    assert list((tmp_path/'trainflow-skill-backups').rglob('SKILL.md')) == [history]
    assert (old/'SKILL.md').read_text() == 'current '+module.NAMES[0]


def test_skill_cleanup_rejects_paths_outside_managed_root(tmp_path):
    module = script('install_skills')
    outside = tmp_path/'outside'/module.NAMES[0]
    outside.mkdir(parents=True)
    (outside/'SKILL.md').write_text('must remain')
    with pytest.raises(FlowError, match='unsafe backup cleanup'):
        module.cleanup_backups(tmp_path/'installed', [outside])
    assert (outside/'SKILL.md').read_text() == 'must remain'


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


@pytest.mark.parametrize('stdout',[
    '{"local_ready": true, "index_current": false, "snapshot_mode": "current"}',
    '{"local_ready": true, "index_current": true, "snapshot_mode": "rollback"}',
    '{"local_ready": true, "index_current": true, "snapshot_mode": "unknown"}',
    '{"local_ready": true}',
    '{"local_ready": "false", "index_current": true, "snapshot_mode": "current"}',
    '[]',
    'not JSON',
])
def test_incomplete_or_rollback_knowledge_cannot_install_skills(tmp_path,monkeypatch,stdout):
    module=script('install_skills')
    monkeypatch.setattr(module,'require_checkout',lambda *a:(tmp_path/'kb',{}))
    monkeypatch.setattr(module.subprocess,'run',lambda *a,**kw:SimpleNamespace(returncode=0,stdout=stdout))
    target=tmp_path/'installed'
    monkeypatch.setattr(sys,'argv',['install_skills.py','--target',str(target)])
    with pytest.raises(SystemExit):module.main()
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


def test_analysis_skill_migration_and_readonly_drift_check(tmp_path, monkeypatch):
    module = script('install_skills')
    module.ROOT = tmp_path/'project'
    target = tmp_path/'installed'
    for name in module.NAMES:
        source = module.ROOT/'skills'/name
        source.mkdir(parents=True)
        (source/'SKILL.md').write_text('current '+name)
    old = target/'hcu-train-optimize'
    old.mkdir(parents=True)
    (old/'SKILL.md').write_text('old optimization entry')
    argv = ['install_skills.py', '--target', str(target), '--workflow-only']
    monkeypatch.setattr(sys, 'argv', [*argv, '--check'])
    before = module.tree_hash(target)
    with pytest.raises(SystemExit) as error:
        module.main()
    assert error.value.code == 1 and module.tree_hash(target) == before
    monkeypatch.setattr(sys, 'argv', [*argv, '--replace'])
    module.main()
    new = target/'hcu-train-analyze-and-optimize'
    assert new.is_dir() and not old.exists()
    monkeypatch.setattr(sys, 'argv', [*argv, '--check'])
    module.main()
    (new/'SKILL.md').write_text('stale installed entry')
    before = module.tree_hash(target)
    with pytest.raises(SystemExit):
        module.main()
    assert module.tree_hash(target) == before


def resource_fixture(project):
    (project/'docs').mkdir(parents=True)
    (project/'docs/skill-reading-map.md').write_text('# Reading routes\n')
    skill = project/'skills/example'
    (skill/'references').mkdir(parents=True)
    (skill/'SKILL.md').write_text('Read `docs/skill-reading-map.md` and [detail](references/detail.md).\n')
    (skill/'references/detail.md').write_text('# Detail\n')
    return skill


def test_reading_resources_detect_missing_guide_and_unreachable_reference(tmp_path):
    module = script('check_skill_resources')
    skill = resource_fixture(tmp_path)
    assert module.check_resources(tmp_path)['status'] == 'current'
    (skill/'references/detail.md').unlink()
    (skill/'references/orphan.md').write_text('Never linked')
    result = module.check_resources(tmp_path)
    assert result['status'] == 'incomplete'
    assert any('missing' in s and 'detail.md' in s for s in result['issues'])
    assert any('no reading route' in s and 'orphan.md' in s for s in result['issues'])


def test_reading_resources_handle_external_paths_examples_and_project_escape(tmp_path):
    module = script('check_skill_resources')
    resource_fixture(tmp_path)
    page = tmp_path/'docs/skill-reading-map.md'
    page.write_text('Upstream has `docs/external.md`. [Online](https://example.org/docs/guide.md)\n'
                    '```markdown\n[Example](missing-example.md)\n```\n')
    assert module.check_resources(tmp_path)['status'] == 'current'
    page.write_text('[Escape](../../outside.md)\n')
    assert any('leaves project' in s for s in module.check_resources(tmp_path)['issues'])


def sync_fixture(tmp_path):
    module = script('sync_local_install')
    project, target = tmp_path/'project', tmp_path/'installed'
    resource_fixture(project)
    for name in module.NAMES:
        write_json(target/name/'workspace.json', {'project_root': str(project.resolve())})
    return module, project, target


def test_local_sync_is_bounded_and_checks_package_before_replacing_skills(tmp_path):
    module, project, target = sync_fixture(tmp_path)
    commands = []
    def run(argv, **kwargs):
        commands.append(argv)
        return SimpleNamespace(returncode=0)
    result = module.sync(project, target, run=run)
    assert result['status'] == 'current'
    assert result['completed_stages'] == ['preflight', 'package-install', 'package-check', 'skills-install', 'skills-check']
    assert '--no-deps' in commands[0] and '--no-build-isolation' in commands[0]
    assert '-I' in commands[1]
    assert '--replace' in commands[2] and '--workflow-only' in commands[2]
    assert '--check' in commands[3]
    assert not any('setup_trainflow.py' in str(c) or 'git' in c for c in commands)
    assert json.loads((project/'.work/setup/local-sync.json').read_text())['status'] == 'current'


@pytest.mark.parametrize('failed_stage', ['package-install', 'package-check', 'skills-install', 'skills-check'])
def test_failed_local_sync_never_leaves_old_success(tmp_path, failed_stage):
    module, project, target = sync_fixture(tmp_path)
    write_json(project/'.work/setup/local-sync.json', {'status': 'current'})
    stages = iter(['package-install', 'package-check', 'skills-install', 'skills-check'])
    def run(argv, **kwargs):
        return SimpleNamespace(returncode=1 if next(stages) == failed_stage else 0)
    with pytest.raises(FlowError, match=failed_stage):
        module.sync(project, target, run=run)
    state = json.loads((project/'.work/setup/local-sync.json').read_text())
    assert state['status'] == 'incomplete' and state['failed_stage'] == failed_stage


def test_local_check_is_readonly_and_never_runs_pip(tmp_path):
    module, project, target = sync_fixture(tmp_path)
    commands = []
    def run(argv, **kwargs):
        commands.append(argv)
        return SimpleNamespace(returncode=0)
    module.sync(project, target, check_only=True, run=run)
    assert len(commands) == 2 and '-I' in commands[0] and '--check' in commands[1]
    assert not (project/'.work').exists()


@pytest.mark.parametrize('binding', ['foreign', 'missing'])
def test_local_sync_refuses_missing_or_foreign_binding_before_pip(tmp_path, binding):
    module, project, target = sync_fixture(tmp_path)
    path = target/module.NAMES[0]/'workspace.json'
    if binding == 'foreign':
        write_json(path, {'project_root': str(tmp_path/'other-project')})
    else:
        path.unlink()
    with pytest.raises(FlowError, match='binding'):
        module.sync(project, target, run=lambda *a, **kw: pytest.fail('No package/Skill mutation before binding check'))


@pytest.mark.parametrize('current,old', [('hcu-train-analyze-and-optimize','hcu-train-optimize'), ('hcu-train-check-and-adapt','hcu-train-environment-check-and-adapt')])
def test_local_sync_accepts_rename_but_rejects_uninstalled_entry(tmp_path,current,old):
    module, project, target = sync_fixture(tmp_path)
    (target/current).rename(target/old)
    module.check_existing_binding(project.resolve(), target.resolve())
    (target/module.NAMES[0]/'workspace.json').unlink()
    (target/module.NAMES[0]).rmdir()
    with pytest.raises(FlowError, match='not installed'):
        module.check_existing_binding(project.resolve(), target.resolve())


def test_interrupted_local_sync_preserves_incomplete_status(tmp_path):
    module, project, target = sync_fixture(tmp_path)
    def run(*a, **kw):
        raise KeyboardInterrupt()
    with pytest.raises(KeyboardInterrupt):
        module.sync(project, target, run=run)
    assert json.loads((project/'.work/setup/local-sync.json').read_text())['status'] == 'interrupted'
