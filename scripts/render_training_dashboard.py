#!/usr/bin/env python3
"""Render a private offline SVG/HTML dashboard from one normalized training attempt."""
import argparse
import json
from pathlib import Path
import sys

_SOURCE = Path(__file__).resolve().parents[1] / "src"
if _SOURCE.exists():
    sys.path.insert(0, str(_SOURCE))

from hcu_trainflow.core import FlowError
from hcu_trainflow.training_dashboard import MODES, render_dashboard


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("normalized_log", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True, help="New/empty private output directory")
    parser.add_argument("--measurement-mode", choices=MODES, default="unspecified")
    parser.add_argument("--attempt-id", help="Select only this attempt; requires --context")
    parser.add_argument("--context", help="Select only this context; requires --attempt-id")
    parser.add_argument("--raw-log", type=Path, help="Optional collected raw log; verify referenced byte ranges/hashes")
    parser.add_argument("--allow-partial-final-line", action="store_true", help="Explicitly exclude one unterminated tail, preserving its bytes/hash")
    parser.add_argument("--throughput-metric", help="Exact numeric key already present in iteration metrics")
    parser.add_argument("--throughput-unit", help="Explicit unit for that metric, such as tokens/s")
    parser.add_argument("--title", default="Training observation snapshot")
    args = parser.parse_args()
    try:
        result = render_dashboard(args.normalized_log, args.output_dir, measurement_mode=args.measurement_mode,
                                  attempt_id=args.attempt_id, context=args.context,
                                  allow_partial_final_line=args.allow_partial_final_line, raw_log=args.raw_log,
                                  throughput_metric=args.throughput_metric, throughput_unit=args.throughput_unit,
                                  title=args.title)
    except (FlowError, OSError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
