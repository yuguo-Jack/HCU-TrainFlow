import importlib.util
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('ci_scope', ROOT / 'scripts/ci_scope.py')
ci = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci)


@pytest.mark.parametrize('paths', [
    ['knowledge/projects/engine/knowledgebase/local/topics/checkpoints.md'],
    ['knowledge/coverage.json', 'docs/wiki.md', 'README.md'],
    ['skills/hcu-trainflow-wiki-search/SKILL.md'],
])
def test_known_prose_and_knowledge_changes_use_meaningful_reduced_lane(paths):
    result = ci.classify(paths)
    assert not result['full'] and any(result[key] for key in ['knowledge', 'docs', 'skills'])
    assert result['data_tests'] and all((ROOT / path).is_file() for path in result['data_tests'])


@pytest.mark.parametrize('path', [
    'src/hcu_trainflow/wiki.py', 'scripts/validate_knowledge.py', 'tests/test_monitor_wiki.py',
    'knowledge/storage.json', 'pyproject.toml', 'thirdparty/manifest.json', 'AGENTS.md',
    '.github/workflows/test.yml', 'unknown.txt', 'skills/example/scripts/query.py',
    '../outside.md', 'docs/../../escape.md', '/absolute.md', 'knowledge\\bad.md',
])
def test_software_schema_and_unknown_changes_always_run_full_matrix(path):
    assert ci.classify([path])['full']
    assert ci.classify(['docs/wiki.md', path])['full']


def test_missing_history_or_unreadable_git_diff_falls_back_to_full():
    assert ci.classify([])['full']
    assert ci.changed_paths(ROOT, '0' * 40, 'a' * 40) is None
    assert ci.changed_paths(ROOT, '--anything', 'a' * 40) is None
    failed = lambda *a, **kw: SimpleNamespace(returncode=1)
    assert ci.changed_paths(ROOT, 'a' * 40, 'b' * 40, run=failed) is None
    result = ci.changed_paths(ROOT, 'a' * 40, 'b' * 40,
        run=lambda *a, **kw: SimpleNamespace(returncode=0, stdout=b'docs/wiki.md\0knowledge/page.md\0'))
    assert result == ['docs/wiki.md', 'knowledge/page.md']


def test_workflow_always_reports_summary_and_keeps_full_software_matrix():
    workflow = yaml.load((ROOT / '.github/workflows/test.yml').read_text(encoding='utf-8'), Loader=yaml.BaseLoader)
    assert set(workflow['on']) == {'push', 'pull_request'}
    jobs = workflow['jobs']
    assert jobs['summary']['if'] == 'always()'
    assert set(jobs['summary']['needs']) == {'scope', 'verify', 'tests'}
    assert jobs['tests']['strategy']['matrix'] == {'os': ['ubuntu-latest', 'windows-latest'], 'python': ['3.10', '3.12']}
    assert jobs['tests']['if'] == "needs.scope.outputs.full == 'true'"
    assert any('validate_knowledge.py' in step.get('run', '') for step in jobs['verify']['steps'])
    for job, depth in [('scope', '2'), ('verify', '1'), ('tests', '1')]:
        checkout = next(step for step in jobs[job]['steps'] if step.get('uses', '').startswith('actions/checkout@'))
        assert checkout['with']['fetch-depth'] == depth
