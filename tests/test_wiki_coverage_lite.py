import importlib.util
import json
from pathlib import Path


spec = importlib.util.spec_from_file_location('wiki_coverage_lite_check', Path(__file__).parents[1] / 'scripts/check_wiki_coverage.py')
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


def fixture(tmp_path):
    knowledge = tmp_path / 'knowledge'
    knowledge.mkdir()
    sources = [{'id': 'upstream', 'repository': 'owner/engine', 'ref': 'main', 'baseline_commit': 'a' * 40}]
    projects = [{'id': 'engine', 'role': 'engine', 'sources': ['upstream'], 'limits': 'Discovery route; no new runtime validation.'}]
    return sources, projects


def save(tmp_path, sources, projects):
    (tmp_path / 'knowledge/sources.json').write_text(json.dumps(sources), encoding='utf-8')
    (tmp_path / 'knowledge/coverage.json').write_text(json.dumps({'schema': 2, 'profile': 'discovery-first', 'projects': projects}), encoding='utf-8')


def test_discovery_source_needs_no_authored_report_or_mechanism_quota(tmp_path):
    sources, projects = fixture(tmp_path)
    save(tmp_path, sources, projects)
    assert check.validate_coverage(tmp_path) == []


def test_existing_authored_links_still_reject_missing_or_generated_pages(tmp_path):
    sources, projects = fixture(tmp_path)
    generated = tmp_path / 'knowledge/projects/example/knowledgebase/upstream/source-map/source.md'
    generated.parent.mkdir(parents=True)
    generated.write_text('# Generated inventory', encoding='utf-8')
    projects[0]['entry'] = 'knowledge/missing.md'
    projects[0]['related_pages'] = [generated.relative_to(tmp_path).as_posix()]
    save(tmp_path, sources, projects)
    errors = check.validate_coverage(tmp_path)
    assert any('invalid knowledge page' in error for error in errors)
    assert any('generated sources' in error for error in errors)


def test_light_registry_keeps_role_assignment_route_and_pin_checks(tmp_path):
    sources, projects = fixture(tmp_path)
    sources[0].update(repository='', baseline_commit='latest')
    sources.append({'id': 'unrouted', 'repository': 'owner/other'})
    projects[0]['role'] = 'invented'
    projects.append(dict(projects[0], id='duplicate-assignment'))
    save(tmp_path, sources, projects)
    errors = check.validate_coverage(tmp_path)
    assert any('invalid role' in error for error in errors)
    assert any('source assigned to multiple' in error for error in errors)
    assert any('source route' in error for error in errors)
    assert any('baseline commit' in error for error in errors)
    assert any('unrouted' in error for error in errors)


def test_parent_gitlink_check_remains_strict_in_discovery_profile(tmp_path):
    sources, projects = fixture(tmp_path)
    sources.append({'id': 'child', 'repository': 'owner/child', 'ref': 'b' * 40, 'baseline_commit': 'b' * 40,
                    'parent_gitlink': {'source': 'upstream', 'path': 'third_party/child'}})
    projects[0]['sources'].append('child')
    inventory = tmp_path / 'knowledge/catalog/repositories/upstream.json'
    inventory.parent.mkdir(parents=True)
    inventory.write_text(json.dumps({'entries': {'third_party/child': {'type': 'commit', 'sha': 'b' * 40}}}), encoding='utf-8')
    save(tmp_path, sources, projects)
    assert check.validate_coverage(tmp_path) == []
    sources[1]['ref'] = sources[1]['baseline_commit'] = 'c' * 40
    save(tmp_path, sources, projects)
    assert any('parent gitlink changed' in error for error in check.validate_coverage(tmp_path))


def test_web_discovery_route_must_be_https_and_credential_free(tmp_path):
    sources, projects = fixture(tmp_path)
    sources[0] = {'id': 'upstream', 'kind': 'web', 'repository': 'https://docs.example.org/engine/'}
    save(tmp_path, sources, projects)
    assert check.validate_coverage(tmp_path) == []
    sources[0]['repository'] = 'https://user:password@docs.example.org/engine/'
    save(tmp_path, sources, projects)
    assert any('official HTTPS source route' in error for error in check.validate_coverage(tmp_path))
