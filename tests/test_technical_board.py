"""Synthetic board protocol tests; these do not qualify any training run."""
import json

import pytest

from hcu_trainflow import flow, technical_board
from hcu_trainflow.core import FlowError, Store


@pytest.fixture
def store(tmp_path):
    result = Store(tmp_path / 'workspace')
    result.create({'schema_version': 1, 'task_id': 't', 'mode': 'analyze',
                   'objective': 'Synthetic technical board fixture', 'context': {'model': 'fixture'}})
    flow.start(result, 't', {'acceptance': {'result': 'Retained analysis'}})
    return result


def status(**extra):
    return {'summary': '正在核对技术证据。', 'progress': [], 'next': [],
            'needs_human': [], 'evidence': [], **extra}


def section(label='Test expectation', **extra):
    return {'summary': label, 'scope': 'Synthetic fixture; no GPU run',
            'qualification': 'not-measured', 'columns': ['检查', '预期 / 结果'],
            'rows': [{'cells': ['collective', '尚未执行'], 'qualification': 'not-measured', 'evidence': []}],
            'notes': ['缺口：仍需真实设备证据。'], 'evidence': [], **extra}


def body(store):
    with store.db() as db:
        return json.loads(db.execute('SELECT payload FROM flow_status WHERE task=?', ('t',)).fetchone()[0])


def board(store):
    return flow.board_paths(store, 't')[1].read_text(encoding='utf8')


def test_persistent_sections_survive_terse_update_and_replace_or_delete_independently(store):
    flow.status_update(store, 't', status(technical={'environment': section(), 'operators': section('Shape bounds')}))
    reopened = Store(store.root)
    result = flow.status_update(reopened, 't', status(summary='短更新仍保留技术细节。'))
    retained = json.loads(reopened.artifact(result['status_artifact']))
    assert retained == body(reopened)
    assert set(retained['technical']) == {'environment', 'operators'}
    assert 'Shape bounds' in board(reopened)
    replacement = section('New environment expectation')
    flow.status_update(reopened, 't', status(technical={'environment': replacement}))
    assert body(reopened)['technical']['environment'] == replacement
    assert 'Shape bounds' in board(reopened)
    flow.status_update(reopened, 't', status(technical={'environment': None}))
    assert set(body(reopened)['technical']) == {'operators'}
    flow.status_update(reopened, 't', status(technical={'operators': None}))
    assert body(reopened)['technical'] == {} and '## 技术详情' not in board(reopened)


def test_all_sections_and_rows_visible_with_scope_and_evidence_without_gate_changes(store):
    proof = store.put(b'Synthetic local test evidence; not hardware validation')
    rows = [{'cells': [f'operator {n}', f'shape {n}; efficiency not measured'],
             'qualification': 'not-measured', 'evidence': []} for n in range(12)]
    rows[0] = {'cells': ['source mapping', 'fixture dispatch'], 'qualification': 'source-only', 'evidence': [proof]}
    rows[1] = {'cells': ['protocol check', 'fixture assertion'], 'qualification': 'local-tested', 'evidence': [proof]}
    rows[2] = {'cells': ['synthetic timing', 'fixture only'], 'qualification': 'measured', 'evidence': [proof]}
    before = flow.next_step(store, 't')
    flow.status_update(store, 't', status(technical={name: section(rows=rows) for name in technical_board.SECTIONS}))
    output = board(store)
    for title in technical_board.SECTIONS.values():
        assert title in output
    for n in range(3, 12):
        assert f'operator {n}' in output
    assert output.count('Synthetic fixture; no GPU run') == 8
    assert all(label in output for label in technical_board.QUALIFICATIONS.values())
    assert f'../../objects/{proof[:2]}/{proof}' in output
    after = flow.next_step(store, 't')
    assert (after['state'], after['action']) == (before['state'], before['action'])
    with pytest.raises(FlowError):
        store.transition('t', 'completed')


def test_context_round_trip_does_not_resurrect_technical_sections(store):
    old = store.task('t')
    flow.status_update(store, 't', status(technical={'analysis': section('Old analysis conclusions')}))
    store.change_context('t', {'model': 'changed'})
    flow.render_board(store, 't')
    assert 'Old analysis conclusions' not in board(store)
    store.change_context('t', old['spec']['context'])
    assert store.task('t')['context'] == old['context']
    with pytest.raises(FlowError, match='context/context_epoch'):
        flow.status_update(store, 't', status(context=old['context'], context_epoch=old['context_epoch']))
    flow.status_update(store, 't', status())
    assert not body(store).get('technical')
    assert 'Old analysis conclusions' not in board(store)


def test_scope_pair_and_current_scoped_update(store):
    task = store.task('t')
    for extra in ({'context': task['context']}, {'context_epoch': task['context_epoch']},
                  {'context': task['context'], 'context_epoch': False}):
        with pytest.raises(FlowError, match='context/context_epoch'):
            flow.status_update(store, 't', status(**extra))
    flow.status_update(store, 't', status(context=task['context'], context_epoch=task['context_epoch'],
                                        technical={'review': section()}))
    assert 'review' in body(store)['technical']


@pytest.mark.parametrize('change', [
    {'summary': ''}, {'scope': []}, {'qualification': 'passed'}, {'qualification': 'measured'},
    {'qualification': 'source-only'}, {'qualification': 'local-tested'}, {'columns': []},
    {'columns': ['same', 'same']}, {'columns': [1]}, {'columns': ['one\ntwo']},
    {'columns': ['x'] * 11}, {'rows': [{}]}, {'rows': 'table'}, {'notes': [None]},
    {'notes': ['x'] * 21}, {'evidence': ['missing']}, {'evidence': ['0' * 64]},
    {'evidence': [{}]}, {'evidence': ['0' * 64] * 65}, {'summary': 'x\x00'},
    {'scope': 'x' * 2001}, {'extra': True},
    {'rows': [{'cells': ['one'], 'qualification': 'not-measured', 'evidence': []}]},
    {'rows': [{'cells': ['one', 2], 'qualification': 'not-measured', 'evidence': []}]},
    {'rows': [{'cells': ['one', 'two'], 'qualification': 'measured', 'evidence': []}]},
    {'rows': [{'cells': ['one', 'two'], 'qualification': 'not-measured', 'evidence': [None]}]},
])
def test_invalid_technical_fields_do_not_replace_status(store, change):
    flow.status_update(store, 't', status(technical={'analysis': section()}))
    previous, output = body(store), board(store)
    with pytest.raises(FlowError):
        flow.status_update(store, 't', status(technical={'analysis': section(**change)}))
    assert body(store) == previous and board(store) == output


@pytest.mark.parametrize('patch', [[], {'unknown': None}, {'analysis': {}}, {'analysis': False}])
def test_invalid_section_container(store, patch):
    with pytest.raises(FlowError):
        flow.status_update(store, 't', status(technical=patch))


def test_row_evidence_can_inherit_verified_section_source(store):
    proof = store.put(b'Synthetic source-only fixture')
    item = section(qualification='source-only', evidence=[proof])
    item['rows'][0]['qualification'] = 'source-only'
    flow.status_update(store, 't', status(technical={'analysis': item}))
    assert '见栏目证据' in board(store)


def test_corrupt_evidence_cannot_qualify_a_section(store):
    flow.status_update(store, 't', status())
    previous = body(store)
    proof = store.put(b'Synthetic source fixture')
    (store.root / 'objects' / proof[:2] / proof).write_bytes(b'corrupted')
    with pytest.raises(FlowError, match='Artifact hash mismatch'):
        flow.status_update(store, 't', status(technical={
            'analysis': section(qualification='source-only', evidence=[proof])}))
    assert body(store) == previous


def test_size_limits_reject_rather_than_silently_truncate(store):
    item = section()
    item['rows'] *= 101
    with pytest.raises(FlowError, match='100 rows'):
        flow.status_update(store, 't', status(technical={'operators': item}))
    row = {'cells': ['项目', '数' * 900], 'qualification': 'not-measured', 'evidence': []}
    item = section(rows=[row] * 70)
    flow.status_update(store, 't', status(technical={'operators': item}))
    with pytest.raises(FlowError, match='256 KiB'):
        flow.status_update(store, 't', status(technical={'experiments': item}))
    assert set(body(store)['technical']) == {'operators'}


def test_markdown_is_literal_and_preserves_human_files(store):
    _, _, guidance = flow.board_paths(store, 't')
    questions = guidance.parent / 'QUESTIONS.md'
    guidance.write_text('# Human original\nKeep this exactly.\n', encoding='utf8')
    questions.write_text('## Q1：人的问题\nOriginal question.\n', encoding='utf8')
    original = (guidance.read_bytes(), questions.read_bytes())
    unsafe = '<img src=x onerror=alert(1)> [run](javascript:alert(1)) ![x](https://bad.invalid/a) | `code` \\ *text*'
    item = section(summary=unsafe, scope=unsafe, columns=['A | B', '[column]'], notes=[unsafe])
    item['rows'][0]['cells'] = [unsafe, 'line 1\n## injected heading\n| injected | row |']
    flow.status_update(store, 't', status(summary=unsafe[:240], progress=[unsafe[:200]], technical={'analysis': item}))
    output = board(store)
    assert '<img' not in output and '[run](javascript:' not in output
    assert '![x](https:' not in output and '\n## injected heading' not in output
    assert '&lt;img' in output and 'A &#124; B' in output and '<br>' in output
    assert (guidance.read_bytes(), questions.read_bytes()) == original


def test_concurrent_update_is_rejected_without_losing_another_section(store, monkeypatch):
    original = flow.retain
    invoked = False

    def interleaved(s, value):
        nonlocal invoked
        if not invoked:
            invoked = True
            flow.status_update(s, 't', status(technical={'environment': section('Concurrent writer')}))
        return original(s, value)

    monkeypatch.setattr(flow, 'retain', interleaved)
    with pytest.raises(FlowError, match='Status changed while merging'):
        flow.status_update(store, 't', status(technical={'operators': section()}))
    assert set(body(store)['technical']) == {'environment'}
    assert 'Concurrent writer' in board(store)


def test_context_change_during_write_rejects_status(store, monkeypatch):
    original = flow.retain

    def reset(s, value):
        s.change_context('t', {'model': 'new'})
        return original(s, value)

    monkeypatch.setattr(flow, 'retain', reset)
    with pytest.raises(FlowError, match='Start/reconcile'):
        flow.status_update(store, 't', status(technical={'operators': section()}))


def test_cli_guidance_retains_actual_text_and_provenance_without_approval(store, tmp_path, capsys):
    from hcu_trainflow.cli import main
    path = tmp_path / 'guidance.json'
    value = {'text': 'Please explain the measured gap.', 'source': 'chat:fixture-1', 'author': 'human-user'}
    path.write_text(json.dumps(value), encoding='utf8')
    args = ['--workspace', str(store.root), 'flow-guidance-record', 't', str(path)]
    human = flow.board_paths(store, 't')[2]
    before = human.read_bytes()
    assert main(args) == 0
    result = json.loads(capsys.readouterr().out)
    retained = json.loads(store.artifact(result['guidance']))
    assert all(retained[key] == val for key, val in value.items())
    assert main(args) == 0
    assert json.loads(capsys.readouterr().out)['new'] == 0
    assert flow.next_step(store, 't')['action'] == 'human'
    assert human.read_bytes() == before
    with store.db() as db:
        assert db.execute('SELECT count(*) FROM operations').fetchone()[0] == 0
