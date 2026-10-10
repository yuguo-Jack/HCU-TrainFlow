import pytest

from hcu_trainflow import chat_guidance, flow
from hcu_trainflow.core import FlowError, Store


def test_chat_guidance_requires_disposition_preserves_human_files_and_deduplicates(tmp_path):
    store = Store(tmp_path)
    store.create({'schema_version': 1, 'task_id': 't', 'mode': 'analyze',
                  'objective': 'Fixture', 'context': {'model': 'fixture'}})
    flow.start(store, 't', {'acceptance': {'result': 'Retained analysis'}})
    path = flow.board_paths(store, 't')[2]
    original = path.read_bytes()
    value = {'text': 'Continue the profile analysis; keep the historical gap open.',
             'source': 'chat:fixture-message-1', 'author': 'human-user'}
    row = chat_guidance.record(store, 't', value)
    assert row['new'] == 1 and path.read_bytes() == original
    assert flow.next_step(store, 't')['action'] == 'human'
    flow.acknowledge(store, 't', row['guidance'], 'applied', 'Continue only the analysis scope.')
    assert flow.next_step(store, 't')['action'] == 'work'
    assert chat_guidance.record(Store(tmp_path), 't', value)['new'] == 0
    assert flow.sync_guidance(store, 't', force=True)['new'] == 0
    assert path.read_bytes() == original
    with store.db() as db:
        assert db.execute('SELECT count(*) FROM operations').fetchone()[0] == 0
    for invalid in ({}, {**value, 'text': ''}, {**value, 'authorized': True}):
        with pytest.raises(FlowError):
            chat_guidance.record(store, 't', invalid)
