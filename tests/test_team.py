"""Protocol fixtures only: no model provider, remote training, or hardware claims."""
from concurrent.futures import ThreadPoolExecutor
import json
import sys
import threading

import pytest

from hcu_trainflow import flow, team
from hcu_trainflow.core import FlowError, Store, utc
from hcu_trainflow.execution import run_command
from hcu_trainflow.coordination import reconcile_operation, dispatch_inbox


@pytest.fixture
def store(tmp_path):
    s = Store(tmp_path / 'workspace')
    s.create({'schema_version': 1, 'task_id': 't', 'mode': 'analyze',
              'objective': 'Analyze independent training evidence',
              'context': {'source': 'fixed'}, 'permissions': ['execute', 'agent-dispatch']})
    flow.start(s, 't', {'acceptance': {'analysis': 'Retain reviewed evidence'}})
    return s


def spec(s, aid, **changes):
    return {'id': aid, 'owner': aid + '-owner', 'goal': 'Analyze ' + aid,
            'scope': 'Read fixed fixture evidence', 'allowed_paths': ['evidence'],
            'acceptance': 'Return supported findings and limitations', 'mode': 'read',
            'budget': {'max_operations': 4, 'max_seconds': 60},
            'context': s.task('t')['context'], **changes}


def plan(s, *specs, limit=3):
    return team.plan(s, 't', {'rationale': 'Independent evidence lanes before integration',
                             'max_parallel': limit, 'assignments': list(specs)})


def artifact(s, value):
    return s.put(json.dumps(value).encode())


def finish(s, claim):
    proof = s.put(b'Synthetic evidence, not a GPU validation')
    report = artifact(s, {'context': s.task('t')['context'], 'inputs': claim['inputs'],
                         'summary': 'Analysis tied to retained fixture', 'evidence': [proof]})
    team.finish(s, claim['id'], claim['owner'], report, claim['token'])
    return report


def accept(s, aid, report, **changes):
    return team.review(s, aid, {'report': report, 'reviewer': 'controller', 'verdict': 'accept',
                                'note': 'Checked raw evidence and scope', 'evidence': [report], **changes})


def msg(s, mid='q', sender='a', recipient='b', **changes):
    return {'id': mid, 'sender': sender, 'recipient': recipient,
            'owner': sender + '-owner' if sender != 'controller' else 'controller',
            'kind': 'question', 'body': 'Confirm the measurement denominator',
            'context': s.task('t')['context'], 'evidence': [], **changes}


def receipt(s, **changes):
    return {'decision': 'handled', 'note': 'Checked and applied answer',
            'evidence': [s.put(b'Checked fixture evidence')], **changes}


def test_dependency_waits_for_acceptance_and_binds_exact_inputs(store):
    decision = plan(store, spec(store, 'a'), spec(store, 'b'), spec(store, 'join', depends_on=['a', 'b']))
    assert decision['dispatchable'] == ['a', 'b']
    assert flow.next_step(store, 't')['action'] == 'coordinate'
    a = team.claim(store, 'a', 'a-owner'); b = team.claim(store, 'b', 'b-owner')
    assert not a['launched']
    team.bind(store, 'a', 'a-owner', a['token'], 'native-session-a')
    with pytest.raises(FlowError, match='already bound'):
        team.bind(store, 'b', 'b-owner', b['token'], 'native-session-a')
    ra = finish(store, a); rb = finish(store, b)
    assert team.schedule(store, 't')['awaiting_acceptance'] == ['a', 'b']
    with pytest.raises(FlowError, match='dependency-not-accepted'):
        team.claim(store, 'join', 'join-owner')
    with pytest.raises(FlowError, match='own result'):
        accept(store, 'a', ra, reviewer='a-owner')
    accept(store, 'a', ra); accept(store, 'b', rb)
    joined = team.claim(store, 'join', 'join-owner')
    assert joined['inputs'] == {'a': ra, 'b': rb}
    wrong = artifact(store, {'context': joined['context'], 'inputs': {}, 'summary': 'wrong', 'evidence': [ra]})
    with pytest.raises(FlowError, match='exact accepted input'):
        team.finish(store, 'join', 'join-owner', wrong, joined['token'])
    accept(store, 'join', finish(store, joined))
    assert flow.next_step(store, 't')['action'] == 'work'
    board = flow.render_board(store, 't')
    from pathlib import Path
    assert 'native-session-a' in Path(board['details']).read_text(encoding='utf8')
    assert '(DETAILS.md)' in Path(board['board']).read_text(encoding='utf8')
    assert Path(board['board']).parent / 'DETAILS.md' == Path(board['details'])


@pytest.mark.parametrize('changes', [
    {'depends_on': ['missing']}, {'peers': ['missing']}, {'depends_on': ['a']},
    {'allowed_paths': ['../escape']}, {'allowed_paths': ['C:/source']},
    {'budget': {'max_seconds': float('nan')}}, {'required': False, 'mode': 'write'},
    {'allowed_paths': ['src/*']}, {'context': 'outdated'}])
def test_invalid_plan_is_atomic(store, changes):
    with pytest.raises(FlowError):
        plan(store, spec(store, 'a', **changes), spec(store, 'b'))
    assert team.schedule(store, 't')['assignments'] == []


def test_cycles_duplicate_and_cross_task_peer_rejected(store):
    with pytest.raises(FlowError, match='Cyclic'):
        plan(store, spec(store, 'a', depends_on=['b']), spec(store, 'b', depends_on=['a']))
    with pytest.raises(FlowError, match='Duplicate'):
        plan(store, spec(store, 'a'), spec(store, 'a'))
    plan(store, spec(store, 'a'))
    with pytest.raises(FlowError, match='immutable'):
        plan(store, spec(store, 'a'))
    store.create({'schema_version': 1, 'task_id': 'other', 'mode': 'analyze', 'objective': 'Other', 'context': {'source': 'fixed'}})
    with pytest.raises(FlowError, match='same current task'):
        team.plan(store, 'other', {'rationale': 'Bad link', 'max_parallel': 2,
                                 'assignments': [spec(store, 'b', peers=['a'])]})


@pytest.mark.parametrize('left,right,reason', [
    ({'mode': 'write', 'allowed_paths': ['src']}, {'allowed_paths': ['SRC/module.py']}, 'shared-checkout-path'),
    ({'resources': ['node-gpu-set']}, {'resources': ['node-gpu-set']}, 'shared-resource'),
    ({'owner': 'same'}, {'owner': 'same'}, 'owner-busy')])
def test_conflict_reservations(store, left, right, reason):
    plan(store, spec(store, 'a', **left), spec(store, 'b', **right))
    team.claim(store, 'a', left.get('owner', 'a-owner'))
    with pytest.raises(FlowError, match=reason):
        team.claim(store, 'b', right.get('owner', 'b-owner'))


def test_isolated_checkouts_and_disjoint_paths_can_run(store):
    plan(store, spec(store, 'a', mode='write', allowed_paths=['src/a']),
         spec(store, 'b', mode='write', allowed_paths=['src/b']),
         spec(store, 'c', allowed_paths=['src'], checkout='frozen-baseline'))
    assert team.schedule(store, 't')['dispatchable'] == ['a', 'b', 'c']


def test_different_operators_develop_in_parallel_and_share_gpu_only_during_measurement(store, tmp_path):
    plan(store, spec(store, 'attention', mode='write', allowed_paths=['src/attention'],
                     resources=['gpu-shared'], resource_scope='operation'),
         spec(store, 'gemm', mode='write', allowed_paths=['src/gemm'],
              resources=['gpu-shared'], resource_scope='operation'))
    a = team.claim(store, 'attention', 'attention-owner')
    g = team.claim(store, 'gemm', 'gemm-owner')
    assert team.schedule(store, 't')['active'] == ['attention', 'gemm']
    # CPU fixture exercises resource semantics only, never a GPU benchmark.
    lease = store.lease('gpu-shared', 'attention-owner')
    with pytest.raises(FlowError, match='leased'):
        store.lease('gpu-shared', 'gemm-owner')
    assert run_command(store, 't', 'attention-measure', command(tmp_path), lease,
                       assignment=a['id'], owner=a['owner'], token=a['token'])['status'] == 'complete'
    store.release(lease)
    gemm_lease = store.lease('gpu-shared', 'gemm-owner')
    with pytest.raises(FlowError, match='fencing token'):
        run_command(store, 't', 'stale-attention', command(tmp_path), lease,
                    assignment=a['id'], owner=a['owner'], token=a['token'])
    assert run_command(store, 't', 'gemm-measure', command(tmp_path), gemm_lease,
                       assignment=g['id'], owner=g['owner'], token=g['token'])['status'] == 'complete'
    assert team.schedule(store, 't')['active'] == ['attention', 'gemm']


def test_simultaneous_claims_reserve_one_slot(store):
    plan(store, spec(store, 'a'), spec(store, 'b'), limit=1)
    barrier = threading.Barrier(2)
    def attempt(aid):
        barrier.wait()
        try:
            team.claim(store, aid, aid + '-owner')
            return True
        except FlowError:
            return False
    with ThreadPoolExecutor(2) as pool:
        outcomes = list(pool.map(attempt, ['a', 'b']))
    assert outcomes.count(True) == 1
    assert len(team.schedule(store, 't')['active']) == 1


def test_revision_requires_new_token_and_new_result(store):
    plan(store, spec(store, 'a'))
    first = team.claim(store, 'a', 'a-owner')
    report = finish(store, first)
    accept(store, 'a', report, verdict='revise')
    second = team.claim(store, 'a', 'a-owner')
    assert second['token'] > first['token']
    with pytest.raises(FlowError, match='owner/token'):
        team.finish(store, 'a', 'a-owner', report, first['token'])
    accept(store, 'a', finish(store, second))
    with pytest.raises(FlowError):
        team.claim(store, 'a', 'a-owner')


def test_peer_question_answer_and_yield_avoid_slot_deadlock(store):
    plan(store, spec(store, 'a', peers=['b']), spec(store, 'b'), limit=1)
    first = team.claim(store, 'a', 'a-owner')
    question = msg(store, blocking=True)
    team.send(store, 't', question)
    assert team.send(store, 't', question)['status'] == 'already-recorded'
    with pytest.raises(FlowError, match='collision'):
        team.send(store, 't', {**question, 'body': 'Different'})
    team.acknowledge(store, 'q', 'b-owner', receipt(store, decision='seen'))
    with pytest.raises(FlowError, match='Unresolved peer'):
        finish(store, first)
    with pytest.raises(FlowError, match='Answer the question'):
        team.acknowledge(store, 'q', 'b-owner', receipt(store))
    team.yield_assignment(store, 'a', 'a-owner', first['token'],
                          {'quiescent': True, 'note': 'Stopped writes before waiting', 'evidence': receipt(store)['evidence']})
    assert team.schedule(store, 't')['dispatchable'] == ['b']
    b = team.claim(store, 'b', 'b-owner')  # incoming question must not block work
    team.send(store, 't', msg(store, 'answer', 'b', 'a', kind='answer', reply_to='q'))
    with pytest.raises(FlowError):
        team.acknowledge(store, 'answer', 'b-owner', receipt(store))
    team.acknowledge(store, 'answer', 'a-owner', receipt(store))
    assert all(m['status'] == 'handled' for m in team.messages(store, 't'))
    accept(store, 'b', finish(store, b))
    second = team.claim(store, 'a', 'a-owner')
    assert second['token'] == first['token'] + 1
    with pytest.raises(FlowError): finish(store, first)
    accept(store, 'a', finish(store, second))


def test_peer_routing_blocker_and_controller_receipt(store):
    plan(store, spec(store, 'a'), spec(store, 'b'), spec(store, 'c', depends_on=['a']))
    with pytest.raises(FlowError, match='relationship'):
        team.send(store, 't', msg(store))
    with pytest.raises(FlowError, match='own dependent'):
        team.send(store, 't', msg(store, recipient='c', blocking=True))
    team.send(store, 't', msg(store, recipient='controller', kind='blocker'))
    with pytest.raises(FlowError, match='requires evidence'):
        team.acknowledge(store, 'q', 'controller', receipt(store, evidence=[]))
    team.acknowledge(store, 'q', 'controller', receipt(store, decision='seen'))
    with store.db() as db: assert 'message:q' in team.completion_blockers(db, 't')
    team.acknowledge(store, 'q', 'controller', receipt(store))


def test_new_context_stales_messages_and_keeps_live_reservations(store):
    plan(store, spec(store, 'a', mode='write'), spec(store, 'b', peers=['a']))
    a = team.claim(store, 'a', 'a-owner')
    team.send(store, 't', msg(store))
    store.change_context('t', {'source': 'next'})
    flow.start(store, 't', {'acceptance': {'analysis': 'Review next source'}}, reason='Source changed')
    with pytest.raises(FlowError, match='stale'):
        team.acknowledge(store, 'q', 'b-owner', receipt(store))
    with pytest.raises(FlowError, match='stale'): finish(store, a)
    assert team.messages(store, 't')[0]['stale']
    assert 'stale-running-assignment:a' in flow.next_step(store, 't')['reasons']
    team.cancel(store, 'a', {'stopped': True, 'note': 'Verified old actor stopped', 'evidence': receipt(store)['evidence']})
    assert flow.next_step(store, 't')['action'] == 'work'


def pending_operation(s, aid, status='started', seconds=5):
    with s.db() as db:
        db.execute('INSERT INTO operations VALUES(?,?,?,?,NULL,?)', ('running-' + aid, 't', 'fixture', status, utc()))
        db.execute('INSERT INTO assignment_operations VALUES(?,?,1)', ('running-' + aid, aid))
        s.event(db, 't', 'operation-started', {'operation': 'running-' + aid, 'timeout_seconds': seconds,
                                               'lease': {'resource': 'cpu-' + aid}})


def command(tmp_path, timeout=5):
    return {'schema_version': 1, 'argv': [sys.executable, '--version'], 'cwd': str(tmp_path),
            'basis': 'Local protocol fixture', 'timeout_seconds': timeout}


def test_independent_executions_and_uncertain_remote_operation(store, tmp_path):
    plan(store, spec(store, 'a', resources=['cpu-a']), spec(store, 'b', resources=['cpu-b']))
    a = team.claim(store, 'a', 'a-owner'); team.claim(store, 'b', 'b-owner')
    pending_operation(store, 'a')
    assert flow.next_step(store, 't')['action'] == 'coordinate'
    lease = store.lease('cpu-b', 'b-owner')
    one = run_command(store, 't', 'b-run', command(tmp_path), lease, assignment='b', owner='b-owner', token=1)
    assert one['status'] == 'complete'
    assert run_command(store, 't', 'b-run', command(tmp_path), lease, assignment='b', owner='b-owner', token=1) == one
    with pytest.raises(FlowError, match='different request'):
        run_command(store, 't', 'b-run', command(tmp_path), lease, assignment='a', owner='a-owner', token=1)
    with pytest.raises(FlowError):
        run_command(store, 't', 'unbound', command(tmp_path), lease)
    for action in (lambda: finish(store, a),
                   lambda: team.cancel(store, 'a', {'stopped': True, 'note': 'Unproved stop', 'evidence': receipt(store)['evidence']}),
                   lambda: team.yield_assignment(store, 'a', 'a-owner', 1, {'quiescent': True, 'note': 'Still running', 'evidence': receipt(store)['evidence']})):
        with pytest.raises(FlowError): action()
    with store.db() as db: db.execute("UPDATE operations SET status='unknown' WHERE id='running-a'")
    assert flow.next_step(store, 't')['action'] == 'reconcile'
    with pytest.raises(FlowError, match='unresolved'):
        run_command(store, 't', 'b-more', command(tmp_path), lease, assignment='b', owner='b-owner', token=1)
    reconcile_operation(store, 'running-a', 'failed', receipt(store)['evidence'], 'Verified absent')
    assert run_command(store, 't', 'b-more', command(tmp_path), lease, assignment='b', owner='b-owner', token=1)['status'] == 'complete'


def test_pending_peer_blocker_invalidates_dependency_consumption(store):
    plan(store, spec(store, 'a'), spec(store, 'b', depends_on=['a']))
    a = team.claim(store, 'a', 'a-owner'); accept(store, 'a', finish(store, a))
    b = team.claim(store, 'b', 'b-owner')
    team.send(store, 't', msg(store, sender='controller', recipient='a', kind='blocker'))
    with pytest.raises(FlowError, match='dependency evidence changed'): finish(store, b)


def test_peer_wakeup_bridge_can_deliver_while_remote_outcome_unknown(store, tmp_path):
    from hcu_trainflow.monitor import inbox
    plan(store, spec(store, 'a', resources=['cpu-a']))
    team.claim(store, 'a', 'a-owner')
    pending_operation(store, 'a', status='unknown')
    team.send(store, 't', msg(store, recipient='controller', kind='blocker'))
    event = next(e for e in store.events() if e['kind'] == 'agent-message')
    bridge = {**command(tmp_path), 'argv': [sys.executable, '-c', 'print("fixture delivery only")']}
    result = dispatch_inbox(store, event['event_id'], 'fixture-consumer', bridge, store.lease('local-bridge', 'controller'))
    assert result['bridge_delivery'] == 'returned-success'
    assert result['incident_resolution'] == 'pending-consumer-ack'
    assert next(e for e in inbox(store) if e['event_id'] == event['event_id'])['status'] == 'claimed'
    assert team.messages(store, 't')[0]['status'] == 'pending'
    assert flow.next_step(store, 't')['action'] == 'reconcile'


def test_parallel_execution_budget_reserves_inflight_time(store, tmp_path):
    with store.db() as db:
        task = json.loads(db.execute("SELECT spec FROM tasks WHERE id='t'").fetchone()['spec'])
        task['budget'] = {'max_operations': 10, 'max_seconds': 10}
        db.execute("UPDATE tasks SET spec=? WHERE id='t'", (json.dumps(task),))
    plan(store, spec(store, 'a', resources=['cpu-a']), spec(store, 'b', resources=['cpu-b']))
    team.claim(store, 'a', 'a-owner'); team.claim(store, 'b', 'b-owner')
    pending_operation(store, 'a', seconds=7)
    with pytest.raises(FlowError, match='remaining execution budget'):
        run_command(store, 't', 'too-much', command(tmp_path, 5), store.lease('cpu-b', 'b-owner'),
                    assignment='b', owner='b-owner', token=1)


def test_guidance_collects_at_five_minutes_and_manual_refresh_is_immediate(store, monkeypatch):
    now = [1000.0]
    monkeypatch.setattr(flow.time, 'time', lambda: now[0])
    assert flow.sync_guidance(store, 't', force=True)['new'] == 0
    human = flow.board_paths(store, 't')[2]
    human.write_text('Please compare memory residency first.', encoding='utf8')
    now[0] += 299
    assert flow.sync_guidance(store, 't')['scan'] == 'not-due'
    assert flow.next_step(store, 't')['action'] == 'work'
    now[0] += 1
    assert flow.next_step(store, 't')['action'] == 'human'
    human.write_text('New immediate instruction', encoding='utf8')
    assert flow.sync_guidance(store, 't', force=True)['new'] == 1
