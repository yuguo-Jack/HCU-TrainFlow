"""Fetch only selected locked dependencies; private knowledge is opt-in."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from hcu_trainflow.core import FlowError
from hcu_trainflow.dependencies import sync_dependencies


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--only', nargs='+', help='Dependency IDs; default: all public dependencies')
    p.add_argument('--include-knowledge', action='store_true', help='Also fetch the optional HCU-Knowledge repository using your own Git access')
    p.add_argument('--status', action='store_true', help='Inspect only; no fetch or checkout')
    p.add_argument('--migrate-origin', action='store_true', help='Explicitly migrate a clean registered upstream baseline to its fork, preserving an upstream remote')
    args = p.parse_args()
    try:
        result = sync_dependencies(ROOT, args.only, args.include_knowledge, args.status, args.migrate_origin)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result['status'] == 'ready' else 2
    except (FlowError, OSError, ValueError, KeyError) as exc:
        print(json.dumps({'status': 'error', 'message': str(exc)}, ensure_ascii=False))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
