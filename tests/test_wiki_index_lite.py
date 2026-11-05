import json
import os
from pathlib import Path
import sqlite3
import subprocess
from concurrent.futures import ThreadPoolExecutor

import pytest

from hcu_trainflow import wiki, wiki_index, source_evidence
from hcu_trainflow.core import FlowError, Store, digest, write_json


def page(root, name, identity, body, **meta):
    import yaml
    path = root / 'knowledge' / name
    path.parent.mkdir(parents=True, exist_ok=True)
    # Production generated_page/atomic_write writes exact UTF-8 bytes. Avoid
    # platform text-newline conversion before Git's independent clean filter.
    path.write_bytes(('---\n' + yaml.safe_dump({'id': identity, 'title': identity, **meta}, allow_unicode=True)
                      + '---\n\n' + body + '\n').encode('utf-8'))
    return path


def project(tmp_path):
    root = tmp_path / 'project'
    write_json(root / 'knowledge/storage.json', {'profile': 'discovery-first', 'index_layout': 'shared-v1'})
    return root, Store(tmp_path / 'state')


def test_shared_versions_noop_and_old_generation_reads(tmp_path):
    root, store = project(tmp_path)
    p = page(root, 'a.md', 'stable', '通信 overlap oldbody', engine='old', stages=['adapt'])
    first = wiki.index_wiki(store, root)
    original = p.read_bytes()
    again = wiki.index_wiki(store, root)
    assert again['unchanged'] and again['pages_parsed'] == 0
    assert again['created_at'] == first['created_at']
    page(root, 'a.md', 'stable', '通信 overlap newbody', engine='new', stages=['optimize'])
    second = wiki.index_wiki(store, root)
    assert second['generation'] != first['generation'] and second['pages_parsed'] == 1
    historic = wiki.read_page(store, 'stable', first['generation'])
    assert 'oldbody' in historic['body']
    assert Path(historic['path']).read_bytes() == original
    assert digest(original) == historic['sha256']
    assert 'newbody' in wiki.read_page(store, 'stable', second['generation'])['body']
    assert wiki.search_wiki(store, '通信', engine='old', index=first)['results'][0]['id'] == 'stable'
    assert not wiki.search_wiki(store, '通信', engine='old', index=second)['results']
    with sqlite3.connect(second['path']) as db:
        assert db.execute('SELECT count(*) FROM versions').fetchone()[0] == 2
        assert db.execute('SELECT count(*) FROM generations').fetchone()[0] == 2
    assert {p.name for p in (store.root / 'wiki').glob('*.sqlite3')} == {'build-lock.sqlite3', 'shared.sqlite3'}


def test_failed_build_never_switches_active_or_indexes_private_data(tmp_path):
    root, store = project(tmp_path)
    page(root, 'a.md', 'one', 'public evidence')
    page(root, 'private.md', 'private', 'hidden_secret', visibility='private')
    active = wiki.index_wiki(store, root)
    assert active['pages'] == 1 and not wiki.search_wiki(store, 'hidden_secret')['results']
    page(root, 'duplicate.md', 'one', 'duplicate')
    with pytest.raises(FlowError, match='Duplicate'):
        wiki.index_wiki(store, root)
    assert json.loads((store.root / 'wiki/active.json').read_text())['generation'] == active['generation']
    with sqlite3.connect(active['path']) as db:
        assert db.execute('SELECT count(*) FROM versions').fetchone()[0] == 1


def test_input_drift_does_not_publish_and_concurrent_noops_share_one_database(tmp_path, monkeypatch):
    root, store = project(tmp_path)
    page(root, 'a.md', 'one', 'stable')
    first = wiki.index_wiki(store, root)
    with ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(lambda _: wiki.index_wiki(store, root), range(3)))
    assert all(x['unchanged'] and x['generation'] == first['generation'] for x in results)
    original = wiki_index._paths
    calls = []
    def paths(base):
        calls.append(1)
        if len(calls) == 2:
            page(root, 'added.md', 'added', 'drifting input')
        return original(base)
    monkeypatch.setattr(wiki_index, '_paths', paths)
    with pytest.raises(FlowError, match='changed during indexing'):
        wiki.index_wiki(store, root)
    assert json.loads((store.root / 'wiki/active.json').read_text())['generation'] == first['generation']


def test_retired_original_and_legacy_generation_restore_exact_git_bytes(tmp_path):
    root = tmp_path / 'project'
    store = Store(tmp_path / 'state')
    relative = 'knowledge/projects/repo/knowledgebase/upstream/prs/Org--Repo/PR-7.md'
    p = page(root, relative.removeprefix('knowledge/'), 'pr-org--repo-7', 'original PR body', kind='source-pr')
    raw = p.read_bytes()
    write_json(root / 'knowledge/sources.json', [{'id': 'repo', 'repository': 'Org/Repo', 'knowledge_project': 'repo'}])
    for args in [['init'], ['-c', 'core.autocrlf=true', 'add', '.'], ['-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-m', 'baseline']]:
        subprocess.run(['git', *args], cwd=root, check=True, capture_output=True)
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
    legacy = wiki.index_wiki(store, root)
    p.unlink()
    write_json(root / 'knowledge/storage.json', {'profile': 'discovery-first', 'index_layout': 'shared-v1', 'legacy_git': {'commit': commit}})
    shared = wiki.index_wiki(store, root)
    old = wiki.read_page(store, 'pr-org--repo-7', legacy['generation'])
    current = wiki.read_page(store, 'pr-org--repo-7', shared['generation'])
    for value in [old, current]:
        assert value['body'] == 'original PR body'
        assert Path(value['path']).read_bytes() == raw
        assert value['sha256'] == digest(raw) and value['review_state'] == 'archived-fixed-source'
    assert source_evidence.read_bytes(root, relative, digest(raw)) == raw
    with pytest.raises(FlowError, match='SHA-256'):
        source_evidence.read_bytes(root, relative, '0' * 64)
    with pytest.raises(FlowError):
        source_evidence.read_bytes(root, '../outside.json')


def test_restored_mtime_same_size_edit_cannot_reuse_stale_body(tmp_path):
    root, store = project(tmp_path)
    p = page(root, 'a.md', 'one', 'oldalpha')
    first = wiki.index_wiki(store, root)
    stat = p.stat()
    p.write_bytes(p.read_bytes().replace(b'oldalpha', b'newomega'))
    os.utime(p, ns=(stat.st_atime_ns, stat.st_mtime_ns))
    second = wiki.index_wiki(store, root)
    assert second['generation'] != first['generation'] and second['pages_parsed'] == 1
    assert wiki.search_wiki(store, 'newomega')['results'][0]['id'] == 'one'
    assert not wiki.search_wiki(store, 'oldalpha')['results']


def test_legacy_body_survives_unavailable_original_revision(tmp_path):
    root = tmp_path / 'project'
    store = Store(tmp_path / 'state')
    name = 'projects/repo/knowledgebase/upstream/prs/Org--Repo/PR-7.md'
    p = page(root, name, 'pr-org--repo-7', 'uncommitted body A', kind='source-pr')
    first = wiki.index_wiki(store, root)
    page(root, name, 'pr-org--repo-7', 'committed body B', kind='source-pr')
    for args in [['init'], ['add', '.'], ['-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-m', 'baseline B']]:
        subprocess.run(['git', *args], cwd=root, check=True, capture_output=True)
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
    p.unlink()
    write_json(root / 'knowledge/storage.json', {'profile': 'discovery-first', 'index_layout': 'shared-v1', 'legacy_git': {'commit': commit}})
    value = wiki.read_page(store, 'pr-org--repo-7', first['generation'])
    assert value['body'] == 'uncommitted body A'
    assert value['original_available'] is False and value['path'] is None
    assert Path(value['snapshot_view_path']).read_text(encoding='utf-8') == value['body']
    assert value['review_state'] == 'indexed-history; original-unavailable'
    annotated = Path(value['snapshot_view_path'])
    annotated.write_text('user annotation', encoding='utf-8')
    again = wiki.read_page(store, 'pr-org--repo-7', first['generation'])
    assert annotated.read_text(encoding='utf-8') == 'user annotation'
    assert Path(again['snapshot_view_path']).read_text(encoding='utf-8') == 'uncommitted body A'


def test_transient_changed_payload_cannot_be_cached_under_another_hash(tmp_path, monkeypatch):
    root, store = project(tmp_path)
    p = page(root, 'a.md', 'one', 'baseline')
    first = wiki.index_wiki(store, root)
    page(root, 'a.md', 'one', 'observed alpha')
    original = Path.read_bytes
    calls = []
    def read(path):
        raw = original(path)
        if path == p:
            calls.append(1)
            if len(calls) == 2:
                return raw.replace(b'alpha', b'omega')
        return raw
    monkeypatch.setattr(Path, 'read_bytes', read)
    with pytest.raises(FlowError, match='changed during indexing'):
        wiki.index_wiki(store, root)
    assert json.loads((store.root / 'wiki/active.json').read_text())['generation'] == first['generation']
