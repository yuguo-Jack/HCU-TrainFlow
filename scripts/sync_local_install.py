"""Refresh this project's Python package and six Skills in an existing installation.

No upstream fetch, dependency upgrade, knowledge rebuild or remote job operation.
First installation and dependency changes use setup_trainflow.py instead.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT/'scripts'))
sys.path.insert(0, str(ROOT/'src'))
from check_skill_resources import check_resources
from check_documentation import check_documentation
from install_skills import NAMES, RENAMED, checked_destination
from hcu_trainflow.core import FlowError, read_json, write_json

# -I prevents PYTHONPATH/current-directory source imports from hiding a stale install.
PACKAGE_PROBE = '''import importlib.metadata as m, json, pathlib, sys
from urllib.parse import urlsplit
from urllib.request import url2pathname
root=pathlib.Path(sys.argv[1]).resolve()
expected=root/'src/hcu_trainflow/__init__.py'
try:
    dist=m.distribution('hcu-trainflow')
except m.PackageNotFoundError:
    dist=None
try:
    import hcu_trainflow
    actual=pathlib.Path(hcu_trainflow.__file__).resolve()
    source_version=hcu_trainflow.__version__
except ModuleNotFoundError as exc:
    if exc.name != 'hcu_trainflow':
        raise
    actual=None
    source_version=None
direct=json.loads(dist.read_text('direct_url.json') or '{}') if dist else {}
url=urlsplit(direct.get('url',''))
editable=direct.get('dir_info',{}).get('editable') is True
origin=pathlib.Path(url2pathname(url.path)).resolve() if url.scheme=='file' else None
foreign=(actual is not None and actual!=expected) or (origin is not None and origin!=root)
repairable=not foreign and (dist is None or (actual==expected and origin==root))
ok=bool(dist and editable and origin==root and actual==expected and dist.version==source_version)
print(json.dumps({'status':'current' if ok else 'incomplete','version':dist.version if dist else None,
                  'module':str(actual) if actual else None,'origin':str(origin) if origin else None,
                  'editable':editable,'foreign':foreign,'repairable':repairable}))
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
    state_path = project/'.work/setup/local-sync.json'
    try:
        prior = read_json(state_path)
    except (OSError, ValueError):
        prior = {}
    if not isinstance(prior, dict):
        prior = {}
    interpreter = str(Path(sys.executable).resolve())
    same_install = prior.get('project_root') == str(project) and prior.get('metadata_interpreter') == interpreter
    state = {'status': 'running', 'project_root': str(project), 'skills_dir': str(target),
             'started_at': datetime.now(timezone.utc).isoformat(), 'completed_stages': []}
    if same_install and prior.get('metadata_fingerprint'):
        state.update(metadata_fingerprint=prior['metadata_fingerprint'], metadata_interpreter=interpreter)
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
    def package_probe():
        result = run([sys.executable, '-I', '-B', '-c', PACKAGE_PROBE, str(project)],
                     cwd=project, check=False, capture_output=True, text=True,
                     encoding='utf-8', errors='replace')
        try:
            details = json.loads(result.stdout)
        except (AttributeError, TypeError, ValueError):
            raise FlowError('package-check failed: isolated package probe did not return valid metadata')
        if not isinstance(details, dict):
            raise FlowError('package-check failed: invalid package metadata')
        state['package'] = details
        return result.returncode == 0 and details.get('status') == 'current', details
    save()
    try:
        check_existing_binding(project, target)
        resources = check_resources(project)
        if resources['issues']:
            raise FlowError('Reading resources incomplete: '+'; '.join(resources['issues']))
        documentation = check_documentation(project)
        if documentation['issues']:
            raise FlowError('Documentation inconsistent: '+'; '.join(documentation['issues']))
        state['completed_stages'].append(stage)
        stage = 'package-check'
        current, details = package_probe()
        packaging = {name: hashlib.sha256((project/name).read_bytes()).hexdigest()
                     for name in ['pyproject.toml', 'setup.cfg', 'setup.py'] if (project/name).is_file()}
        metadata_fingerprint = hashlib.sha256(json.dumps(packaging, sort_keys=True).encode()).hexdigest()
        if same_install and prior.get('metadata_fingerprint') and prior['metadata_fingerprint'] != metadata_fingerprint:
            current = False
        state['package_action'] = 'reused'
        if not current:
            if check_only:
                raise FlowError('package-check failed: installed package metadata/source is not current')
            if details.get('foreign') or not details.get('repairable'):
                raise FlowError('package-check failed: foreign/unknown package binding; inspect and explicitly repair with setup_trainflow.py')
            stage = 'package-install'
            command([sys.executable, '-m', 'pip', 'install', '--no-index', '--no-deps',
                     '--no-build-isolation', '--no-compile', '-e', str(project)])
            stage = 'package-check'
            current, _ = package_probe()
            if not current:
                raise FlowError('package-check failed: package still differs after metadata refresh')
            state['package_action'] = 'refreshed'
        state['completed_stages'].append(stage)
        state.update(metadata_fingerprint=metadata_fingerprint, metadata_interpreter=interpreter)
        save()
        installer = [sys.executable, '-B', '-X', 'utf8', str(project/'scripts/install_skills.py'),
                     '--target', str(target), '--workflow-only']
        stage = 'skills-check'
        checked = run([*installer, '--check'], cwd=project, check=False)
        state['skills_action'] = 'reused'
        if checked.returncode:
            if check_only:
                raise FlowError(f'skills-check failed (exit {checked.returncode})')
            stage = 'skills-install'
            command([*installer, '--replace'])
            stage = 'skills-check'
            command([*installer, '--check'])
            state['skills_action'] = 'refreshed'
        else:
            state['completed_stages'].append(stage)
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
