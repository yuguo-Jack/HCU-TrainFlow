import importlib.util
import json
from pathlib import Path

spec = importlib.util.spec_from_file_location('wiki_coverage_check', Path(__file__).parents[1] / 'scripts/check_wiki_coverage.py')
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


def fixture(tmp_path):
    kb = tmp_path / 'knowledge'
    kb.mkdir()
    (kb / 'engine.md').write_text('# Engine\n\nAuthored explanation.\n', encoding='utf-8')
    (kb / 'sources.json').write_text(json.dumps([{'id': 'upstream'}]), encoding='utf-8')
    row = {'id': 'engine', 'role': 'engine', 'sources': ['upstream'], 'entry': 'knowledge/engine.md',
           'dimensions': {d: ['knowledge/engine.md'] for d in check.DIMENSIONS},
           'mechanisms': [{'topic': topic, 'page': 'knowledge/engine.md'} for topic in ['sharding', 'recovery']],
           'limits': 'Not GPU validated'}
    return row


def save(tmp_path, row):
    (tmp_path / 'knowledge/coverage.json').write_text(json.dumps({'projects': [row]}), encoding='utf-8')


def test_new_source_requires_authored_route(tmp_path):
    row = fixture(tmp_path)
    save(tmp_path, row)
    assert check.validate_coverage(tmp_path) == []
    (tmp_path / 'knowledge/sources.json').write_text(json.dumps([{'id': 'upstream'}, {'id': 'new-engine'}]))
    assert any('new-engine' in x for x in check.validate_coverage(tmp_path))


def test_missing_dimension_and_generated_page_cannot_pass(tmp_path):
    row = fixture(tmp_path)
    del row['dimensions']['call_chain']
    generated = tmp_path / 'knowledge/projects/example/knowledgebase/upstream/source-map/upstream.md'
    generated.parent.mkdir(parents=True)
    generated.write_text('# File listing')
    row['entry'] = 'knowledge/projects/example/knowledgebase/upstream/source-map/upstream.md'
    save(tmp_path, row)
    errors = check.validate_coverage(tmp_path)
    assert any('call_chain' in x for x in errors)
    assert any('generated' in x for x in errors)


def test_external_and_missing_pages_rejected(tmp_path):
    row = fixture(tmp_path)
    outside = tmp_path / 'outside.md'
    outside.write_text('not knowledge')
    row['dimensions']['scope'] = ['knowledge/../outside.md', 'knowledge/missing.md']
    save(tmp_path, row)
    assert len([x for x in check.validate_coverage(tmp_path) if 'invalid knowledge page' in x]) == 2


def test_parent_gitlink_cannot_silently_follow_child_head(tmp_path):
    row = fixture(tmp_path)
    row['sources'] += ['child']
    save(tmp_path, row)
    kb = tmp_path / 'knowledge'
    pinned = 'a' * 40
    registry = [{'id': 'upstream'}, {'id': 'child', 'ref': pinned, 'baseline_commit': pinned,
                 'parent_gitlink': {'source': 'upstream', 'path': 'third_party/child'}}]
    (kb / 'sources.json').write_text(json.dumps(registry))
    catalog = kb / 'catalog/repositories/upstream.json'
    catalog.parent.mkdir(parents=True)
    catalog.write_text(json.dumps({'entries': {'third_party/child': {'type': 'commit', 'sha': pinned}}}))
    assert check.validate_coverage(tmp_path) == []
    catalog.write_text(json.dumps({'entries': {'third_party/child': {'type': 'commit', 'sha': 'b' * 40}}}))
    assert any('parent gitlink changed' in x for x in check.validate_coverage(tmp_path))
