import pytest
from hcu_trainflow.analysis import analyze_trace, model_operator, profile_plan
from hcu_trainflow.quality import compare_loss, proxy_contract, assess_iteration
from hcu_trainflow.environment import assess_health
from hcu_trainflow.core import FlowError

def trace(durations):
    return {'rank':0,'traceEvents':[{'ph':'X','cat':'kernel','name':name,'ts':start,'dur':duration,'args':{'shape':[8,8],'dtype':'fp32'}} for name,start,duration in durations]}

def test_overlap_does_not_double_count():
    r=analyze_trace(trace([('a',0,80),('b',20,80)]),{'start_us':0,'end_us':100})['ranks']['0']
    assert r['busy_union_us']==100 and r['overlap_us']==60
    assert sum(x['attributed_us'] for x in r['operators'])==100
    assert sum(x['raw_us'] for x in r['operators'])==160

def test_idle_gap_cannot_fake_90_percent():
    r=analyze_trace(trace([('a',0,40)]),{'start_us':0,'end_us':100},{'a':{'flops':1,'peak_flops_s':1e6,'basis':'fixture'}})
    assert r['status']=='incomplete' and r['ranks']['0']['operator_e2e_coverage']==0.4

def test_bound_and_interference():
    model={'kind':'gemm','m':10,'n':10,'k':10,'peak_flops_s':1e9,'bytes':1000,'bandwidth_bytes_s':1e9,'basis':'matched measurement','isolated_us':3}
    result=model_operator(model,10)
    assert result['lower_bound_us']==2 and result['decision']=='investigate-system-interference'
    assert model_operator(model,1)['status']=='inconsistent'

def test_bound_reports_assumptions_without_claiming_measured_bottleneck():
    result = model_operator({'flops': 2000, 'peak_flops_s': 1e9,
                             'bytes': 1000, 'bandwidth_bytes_s': 5e8,
                             'latency_floor_us': 1, 'basis': 'synthetic matched units'}, 5)
    assert result['bound_terms_us'] == {'compute': 2, 'memory': 2, 'latency': 1}
    assert result['limiting_terms'] == ['compute', 'memory']
    assert result['arithmetic_intensity_flops_per_byte'] == 2
    assert result['decision'] == 'compare-reachable-reference'
    assert result['eta_bound'] == .4

@pytest.mark.parametrize('key,value', [
    ('slowdown_threshold', float('nan')), ('slowdown_threshold', float('inf')),
    ('slowdown_threshold', True), ('slowdown_threshold', .5),
    ('efficiency_target', float('nan')), ('efficiency_target', 1.5),
    ('efficiency_target', True),
])
@pytest.mark.parametrize('actual_us', [1, 10])
def test_invalid_decision_thresholds_never_hide_behind_another_branch(key, value, actual_us):
    with pytest.raises(FlowError):
        model_operator({'latency_floor_us': 2, 'isolated_us': 1, 'basis': 'fixture', key: value}, actual_us)

def test_copy_can_have_zero_flops_but_empty_work_is_not_a_bound():
    result = model_operator({'flops': 0, 'bytes': 1000, 'bandwidth_bytes_s': 1e9, 'basis': 'copy fixture'}, 2)
    assert result['lower_bound_us'] == 1 and result['limiting_terms'] == ['memory']
    assert result['arithmetic_intensity_flops_per_byte'] == 0
    assert model_operator({'flops': 0, 'peak_flops_s': 1e9, 'basis': 'empty'}, 2)['status'] == 'incomplete'

@pytest.mark.parametrize('change', [
    {'kind': 'gemm', 'm': 1e200, 'n': 1e200, 'k': 10},
    {'flops': 1e308, 'peak_flops_s': 1e-300},
    {'flops': -1}, {'bytes': float('nan')},
])
def test_invalid_or_overflowed_work_cannot_form_a_valid_model(change):
    with pytest.raises(FlowError):
        model_operator({'latency_floor_us': 2, 'basis': 'fixture', **change}, 10)

def test_no_trace_no_success():
    assert analyze_trace([],{'start_us':0,'end_us':100})['status']=='incomplete'
    assert profile_plan([{'domain':'tp','ranks':[0,2]}],[0,1])['status']=='incomplete'
    assert profile_plan([{'domain':'tp','ranks':[0]}],[0])['status']=='pass'

def test_missing_shape_or_rank():
    t={'traceEvents':[{'ph':'X','cat':'kernel','name':'x','ts':0,'dur':100}]}
    assert analyze_trace(t,{'start_us':0,'end_us':100},{'x':{'flops':1,'peak_flops_s':1e6,'basis':'test'}})['status']=='incomplete'

def test_proxy_only_layers():
    assert proxy_contract({'num_layers':10,'hidden':16},{'num_layers':2,'hidden':16})['is_proxy']
    assert proxy_contract({'num_layers':10,'hidden':16},{'num_layers':2,'hidden':8})['status']=='fail'

def loss_fixture():
    c={'context':'ctx','sample_fingerprint':'s','aggregation':'tokens','min_steps':3,'atol':0.01,'rtol':0,'tolerance_basis':'fixture'}
    r={'context':'ctx','sample_fingerprint':'s','aggregation':'tokens','executed':3,'evidence':['raw'],'candidate_path_exercised':True,'steps':[1,2,3],'loss':[2.,1.9,1.8]}
    return c,r

@pytest.mark.parametrize('change',[{'executed':0},{'candidate_path_exercised':False},{'loss':[float('nan'),1.9,1.8]},{'steps':[4,5,6]},{'sample_fingerprint':'other'},{'skipped_required':1}])
def test_invalid_loss_never_passes(change):
    c,r=loss_fixture();assert compare_loss(c,r,{**r,**change})['status']=='incomplete'

def test_numerical_regression_rejected():
    c,r=loss_fixture();assert compare_loss(c,r,{**r,'loss':[2.2,1.9,1.8]})['status']=='fail'
    assert compare_loss(c,r,r)['status']=='pass'

def test_loss_cannot_hide_failed_tests_or_repeated_steps():
    c,r=loss_fixture()
    assert compare_loss(c,r,{**r,'failures':1})['status']=='incomplete'
    assert compare_loss(c,{**r,'steps':[1,1,1]},{**r,'steps':[1,1,1]})['status']=='incomplete'
    assert proxy_contract({'num_layers':10},{'num_layers':True})['status']=='fail'

def test_iteration_not_production_acceptance():
    _,r=loss_fixture();r.update(profiler_off=True,measurement_protocol='paired warm runs')
    result=assess_iteration(r,[10,11,10],[9,10,9],'ctx')
    assert result['status']=='iteration-kept' and result['production_default'] is False


@pytest.mark.parametrize('status', ['blocked', 'rejected', 'error', 'skipped', 'unknown', 'complete', None, False, ['pass']])
def test_nonpass_outcome_cannot_pass_numerical_or_iteration_gate(status):
    contract, record = loss_fixture()
    changed = {**record, 'status': status, 'profiler_off': True, 'measurement_protocol': 'paired warm runs'}
    assert compare_loss(contract, record, changed)['status'] == 'incomplete'
    assert compare_loss(contract, changed, record)['status'] == 'incomplete'
    assert assess_iteration(changed, [10, 11, 10], [9, 10, 9], 'ctx')['status'] == 'incomplete'


@pytest.mark.parametrize('evidence', ['raw', {'raw': True}, [None], [''], []])
def test_numerical_evidence_must_be_a_nonempty_id_array(evidence):
    contract, record = loss_fixture()
    assert compare_loss(contract, record, {**record, 'evidence': evidence})['status'] == 'incomplete'


@pytest.mark.parametrize('steps', [[True, 2, 3], [1., 2., 3.], [1, 2, 2], None, '123'])
def test_candidate_steps_checked_independently_of_python_numeric_equality(steps):
    contract, record = loss_fixture()
    assert compare_loss(contract, record, {**record, 'steps': steps})['status'] == 'incomplete'


def test_predeclared_timing_stability_blocks_a_faster_but_noisy_candidate():
    _, record = loss_fixture()
    record.update(profiler_off=True, measurement_protocol={'description': 'interleaved warm runs', 'max_relative_mad': .1})
    result = assess_iteration(record, [10, 10.1, 10, 10.1, 10], [1, 5, 9, 5, 1], 'ctx')
    assert result['status'] == 'incomplete'
    assert result['timing']['candidate_median'] == 5
    assert result['timing']['candidate_relative_mad'] == .8
    result = assess_iteration(record, [10, 10.1, 10, 10.1, 10], [9, 9.1, 9, 9.1, 9], 'ctx')
    assert result['status'] == 'iteration-kept'
    assert result['timing']['stability'] == 'pass'


def test_legacy_protocol_does_not_claim_stability_was_checked():
    _, record = loss_fixture()
    record.update(profiler_off=True, measurement_protocol='paired warm runs')
    assert assess_iteration(record, [10, 10, 10], [9, 9, 9], 'ctx')['timing']['stability'] == 'not-specified'


@pytest.mark.parametrize('key', ['initial_state_fingerprint', 'training_recipe_fingerprint'])
def test_frozen_stage_comparison_rejects_equal_loss_from_different_inputs(key):
    contract, record = loss_fixture()
    contract[key] = 'frozen-identity'
    bound = {**record, key: 'frozen-identity'}
    assert compare_loss(contract, bound, record)['status'] == 'incomplete'
    assert compare_loss(contract, bound, {**bound, key: 'different'})['status'] == 'incomplete'
    assert compare_loss(contract, {**bound, key: 'different'}, bound)['status'] == 'incomplete'
    assert key in compare_loss(contract, bound, bound)['matched_identity_fields']

def test_missing_required_coverage_blocks_loss_and_iteration():
    c,r=loss_fixture()
    r.update(required_missing=['backward'],profiler_off=True,measurement_protocol='paired warm runs')
    assert compare_loss(c,r,r)['status']=='incomplete'
    assert assess_iteration(r,[10,11,10],[9,10,9],'ctx')['status']=='incomplete'
    with pytest.raises(FlowError,match='min_steps'):
        compare_loss({**c,'min_steps':True},r,r)

def test_environment_requires_every_device():
    required=[{'node':'n','device':x,'check':'gemm','kind':'performance','conditions':{'dtype':'bf16'},'minimum':100,'basis':'matching peak'} for x in ('0','1')]
    m={'node':'n','device':'0','check':'gemm','conditions':{'dtype':'bf16'},'context':'c','value':120,'status':'pass','executed':1,'evidence':['raw']}
    assert assess_health({'context':'c','required':required},[m])['status']=='incomplete'
    assert assess_health({'context':'c','required':required},[m,{**m,'device':'1','value':80}])['status']=='fail'

@pytest.mark.parametrize('invalid',[{'executed':True},{'executed':1.5},{'executed':'1'},
    {'skipped_required':1},{'required_missing':['peer test']},{'failures':1}])
def test_environment_pass_requires_valid_executed_coverage(invalid):
    contract={'context':'c','required':[{'node':'n','device':'0','check':'health','conditions':{}}]}
    measurement={'context':'c','node':'n','device':'0','check':'health','conditions':{},'status':'pass','executed':1,'evidence':['raw']}
    assert assess_health(contract,[{**measurement,**invalid}])['status']=='incomplete'
