"""Independent native Torch foreach-copy qualification; never changes a model.

Contract: detached contiguous disjoint FP32 -> BF16 pairs, exact native copy_
bytes (including NaNs/subnormals), sources unchanged. No alias/capture claim.
"""
import argparse
from pathlib import Path
import hashlib,json,time,statistics,gzip
import torch

p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args()
out=Path(a.output);out.mkdir(parents=True,exist_ok=False)
report={'contract':'Bitwise parity to sequential copy_ including finite rounding, signed zero, subnormal and NaN payload; source unchanged; this is standalone, not model loss/performance','torch':torch.__version__,'torch_git':torch.version.git_version,'hip':torch.version.hip,'cases':[],'benchmarks':[]}
def save(): (out/'result.json').write_text(json.dumps(report,indent=2)+'\n')
def sequential(dst,src):
 for d,s in zip(dst,src):d.copy_(s)
def foreach(dst,src): torch._foreach_copy_(dst,src)
def check(name,source,shapes):
 # Single contiguous backing, including offset, preserves exact source bits.
 source=source.cuda();old=source.view(torch.uint8).clone();n=source.numel()
 dst=torch.full((n+2,),-7.,dtype=torch.bfloat16,device='cuda');expected=dst.clone()
 sources=[];targets=[];refs=[];offset=0
 for shape in shapes:
  size=1
  for dim in shape:size*=dim
  sources.append(source[offset:offset+size].reshape(shape));targets.append(dst[1+offset:1+offset+size].reshape(shape));refs.append(expected[1+offset:1+offset+size].reshape(shape));offset+=size
 assert offset==n
 sequential(refs,sources);foreach(targets,sources);torch.cuda.synchronize()
 errors=int((dst.view(torch.uint8)!=expected.view(torch.uint8)).count_nonzero().item());source_errors=int((source.view(torch.uint8)!=old).count_nonzero().item())
 row={'case':name,'pairs':len(shapes),'source_elements':n,'mismatched_destination_bytes':errors,'modified_source_bytes':source_errors,'passed':errors==source_errors==0};report['cases'].append(row);save()
 if not row['passed']: raise RuntimeError('Native foreach copy differs; candidate rejected without model changes')

with torch.no_grad():
 g=torch.Generator().manual_seed(20261010)
 shapes=[(),(0,),(1,),(3,),(4,),(5,),(127,),(128,),(129,),(65535,),(65536,),(65537,),(128,128),(256,128)]
 n=sum(__import__('math').prod(x) for x in shapes)
 check('tails_empty_scalar_expert_shapes',torch.randn(n,generator=g),shapes)
 high=torch.arange(65536,dtype=torch.int64).repeat_interleave(6)<<16
 low=torch.tensor([0,1,0x7fff,0x8000,0x8001,0xffff],dtype=torch.int64).repeat(65536)
 bits=(high|low).to(torch.int32).view(torch.float32)
 check('all_bf16_highwords_six_rounding_lowwords',bits,[(bits.numel(),)])
 check('many_empty_and_offset',torch.randn(17,generator=g),[(0,)]*130+[(17,)]+[(0,)]*70)
 # EP2 actual per-rank expert projection count =12*448*2=10752.
 for count in (64,1024,10752):
  shapes=[(256,128)]*(count//2)+[(128,128)]*(count//2)
  elements=sum(x*y for x,y in shapes)
  source=torch.randn(elements,device='cuda',dtype=torch.float32)
  dst=torch.empty(elements,dtype=torch.bfloat16,device='cuda');ref=torch.empty_like(dst)
  srcs=[];dsts=[];refs=[];off=0
  for x,y in shapes:
   size=x*y;srcs.append(source[off:off+size].view(x,y));dsts.append(dst[off:off+size].view(x,y));refs.append(ref[off:off+size].view(x,y));off+=size
  sequential(refs,srcs);foreach(dsts,srcs);torch.cuda.synchronize()
  mismatches=int((dst.view(torch.uint8)!=ref.view(torch.uint8)).count_nonzero().item())
  report['cases'].append({'case':'actual-expert-shapes-'+str(count),'pairs':count,'mismatched_destination_bytes':mismatches,'passed':mismatches==0});save()
  if mismatches:raise RuntimeError('Large-list parity failed')
  measurements=[]
  for label,fn in [('native-loop',sequential),('native-foreach',foreach),('native-foreach',foreach),('native-loop',sequential)]:
   for _ in range(3):fn(dsts,srcs)
   torch.cuda.synchronize();wall=[];gpu=[]
   for _ in range(10):
    start=torch.cuda.Event(enable_timing=True);end=torch.cuda.Event(enable_timing=True)
    torch.cuda.synchronize();t=time.perf_counter();start.record();fn(dsts,srcs);end.record();end.synchronize();wall.append((time.perf_counter()-t)*1000);gpu.append(start.elapsed_time(end))
   measurements.append({'implementation':label,'cpu_to_completion_ms':wall,'device_event_ms':gpu,'median_wall_ms':statistics.median(wall),'median_gpu_ms':statistics.median(gpu)})
  report['benchmarks'].append({'pairs':count,'elements':elements,'logical_bytes':elements*6,'warmup_per_block':3,'repeats_per_block':10,'order':'A B B A','timing':'synchronized CPU-to-completion and device event include submissions; not raw kernel sum','measurements':measurements});save()
  if count==1024:
   with torch.profiler.profile(activities=[torch.profiler.ProfilerActivity.CPU,torch.profiler.ProfilerActivity.CUDA],record_shapes=True) as prof:
    with torch.profiler.record_function('sequential_copy_1024'):sequential(dsts,srcs)
    torch.cuda.synchronize()
    with torch.profiler.record_function('foreach_copy_1024'):foreach(dsts,srcs)
    torch.cuda.synchronize()
   trace=out/'trace.json';prof.export_chrome_trace(str(trace));raw=trace.read_bytes();(out/'trace.json.gz').write_bytes(gzip.compress(raw,mtime=0));trace.unlink()
   report['trace_sha256']=hashlib.sha256(raw).hexdigest();save()
  del srcs,dsts,refs,source,dst,ref
 report['status']='standalone-qualified';save();print(json.dumps({'status':report['status'],'result':str(out/'result.json'),'limits':'No model integration or stage-loss qualification'}))
