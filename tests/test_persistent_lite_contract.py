"""The installed maintenance route must not silently fall back to main/legacy."""
import json
from pathlib import Path
import re
import shlex


ROOT = Path(__file__).resolve().parents[1]


def test_storage_declares_persistent_branch_without_freezing_future_source_updates():
    settings = json.loads((ROOT/'knowledge/storage.json').read_text(encoding='utf-8'))
    assert settings['profile'] == 'discovery-first'
    assert settings['maintenance_branch'] == 'lite'
    assert 'source_facts_refreshed' not in settings
    assert 'historical_limits' not in settings
    snapshot = settings['refactor_snapshot']
    assert re.fullmatch(r'\d{4}-\d{2}-\d{2}', snapshot['observed_on'])
    assert re.fullmatch(r'[0-9a-f]{40}', snapshot['completed_commit'])
    assert snapshot['source_facts_refreshed'] is False
    assert settings['legacy_git']['commit'] == '0f2e883b101fc1cebf627d9203b03068827a6a5a'


def test_new_install_instructions_explicitly_select_lite_without_full_history():
    for name in ['README.md', 'docs/quickstart.md', 'docs/integrations.md']:
        text = (ROOT/name).read_text(encoding='utf-8')
        clones = re.findall(r'git clone [^\n`]*https://github\.com/yuguo-Jack/HCU-TrainFlow\.git', text)
        assert clones, name
        for command in clones:
            args = shlex.split(command)
            assert args[args.index('--branch')+1] == 'lite'
            assert '--single-branch' in args
            assert args[args.index('--depth')+1] == '1'


def test_knowledge_dependency_tracks_lite_with_an_exact_commit_and_independent_origin():
    manifest = json.loads((ROOT/'thirdparty/manifest.json').read_text(encoding='utf-8'))
    knowledge = next(row for row in manifest['dependencies'] if row['id'] == 'hcu-knowledge')
    assert knowledge['ref'] == 'lite'
    assert re.fullmatch(r'[0-9a-f]{40}', knowledge['commit'])
    assert knowledge['url'] == 'https://github.com/yuguo-Jack/HCU-Knowledge.git'
    assert knowledge['optional'] is False and knowledge['lfs'] is True
