"""Exercise actual CLI decisions against installed Skill entrypoints."""
import json
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

from hcu_trainflow import flow
from hcu_trainflow.cli import main
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


@pytest.mark.parametrize('mode,expected', [
    ('environment', 'hcu-train-environment-check-and-adapt'),
    ('adapt', 'hcu-train-environment-check-and-adapt'),
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
        ('environment_checked', 'hcu-train-environment-check-and-adapt'),
        ('baseline_validated', 'hcu-train-environment-check-and-adapt'),
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
        flow.advance(store, 't')
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
