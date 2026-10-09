"""Regression coverage for evidence resets and reservations across controllers."""
from concurrent.futures import ThreadPoolExecutor
import json
import threading

import pytest

from hcu_trainflow import flow, team
from hcu_trainflow.core import FlowError, Store


def create(store, tid='t', *, attached=True):
    store.create({'schema_version': 1, 'task_id': tid, 'mode': 'adapt',
                  'objective': 'Synthetic reviewed evidence fixture',
                  'context': {'source': 'a'}})
    if attached:
        flow.start(store, tid, {'acceptance': {'result': 'Validate retained fixture'}})


def assignment(store, tid, aid, **changes):
    return {'id': aid, 'owner': aid + '-owner', 'goal': 'Inspect fixture',
            'scope': 'Synthetic evidence only', 'allowed_paths': ['src'],
            'acceptance': 'Return supported evidence', 'mode': 'read',
            'budget': {'max_operations': 2}, 'context': store.task(tid)['context'], **changes}


def plan(store, tid, *specs):
    return team.plan(store, tid, {'rationale': 'Independent fixture work',
                                 'max_parallel': 3, 'assignments': list(specs)})


def finish(store, claim):
    report = flow.retain(store, {'context': claim['context'], 'inputs': claim['inputs'],
                                'summary': 'Fixture findings',
                                'evidence': [store.put(b'Synthetic fixture evidence')]})
    team.finish(store, claim['id'], claim['owner'], report, claim['token'])
    return report


def review(store, aid, report):
    return team.review(store, aid, {'report': report, 'reviewer': 'controller',
                                    'verdict': 'accept', 'note': 'Reviewed fixture evidence',
                                    'evidence': [report]})


def baseline(store, **changes):
    return {'context': store.task('t')['context'], 'status': 'pass', 'executed': 1,
            'candidate_snapshot': store.put(b'Synthetic snapshot'),
            'evidence': [store.put(b'Synthetic baseline evidence')], **changes}


@pytest.mark.parametrize('changes', [{'executed': True}, {'executed': 1.5},
                                    {'skipped_required': 1}, {'required_missing': ['rank1']}])
def test_invalid_required_coverage_cannot_be_recorded_as_pass(tmp_path, changes):
    store = Store(tmp_path)
    create(store)
    with pytest.raises(FlowError, match='PASS requires'):
        store.report('t', 'baseline', baseline(store, **changes))


def test_legacy_invalid_pass_is_not_current_evidence(tmp_path):
    store = Store(tmp_path)
    create(store, attached=False)
    body = baseline(store, executed=True, skipped_required=1)
    sha = flow.retain(store, body)
    # Model a workspace written before the report validator was corrected.
    with store.db() as db:
        db.execute('INSERT INTO reports VALUES(?,?,?,?,?,?)',
                   ('t', 'baseline', body['context'], sha, 'pass', 'legacy'))
        store.event(db, 't', 'report-recorded', {'kind': 'baseline', 'artifact': sha, 'status': 'pass'})
    with pytest.raises(FlowError, match='Missing requested deliverable'):
        store.transition('t', 'completed')
    assert json.loads(store.artifact(sha)) == body


def test_context_roundtrip_preserves_history_but_invalidates_report_and_flow(tmp_path):
    store = Store(tmp_path)
    create(store)
    body = baseline(store)
    report = store.report('t', 'baseline', body)['artifact']
    store.change_context('t', {'source': 'b'})
    store.change_context('t', {'source': 'a'})
    assert flow.next_step(store, 't')['action'] == 'human'
    with pytest.raises(FlowError, match='flow-replan'):
        flow.start(store, 't', {'acceptance': {'result': 'Validate retained fixture'}})
    flow.start(store, 't', {'acceptance': {'result': 'Validate retained fixture'}},
               reason='Revalidate restored source after environment changes')
    with store.db() as db:
        assert not store.current_reports(db, 't', body['context'])
        assert db.execute('SELECT artifact FROM reports WHERE task=?', ('t',)).fetchone()[0] == report
    assert json.loads(store.artifact(report)) == body
    decision = flow.next_step(store, 't')
    candidate = {'author': 'worker', 'context': body['context'], 'goal': decision['goal'],
                 'snapshot': body['candidate_snapshot'], 'summary': 'Old baseline reused',
                 'reports': {'baseline': report}, 'target': 'completed', 'evidence': body['evidence']}
    with store.db() as db:
        assert 'missing-or-replaced-report:baseline' in flow.gate(store, db, store.task('t'), candidate)


def test_context_roundtrip_also_invalidates_unattached_task_evidence(tmp_path):
    store = Store(tmp_path)
    create(store, attached=False)
    store.report('t', 'baseline', baseline(store))
    store.change_context('t', {'source': 'b'})
    store.change_context('t', {'source': 'a'})
    with pytest.raises(FlowError, match='Missing requested deliverable'):
        store.transition('t', 'completed')
    store.report('t', 'baseline', baseline(store, evidence=[store.put(b'Fresh revalidation evidence')]))
    assert store.transition('t', 'completed')['state'] == 'completed'


def test_context_change_during_report_retention_rejects_late_report(tmp_path, monkeypatch):
    store = Store(tmp_path)
    create(store)
    body = baseline(store)
    original_put = store.put

    def race(data, visibility='private'):
        sha = original_put(data, visibility)
        store.change_context('t', {'source': 'b'})
        store.change_context('t', {'source': 'a'})
        return sha

    monkeypatch.setattr(store, 'put', race)
    with pytest.raises(FlowError, match='context changed while recording'):
        store.report('t', 'baseline', body)
    with store.db() as db:
        assert db.execute('SELECT count(*) FROM reports').fetchone()[0] == 0


@pytest.mark.parametrize('scope', [
    {'resources': ['shared-gpu'], 'resource_scope': 'assignment'},
    {'checkout': 'shared-source', 'mode': 'write'},
])
def test_cross_task_claims_serialize_explicit_shared_scopes(tmp_path, scope):
    store = Store(tmp_path)
    create(store, 't1')
    create(store, 't2')
    plan(store, 't1', assignment(store, 't1', 'a', **scope))
    plan(store, 't2', assignment(store, 't2', 'b', **scope))
    barrier = threading.Barrier(2)

    def claim(aid):
        barrier.wait()
        try:
            team.claim(store, aid, aid + '-owner')
            return True
        except FlowError:
            return False

    with ThreadPoolExecutor(2) as pool:
        assert list(pool.map(claim, ['a', 'b'])).count(True) == 1
    active = team.schedule(store, 't1')['active'] + team.schedule(store, 't2')['active']
    assert len(active) == 1
    waiting_task = 't2' if active == ['a'] else 't1'
    assert not team.schedule(store, waiting_task)['dispatchable']


def test_separate_default_checkouts_and_operation_scopes_remain_parallel(tmp_path):
    store = Store(tmp_path)
    for tid, aid in [('t1', 'a'), ('t2', 'b')]:
        create(store, tid)
        plan(store, tid, assignment(store, tid, aid, mode='write',
                                   resources=['shared-gpu'], resource_scope='operation'))
        assert team.claim(store, aid, aid + '-owner')['status'] == 'claimed'


def test_assignment_dependencies_do_not_revive_after_context_roundtrip(tmp_path):
    store = Store(tmp_path)
    create(store, attached=False)
    plan(store, 't', assignment(store, 't', 'a'))
    review(store, 'a', finish(store, team.claim(store, 'a', 'a-owner')))
    store.change_context('t', {'source': 'b'})
    store.change_context('t', {'source': 'a'})
    with pytest.raises(FlowError, match='Dependency/peer'):
        plan(store, 't', assignment(store, 't', 'b', depends_on=['a']))
    plan(store, 't', assignment(store, 't', 'fresh'))
    assert team.claim(store, 'fresh', 'fresh-owner')['status'] == 'claimed'


@pytest.mark.parametrize('accepted_middle', [False, True])
def test_late_upstream_blocker_prevents_acceptance_and_transitive_consumption(tmp_path, accepted_middle):
    store = Store(tmp_path)
    create(store)
    plan(store, 't', assignment(store, 't', 'a'),
         assignment(store, 't', 'b', depends_on=['a']),
         assignment(store, 't', 'c', depends_on=['b']))
    review(store, 'a', finish(store, team.claim(store, 'a', 'a-owner')))
    report = finish(store, team.claim(store, 'b', 'b-owner'))
    if accepted_middle:
        review(store, 'b', report)
    team.send(store, 't', {'id': 'upstream-invalid', 'sender': 'controller', 'recipient': 'a',
                          'owner': 'controller', 'kind': 'blocker', 'body': 'Original input is invalid',
                          'context': store.task('t')['context'], 'evidence': []})
    if not accepted_middle:
        with pytest.raises(FlowError, match='dependency evidence changed'):
            review(store, 'b', report)
    with pytest.raises(FlowError, match='dependency'):
        team.claim(store, 'c', 'c-owner')
    assert 'dependency-has-peer-blocker:a' in team.schedule(store, 't')['waiting']['c']


def test_cancelled_required_work_explains_whole_flow_replan_recovery(tmp_path):
    store = Store(tmp_path)
    create(store)
    plan(store, 't', assignment(store, 't', 'a'))
    team.cancel(store, 'a', {'stopped': True, 'note': 'Verified worker stopped',
                            'evidence': [store.put(b'Synthetic stopped-process evidence')]})
    decision = flow.next_step(store, 't')
    assert decision['action'] == 'coordinate'
    assert decision['team']['replan_required'][0]['action'] == 'flow-replan'
    flow.start(store, 't', {'acceptance': {'result': 'Validate retained fixture'}},
               reason='Replace stopped required worker with revised assignment')
    plan(store, 't', assignment(store, 't', 'replacement'))
    assert team.claim(store, 'replacement', 'replacement-owner')['status'] == 'claimed'
