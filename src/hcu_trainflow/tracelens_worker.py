"""Isolated TraceLens public API invocation; stdout/stderr belong to the report."""
import argparse
import json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['pytorch', 'collective'])
    parser.add_argument('request')
    args = parser.parse_args()
    with open(args.request, encoding='utf-8') as stream:
        kwargs = json.load(stream)
    if args.mode == 'pytorch':
        from TraceLens.Reporting.generate_perf_report_pytorch import generate_perf_report_pytorch
        generate_perf_report_pytorch(**kwargs)
    else:
        from TraceLens.Reporting.generate_multi_rank_collective_report_pytorch import generate_collective_report
        generate_collective_report(**kwargs)


if __name__ == '__main__':
    main()
