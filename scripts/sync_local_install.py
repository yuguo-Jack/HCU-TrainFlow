"""Refresh this project's Python package and six Skills in an existing installation.

No upstream fetch, dependency upgrade, knowledge rebuild or remote job operation.
First installation and dependency changes use setup_trainflow.py instead.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT/'scripts'))
sys.path.insert(0, str(ROOT/'src'))
from check_skill_resources import check_resources
from install_skills import NAMES, RENAMED, checked_destination
from hcu_trainflow.core import FlowError, write_json

# -I prevents PYTHONPATH/current-directory source imports from hiding a stale install.
PACKAGE_PROBE = '''import importlib.metadata as m, json, pathlib, sys
from urllib.parse import urlsplit
from urllib.request import url2pathname
import hcu_trainflow
root=pathlib.Path(sys.argv[1]).resolve()
dist=m.distribution('hcu-trainflow')
direct=json.loads(dist.read_text('direct_url.json') or '{}')
url=urlsplit(direct.get('url',''))
editable=direct.get('dir_info',{}).get('editable') is True
origin=pathlib.Path(url2pathname(url.path)).resolve() if url.scheme=='file' else None
actual=pathlib.Path(hcu_trainflow.__file__).resolve()
expected=root/'src/hcu_trainflow/__init__.py'
ok=editable and origin==root and actual==expected and dist.version==hcu_trainflow.__version__
print(json.dumps({'status':'current' if ok else 'incomplete','version':dist.version,'module':str(actual),'editable':editable}))
sys.exit(0 if ok else 1)
'''


def check_existing_binding(project, target):
    """Do not silently replace another checkout's Skills or pretend to do first setup."""
    for name in NAMES:
        candidates = [name, *(old for old, new in RENAMED.items() if new == name)]
        found = False
        for entry in candidates:
            dest = checked_destination(target, entry)
            if not dest.exists():
                continue
            found = True
            try:
                binding = json.loads((dest/'workspace.json').read_text(encoding='utf-8'))
                bound = binding['project_root']
                valid = isinstance(bound, str) and Path(bound).is_absolute() and Path(bound).resolve() == project
            except (OSError, ValueError, KeyError, TypeError):
                valid = False
            if not valid:
                raise FlowError(f'{entry}: missing/foreign project binding; inspect and explicitly rebind with setup_trainflow.py --replace')
        if not found:
            raise FlowError(f'{name}: not installed; use setup_trainflow.py for installation/repair')


def sync(project, target, *, check_only=False, run=subprocess.run):
    project, target = Path(project).resolve(), Path(target).expanduser().resolve()
    state = {'status': 'running', 'project_root': str(project), 'skills_dir': str(target),
             'started_at': datetime.now(timezone.utc).isoformat(), 'completed_stages': []}
    state_path = project/'.work/setup/local-sync.json'
    stage = 'preflight'
    def save():
        if not check_only:
            write_json(state_path, state)
    def command(argv):
        result = run(argv, cwd=project, check=False)
        if result.returncode:
            raise FlowError(f'{stage} failed (exit {result.returncode})')
        state['completed_stages'].append(stage)
        save()
    save()
    try:
        check_existing_binding(project, target)
        resources = check_resources(project)
        if resources['issues']:
            raise FlowError('Reading resources incomplete: '+'; '.join(resources['issues']))
        state['completed_stages'].append(stage)
        if not check_only:
            stage = 'package-install'
            command([sys.executable, '-m', 'pip', 'install', '--no-deps', '--no-build-isolation', '-e', str(project)])
        stage = 'package-check'
        command([sys.executable, '-I', '-B', '-c', PACKAGE_PROBE, str(project)])
        installer = [sys.executable, '-B', '-X', 'utf8', str(project/'scripts/install_skills.py'),
                     '--target', str(target), '--workflow-only']
        if not check_only:
            stage = 'skills-install'
            command([*installer, '--replace'])
        stage = 'skills-check'
        command([*installer, '--check'])
        state['status'] = 'current'
        state['scope'] = 'TrainFlow package, six Skills, bindings and reading resources; external dependencies not requalified'
        save()
        return state
    except (FlowError, OSError, ValueError, KeyboardInterrupt) as exc:
        state.update(status='interrupted' if isinstance(exc, KeyboardInterrupt) else 'incomplete',
                     failed_stage=stage, error=str(exc))
        save()
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', type=Path, required=True, help='Actual Agent Skills directory; never inferred from cwd')
    parser.add_argument('--check', action='store_true', help='Read-only verification; no pip, file writes or replacements')
    args = parser.parse_args()
    try:
        result = sync(ROOT, args.target, check_only=args.check)
    except (FlowError, OSError, ValueError) as exc:
        parser.exit(1, str(exc)+'\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
