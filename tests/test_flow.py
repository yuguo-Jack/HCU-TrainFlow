import json
import sys

import pytest

from hcu_trainflow import flow
from hcu_trainflow.core import FlowError, Store
from hcu_trainflow.execution import run_command
from hcu_trainflow.coordination import dispatch_inbox


def setup(tmp_path, mode='analyze', **limits):
    store = Store(tmp_path / 'workspace')
    store.create({'schema_version':1, 'task_id':'t', 'mode':mode, 'objective':'A verifiable training task',
                  'context':{'source':'initial', 'data':'frozen'}, 'permissions':['execute','agent-dispatch']})
    flow.start(store, 't', {'acceptance':{'result':'Deliver evidence in the requested scope'}, **limits})
    return store


def candidate(store, target=None, experiment=False, label='candidate-1'):
    task = store.task('t')
    decision = flow.next_step(store, 't')
    snap = flow.retain(store, {'source':label, 'build':'fixture', 'data':'frozen'})
    proof = store.put(('Synthetic fixture evidence: ' + label).encode())
    destination = target or flow.target(task)
    reports = {}
    for kind in flow.required_reports(task, destination):
        reports[kind] = store.report('t', kind, {'context':task['context'], 'candidate_snapshot':snap,
             'status':'pass', 'executed':3, 'evidence':[proof]})['artifact']
    value = {'author':'actor', 'context':task['context'], 'goal':decision['goal'], 'snapshot':snap,
             'summary':label, 'reports':reports, 'target':destination, 'evidence':[proof]}
    if experiment:
        value['experiment'] = flow.retain(store, {'context':task['context'],
             'correctness':{'context':task['context'], 'candidate_snapshot':snap, 'evidence':[proof],
                'executed':3, 'failures':0, 'candidate_path_exercised':True, 'profiler_off':True,
                'measurement_protocol':'same fixture shape/dtype/stream'},
             'baseline_times':[10,10,10], 'candidate_times':[8,8,8]})
    return value


def verdict(store, verdict='accept', **changes):
    decision = flow.next_step(store, 't')
    item = flow.artifact_json(store, decision['candidate'])
    value = {k:decision[k] for k in ('round','candidate','goal','context')}
    value.update(reviewer='independent-reviewer', verdict=verdict, summary='Reviewed retained evidence and requested scope',
                 findings=[], acceptance={'result':'met'}, progress='advanced', full_alignment=True, evidence=item['evidence'])
    return {**value, **changes}


def test_resume_review_and_finish(tmp_path):
    store = setup(tmp_path)
    flow.submit(store, 't', candidate(store))
    assert flow.next_step(Store(store.root), 't')['action'] == 'review'
    flow.review(store, 't', verdict(store, 'revise', findings=[{'severity':'blocking','detail':'Clarify scope'}]))
    assert flow.next_step(store, 't')['action'] == 'repair'
    flow.submit(store, 't', candidate(store, label='corrected'))
    flow.review(store, 't', verdict(store))
    assert flow.advance(Store(store.root), 't')['action'] == 'completed'
    assert 'corrected' in flow.board_paths(store, 't')[1].read_text(encoding='utf8')


def test_review_validation_and_bounded_failures(tmp_path):
    store = setup(tmp_path, max_review_failures=3)
    flow.submit(store, 't', candidate(store))
    good = verdict(store)
    for bad in ({}, {**good, 'reviewer':'actor'}, {**good, 'full_alignment':False}):
        with pytest.raises(FlowError):
            flow.review(store, 't', bad)
    assert flow.next_step(store, 't')['reasons'] == ['review-failures']
    with pytest.raises(FlowError):
        flow.advance(store, 't')


@pytest.mark.parametrize('change', [
    {'findings':[{'severity':'blocking','detail':'Incorrect gradient'}]},
    {'acceptance':{'result':'pending'}}, {'evidence':[]}, {'goal':'old-goal'}])
def test_false_completion_rejected(tmp_path, change):
    store = setup(tmp_path)
    flow.submit(store, 't', candidate(store))
    with pytest.raises(FlowError):
        flow.review(store, 't', verdict(store, **change))


def test_manual_transition_and_replaced_report_do_not_bypass(tmp_path):
    store = setup(tmp_path)
    value = candidate(store)
    with pytest.raises(FlowError, match='review-required'):
        store.transition('t','completed')
    flow.submit(store, 't', value)
    flow.review(store, 't', verdict(store))
    replacement = flow.artifact_json(store, value['reports']['analysis'])
    store.report('t','analysis',{**replacement, 'note':'changed after review'})
    assert flow.next_step(store, 't')['action'] == 'repair'
    with pytest.raises(FlowError, match='replaced-report'):
        store.transition('t','completed')


def test_context_and_replan_invalidate_review(tmp_path):
    store = setup(tmp_path)
    flow.submit(store, 't', candidate(store))
    old = verdict(store)
    store.change_context('t', {'source':'updated', 'data':'frozen'})
    assert flow.next_step(store, 't')['action'] == 'human'
    with pytest.raises(FlowError):
        flow.review(store, 't', old)
    flow.start(store, 't', {'acceptance':{'result':'Deliver evidence'}}, reason='New source requires revalidation')
    assert flow.next_step(store, 't')['action'] == 'repair'
    assert flow.next_step(store, 't')['goal'] != old['goal']


def test_iteration_is_not_stage_loss_validation(tmp_path):
    store = setup(tmp_path, mode='optimize')
    flow.submit(store, 't', candidate(store, target='iterate', experiment=True))
    flow.review(store, 't', verdict(store, acceptance={'result':'pending'}))
    assert flow.advance(store, 't')['action'] == 'work'
    assert store.task('t')['state'] == 'prepared'
    final = candidate(store, experiment=True)
    final['reports'].pop('stage-quality')
    flow.submit(store, 't', final)
    flow.review(store, 't', verdict(store))
    assert 'missing-or-replaced-report:stage-quality' in flow.next_step(store, 't')['reasons']
    with pytest.raises(FlowError):
        flow.advance(store, 't')


def test_rejected_measurement_cannot_advance_iteration(tmp_path):
    store = setup(tmp_path, mode='optimize')
    value = candidate(store, target='iterate', experiment=True)
    data = flow.artifact_json(store, value['experiment'])
    data['correctness']['candidate_path_exercised'] = False
    value['experiment'] = flow.retain(store, data)
    flow.submit(store, 't', value)
    flow.review(store, 't', verdict(store))
    assert 'iteration-not-kept' in flow.next_step(store, 't')['reasons']


def test_guidance_supersedes_review_and_is_never_overwritten(tmp_path):
    store = setup(tmp_path)
    flow.submit(store, 't', candidate(store))
    flow.review(store, 't', verdict(store))
    path = flow.board_paths(store, 't')[2]
    text = '# Expert guidance\nDo not use the previous timing denominator.\n'
    path.write_text(text, encoding='utf8')
    first = flow.sync_guidance(store, 't')
    assert first['new'] == 1 and flow.sync_guidance(store, 't')['new'] == 0
    assert flow.next_step(store, 't')['action'] == 'human'
    flow.render_board(store, 't')
    assert path.read_text(encoding='utf8') == text
    flow.acknowledge(store, 't', first['guidance'], 'applied', 'Will recompute with wall-clock denominator')
    assert flow.next_step(store, 't')['action'] == 'repair'
    with pytest.raises(FlowError): flow.advance(store, 't')
    path.write_text(text + 'Second comment', encoding='utf8')
    second = flow.sync_guidance(store, 't')
    flow.acknowledge(store, 't', second['guidance'], 'applied', 'Addressed')
    path.write_text(text, encoding='utf8')
    assert flow.sync_guidance(store, 't')['new'] == 1


def test_questions_require_human_answer(tmp_path):
    store = setup(tmp_path)
    flow.question(store,'t',{'id':'q1','title':'Which allocation?','body':'Please name the allocated resource','blocking':True})
    assert flow.next_step(store,'t')['action'] == 'human'
    with pytest.raises(FlowError): flow.close_question(store,'t','q1','missing','Guessed a pool')
    flow.board_paths(store, 't')[2].write_text('q1: Use the previously allocated pool.', encoding='utf8')
    answer = flow.sync_guidance(store,'t')['guidance']
    flow.acknowledge(store,'t',answer,'applied','Using existing allocation')
    flow.close_question(store,'t','q1',answer,'Confirmed scope')
    assert flow.next_step(store,'t')['action'] == 'work'


def test_pending_guidance_blocks_work_but_not_authorized_bridge(tmp_path):
    store = setup(tmp_path)
    flow.board_paths(store,'t')[2].write_text('Pause and inspect the metrics.', encoding='utf8')
    event = flow.sync_guidance(store,'t')['event_id']
    card = {'schema_version':1, 'argv':[sys.executable,'-c','print("synthetic bridge")'],
            'cwd':str(tmp_path), 'basis':'fixture', 'timeout_seconds':10}
    lease = store.lease('local-cpu','controller')
    with pytest.raises(FlowError): run_command(store,'t','work',card,lease)
    result = dispatch_inbox(store,event,'consumer',card,lease)
    assert result['bridge_delivery'] == 'returned-success'
    assert flow.next_step(store,'t')['action'] == 'human'  # delivery is not handling


def test_unresolved_operation_prevents_advance(tmp_path):
    store = setup(tmp_path)
    flow.submit(store,'t',candidate(store))
    flow.review(store,'t',verdict(store))
    with store.db() as db:
        db.execute("INSERT INTO operations VALUES('remote','t','hash','unknown',NULL,'now')")
    assert flow.next_step(store,'t')['action'] == 'reconcile'
    with pytest.raises(FlowError, match='unresolved-execution'):
        store.transition('t','completed')


def test_plateau_and_blocked_review_require_intervention(tmp_path):
    store = setup(tmp_path, max_stalled_rounds=1)
    flow.submit(store,'t',candidate(store))
    flow.review(store,'t',verdict(store, 'revise', progress='stalled'))
    assert flow.next_step(store,'t')['action'] == 'human'
    flow.start(store,'t',{'acceptance':{'result':'Deliver evidence'}},reason='Expert supplied a new hypothesis')
    flow.submit(store,'t',candidate(store))
    flow.review(store,'t',verdict(store, 'blocked'))
    assert flow.next_step(store,'t')['reasons'] == ['review-blocked']


def test_full_stages_and_crash_after_final_transition(tmp_path):
    store = setup(tmp_path, mode='full')
    targets = ['environment_checked','baseline_validated','profiling','optimizing','scale_ready','training','completed']
    for destination in targets:
        flow.submit(store,'t',candidate(store, experiment=destination == 'scale_ready'))
        flow.review(store,'t',verdict(store))
        if destination == 'completed':
            store.transition('t', destination)  # crash before flow-advance updates its round
            assert flow.next_step(Store(store.root),'t')['action'] == 'completed'
            with store.db() as db: assert flow.last_round(db,'t')['status'] == 'advanced'
        else:
            flow.advance(store,'t')
            assert store.task('t')['state'] == destination


def test_cli_collaboration_fixture(tmp_path, capsys):
    from hcu_trainflow.cli import main
    target = tmp_path / 'fixture'
    assert main(['--workspace',str(tmp_path/'cli'), 'collaboration-demo', str(target)]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result['action'] == 'completed'
    assert result['validation'] == 'scripted-protocol-fixture-only'


def test_queued_guidance_must_be_resolved_before_completion(tmp_path):
    store = setup(tmp_path)
    flow.board_paths(store,'t')[2].write_text('Please also explain the memory peak.', encoding='utf8')
    sha = flow.sync_guidance(store,'t')['guidance']
    flow.acknowledge(store,'t',sha,'queued','Will include memory peak in the final analysis')
    flow.submit(store,'t',candidate(store))
    flow.review(store,'t',verdict(store))
    assert 'queued-human-guidance-needs-final-disposition' in flow.next_step(store,'t')['reasons']
    flow.acknowledge(store,'t',sha,'applied','Final report includes the measured peak and its scope')
    assert flow.advance(store,'t')['action'] == 'completed'


def test_round_budget_and_revision_prevent_extra_work(tmp_path):
    store = setup(tmp_path, max_rounds=1)
    flow.submit(store,'t',candidate(store))
    flow.review(store,'t',verdict(store,'revise'))
    assert flow.next_step(store,'t')['action'] == 'human'
    with pytest.raises(FlowError): flow.submit(store,'t',candidate(store,label='another'))


def test_repeated_submit_cannot_replace_pending_independent_review(tmp_path):
    store = setup(tmp_path)
    value = candidate(store)
    flow.submit(store,'t',value)
    with pytest.raises(FlowError): flow.submit(store,'t',value)
    store.transition('t','paused','Operator paused the task')
    store.transition('t','prepared')
    assert flow.next_step(store,'t')['reasons'] == ['stale-round']


def test_snapshot_mismatch_prevents_advance(tmp_path):
    store = setup(tmp_path)
    value = candidate(store)
    value['snapshot'] = store.put(b'A different candidate manifest')
    flow.submit(store,'t',value)
    flow.review(store,'t',verdict(store))
    assert 'snapshot-mismatch:analysis' in flow.next_step(store,'t')['reasons']


def test_guidance_watch_cli_does_not_act_on_user_content(tmp_path,capsys):
    from hcu_trainflow.cli import main
    store = setup(tmp_path)
    flow.board_paths(store,'t')[2].write_text('Consider a different hypothesis.',encoding='utf8')
    args=['--workspace',str(store.root),'flow-watch','t','--once']
    assert main(args) == 0
    assert json.loads(capsys.readouterr().out)['new'] == 1
    assert main(args) == 0
    assert json.loads(capsys.readouterr().out)['new'] == 0
    with store.db() as db:
        assert db.execute('SELECT count(*) FROM operations').fetchone()[0] == 0
