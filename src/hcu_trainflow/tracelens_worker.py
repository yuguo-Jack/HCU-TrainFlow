"""Isolated TraceLens public API invocation; stdout/stderr belong to the report."""
import argparse
import importlib.metadata
import json
from pathlib import Path
import sys
import warnings

from .core import write_json


def summarize_warnings(records):
    """Retain native analysis limits without treating every numerical warning as fatal."""
    result = {}
    for record in records:
        message = str(record.message)
        key = (record.category.__name__, message, record.filename, record.lineno)
        row = result.setdefault(key, {'category': key[0], 'message': message,
                                      'filename': record.filename, 'lineno': record.lineno,
                                      'count': 0, 'code': 'native-warning'})
        row['count'] += 1
        if 'Inconsistent kernel list length found. Skipping a row.' in message:
            row['code'] = 'native-kernel-detail-samples-skipped'
    return list(result.values())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['pytorch', 'collective'])
    parser.add_argument('request')
    args = parser.parse_args()
    with open(args.request, encoding='utf-8') as stream:
        kwargs = json.load(stream)
    attribution_request = kwargs.pop('_trainflow_attribution', None)
    captured = []
    try:
        with warnings.catch_warnings(record=True) as captured:
            if args.mode == 'pytorch':
                from TraceLens.Reporting.generate_perf_report_pytorch import generate_perf_report_pytorch
                tables = generate_perf_report_pytorch(**kwargs)
            else:
                from TraceLens.Reporting.generate_multi_rank_collective_report_pytorch import generate_collective_report
                tables = generate_collective_report(**kwargs)
    finally:
        # Preserve the original diagnostic channel even if native analysis fails.
        for record in captured:
            sys.stderr.write(warnings.formatwarning(record.message, record.category,
                                                    record.filename, record.lineno))
    native_warnings = summarize_warnings(captured)
    # Save the public API's actual result, independently of files left in the
    # output directory. A GPU-only table must not imply CPU operator attribution.
    if not isinstance(tables, dict):
        raise RuntimeError('TraceLens public API returned no table mapping')
    versions = {}
    for name in ('pandas', 'numpy', 'orjson'):
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    summary = {name: {'rows': len(table), 'columns': [str(x) for x in table.columns]}
               for name, table in tables.items()}
    if attribution_request is not None:
        from .tracelens import export_attribution
        if args.mode != 'pytorch':
            raise RuntimeError('Attribution requires a single-rank PyTorch trace')
        attribution = export_attribution(kwargs['profile_json_path'], **attribution_request)
        write_json(Path(args.request).parent / 'attribution.json', attribution)
    write_json(Path(args.request).parent / 'worker.json',
               {'python': sys.version, 'python_executable': sys.executable,
                'package_versions': versions, 'mode': args.mode, 'tables': summary,
                'native_warnings': native_warnings,
                'cpu_attribution_rows': summary.get('ops_summary', {}).get('rows', 0)})


if __name__ == '__main__':
    main()
