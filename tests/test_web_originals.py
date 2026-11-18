"""Portable web originals survive task Store loss and fail closed on damage."""
import shutil
from pathlib import Path

import pytest

from hcu_trainflow import cli, official, web_evidence, wiki
from hcu_trainflow.core import FlowError, Store, digest, fingerprint, read_json, write_json


def project(tmp_path):
    root = tmp_path / 'project'
    source = {'id': 'website', 'kind': 'web', 'repository': 'https://docs.nvidia.com/example/',
              'knowledge_project': 'example', 'paths': ['index'],
              'documents': {'index': 'https://docs.nvidia.com/example/index.html'}}
    write_json(root / 'knowledge/storage.json', {'profile': 'discovery-first'})
    write_json(root / 'knowledge/sources.json', [source])
    write_json(root / 'knowledge/source-lock.json', {'files': []})
    return root, Store(tmp_path / 'private')


def stage(store, root, *, body='Fixed official content'):
    source = read_json(root / 'knowledge/sources.json')[0]
    text = body.encode()
    raw = f'<html><body>{body}</body></html>'.encode()
    files = {'index': {'sha256': store.put(text, 'public'), 'raw_sha256': store.put(raw, 'public'),
                       'url': source['documents']['index']}}
    revision = fingerprint({name: {'sha256': row['sha256'], 'url': row['url']} for name, row in files.items()})
    value = wiki.stage_source_refresh(store, root, source, revision, files, [], 'registered-official-pages')
    wiki.review_refresh(store, value['stage_id'], {}, root)
    return value, raw, text


def test_apply_shares_exact_originals_and_cold_cli_needs_neither_store_nor_network(tmp_path, monkeypatch):
    root, store = project(tmp_path)
    value, raw, text = stage(store, root)
    result = official.apply_refresh(store, root, value['stage_id'])
    assert result['website_evidence']['originals'] == 1
    assert not web_evidence.validate(root)
    cold = tmp_path / 'cold'
    shutil.copytree(root, cold)
    monkeypatch.setattr(cli, 'Store', lambda *a: pytest.fail('Shared original reading needs no private Store'))
    monkeypatch.setattr(wiki, '_get_json', lambda *a: pytest.fail('A fixed original must not be fetched again'))
    args = cli.parser().parse_args(['--workspace', str(tmp_path / 'unused'), 'wiki-original', str(cold), 'website', 'index'])
    read = cli.execute(args)
    assert Path(read['local_path']).read_bytes() == raw
    assert read['sha256'] == digest(raw) and read['bytes'] == len(raw)
    assert not read['source_refreshed'] and not (tmp_path / 'unused').exists()
    read = web_evidence.read_original(cold, 'website', 'index', text=True, max_chars=5)
    assert read['content'] == text.decode()[:5] and read['truncated']
    assert Path(read['local_path']).read_bytes() == text


def test_repeated_apply_reuses_objects_and_preserves_old_revision(tmp_path):
    root, store = project(tmp_path)
    first, first_raw, _ = stage(store, root)
    official.apply_refresh(store, root, first['stage_id'])
    snapshot = {p: (p.read_bytes(), p.stat().st_mtime_ns)
                for p in (root / 'knowledge/evidence/web').iterdir()}
    index = root / web_evidence.INDEX
    index_mtime = index.stat().st_mtime_ns
    official.apply_refresh(store, root, first['stage_id'])
    assert snapshot == {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in snapshot}
    assert index.stat().st_mtime_ns == index_mtime
    assert len(web_evidence.originals(root)) == 1
    second, _, _ = stage(store, root, body='New version of official content')
    official.apply_refresh(store, root, second['stage_id'])
    assert len(web_evidence.originals(root)) == 2
    assert len(list((root / 'knowledge/evidence/web').iterdir())) == 4
    read = web_evidence.read_original(root, 'website', 'index', revision=first['commit'])
    assert Path(read['local_path']).read_bytes() == first_raw
    assert web_evidence.read_original(root, 'website', 'index')['revision'] == second['commit']


def test_html_only_changes_preserve_both_originals_without_duplicate_text(tmp_path):
    root, store = project(tmp_path)
    first, raw, text = stage(store, root)
    official.apply_refresh(store, root, first['stage_id'])
    source = read_json(root / 'knowledge/sources.json')[0]
    changed = {name: dict(row) for name, row in first['files'].items()}
    changed['index']['raw_sha256'] = store.put(raw.replace(b'<html>', b'<html lang="en">'), 'public')
    second = wiki.stage_source_refresh(store, root, source, first['commit'], changed, [], 'registered-official-pages')
    wiki.review_refresh(store, second['stage_id'], {}, root)
    official.apply_refresh(store, root, second['stage_id'])
    rows = web_evidence.originals(root)
    assert len(rows) == 2 and {row['revision'] for row in rows} == {first['commit']}
    assert {row['original']['sha256'] for row in rows} == {digest(raw), changed['index']['raw_sha256']}
    assert {row['extracted_text']['sha256'] for row in rows} == {digest(text)}
    assert len(list((root / 'knowledge/evidence/web').iterdir())) == 3
    assert web_evidence.read_original(root, 'website', 'index')['sha256'] == changed['index']['raw_sha256']


@pytest.mark.parametrize('damage', ['missing-private', 'bad-private', 'bad-shared', 'url-change', 'path-change'])
def test_apply_preflights_all_bytes_and_registration_before_advancing_locks(tmp_path, damage):
    root, store = project(tmp_path)
    value, raw, _ = stage(store, root)
    raw_sha = value['files']['index']['raw_sha256']
    if damage == 'missing-private':
        (store.root / 'objects' / raw_sha[:2] / raw_sha).unlink()
    elif damage == 'bad-private':
        (store.root / 'objects' / raw_sha[:2] / raw_sha).write_bytes(b'corrupt')
    elif damage == 'bad-shared':
        target = root / f'knowledge/evidence/web/{raw_sha}.html'
        target.parent.mkdir(parents=True)
        target.write_bytes(b'corrupt')
    else:
        registry = read_json(root / 'knowledge/sources.json')
        if damage == 'url-change':
            registry[0]['documents']['index'] = 'https://docs.nvidia.com/example/moved.html'
        else:
            registry[0]['paths'].append('uncollected')
        write_json(root / 'knowledge/sources.json', registry)
    before = {name: (root / 'knowledge' / name).read_bytes() for name in ('sources.json', 'source-lock.json')}
    with pytest.raises((FlowError, OSError), match='artifact|hash|registration|evidence|cannot find|No such file'):
        official.apply_refresh(store, root, value['stage_id'])
    assert before == {name: (root / 'knowledge' / name).read_bytes() for name in before}
    assert not (root / web_evidence.INDEX).exists()


@pytest.mark.parametrize('damage', ['missing', 'hash', 'bytes', 'unsafe-path'])
def test_read_and_validation_reject_missing_corrupt_or_unsafe_shared_original(tmp_path, damage):
    root, store = project(tmp_path)
    value, _, _ = stage(store, root)
    official.apply_refresh(store, root, value['stage_id'])
    index = read_json(root / web_evidence.INDEX)
    declaration = index['originals'][0]['original']
    target = root / declaration['file']
    if damage == 'missing':
        target.unlink()
    elif damage == 'hash':
        target.write_bytes(b'X' * declaration['bytes'])
    elif damage == 'bytes':
        declaration['bytes'] += 1
        write_json(root / web_evidence.INDEX, index)
    else:
        declaration['file'] = '../outside.html'
        write_json(root / web_evidence.INDEX, index)
    assert web_evidence.validate(root)
    with pytest.raises(FlowError):
        web_evidence.read_original(root, 'website', 'index')


def test_compatible_dated_receipt_is_read_and_adopted_without_rewriting_originals(tmp_path):
    root, store = project(tmp_path)
    value, raw, _ = stage(store, root)
    official.apply_refresh(store, root, value['stage_id'])
    index = root / web_evidence.INDEX
    old = index.with_name('web-originals-20200101.json')
    old.write_bytes(index.read_bytes())
    original_receipt = old.read_bytes()
    index.unlink()
    assert web_evidence.read_original(root, 'website', 'index')['sha256'] == digest(raw)
    web_evidence.migrate_index(root)
    assert old.read_bytes() == original_receipt
    assert len(web_evidence.originals(root)) == 1
    assert not web_evidence.validate(root)


@pytest.mark.parametrize('field', ['missing', 'raw_sha256', 'sha256', 'url'])
def test_validation_checks_current_source_lock_not_just_the_shared_index(tmp_path, field):
    root, store = project(tmp_path)
    value, _, _ = stage(store, root)
    official.apply_refresh(store, root, value['stage_id'])
    lock = read_json(root / 'knowledge/source-lock.json')
    if field == 'missing':
        lock['files'] = []
    else:
        lock['files'][0][field] = 'https://docs.nvidia.com/wrong.html' if field == 'url' else 'f' * 64
    write_json(root / 'knowledge/source-lock.json', lock)
    assert 'lock differs from baseline' in web_evidence.validate(root)[0]


def test_validation_requires_current_bytes_but_preserves_unavailable_legacy_lock_meaning(tmp_path):
    root, store = project(tmp_path)
    value, _, _ = stage(store, root)
    official.apply_refresh(store, root, value['stage_id'])
    lock = read_json(root / 'knowledge/source-lock.json')
    lock['files'].append({'repo': 'https://docs.nvidia.com/example/', 'commit': 'f' * 64,
                         'path': 'old-missing', 'sha256': 'c' * 64, 'status': 'unavailable'})
    write_json(root / 'knowledge/source-lock.json', lock)
    assert not web_evidence.validate(root)
    with pytest.raises(FlowError, match='not shared'):
        web_evidence.read_original(root, 'website', 'old-missing', revision='f' * 64)
    (root / web_evidence.INDEX).unlink()
    assert 'lacks shared fixed bytes' in web_evidence.validate(root)[0]
