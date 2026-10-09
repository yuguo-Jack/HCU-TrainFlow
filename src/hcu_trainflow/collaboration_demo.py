"""A deterministic CPU fixture for the protocol, NOT a real Agent or GPU run."""
from pathlib import Path

from . import flow, team
from .core import FlowError, Store


def run_demo(destination):
    root = Path(destination).resolve()
    if root.exists():
        raise FlowError('Use a fresh directory for the synthetic collaboration demonstration')
    store = Store(root)
    store.create({'schema_version': 1, 'task_id': 'synthetic-analysis', 'mode': 'analyze',
                  'objective': 'Demonstrate review, correction, human guidance and resume with synthetic evidence',
                  'context': {'hardware': 'none', 'fixture': 'CPU-only, not a performance assessment'}})
    tid = 'synthetic-analysis'
    flow.start(store, tid, {'acceptance': {'scope': 'Clearly identify the synthetic evidence and its limitations'}})
    evidence = store.put(b'SYNTHETIC: no HCU execution; durations and review replies are scripted fixtures.')
    snapshot = flow.retain(store, {'files': {}, 'fixture': True, 'evidence': [evidence]})
    context = store.task(tid)['context']
    # Both lanes are scripted, not model sessions. Claims demonstrate parallel
    # eligibility; this fixture does not prove real harness launch/delivery.
    specs = [{'id': name, 'owner': name + '-fixture', 'goal': 'Read synthetic ' + name,
              'scope': 'Fixed CPU fixture only', 'allowed_paths': ['fixture'], 'mode': 'read',
              'acceptance': 'Label synthetic inputs and limits', 'budget': {'max_operations': 2},
              'context': context, 'peers': ['comms' if name == 'compute' else 'compute']}
             for name in ('compute', 'comms')]
    team.plan(store, tid, {'rationale': 'Two independent read lanes with a shared denominator question',
                           'max_parallel': 2, 'assignments': specs})
    claims = [team.claim(store, s['id'], s['owner']) for s in specs]
    team.send(store, tid, {'id': 'denominator-question', 'sender': 'compute', 'recipient': 'comms',
                          'owner': 'compute-fixture', 'kind': 'question', 'blocking': True,
                          'body': 'Does the fixture use the same wall-clock denominator?',
                          'context': context, 'evidence': [evidence]})
    team.acknowledge(store, 'denominator-question', 'comms-fixture',
                     {'decision': 'seen', 'note': 'Scripted recipient read the question', 'evidence': []})
    team.send(store, tid, {'id': 'denominator-answer', 'sender': 'comms', 'recipient': 'compute',
                          'owner': 'comms-fixture', 'kind': 'answer', 'reply_to': 'denominator-question',
                          'body': 'Yes, synthetic fixture only; no real training measurement.',
                          'context': context, 'evidence': [evidence]})
    team.acknowledge(store, 'denominator-answer', 'compute-fixture',
                     {'decision': 'handled', 'note': 'Scripted asker confirmed the scope', 'evidence': [evidence]})
    for claim in claims:
        report = flow.retain(store, {'context': context, 'inputs': claim['inputs'],
                                     'summary': 'Scripted lane; no hardware conclusion', 'evidence': [evidence]})
        team.finish(store, claim['id'], claim['owner'], report, claim['token'])
        team.review(store, claim['id'], {'report': report, 'reviewer': 'scripted-controller',
                                         'verdict': 'accept', 'note': 'Checked fixture scope only', 'evidence': [evidence]})

    def candidate(summary):
        decision = flow.next_step(store, tid)
        report = store.report(tid, 'analysis', {'context': decision['context'], 'status': 'complete',
            'candidate_snapshot': snapshot, 'evidence': [evidence], 'summary': summary})
        return flow.submit(store, tid, {'author': 'scripted-actor', 'context': decision['context'],
            'goal': decision['goal'], 'snapshot': snapshot, 'summary': summary, 'reports': {'analysis': report['artifact']},
            'target': 'completed', 'evidence': [evidence]})

    def review(verdict):
        decision = flow.next_step(store, tid)
        value = {k: decision[k] for k in ('round','candidate','context','goal')}
        value.update(reviewer='scripted-review-fixture', verdict=verdict,
            summary='Synthetic review: clarify evidence scope' if verdict == 'revise' else 'Synthetic scope now explicit',
            findings=[{'severity':'blocking','detail':'State explicitly that no GPU was used'}] if verdict == 'revise' else [],
            acceptance={'scope':'pending' if verdict == 'revise' else 'met'}, progress='advanced',
            full_alignment=True, evidence=[evidence])
        return flow.review(store, tid, value)

    candidate('Synthetic draft report')
    review('revise')
    _, _, guidance = flow.board_paths(store, tid)
    with guidance.open('a', encoding='utf8') as stream:
        stream.write('\nDemo human comment: retain the lack of real GPU validation in the conclusion.\n')
    observed = flow.sync_guidance(store, tid, force=True)
    flow.acknowledge(store, tid, observed['guidance'], 'applied', 'Will state that this is only a protocol fixture.')
    # Reopen the same persistent store as a controller would after interruption.
    store = Store(root)
    candidate('Synthetic protocol demonstration only. No GPU performance or training correctness was validated.')
    review('accept')
    result = flow.advance(store, tid)
    return {**result, **flow.render_board(store, tid), 'team': team.schedule(store, tid),
            'validation': 'scripted-protocol-fixture-only'}
