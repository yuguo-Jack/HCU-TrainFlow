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

def test_environment_requires_every_device():
    required=[{'node':'n','device':x,'check':'gemm','kind':'performance','conditions':{'dtype':'bf16'},'minimum':100,'basis':'matching peak'} for x in ('0','1')]
    m={'node':'n','device':'0','check':'gemm','conditions':{'dtype':'bf16'},'context':'c','value':120,'status':'pass','executed':1,'evidence':['raw']}
    assert assess_health({'context':'c','required':required},[m])['status']=='incomplete'
    assert assess_health({'context':'c','required':required},[m,{**m,'device':'1','value':80}])['status']=='fail'
