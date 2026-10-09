"""Bounded device diagnostics in an already admitted remote training environment.

No site defaults or resource reservation. The coordinator must perform a fresh
occupancy check before --run-benchmarks. These measurements are observed rates,
not hardware peak certification or a replacement for NHC/RCCL acceptance.
"""
import argparse
import datetime
import importlib.metadata
import json
from pathlib import Path
import statistics
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--devices', required=True, help='Explicit visible device indices, comma separated')
    parser.add_argument('--output', required=True)
    parser.add_argument('--run-benchmarks', action='store_true')
    parser.add_argument('--trace', help='Optional diagnostic forward/backward trace on first selected device')
    args = parser.parse_args()
    devices = [int(x) for x in args.devices.split(',')]
    if not devices or len(set(devices)) != len(devices) or min(devices) < 0:
        parser.error('Select distinct nonnegative device indices')
    if args.trace and not args.run_benchmarks:
        parser.error('Trace collection executes GPU work; requires --run-benchmarks')
    import torch
    torch.set_num_threads(8)
    if max(devices) >= torch.cuda.device_count():
        parser.error('Device index is not visible to this process')
    report = {'schema_version': 1, 'observed_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'kind': 'torch-device-diagnostic', 'torch': torch.__version__, 'hip': torch.version.hip,
              'packages': {}, 'devices': [], 'limits': 'Bounded local diagnostics only; no full environment, hardware-peak, model or communication acceptance.'}
    for name in ['torch', 'triton', 'transformer-engine', 'flash-linear-attention', 'fla-core']:
        try: report['packages'][name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError: report['packages'][name] = None
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    def save():
        temporary = output.with_suffix(output.suffix + '.tmp')
        temporary.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
        temporary.replace(output)

    def measure(fn, warmup=10, iterations=30, repeats=3):
        for _ in range(warmup): fn()
        torch.cuda.synchronize()
        samples = []
        for _ in range(repeats):
            start, end = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
            start.record()
            for _ in range(iterations): fn()
            end.record(); end.synchronize()
            samples.append(start.elapsed_time(end) / iterations)
        return {'warmup': warmup, 'iterations': iterations, 'repeats': repeats, 'milliseconds_per_call': samples, 'median_ms': statistics.median(samples), 'timer': 'device-events', 'profiler': False}

    for index in devices:
        torch.cuda.set_device(index)
        prop = torch.cuda.get_device_properties(index)
        item = {'index': index, 'name': prop.name, 'gcn_arch': getattr(prop, 'gcnArchName', None),
                'total_memory_bytes': prop.total_memory, 'multiprocessors': prop.multi_processor_count,
                'uuid': str(getattr(prop, 'uuid', 'unknown')), 'benchmarks': []}
        report['devices'].append(item)
        if args.run_benchmarks:
            torch.manual_seed(1234)
            # Small independent CPU FP32 reference: integer operands make the
            # BF16 expected output exactly representable for this test shape.
            a_cpu = torch.randint(-1, 2, (64, 64)).float()
            b_cpu = torch.randint(-1, 2, (64, 64)).float()
            got = a_cpu.to(index, dtype=torch.bfloat16) @ b_cpu.to(index, dtype=torch.bfloat16)
            error = (got.float().cpu() - a_cpu @ b_cpu).abs().max().item()
            item['correctness'] = {'shape': [64, 64, 64], 'dtype': 'bf16', 'max_abs_error': error, 'passed': error == 0, 'reference': 'CPU FP32 matmul of {-1,0,1} operands'}
            if error != 0:
                save(); raise RuntimeError('Diagnostic GEMM correctness failed')
            for size in (4096, 8192):
                a = torch.randn((size, size), device=index, dtype=torch.bfloat16)
                b = torch.randn_like(a); c = torch.empty_like(a)
                result = measure(lambda: torch.mm(a, b, out=c))
                result.update(kind='gemm', shape=[size, size, size], dtype='bf16', flops=2*size**3,
                              measured_tflops=(2*size**3)/(result['median_ms']*1e9))
                item['benchmarks'].append(result)
                del a, b, c
            count = 128 * 1024 * 1024
            source = torch.ones(count, device=index, dtype=torch.float32)
            target = torch.empty_like(source)
            result = measure(lambda: target.copy_(source))
            result.update(kind='device-copy', bytes_read_plus_written=2*count*4,
                          measured_gb_s=(2*count*4)/(result['median_ms']*1e6), working_set_bytes=2*count*4)
            item['benchmarks'].append(result)
            item['copy_correctness'] = bool(torch.equal(source, target))
            del source, target
            item['peak_allocated_bytes'] = torch.cuda.max_memory_allocated(index)
            torch.cuda.empty_cache()
        save()
    if args.trace:
        index = devices[0]; torch.cuda.set_device(index)
        layer = torch.nn.Linear(2048, 2048, bias=False, device=index, dtype=torch.bfloat16)
        value = torch.randn((256, 2048), device=index, dtype=torch.bfloat16, requires_grad=True)
        for _ in range(3):
            layer.zero_grad(set_to_none=True); value.grad = None
            layer(value).float().square().mean().backward()
        torch.cuda.synchronize()
        with torch.profiler.profile(activities=[torch.profiler.ProfilerActivity.CPU, torch.profiler.ProfilerActivity.CUDA], record_shapes=True, profile_memory=True, with_stack=False) as profiler:
            for step in range(3):
                with torch.profiler.record_function(f'trainflow_diagnostic_step_{step}'):
                    layer.zero_grad(set_to_none=True); value.grad = None
                    layer(value).float().square().mean().backward()
                    torch.cuda.synchronize()
                profiler.step()
        trace = Path(args.trace); trace.parent.mkdir(parents=True, exist_ok=True)
        profiler.export_chrome_trace(str(trace))
        report['trace'] = {'path': str(trace), 'scope': 'single-rank diagnostic forward/backward, not Kimi-K3', 'steps': 3, 'rank': 0}
        save()
    print(json.dumps(report))


if __name__ == '__main__':
    main()
