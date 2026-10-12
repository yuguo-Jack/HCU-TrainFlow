"""Exercise actual CLI decisions against installed Skill entrypoints."""
import json
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

from hcu_trainflow import flow
from hcu_trainflow.cli import main
from hcu_trainflow.core import Store
from hcu_trainflow.skill_registry import WORKFLOW_SKILLS, WIKI_UPDATE_SKILL
from test_flow import setup, candidate, verdict

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope='module')
def installed_skills(tmp_path_factory):
    target = tmp_path_factory.mktemp('routing-install')/'skills'
    subprocess.run([sys.executable, str(ROOT/'scripts/install_skills.py'),
                    '--workflow-only', '--target', str(target)], check=True, capture_output=True)
    return target


def cli_decision(store, capsys):
    assert main(['--workspace', str(store.root), 'flow-next', 't']) == 0
    return json.loads(capsys.readouterr().out)


def assert_installed(decision, expected, installed):
    assert decision['skill'] == expected
    path = installed/decision['skill']/'SKILL.md'
    assert path.is_file(), f'CLI selected a Skill the installer does not provide: {path}'
    frontmatter = yaml.safe_load(path.read_text(encoding='utf-8').split('---', 2)[1])
    assert frontmatter['name'] == decision['skill']
    binding = json.loads((path.parent/'workspace.json').read_text(encoding='utf-8'))
    assert Path(binding['project_root']) == ROOT


def test_installed_menu_matches_english_skill_ids(installed_skills):
    assert sorted(p.name for p in installed_skills.iterdir() if p.is_dir()) == sorted(WORKFLOW_SKILLS)
    for name in WORKFLOW_SKILLS:
        entry = installed_skills/name
        metadata = yaml.safe_load((entry/'agents/openai.yaml').read_text(encoding='utf-8'))['interface']
        frontmatter = yaml.safe_load((entry/'SKILL.md').read_text(encoding='utf-8').split('---', 2)[1])
        assert metadata['display_name'] == frontmatter['name'] == name
        assert '$' + name in metadata['default_prompt']
        assert name.isascii()


def test_knowledge_reminders_resume_without_changing_acceptance(tmp_path, installed_skills, capsys):
    store = setup(tmp_path, mode='analyze')
    initial = cli_decision(store, capsys)
    followup = initial['knowledge_followup']
    assert followup['phase'] == 'task-start'
    assert followup['task_mode'] == 'analyze'
    assert followup['skill'] == WIKI_UPDATE_SKILL
    assert (installed_skills/followup['skill']/'SKILL.md').is_file()
    assert followup['blocking'] is False and followup['automatic_execution'] is False
    assert flow.next_step(Store(store.root), 't')['knowledge_followup'] == followup
    # No maintenance report or response is required to advance actual task evidence.
    flow.submit(store, 't', candidate(store))
    flow.review(store, 't', verdict(store))
    result = flow.advance(store, 't')
    assert result['action'] == 'completed'
    assert result['knowledge_followup']['phase'] == 'task-completion'
    assert result['knowledge_followup']['task_mode'] == 'analyze'
    assert result['knowledge_followup']['disposition_key'] != followup['disposition_key']
    assert flow.next_step(Store(store.root), 't')['knowledge_followup'] == result['knowledge_followup']
    assert 'skill' not in result  # Completion remains terminal, not a new training stage.


def test_iteration_does_not_repeat_initial_wiki_check(tmp_path):
    store = setup(tmp_path, mode='optimize')
    flow.submit(store, 't', candidate(store, target='iterate', experiment=True))
    flow.review(store, 't', verdict(store))
    result = flow.advance(store, 't')
    assert result['action'] == 'work'
    assert 'knowledge_followup' not in result


def test_cancelled_task_has_no_success_curation_prompt(tmp_path):
    store = setup(tmp_path)
    store.transition('t', 'cancelled', reason='User ended this task')
    result = flow.next_step(store, 't')
    assert result['action'] == 'cancelled'
    assert 'knowledge_followup' not in result


@pytest.mark.parametrize('mode,expected', [
    ('environment', 'hcu-train-check-and-adapt'),
    ('adapt', 'hcu-train-check-and-adapt'),
    ('analyze', 'hcu-train-analyze-and-optimize'),
    ('optimize', 'hcu-train-analyze-and-optimize'),
    ('diagnose', 'hcu-train-scale-and-stability'),
    ('operate', 'hcu-train-scale-and-stability'),
])
def test_standalone_cli_routes_to_installed_skill(tmp_path, mode, expected, installed_skills, capsys):
    store = setup(tmp_path, mode=mode)
    decision = cli_decision(store, capsys)
    assert decision['action'] == 'work'
    assert_installed(decision, expected, installed_skills)


def test_complete_pipeline_routes_each_real_transition(tmp_path, installed_skills, capsys):
    store = setup(tmp_path, mode='full')
    routes = [
        ('environment_checked', 'hcu-train-check-and-adapt'),
        ('baseline_validated', 'hcu-train-check-and-adapt'),
        ('profiling', 'hcu-train-analyze-and-optimize'),
        ('optimizing', 'hcu-train-analyze-and-optimize'),
        ('scale_ready', 'hcu-train-analyze-and-optimize'),
        ('training', 'hcu-train-scale-and-stability'),
        ('completed', 'hcu-train-scale-and-stability'),
    ]
    for destination, expected in routes:
        decision = cli_decision(store, capsys)
        assert decision['target'] == destination
        assert_installed(decision, expected, installed_skills)
        if destination == 'profiling':
            assert decision['action'] == 'advance' and decision['review_reused'] is True
        else:
            value = candidate(store, experiment=destination == 'scale_ready')
            flow.submit(store, 't', value)
            flow.review(store, 't', verdict(store))
        advanced = flow.advance(store, 't')
        expected_phase = {'environment_checked': 'environment-milestone',
                          'scale_ready': 'optimization-milestone',
                          'completed': 'task-completion'}.get(destination)
        if expected_phase:
            assert advanced['knowledge_followup']['phase'] == expected_phase
        else:
            assert 'knowledge_followup' not in advanced
    finished = cli_decision(store, capsys)
    assert finished['action'] == 'completed'
    assert 'skill' not in finished


def test_repair_after_replaced_report_keeps_dispatch_information(tmp_path, installed_skills, capsys):
    store = setup(tmp_path)
    value = candidate(store)
    flow.submit(store, 't', value)
    flow.review(store, 't', verdict(store))
    report = flow.artifact_json(store, value['reports']['analysis'])
    store.report('t', 'analysis', {**report, 'note': 'Revised attribution requires review'})
    decision = cli_decision(store, capsys)
    assert decision['action'] == 'repair'
    assert_installed(decision, 'hcu-train-analyze-and-optimize', installed_skills)
