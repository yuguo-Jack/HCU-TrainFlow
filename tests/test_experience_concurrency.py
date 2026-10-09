from concurrent.futures import ThreadPoolExecutor
from itertools import count
from pathlib import Path
from threading import Barrier, Event

import pytest

from hcu_trainflow import experience
from hcu_trainflow.core import FlowError, Store, fingerprint, write_json


def training(tmp_path):
    store = Store(tmp_path / 'private')
    store.create({'schema_version': 1, 'task_id': 't', 'mode': 'optimize',
                  'objective': 'measure overlap', 'context': {'model': 'm', 'environment': 'e'}})
    evidence = store.put(b'retained measurement')
    value = {'context': store.task('t')['context'], 'milestone': 'trial',
             'kind': 'optimization', 'summary': 'Overlap measurement',
             'outcome': 'observed', 'evidence': [evidence]}
    return store, value


def test_concurrent_manual_retries_share_one_record(tmp_path, monkeypatch):
    store, value = training(tmp_path)
    ready = Barrier(2)
    timestamps = count()
    original_save = experience.save

    def synchronized_save(*args, **kwargs):
        ready.wait(timeout=10)
        return original_save(*args, **kwargs)

    monkeypatch.setattr(experience, 'utc', lambda: f'2026-10-09T00:00:0{next(timestamps)}Z')
    monkeypatch.setattr(experience, 'save', synchronized_save)
    with ThreadPoolExecutor(max_workers=2) as pool:
        calls = [pool.submit(experience.record, store, 't', dict(value)) for _ in range(2)]
        results = [call.result(timeout=15) for call in calls]
    assert results[0]['id'] == results[1]['id']
    with store.db() as db:
        assert db.execute('SELECT count(*) FROM experiences').fetchone()[0] == 1
        assert db.execute('SELECT count(*) FROM experience_fts').fetchone()[0] == 1
    assert len(list((store.root / 'experience/records').glob('*.json'))) == 1


def test_concurrent_index_publication_keeps_both_records(tmp_path, monkeypatch):
    store, value = training(tmp_path)
    first_snapshot = Event()
    second_finished = Event()
    original_write = experience.atomic_write
    index_path = store.root / 'experience/INDEX.md'

    def delayed_index(path, body):
        if Path(path) == index_path and body.count('](pages/') == 1 and not first_snapshot.is_set():
            first_snapshot.set()
            # A competing save can finish here only if publication is outside its write lock.
            second_finished.wait(timeout=1)
        original_write(path, body)

    def second_save():
        try:
            return experience.record(store, 't', {**value, 'milestone': 'second'})
        finally:
            second_finished.set()

    monkeypatch.setattr(experience, 'atomic_write', delayed_index)
    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(experience.record, store, 't', value)
        assert first_snapshot.wait(timeout=10)
        second = pool.submit(second_save)
        results = [first.result(timeout=15), second.result(timeout=15)]
    index = index_path.read_text(encoding='utf-8')
    assert all(result['id'] in index for result in results)


def test_rebuild_recovers_manual_event_mapping(tmp_path, monkeypatch):
    store, value = training(tmp_path)
    monkeypatch.setattr(experience, 'utc', lambda: '2026-10-09T00:00:00Z')
    original = experience.record(store, 't', value)
    with store.db() as db:
        db.execute('DELETE FROM experience_events')
        db.execute('DELETE FROM experiences')
        db.execute('DELETE FROM experience_fts')
    Path(original['page']).unlink()
    assert experience.rebuild(store)['records'] == 1
    monkeypatch.setattr(experience, 'utc', lambda: '2026-10-10T00:00:00Z')
    assert experience.record(store, 't', value)['id'] == original['id']
    with store.db() as db:
        assert db.execute('SELECT count(*) FROM experiences').fetchone()[0] == 1


def test_rebuild_recovers_automatic_event_mapping(tmp_path):
    store, value = training(tmp_path)
    result = store.report('t', 'performance', {'context': value['context'],
                           'status': 'complete', 'evidence': value['evidence'], 'step_ms': 10})
    assert result['knowledge']['records'] == 1
    with store.db() as db:
        db.execute('DELETE FROM experience_events')
    assert experience.rebuild(store)['records'] == 1
    assert experience.sync(store)['records'] == 0


def test_rebuild_rejects_invalid_context_before_replacing_index(tmp_path):
    store, value = training(tmp_path)
    original = experience.record(store, 't', value)
    invalid = {**experience.get(store, original['id'])['record'],
               'context_spec': {'model': 'different'}}
    write_json(store.root / 'experience/records' / f'{fingerprint(invalid)}.json', invalid)
    index_before = (store.root / 'experience/INDEX.md').read_bytes()
    with pytest.raises(FlowError, match='context'):
        experience.rebuild(store)
    assert experience.get(store, original['id'])['id'] == original['id']
    assert experience.search(store, 'Overlap')['results'][0]['id'] == original['id']
    assert (store.root / 'experience/INDEX.md').read_bytes() == index_before


def test_empty_rebuild_clears_index_and_stale_event_mapping(tmp_path):
    store, value = training(tmp_path)
    original = experience.record(store, 't', value)
    (store.root / 'experience/records' / f'{original["id"]}.json').unlink()
    assert experience.rebuild(store)['records'] == 0
    assert original['id'] not in (store.root / 'experience/INDEX.md').read_text(encoding='utf-8')
    with store.db() as db:
        assert db.execute('SELECT count(*) FROM experience_events').fetchone()[0] == 0


def test_failed_page_publication_retry_keeps_original_record(tmp_path, monkeypatch):
    store, value = training(tmp_path)
    original_write = experience.atomic_write

    def fail_page(path, body):
        if Path(path).parent.name == 'pages':
            raise OSError('simulated page publication failure')
        original_write(path, body)

    monkeypatch.setattr(experience, 'utc', lambda: '2026-10-09T00:00:00Z')
    monkeypatch.setattr(experience, 'atomic_write', fail_page)
    with pytest.raises(OSError, match='publication'):
        experience.record(store, 't', value)
    original_record = next((store.root / 'experience/records').glob('*.json'))
    monkeypatch.setattr(experience, 'atomic_write', original_write)
    monkeypatch.setattr(experience, 'utc', lambda: '2026-10-10T00:00:00Z')
    retry = experience.record(store, 't', value)
    assert retry['id'] == original_record.stem
    assert Path(retry['page']).is_file()
    assert experience.rebuild(store)['records'] == 1


@pytest.mark.parametrize('existing_index', [False, True])
def test_sync_repairs_index_after_page_publication(tmp_path, monkeypatch, existing_index):
    store, value = training(tmp_path)
    index_path = store.root / 'experience/INDEX.md'
    if existing_index:
        index_path.parent.mkdir(parents=True, exist_ok=True)
        index_path.write_text('# Previous empty index\n', encoding='utf-8')
    original_write = experience.atomic_write

    def fail_index(path, body):
        if Path(path) == index_path:
            raise OSError('simulated index publication failure')
        original_write(path, body)

    monkeypatch.setattr(experience, 'atomic_write', fail_index)
    result = store.report('t', 'performance', {'context': value['context'],
                          'status': 'complete', 'evidence': value['evidence'], 'step_ms': 10})
    assert result['knowledge']['status'] == 'pending'
    with store.db() as db:
        ident = db.execute('SELECT id FROM experiences').fetchone()[0]
    assert (store.root / 'experience/pages' / f'{ident}.md').is_file()
    assert not index_path.exists() or ident not in index_path.read_text(encoding='utf-8')

    monkeypatch.setattr(experience, 'atomic_write', original_write)
    retry = experience.sync(store)
    assert retry['status'] == 'complete' and retry['records'] == 0
    assert ident in index_path.read_text(encoding='utf-8')
    with store.db() as db:
        assert db.execute('SELECT count(*) FROM experiences').fetchone()[0] == 1


def test_manual_record_cannot_choose_source_event(tmp_path):
    store, value = training(tmp_path)
    supplied = {**value, 'source_event': 'unrelated-event'}
    saved = experience.record(store, 't', supplied)
    expected_event = 'manual:' + fingerprint(['t', supplied])
    assert experience.get(store, saved['id'])['record']['source_event'] == expected_event
    with store.db() as db:
        db.execute('DELETE FROM experience_events')
    experience.rebuild(store)
    with store.db() as db:
        bindings = dict(db.execute('SELECT event,experience FROM experience_events'))
    assert bindings == {expected_event: saved['id']}
