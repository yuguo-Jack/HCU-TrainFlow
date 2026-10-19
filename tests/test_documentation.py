"""Regression coverage for stale docs that link/file-only checks used to miss."""
import argparse
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('documentation_check', ROOT/'scripts/check_documentation.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def write(project, path, text):
    file = project / path
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(text, encoding='utf-8')
    return file


def fixture(project):
    write(project, 'README.md', '# Example\n[Guide](docs/guide.md#使用)\n')
    write(project, 'docs/guide.md', '# Guide\n\n## 使用\n')


def test_root_and_thirdparty_links_anchors_and_orphans(tmp_path):
    fixture(tmp_path)
    assert checker.check_documentation(tmp_path)['status'] == 'current'
    write(tmp_path, 'README.md', '[Guide](docs/guide.md#renamed)\n[Lost](removed.md)\n')
    write(tmp_path, 'thirdparty/README.md', '[Missing](missing.md)\n')
    write(tmp_path, 'docs/forgotten.md', '# Abandoned instructions\n')
    errors = checker.check_documentation(tmp_path)['issues']
    assert any('README.md: missing heading anchor' in e for e in errors)
    assert any('README.md: missing link target' in e for e in errors)
    assert any('thirdparty/README.md: missing link target' in e for e in errors)
    assert any('forgotten.md: no incoming' in e for e in errors)


def test_reference_links_encoded_headings_and_fenced_templates(tmp_path):
    fixture(tmp_path)
    write(tmp_path, 'README.md', '[Guide][g]\n\n[g]: docs/guide.md#%E4%BD%BF%E7%94%A8\n')
    write(tmp_path, 'docs/guide.md', '# Guide\n## 使用\n## 使用\n'
          '[Same heading](#使用-1)\n'
          '```markdown\n[Template](missing-file.md)\n```\n')
    assert checker.check_documentation(tmp_path)['status'] == 'current'


def test_skill_root_paths_form_real_reading_routes(tmp_path):
    write(tmp_path, 'skills/example/SKILL.md', 'Read `docs/guide.md#使用`.\n')
    write(tmp_path, 'docs/guide.md', '# Guide\n## 使用\n')
    assert checker.check_documentation(tmp_path)['status'] == 'current'


def test_bracketed_pr_titles_do_not_hide_broken_links(tmp_path):
    fixture(tmp_path)
    write(tmp_path, 'README.md', '[PR: [dev] overlap](gone.md)\n'
          '[PR: [PyTorch] linear](docs/guide.md#missing)\n')
    issues = checker.check_documentation(tmp_path)['issues']
    assert any('missing link target: gone.md' in issue for issue in issues)
    assert any('missing heading anchor: docs/guide.md#missing' in issue for issue in issues)


def test_clickable_images_keep_image_destination_checks(tmp_path):
    fixture(tmp_path)
    write(tmp_path, 'target.bin', 'data')
    write(tmp_path, 'README.md', '[Guide](docs/guide.md)\n[![diagram](missing.svg)](target.bin)\n')
    issues = checker.check_documentation(tmp_path)['issues']
    assert any('missing link target: missing.svg' in issue for issue in issues)


def test_invalid_outer_nested_link_is_not_a_destination(tmp_path):
    fixture(tmp_path)
    write(tmp_path, 'README.md', '[outer [inner](docs/guide.md)](literal-text.md)\n')
    assert checker.check_documentation(tmp_path)['status'] == 'current'


def test_escaped_and_case_sensitive_paths_and_main_self_links(tmp_path):
    fixture(tmp_path)
    write(tmp_path, 'README.md', '[Guide](docs/Guide.md)\n[Escape](../outside.md)\n'
          '[Current](https://github.com/yuguo-Jack/HCU-TrainFlow/blob/main/missing.md)\n'
          '[Fixed](https://github.com/yuguo-Jack/HCU-TrainFlow/blob/abcdef/historical.md)\n')
    errors = checker.check_documentation(tmp_path)['issues']
    assert any('Guide.md' in e and ('case mismatch' in e or 'missing link' in e) for e in errors)
    assert any('leaves project' in e for e in errors)
    assert any('main/missing.md' in e for e in errors)
    assert not any('historical.md' in e for e in errors)


def test_cli_examples_are_parsed_without_running_handlers(tmp_path):
    fixture(tmp_path)
    cli = argparse.ArgumentParser()
    sub = cli.add_subparsers(dest='command', required=True)
    command = sub.add_parser('inspect')
    command.add_argument('--input', required=True)
    command.set_defaults(func=lambda *_: pytest.fail('Checker executed an example'))
    write(tmp_path, 'docs/guide.md', '# Guide\n## 使用\n'
          '```bash\nhcu-trainflow inspect \\\n  --input example.json\n```\n')
    result = checker.check_documentation(tmp_path, cli)
    assert result['status'] == 'current' and result['cli_examples'] == 1
    write(tmp_path, 'docs/guide.md', '# Guide\n## 使用\n'
          '```powershell\nhcu-trainflow inspect --retired-option file.json\n```\n')
    assert any('invalid CLI example' in e for e in checker.check_documentation(tmp_path, cli)['issues'])


def test_json_examples_are_syntax_checked(tmp_path):
    fixture(tmp_path)
    write(tmp_path, 'docs/guide.md', '# Guide\n## 使用\n```json\n{"mode":}\n```\n')
    result = checker.check_documentation(tmp_path)
    assert result['json_examples'] == 1
    assert any('invalid JSON example' in e for e in result['issues'])


def test_history_upstream_versions_and_stable_ids_are_not_rewritten(tmp_path):
    fixture(tmp_path)
    write(tmp_path, 'CHANGELOG.md', 'HCU-TrainFlow v0.1.0 $hcu-train-prepare\n[Old](gone.md)\n')
    write(tmp_path, 'task_plan.md', 'Historical v0.1.0\n[Old](gone.md)\n')
    write(tmp_path, 'knowledge/projects/tool/knowledgebase/upstream/docs/source.md',
          'Upstream $hcu-train-prepare\n[Upstream relative](gone.md)\n')
    write(tmp_path, 'docs/guide.md', '# Guide\n## 使用\n'
          'Keep `official-megatron-wiki/cases/paged-stash-launch` as a stable ID.\n'
          'Installer migrates `hcu-train-prepare`; DTK 26.10 and upstream v0.1.0 retain their meaning.\n')
    assert checker.check_documentation(tmp_path)['status'] == 'current'
    with (tmp_path/'docs/guide.md').open('a', encoding='utf-8') as f:
        f.write('Start with `$hcu-train-prepare`.\n')
    assert any('retired Skill invocation' in e for e in checker.check_documentation(tmp_path)['issues'])


def test_version_drift_and_duplicated_project_versions(tmp_path):
    fixture(tmp_path)
    write(tmp_path, 'pyproject.toml', '[project]\nversion = "0.6.8"\n')
    write(tmp_path, 'src/hcu_trainflow/__init__.py', '__version__ = "0.6.8"\n')
    write(tmp_path, 'README.md', '**当前版本：`0.1.0`。**\n[Guide](docs/guide.md#使用)\n')
    assert any('current version must match' in e for e in checker.check_documentation(tmp_path)['issues'])
    write(tmp_path, 'README.md', '**当前版本：`0.6.8`。**\n[Guide](docs/guide.md#使用)\n')
    assert checker.check_documentation(tmp_path)['status'] == 'current'
    with (tmp_path/'docs/guide.md').open('a', encoding='utf-8') as f:
        f.write('设计已落实为可执行 v0.1.0。\n')
    assert any('project version belongs' in e for e in checker.check_documentation(tmp_path)['issues'])


def test_registered_sources_and_dependency_mirrors_need_attribution(tmp_path):
    fixture(tmp_path)
    write(tmp_path, 'knowledge/sources.json', json.dumps([{'repository': 'org/engine'}]))
    write(tmp_path, 'thirdparty/manifest.json', json.dumps({'dependencies': [
        {'url': 'https://github.com/org/tool.git', 'upstream_url': 'https://github.com/upstream/tool.git',
         'mirrors': {'internal': 'https://git.example/org/tool.git'}}]}))
    errors = checker.check_documentation(tmp_path)['issues']
    assert sum('registered source not linked' in e for e in errors) == 4
    write(tmp_path, 'THIRD_PARTY_NOTICES.md',
          '[Engine](https://github.com/org/engine)\n[Tool](https://github.com/org/tool)\n'
          '[Upstream](https://github.com/upstream/tool)\n[Mirror](https://git.example/org/tool)\n')
    with (tmp_path/'README.md').open('a', encoding='utf-8') as f:
        f.write('[Notices](THIRD_PARTY_NOTICES.md)\n')
    assert checker.check_documentation(tmp_path)['status'] == 'current'
