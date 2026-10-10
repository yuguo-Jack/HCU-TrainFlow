import hashlib
import json
from pathlib import Path

import pytest

from hcu_trainflow.core import Store
from hcu_trainflow.knowledge_evidence import validate_manifests
from hcu_trainflow.wiki import index_wiki, read_page, search_wiki


def fixture_manifest(tmp_path):
    site = tmp_path / 'repo/knowledge/sites/example'
    site.mkdir(parents=True)
    raw = b'actual evidence\n'
    (site / 'proof.txt').write_bytes(raw)
    sha = hashlib.sha256(raw).hexdigest()
    row = {'path': 'proof.txt', 'sha256': sha, 'bytes': len(raw),
           'source': 'original-task/proof.txt', 'representation': 'verbatim', 'source_sha256': sha}
    manifest = site / 'manifest.json'
    manifest.write_text(json.dumps({'schema_version': 1, 'files': [row]}))
    return tmp_path / 'repo', site, manifest, row


def test_changed_and_missing_evidence_fail(tmp_path):
    root, site, _, _ = fixture_manifest(tmp_path)
    assert not validate_manifests(root)
    (site / 'proof.txt').write_text('edited conclusion')
    assert 'hash mismatch' in str(validate_manifests(root))
    (site / 'proof.txt').unlink()
    assert 'missing' in str(validate_manifests(root))


@pytest.mark.parametrize('name', ['../outside.txt', '/outside.txt', 'C:/outside.txt', r'..\outside.txt'])
def test_external_paths_rejected(tmp_path, name):
    root, _, manifest, row = fixture_manifest(tmp_path)
    row['path'] = name
    manifest.write_text(json.dumps({'schema_version': 1, 'files': [row]}))
    assert validate_manifests(root)


def test_invalid_manifest_and_duplicate_declaration_rejected(tmp_path):
    root, _, manifest, row = fixture_manifest(tmp_path)
    for value in ([], {'schema_version': 1, 'files': [row, row]}, {'schema_version': 1, 'files': []}):
        manifest.write_text(json.dumps(value))
        assert validate_manifests(root)


def _symlink(link, target, directory=False):
    try:
        link.symlink_to(target, target_is_directory=directory)
    except OSError as exc:
        pytest.skip(f'Symlink privilege unavailable: {exc}')


def test_relative_project_rejects_linked_evidence(tmp_path, monkeypatch):
    root, site, _, _ = fixture_manifest(tmp_path)
    original = site / 'original.txt'
    (site / 'proof.txt').rename(original)
    _symlink(site / 'proof.txt', original)
    monkeypatch.chdir(tmp_path)
    assert 'symlink' in str(validate_manifests(Path('repo')))


def test_external_site_directory_link_rejected(tmp_path):
    root, site, _, _ = fixture_manifest(tmp_path)
    external = tmp_path / 'old-workspace'
    site.rename(external)
    _symlink(site, external, directory=True)
    assert 'linked manifest/site' in str(validate_manifests(root))


def test_fresh_task_reads_repo_site_without_original_store(tmp_path):
    root, site, _, _ = fixture_manifest(tmp_path)
    (site / 'README.md').write_text('''---
id: sites/example
title: RCCL RoCE site measurements
engine: cross-engine
kind: site-knowledge
stages: [adapt, optimize, fault-tolerance]
---
# RCCL communication
NCCL_ROCE_SRC_PORT_LIST results require actual topology; [proof](proof.txt).
''')
    store = Store(tmp_path / 'brand-new-task')
    indexed = index_wiki(store, root)
    found = search_wiki(store, 'NCCL_ROCE_SRC_PORT_LIST', kind='site-knowledge', index=indexed)
    assert [x['id'] for x in found['results']] == ['sites/example']
    page = read_page(store, found['results'][0]['id'], indexed['generation'])
    assert 'proof.txt' in page['body']
    assert Path(page['path']).parent.joinpath('proof.txt').read_text() == 'actual evidence\n'
    assert not validate_manifests(root)
