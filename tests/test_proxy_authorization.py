import pytest

from hcu_trainflow.core import FlowError
from hcu_trainflow.quality import proxy_contract

FULL = {'num_layers': 24, 'hidden_size': 2048, 'num_heads': 16, 'dtype': 'bf16'}
SMALL = {**FULL, 'num_layers': 4, 'hidden_size': 512}
AUTH = {'authority': 'User explicitly permitted dimension reduction', 'reason': 'Limited hardware adaptation proxy', 'allowed_dimension_reductions': ['hidden_size']}


def test_dimension_reduction_requires_explicit_scope():
    assert proxy_contract(FULL, SMALL)['status'] == 'fail'
    result = proxy_contract(FULL, SMALL, AUTH)
    assert result['status'] == 'pass'
    assert result['scope'] == 'dimension-proxy'
    assert result['runtime_validated'] is False
    assert result['full_model_equivalent'] is False
    assert 'architecture-constraints' in result['required_followup']


@pytest.mark.parametrize('value', [True, 0, -1, 2049, 512.0, '512', None])
def test_authorization_cannot_bypass_valid_numeric_reduction(value):
    assert proxy_contract(FULL, {**SMALL, 'hidden_size': value}, AUTH)['status'] == 'fail'


def test_other_semantic_changes_remain_forbidden():
    assert proxy_contract(FULL, {**SMALL, 'dtype': 'fp16'}, AUTH)['status'] == 'fail'
    assert proxy_contract(FULL, {**SMALL, 'num_heads': 8}, AUTH)['status'] == 'fail'


@pytest.mark.parametrize('auth', [{}, {**AUTH, 'authority': ''}, {**AUTH, 'allowed_dimension_reductions': '*'}, {**AUTH, 'allowed_dimension_reductions': ['hidden_size', 'hidden_size']}])
def test_incomplete_authorization_rejected(auth):
    with pytest.raises(FlowError):
        proxy_contract(FULL, SMALL, auth)


@pytest.mark.parametrize('left,right', [
    ({'num_layers': 1}, {'num_layers': True}),
    ({'num_layers': 1}, {'num_layers': 1.0}),
    ({'num_layers': 2}, {'num_layers': 2, 'optional': None}),
    ({'num_layers': 2, 'optional': None}, {'num_layers': 2}),
    ({'config': {'enabled': 1}}, {'config': {'enabled': True}}),
    ({'shape': [1, 2]}, {'shape': [True, 2]}),
])
def test_proxy_rejects_presence_and_recursive_type_changes(left, right):
    result = proxy_contract(left, right)
    assert result['status'] == 'fail'
    assert result['full_model_equivalent'] is False
    assert result['changes']


def test_identical_nested_model_keeps_equivalence():
    value = {'num_layers': 2, 'config': {'nullable': None, 'shape': [1, 2], 'enabled': True}}
    assert proxy_contract(value, value)['full_model_equivalent'] is True
