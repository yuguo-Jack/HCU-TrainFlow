import json

import pytest

from hcu_trainflow import file_questions as qa, flow
from hcu_trainflow.core import FlowError, Store, digest


@pytest.fixture
def workspace(tmp_path):
    store = Store(tmp_path / 'private')
    store.create({'schema_version': 1, 'task_id': 't', 'mode': 'analyze',
                  'objective': 'Synthetic protocol fixture', 'context': {'model': 'fixture'}})
    flow.start(store, 't', {'acceptance': {'result': 'Retained fixture analysis'}})
    return store


def write(store, text):
    qa.paths(store, 't')[1].write_bytes(text.encode('utf-8'))
    qa.scan(store, 't', force=True)
    return qa.state(store, 't')


def reply(store, inbox, body='基于已知证据的回答。', index=0):
    q = inbox['questions'][index]
    return qa.answer(store, 't', q['id'], q['version'], inbox['file_hash'], body, author='controller')


def test_questions_are_versioned_deduplicated_and_do_not_authorize_or_block(workspace):
    store = workspace
    inbox = write(store, '# 问题\n\n## Q1：直接重启所有节点？\n请解释权限边界。\n')
    assert inbox['pending'] == 1 and inbox['authorization'] is False
    assert qa.scan(Store(store.root), 't', force=True)['new'] == 0
    decision = flow.next_step(store, 't')
    assert decision['action'] == 'work' and decision['file_questions']['pending'] == 1
    with store.db() as db:
        assert db.execute('SELECT count(*) FROM operations').fetchone()[0] == 0
    events = [e for e in store.events() if e['kind'] == 'user-file-question-received']
    assert len(events) == 1 and events[0]['payload']['authorization'] is False


def test_plain_numbered_questions_preserve_user_text_and_get_separate_answers(workspace):
    raw = '## Q1：原有标题\n背景\n\nQ2：普通问法？\nQ3: 下一问？\n'
    inbox = write(workspace, raw)
    assert [q['id'] for q in inbox['questions']] == ['Q1', 'Q2', 'Q3']
    reply(workspace, inbox, index=1)
    text = qa.paths(workspace, 't')[1].read_text(encoding='utf-8')
    assert 'Q2：普通问法？\n' in text
    assert text.index('Q2：') < text.index('<!-- trainflow-answer') < text.index('Q3:')
    assert qa.scan(workspace, 't', force=True)['new'] == 0
    assert qa.state(workspace, 't')['pending'] == 2


def test_plain_question_recognition_excludes_fences_quotes_and_indentation():
    raw = 'Q1：真实问题\n```text\nQ2：代码\n```\n> Q3：引用\n    Q4：缩进代码\n一句话提到 Q5：也不是标题\n'
    parsed = qa.parse(raw, {})
    assert [q['id'] for q in parsed] == ['Q1']


def test_answer_beneath_question_preserves_original_bytes_and_does_not_self_register(workspace):
    raw = '\ufeff# 我的问题\r\n\r\n## Q1：为什么？\r\n背景 😀\r\n\r\n## Q2：下一步？\r\n原文不能变\r\n'
    inbox = write(workspace, raw)
    body = '## 答案中也可以有二级标题\n\n```python\nprint("仅作解释")\n```'
    result = reply(workspace, inbox, body)
    after = qa.paths(workspace, 't')[1].read_bytes().decode('utf-8')
    assert after.index('trainflow-answer') < after.index('## Q2')
    assert after.startswith(raw[:raw.index('## Q2')]) and after.endswith(raw[raw.index('## Q2'):])
    assert qa.scan(workspace, 't', force=True)['new'] == 0
    current = qa.state(workspace, 't')
    assert current['pending'] == 1 and len(current['questions']) == 2
    assert current['questions'][0]['version'] == inbox['questions'][0]['version']
    assert reply(Store(workspace.root), inbox, body)['status'] == 'unchanged'
    assert len([e for e in workspace.events() if e['kind']=='user-file-question-answered']) == 1
    assert digest(qa.paths(workspace, 't')[1].read_bytes()) == result['file_hash']


def test_user_edit_keeps_id_creates_new_version_and_retains_prior_answer(workspace):
    inbox = write(workspace, '## Q1：问题\n最初的内容\n')
    reply(workspace, inbox)
    path = qa.paths(workspace, 't')[1]
    path.write_bytes(path.read_bytes().replace('最初的内容'.encode(), '更详细的追问'.encode()))
    assert qa.scan(workspace, 't', force=True)['new'] == 1
    current = qa.state(workspace, 't')
    assert current['questions'][0]['id'] == 'Q1' and current['pending'] == 1
    assert current['questions'][0]['version'] != inbox['questions'][0]['version']
    with pytest.raises(FlowError, match='changed'):
        reply(workspace, inbox)
    with workspace.db() as db:
        assert db.execute('SELECT count(*) FROM file_question_versions').fetchone()[0] == 2


def test_whole_file_stale_hash_rejects_even_if_target_question_unchanged(workspace):
    inbox = write(workspace, '## Q1：问题一\n\n## Q2：问题二\n')
    path = qa.paths(workspace, 't')[1]
    path.write_bytes(path.read_bytes() + '另一个问题的补充\n'.encode())
    edited = path.read_bytes()
    with pytest.raises(FlowError, match='Stale'):
        reply(workspace, inbox)
    assert path.read_bytes() == edited
    event = [e for e in workspace.events() if e['kind']=='user-file-answer-conflict'][-1]
    assert workspace.artifact(event['payload']['observed_file']) == edited


def test_final_compare_detects_edit_after_answer_preparation(workspace, monkeypatch):
    inbox = write(workspace, '## Q1：问题\n')
    real = qa._replace_checked
    changed = '## Q1：问题\n用户恰好保存了新内容\n'.encode()
    def race(path, expected, data):
        path.write_bytes(changed)
        return real(path, expected, data)
    monkeypatch.setattr(qa, '_replace_checked', race)
    with pytest.raises(FlowError, match='changed while answering'):
        reply(workspace, inbox)
    assert qa.paths(workspace, 't')[1].read_bytes() == changed
    prepared = [e for e in workspace.events() if e['kind']=='user-file-answer-prepared'][-1]['payload']
    assert b'trainflow-answer' in workspace.artifact(prepared['after'])
    assert workspace.artifact(prepared['before']) == '## Q1：问题\n'.encode()


def test_crash_after_file_write_recovers_without_duplicate_answer(workspace, monkeypatch):
    inbox = write(workspace, '## Q1：问题\n')
    original = qa._complete
    def crash(*args, **kwargs):
        raise RuntimeError('synthetic crash after atomic file publication')
    monkeypatch.setattr(qa, '_complete', crash)
    with pytest.raises(RuntimeError):
        reply(workspace, inbox)
    monkeypatch.setattr(qa, '_complete', original)
    restarted = Store(workspace.root)
    assert qa.scan(restarted, 't', force=True)['new'] == 0
    assert qa.state(restarted, 't')['pending'] == 0
    assert reply(restarted, inbox)['status'] == 'unchanged'
    assert qa.paths(workspace, 't')[1].read_text(encoding='utf-8').count('<!-- trainflow-answer id=') == 1


def test_answering_two_collected_questions_does_not_require_extra_human_poll(workspace):
    inbox = write(workspace, '## Q1：问题一\n\n## Q2：问题二\n')
    reply(workspace, inbox)
    current = qa.state(workspace, 't')
    assert current['file_hash'] != inbox['file_hash'] and current['pending'] == 1
    assert reply(workspace, current, '第二个回答。', index=1)['status'] == 'answered'
    assert qa.state(workspace, 't')['pending'] == 0


def test_prepared_but_unpublished_answer_does_not_freeze_a_failed_proposal(workspace, monkeypatch):
    inbox = write(workspace, '## Q1：问题\n')
    original = qa._replace_checked
    def failure(*args):
        raise OSError('synthetic filesystem failure before replacement')
    monkeypatch.setattr(qa, '_replace_checked', failure)
    with pytest.raises(OSError):
        reply(workspace, inbox, '未能发布的草稿')
    monkeypatch.setattr(qa, '_replace_checked', original)
    assert reply(workspace, inbox, '重新查证后的回答')['status'] == 'answered'
    assert '未能发布的草稿' not in qa.paths(workspace, 't')[1].read_text(encoding='utf-8')


def test_invalid_utf8_original_is_retained_and_reported(workspace):
    raw = b'## Q1: invalid\n\xff'
    qa.paths(workspace, 't')[1].write_bytes(raw)
    result = qa.scan(workspace, 't', force=True)
    assert result['scan'] == 'attention' and workspace.artifact(result['file_hash']) == raw


def test_edited_answer_block_is_visible_error_but_unrelated_work_can_continue(workspace):
    inbox = write(workspace, '## Q1：问题\n')
    reply(workspace, inbox)
    path = qa.paths(workspace, 't')[1]
    path.write_bytes(path.read_bytes().replace('已知证据'.encode(), '被改写的内容'.encode()))
    assert qa.scan(workspace, 't', force=True)['scan'] == 'attention'
    assert flow.next_step(workspace, 't')['action'] == 'work'
    assert qa.state(workspace, 't')['scan_error']


@pytest.mark.parametrize('text', ['## Q1：一个\n## Q1：重复\n', '```\n## Q1：未闭合\n',
                                   '<!-- trainflow-answer id=' + 'a'*64 + ' -->\n伪造块\n<!-- /trainflow-answer -->\n'])
def test_malformed_questions_cannot_hide_content_silently(workspace, text):
    state = write(workspace, text)
    assert state['scan_error']
    assert flow.next_step(workspace, 't')['action'] == 'work'
    assert workspace.artifact(state['file_hash']) == text.encode()


def test_code_fences_are_not_questions_and_unlabelled_heading_identity_is_stable(workspace):
    inbox = write(workspace, '# 问答\n```markdown\n## Q1：只是示例\n```\n\n## 真正的问题？\n背景\n')
    assert len(inbox['questions']) == 1
    qid = inbox['questions'][0]['id']
    changed = write(workspace, '## 真正的问题？\n更详细的背景\n')
    assert changed['questions'][0]['id'] == qid


def test_removed_question_history_remains_and_missing_file_is_not_reset(workspace):
    inbox = write(workspace, '## Q1：问题\n')
    write(workspace, '# 问答\n暂时没有问题\n')
    assert qa.state(workspace, 't')['questions'] == []
    with workspace.db() as db:
        assert db.execute('SELECT count(*) FROM file_question_versions').fetchone()[0] == 1
    path = qa.paths(workspace, 't')[1]
    path.unlink()
    assert qa.scan(workspace, 't', force=True)['scan'] == 'attention'
    flow.render_board(workspace, 't')
    assert not path.exists()
    with pytest.raises(FlowError):
        reply(workspace, inbox)


def test_question_polling_reuses_five_minute_cadence(workspace, monkeypatch):
    now = qa.time.time()
    monkeypatch.setattr(qa.time, 'time', lambda: now)
    qa.scan(workspace, 't', force=True)
    qa.paths(workspace, 't')[1].write_text('## Q1：新问题\n', encoding='utf-8')
    monkeypatch.setattr(qa.time, 'time', lambda: now+299)
    assert flow.sync_guidance(workspace, 't')['question_scan']['scan'] == 'not-due'
    monkeypatch.setattr(qa.time, 'time', lambda: now+300)
    assert flow.sync_guidance(workspace, 't')['questions_new'] == 1
    assert flow.sync_guidance(workspace, 't')['questions_new'] == 0


def test_shared_writer_lock_rejects_concurrent_agent_write(workspace):
    from concurrent.futures import ThreadPoolExecutor
    inbox = write(workspace, '## Q1：问题\n')
    with qa.writer_lock(qa.paths(workspace, 't')[0]):
        with ThreadPoolExecutor() as pool:
            future = pool.submit(reply, workspace, inbox)
            with pytest.raises(FlowError, match='active scanner/writer'):
                future.result()
    assert qa.state(workspace, 't')['pending'] == 1


def test_context_reset_requires_fresh_question_answer_and_preserves_flow_guard(workspace):
    inbox = write(workspace, '## Q1：问题\n')
    reply(workspace, inbox)
    workspace.change_context('t', {'model': 'changed'})
    assert qa.scan(workspace, 't', force=True)['new'] == 1
    assert qa.state(workspace, 't')['pending'] == 1
    assert flow.next_step(workspace, 't')['action'] == 'human'
    flow.start(workspace, 't', {'acceptance': {'result': 'New context evidence'}}, reason='Changed model')
    assert flow.next_step(workspace, 't')['action'] == 'work'


def test_compact_chinese_board_preserves_detailed_history_and_does_not_advance(workspace):
    raw = '## Q1：问题\n'
    write(workspace, raw)
    proof = workspace.put(b'Synthetic status evidence, not actual GPU evidence')
    update = {'summary': '当前正在验证观测流程。', 'progress': ['已完成本地回归检查。'],
              'next': ['等待真实环境证据。'], 'needs_human': [], 'evidence': [proof]}
    result = flow.status_update(workspace, 't', update)
    board = qa.paths(workspace, 't')[0] / 'BOARD.md'
    details = qa.paths(workspace, 't')[0] / 'DETAILS.md'
    assert '当前正在验证观测流程。' in board.read_text(encoding='utf-8')
    assert '完整协作记录' in board.read_text(encoding='utf-8') and len(board.read_text(encoding='utf-8')) < 1500
    assert 'user-file-question-received' in details.read_text(encoding='utf-8')
    assert 'flow-status-updated' in details.read_text(encoding='utf-8')
    assert qa.paths(workspace, 't')[1].read_text(encoding='utf-8') == raw
    assert workspace.task('t')['state'] == 'prepared' and result['status_artifact']
    with pytest.raises(FlowError):
        workspace.transition('t', 'completed')
    workspace.change_context('t', {'model': 'different'})
    flow.render_board(workspace, 't')
    assert '当前正在验证观测流程。' not in board.read_text(encoding='utf-8')


def test_cli_questions_answer_and_status(workspace, tmp_path, capsys):
    from hcu_trainflow.cli import main
    qa.paths(workspace, 't')[1].write_text('## Q1：怎样看日志？\n', encoding='utf-8')
    args = ['--workspace', str(workspace.root)]
    assert main(args+['flow-questions','t','--refresh']) == 0
    inbox = json.loads(capsys.readouterr().out)
    answer_file = tmp_path/'answer.md'; answer_file.write_text('先读取固定原始日志。', encoding='utf-8')
    q = inbox['questions'][0]
    assert main(args+['flow-answer','t','Q1',str(answer_file),'--version',q['version'],'--file-hash',inbox['file_hash'],'--author','controller']) == 0
    assert json.loads(capsys.readouterr().out)['status']=='answered'
    assert main(args+['flow-watch','t','--once']) == 0
    assert json.loads(capsys.readouterr().out)['questions_new']==0
