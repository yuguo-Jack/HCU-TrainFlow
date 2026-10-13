"""Native advanced features, executed only from the reviewed dependency checkout."""
import importlib
from pathlib import Path
import sys

from .core import read_json, write_json


def run_native(module, *args):
    previous = sys.argv
    sys.argv = [module, *map(str, args)]
    try:
        try:
            code = importlib.import_module(module).main()
        except SystemExit as exc:
            code = exc.code
        if code not in (None, 0):
            raise RuntimeError('Native analysis rejected the input: ' + module)
    finally:
        sys.argv = previous


def analyze(request, output):
    mode = request['mode']
    if mode == 'compare':
        from TraceLens.Reporting.generate_perf_report_pytorch import generate_perf_report_pytorch
        common = dict(gpu_arch_json_path=request.get('gpu_arch_json'), include_unlinked_kernels=True,
                      kernel_summary=True, include_overlap_info=True)
        tables = generate_perf_report_pytorch(profile_json_path=request['trace'],
            comparison_json_path=request['comparison_trace'], output_csvs_dir=str(output / 'before'), **common)
        after = generate_perf_report_pytorch(profile_json_path=request['comparison_trace'],
            output_csvs_dir=str(output / 'after'), **common)
        signal_tables = ('ops_summary', 'unified_perf_summary', 'kernel_summary')
        if not any(len(tables.get(key, ())) for key in signal_tables) or not any(len(after.get(key, ())) for key in signal_tables):
            return {'status': 'incomplete', 'gaps': ['Comparison has no native report rows']}
        run_native('TraceLens.Reporting.compare_perf_reports_pytorch', output / 'before', output / 'after',
                   '--names', 'before', 'after', '--output', output / 'comparison.xlsx',
                   '--output_csvs_dir', output / 'comparison')
        return {'status': 'generated', 'gaps': ['Caller must match shape, phase, precision, rank and timing windows; a trace difference is not profiler-off E2E speedup']}
    if mode == 'split':
        run_native('TraceLens.TraceUtils.split_trace.main', request['trace'],
                   '--output-dir', output / 'split', '--iterations', request['iterations'])
        details_path = output / 'split/execution_details.json'
        details = read_json(details_path) if details_path.is_file() else []
        valid = bool(details) and all(row.get('event_count', 0) > 0 and Path(row['output_path']).is_file() for row in details)
        start = int(request['iterations'].split(':')[0])
        end = int(request['iterations'].split(':')[1]) if ':' in request['iterations'] else start + 1
        valid = valid and len(details) == 1 and details[0].get('idx') == f'{start}:{end}'
        return {'status': 'generated' if valid else 'incomplete', 'selection': request['iterations'], 'extractions': details,
                'gaps': ['Verify native detected annotations and extracted range against training steps; no automatic steady-state selection']}
    if mode == 'merge':
        import gzip
        import json
        from TraceLens.TraceFusion.trace_fuse import TraceFuse
        ranks = {int(rank): path for rank, path in request['traces'].items()}
        path = TraceFuse(ranks).merge_and_save(str(output / 'merged.json'))
        with gzip.open(path, 'rt', encoding='utf-8') as stream:
            events = json.load(stream)['traceEvents']
        counts = {rank: 0 for rank in ranks}
        for event in events:
            rank = event.get('args', {}).get('rank')
            if event.get('ph') == 'X' and rank in counts:
                counts[rank] += 1
        return {'status': 'generated' if all(counts.values()) else 'incomplete', 'ranks': sorted(ranks), 'duration_events_by_rank': counts,
                'gaps': ['Visualization merge does not align node clocks, prove causality or replace process-group collective analysis']}
    if mode == 'hipprof':
        from TraceLens.Reporting.hipprof import generate_perf_report_hipprof
        tables = generate_perf_report_hipprof(request['trace'], str(output / 'tables'), request.get('traceconv_path'))
        receipt = read_json(output / 'tables/qualification.json')
        status = 'generated' if receipt.get('status') == 'converted' and len(tables['kernel_summary']) else 'incomplete'
        return {'status': status, 'qualification': receipt,
                'gaps': ['HIP API and GPU dispatch evidence; no ATen shape or model phase is inferred']}
    if mode == 'graph':
        args = ['--manifest', request['manifest'], '--capture-folder', request['capture_folder'],
                '--report', output / 'graph.json', '--csvs-dir', output / 'tables']
        if request.get('gpu_arch_json'):
            args += ['--gpu-arch-json', request['gpu_arch_json']]
        run_native('TraceLens.Trace2Tree.training_graph', *args)
        result = read_json(output / 'graph.json')
        return {'status': 'generated' if result.get('status') == 'complete' else 'incomplete', 'qualification': result,
                'gaps': ['Serialized single-stream manifest required; eager CPU duration is not replay CPU time']}
    if mode == 'roofline':
        import pandas as pd
        from TraceLens.PerfModel.hcu_roofline import export_hcu_roofline
        result = export_hcu_roofline(pd.read_csv(request['perf_csv']), read_json(request['gpu_arch_json']),
                                    request.get('wallclock_time_us'))
        write_json(output / 'roofline.json', result)
        summary = result['summary']
        return {'status': 'generated' if summary['operation_rows'] and not summary['unknown_rows'] else 'incomplete',
                'qualification': summary,
                'gaps': ['Unknown operators still need modeling; measured-envelope headroom is not guaranteed speedup']}
    if mode == 'counters':
        from TraceLens.Reporting.xcompute import generate_perf_report_xcompute
        result = generate_perf_report_xcompute(request['manifest'], str(output / 'counters'))
        return {'status': 'generated' if result.get('status') == 'parsed' and result.get('captures') and not result.get('gaps') else 'incomplete', 'qualification': result,
                'gaps': ['Profiled counter/SQTT duration is not the profiler-off baseline; shape joins require explicit binding']}
    if mode == 'agent':
        from TraceLens.Reporting.generate_perf_report_pytorch import generate_perf_report_pytorch
        arch = read_json(request['gpu_arch_json'])
        generate_perf_report_pytorch(profile_json_path=request['trace'], output_csvs_dir=str(output / 'perf_report_csvs'),
                                     gpu_arch_json_path=request['gpu_arch_json'], include_unlinked_kernels=True,
                                     kernel_summary=True, include_overlap_info=True)
        run_native('TraceLens.Agent.Analysis.utils.orchestrator_prepare', '--trace-path', request['trace'],
                   '--platform', arch['name'], '--gpu-arch-json', request['gpu_arch_json'], '--output-dir', output)
        run_native('TraceLens.Agent.Analysis.utils.hcu_analysis', 'run', '--output-dir', output)
        result = read_json(output / 'hcu_native_analysis.json')
        return {'status': 'needs-agent-review', 'qualification': result,
                'gaps': ['Active workflow Agent must read category instructions, inspect raw evidence, write findings and review analysis.md',
                         'Native top-N candidates do not replace TrainFlow cumulative 90% non-communication coverage']}
    raise ValueError('Unsupported native analysis mode')


def main():
    path = Path(sys.argv[1]).resolve()
    result = analyze(read_json(path), path.parent)
    write_json(path.parent / 'worker.json', result)


if __name__ == '__main__':
    main()
