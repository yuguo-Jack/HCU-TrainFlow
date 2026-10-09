"""A deterministic CPU fixture for the protocol, NOT a real Agent or GPU run."""
from pathlib import Path

from . import flow
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
    observed = flow.sync_guidance(store, tid)
    flow.acknowledge(store, tid, observed['guidance'], 'applied', 'Will state that this is only a protocol fixture.')
    # Reopen the same persistent store as a controller would after interruption.
    store = Store(root)
    candidate('Synthetic protocol demonstration only. No GPU performance or training correctness was validated.')
    review('accept')
    result = flow.advance(store, tid)
    return {**result, **flow.render_board(store, tid), 'validation': 'scripted-protocol-fixture-only'}
