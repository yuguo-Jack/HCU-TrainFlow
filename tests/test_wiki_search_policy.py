"""A local candidate is not proof that fresh online evidence is unnecessary."""
import pytest

from hcu_trainflow import official, wiki_search_policy as policy
from hcu_trainflow.core import Store, write_json


def project(tmp_path, lite=True):
    root = tmp_path/'project'
    (root/'knowledge').mkdir(parents=True)
    write_json(root/'knowledge/sources.json', [])
    if lite:
        write_json(root/'knowledge/storage.json', {'profile':'discovery-first'})
    return root


def row(title, engine='megatron', **fields):
    return {'title':title, 'metadata':{'engine':engine}, **fields}


def online(monkeypatch):
    calls = []
    monkeypatch.setattr(official, 'engine_repos', lambda project, engine=None, source=None, repos=():
                        list(repos) or ([f'org/{engine}'] if engine else []))
    def search(store, query, repos, **kwargs):
        calls.append((query, repos, kwargs))
        return {'status':'ok', 'results':[]}
    monkeypatch.setattr(official, 'search_prs', search)
    return calls


def test_weak_local_hit_augments_but_strong_current_hit_does_not(tmp_path, monkeypatch):
    root = project(tmp_path)
    calls = online(monkeypatch)
    result = policy.augment(None, root, {'results':[row('unrelated overview')]}, 'gradient accumulation')
    assert calls[0][1] == ['org/megatron']
    assert not result['evidence_sufficiency']['lexically_adequate']
    result = policy.augment(None, root, {'results':[row('gradient accumulation semantics')]}, 'gradient accumulation')
    assert len(calls) == 1 and result['online_pr']['status'] == 'not-requested'
    assert not result['evidence_sufficiency']['semantic_answer_verified']


def test_mixed_chinese_topic_is_not_satisfied_by_engine_name_alone(tmp_path, monkeypatch):
    root = project(tmp_path)
    calls = online(monkeypatch)
    result = policy.augment(None, root, {'results':[row('Megatron training')]}, 'Megatron 检查点损坏恢复')
    assert calls and not result['evidence_sufficiency']['lexically_adequate']
    assert policy.adequate([row('Megatron 检查点损坏恢复')], 'Megatron 检查点损坏恢复')


@pytest.mark.parametrize('query', ['最新 gradient accumulation', 'gradient accumulation PR',
                                  'gradient accumulation MR', 'recent gradient accumulation'])
def test_freshness_or_explicit_pr_intent_queries_online(tmp_path, monkeypatch, query):
    root = project(tmp_path)
    calls = online(monkeypatch)
    result = policy.augment(None, root, {'results':[row(query)]}, query)
    assert calls and result['evidence_sufficiency']['freshness_or_pr_intent']


@pytest.mark.parametrize('query', ['profile performance', 'precision stability'])
def test_pr_substrings_do_not_trigger_online(tmp_path, monkeypatch, query):
    root = project(tmp_path)
    calls = online(monkeypatch)
    result = policy.augment(None, root, {'results':[row(query)]}, query)
    assert not calls and not result['evidence_sufficiency']['freshness_or_pr_intent']


def test_off_short_circuits_and_changed_page_is_weak(tmp_path, monkeypatch):
    root = project(tmp_path)
    calls = online(monkeypatch)
    assert policy.augment(None, root, {}, 'latest PR', mode='off')['online_pr']['status'] == 'disabled'
    assert not calls
    policy.augment(None, root, {'results':[row('gradient accumulation', review_state='local-page-changed')]},
                   'gradient accumulation')
    assert len(calls) == 1


def test_explicit_scopes_are_complete_and_inferred_scopes_bounded(tmp_path, monkeypatch):
    root = project(tmp_path)
    calls = online(monkeypatch)
    repos = [f'org/engine{i}' for i in range(8)]
    policy.augment(None, root, {'results':[]}, 'gradient', repos=repos)
    assert calls[-1][1] == repos
    monkeypatch.setattr(official, 'engine_repos', lambda project, engine=None, source=None, repos=():
        [f'org/{engine}-{i}' for i in range(4)] if engine else [])
    candidates = [row('unrelated', value) for value in ['unknown', 'cross-engine', 'one', 'two', 'three', 'four']]
    result = policy.augment(None, root, {'results':candidates}, 'gradient')
    scope = result['online_pr']['scope_selection']
    assert scope['inferred_engines'] == ['one', 'two', 'three']
    assert len(scope['repositories']) == 6
    assert 'four' not in ' '.join(scope['repositories'])
    result = policy.augment(None, root, {'results':[row('unrelated', 'unknown')]}, 'gradient')
    assert result['online_pr']['status'] == 'scope-required'


def test_private_context_kept_local_until_explicit_public_terms_supplied(tmp_path, monkeypatch):
    root = project(tmp_path)
    store = Store(tmp_path/'private')
    monkeypatch.setattr(official, 'engine_repos', lambda *args, **kwargs: ['org/engine'])
    from hcu_trainflow import wiki
    calls = []
    def get(*args, **kwargs):
        calls.append(args[0])
        return {'total_count':0, 'items':[]}, ''
    monkeypatch.setattr(wiki, '_get_json', get)
    result = policy.augment(store, root, {'results':[]}, 'gradient job_id=private-123', engine='engine')
    assert result['online_pr']['status'] == 'public-query-required' and not calls
    result = policy.augment(store, root, {'results':[]}, 'gradient job_id=private-123',
                           engine='engine', pr_query='gradient accumulation')
    assert result['online_pr']['status'] == 'ok' and len(calls) == 1
    assert 'private' not in calls[0]


def test_legacy_keeps_empty_only_fallback_and_partial_is_visible(tmp_path, monkeypatch):
    root = project(tmp_path, lite=False)
    calls = online(monkeypatch)
    result = policy.augment(None, root, {'results':[row('unrelated')]}, 'latest gradient PR')
    assert not calls and 'online_pr' not in result
    monkeypatch.setattr(official, 'search_prs', lambda *args, **kwargs: {'status':'partial', 'results':[]})
    result = policy.augment(None, root, {'results':[]}, 'gradient', engine='engine')
    assert result['status'] == 'partial'
