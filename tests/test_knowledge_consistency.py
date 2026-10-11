"""Offline release checks distinguish current dependency coverage from history."""
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest
import yaml


spec = importlib.util.spec_from_file_location(
    'knowledge_validator', Path(__file__).resolve().parents[1] / 'scripts/validate_knowledge.py'
)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)

OLD = 'a' * 40
CURRENT = 'b' * 40
OLD_HASH = hashlib.sha256(b'old implementation').hexdigest()
CURRENT_HASH = hashlib.sha256(b'current implementation').hexdigest()


def write_json(root, name, value):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding='utf-8')


def edit_json(root, name, edit):
    value = json.loads((root / name).read_text(encoding='utf-8'))
    edit(value)
    write_json(root, name, value)


def page(root, name, meta, body='# Topic'):
    if meta.get('kind') in {'source-map', 'source-document', 'source-pr'}:
        meta['generated_body_sha256'] = hashlib.sha256(body.strip().encode()).hexdigest()
        meta.setdefault('runtime_validated', False)
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('---\n' + yaml.safe_dump(meta) + '---\n\n' + body + '\n', encoding='utf-8')


def source_ref(commit, sha):
    return {'source': 'tool', 'commit': commit, 'path': 'kernel.py', 'sha256': sha}


@pytest.fixture
def project(tmp_path):
    write_json(tmp_path, 'knowledge/sources.json', [{
        'id': 'tool', 'repository': 'org/tool', 'ref': 'main',
        'paths': ['kernel.py'], 'baseline_commit': CURRENT,
        'baseline_files': {'kernel.py': {'sha256': CURRENT_HASH}},
    }])
    write_json(tmp_path, 'knowledge/source-lock.json', {'files': [
        {'repo': 'org/tool', 'commit': commit, 'path': 'kernel.py', 'sha256': sha}
        for commit, sha in [(OLD, OLD_HASH), (CURRENT, CURRENT_HASH)]
    ]})
    write_json(tmp_path, 'knowledge/maintenance.json', [{
        'source': 'tool', 'paths': ['kernel.py'], 'targets': ['knowledge/current.md'],
    }])
    write_json(tmp_path, 'thirdparty/manifest.json', {
        'dependencies': [{'id': 'runtime', 'url': 'https://github.com/org/tool.git',
                          'ref': 'main', 'commit': CURRENT}],
        'dependency_sources': [{'dependency': 'runtime', 'source': 'tool',
                                'current_pages': ['knowledge/current.md']}],
    })
    page(tmp_path, 'knowledge/current.md', {'id': 'current', 'sources': [source_ref(CURRENT, CURRENT_HASH)]})
    page(tmp_path, 'knowledge/historical.md', {'id': 'historical', 'sources': [source_ref(OLD, OLD_HASH)]})
    page(tmp_path, 'knowledge/source-maps/tool.md', {'id': 'map', 'kind': 'source-map'},
         f'# Directory\n\nCommit `{CURRENT}` · ref `main`.')
    write_json(tmp_path, 'knowledge/catalog/repositories/tool.json', {
        'source': 'tool', 'repository': 'org/tool', 'ref': 'main', 'commit': CURRENT, 'entries': {},
    })
    return tmp_path


def errors(project):
    return validator.validate(project)['errors']


def test_current_coverage_allows_intentionally_pinned_history(project):
    assert errors(project) == []


def test_dependency_drift_cannot_pass_with_internally_consistent_old_wiki(project):
    edit_json(project, 'thirdparty/manifest.json', lambda v: v['dependencies'][0].update(commit='c' * 40))
    result = errors(project)
    assert any('Wiki baseline differs' in e for e in result)
    assert any('current page cites a different commit' in e for e in result)
    assert any('current source inventory differs' in e for e in result)


def test_current_page_drift_is_detected_even_after_baseline_and_inventory_advance(project):
    page(project, 'knowledge/current.md', {'id': 'current', 'sources': [source_ref(OLD, OLD_HASH)]})
    assert any('current page cites a different commit' in e for e in errors(project))


def test_baseline_hash_is_checked_without_a_page_citing_that_file(project):
    page(project, 'knowledge/current.md', {'id': 'current', 'sources': []})
    edit_json(project, 'knowledge/source-lock.json', lambda v: v['files'][1].update(sha256=OLD_HASH))
    assert any('baseline source missing/hash mismatch' in e for e in errors(project))


def test_binding_cannot_attach_an_unrelated_repository(project):
    edit_json(project, 'thirdparty/manifest.json', lambda v: v['dependencies'][0].update(url='https://github.com/other/tool.git'))
    assert any('repository mismatch' in e for e in errors(project))


def test_equal_commit_can_be_referenced_by_a_release_tag(project):
    edit_json(project, 'thirdparty/manifest.json', lambda v: v['dependencies'][0].update(ref='v1.0'))
    assert errors(project) == []


@pytest.mark.parametrize('binding', [
    {'dependency': 'missing', 'source': 'tool', 'current_pages': ['knowledge/current.md']},
    {'dependency': 'runtime', 'source': 'missing', 'current_pages': ['knowledge/current.md']},
    {'dependency': 'runtime', 'source': 'tool', 'current_pages': []},
    {'dependency': 'runtime', 'source': 'tool', 'current_pages': ['knowledge/source-maps/tool.md']},
])
def test_binding_requires_real_dependency_source_and_authored_coverage(project, binding):
    edit_json(project, 'thirdparty/manifest.json', lambda v: v.update(dependency_sources=[binding]))
    assert errors(project)


def test_a_valid_generated_body_hash_does_not_hide_stale_map_commit(project):
    page(project, 'knowledge/source-maps/tool.md', {'id': 'map', 'kind': 'source-map'},
         f'# Directory\n\nCommit `{OLD}` · ref `main`.')
    assert any('source map/catalog commit mismatch' in e for e in errors(project))


def document(project, commit=OLD, sha=OLD_HASH):
    page(project, 'knowledge/upstream-docs/tool/readme.md', {
        'id': 'doc', 'kind': 'source-document', 'repository': 'org/tool',
        'path': 'README.md', 'commit': commit, 'raw_sha256': sha,
    }, '# Upstream\n\n[Upstream relative link](not-copied.md)')
    write_json(project, 'knowledge/catalog/document-ledgers/tool.json', {
        'commit': CURRENT, 'historical_paths': [],
        'records': {'README.md': {'commit': OLD, 'sha256': OLD_HASH,
                                 'page': 'knowledge/upstream-docs/tool/readme.md'}},
    })


def test_unchanged_old_document_and_upstream_relative_links_remain_valid(project):
    document(project)
    assert errors(project) == []


def test_generated_document_metadata_cannot_disagree_with_its_ledger(project):
    document(project, commit=CURRENT)
    assert any('document page/ledger identity or hash mismatch' in e for e in errors(project))


def test_inventory_is_not_runtime_validation_but_a_measured_site_may_be(project):
    page(project, 'knowledge/site.md', {'id': 'site', 'kind': 'site-knowledge', 'runtime_validated': True})
    assert errors(project) == []
    page(project, 'knowledge/source-maps/tool.md', {'id': 'map', 'kind': 'source-map', 'runtime_validated': True},
         f'# Directory\n\nCommit `{CURRENT}` · ref `main`.')
    assert any('cannot claim runtime validation' in e for e in errors(project))


def test_broken_authored_pr_link_is_detected(project):
    page(project, 'knowledge/historical.md', {'id': 'historical'},
         '# Case\n\n[PR evidence](prs/no-such-pr.md)\n\n```text\n[example](nonexistent.md)\n```')
    result = errors(project)
    assert len(result) == 1 and 'broken local knowledge link' in result[0]


def test_authored_links_use_exact_case_on_case_insensitive_hosts_too(project):
    page(project, 'knowledge/CaseSensitive.md', {'id': 'case-target'})
    page(project, 'knowledge/historical.md', {'id': 'historical'}, '[target](casesensitive.md)')
    assert any('local knowledge link' in e for e in errors(project))
    page(project, 'knowledge/historical.md', {'id': 'historical'}, '[target](CaseSensitive.md)')
    assert errors(project) == []


def test_matching_artifact_hash_does_not_hide_wrong_pr_identity(project):
    artifact = {'repository': 'other/tool', 'number': 12}
    name = 'knowledge/evidence/prs/org--tool/12.json'
    write_json(project, name, artifact)
    page(project, 'knowledge/prs/org--tool/PR-12.md', {
        'id': 'pr-org--tool-12', 'kind': 'source-pr', 'repository': 'org/tool',
        'pr_number': 12, 'artifact_path': name,
        'artifact_sha256': hashlib.sha256((project / name).read_bytes()).hexdigest(),
    })
    assert any('PR evidence identity mismatch' in e for e in errors(project))


def test_pr_reference_must_identify_a_pr_source_not_an_authored_page(project):
    page(project, 'knowledge/historical.md', {'id': 'historical', 'pr_sources': ['current']})
    assert any('missing related PR source current' in e for e in errors(project))
