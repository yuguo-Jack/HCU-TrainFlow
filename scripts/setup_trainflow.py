"""Complete local TrainFlow setup using system Python and the user's Git access."""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from hcu_trainflow.core import FlowError, write_json
from hcu_trainflow.dependencies import bind_knowledge, knowledge_ready, require_checkout, sync_dependencies


def setup(project, skills_dir, knowledge_root=None, replace=False, run=subprocess.run):
    project = Path(project).resolve()
    record = project / '.work/setup/status.json'
    state = {'status': 'running', 'completed_stages': []}
    write_json(record, state)
    stage = 'dependencies'

    def command(name, argv, cwd=project):
        nonlocal stage
        stage = name
        state['current_stage'] = name
        write_json(record, state)
        print('Setup: ' + name, flush=True)
        # Stream output so long index builds remain visible; never capture credentials.
        result = run(argv, cwd=cwd)
        if result.returncode:
            raise FlowError(f'{name} failed (exit {result.returncode}); resolve it and rerun setup')
        state['completed_stages'].append(name)
        write_json(record, state)

    try:
        if knowledge_root:
            bind_knowledge(project, knowledge_root)
        result = sync_dependencies(project)
        state['dependencies'] = result
        write_json(record, state)
        if result['status'] != 'ready':
            missing = ', '.join(x['id'] + ':' + x['status'] for x in result['dependencies'] if x['status'] != 'ready')
            raise FlowError('Required dependencies unavailable: ' + missing + '; check Git access or use --knowledge-root')
        knowledge, _ = require_checkout(project, 'hcu-knowledge')
        tracelens, _ = require_checkout(project, 'tracelens')
        state['completed_stages'].append(stage)
        command('python-packages', [sys.executable, '-m', 'pip', 'install', '-e', str(project), '-e', str(tracelens), '-e', str(knowledge)])
        kb_state = next(x for x in result['dependencies'] if x['id'] == 'hcu-knowledge')
        if not kb_state['external']:
            command('knowledge-lfs-config', ['git', 'lfs', 'install', '--local'], knowledge)
            command('knowledge-lfs', ['git', 'lfs', 'pull'], knowledge)
        doctor = [sys.executable, '-X', 'utf8', str(knowledge/'tools/setup_workspace.py'), 'doctor']
        reusable = False
        if kb_state['external']:
            stage = 'knowledge-readiness'
            state['current_stage'] = stage
            write_json(record, state)
            probe = run(doctor, cwd=knowledge, capture_output=True, text=True, encoding='utf-8', errors='replace')
            reusable = knowledge_ready(probe)
        if reusable:
            state['completed_stages'].append('knowledge-bootstrap-reused')
            print('Setup: reusing current external knowledge index (no historical rehash)', flush=True)
        else:
            command('knowledge-bootstrap', [sys.executable, '-X', 'utf8', str(knowledge/'tools/setup_workspace.py'), 'bootstrap'], knowledge)
        command('knowledge-doctor', doctor, knowledge)
        command('skills', [sys.executable, '-X', 'utf8', str(project/'scripts/install_skills.py'), '--target', str(skills_dir), *(['--replace'] if replace else [])])
        state.update(status='ready', knowledge_root=str(knowledge), skills_dir=str(Path(skills_dir).expanduser().resolve()),
                     note='Local search and 11 Skills installed; online accounts and real HCU execution require site validation')
    except (FlowError, OSError) as exc:
        state.update(status='incomplete', failed_stage=stage, message=str(exc))
        raise
    except KeyboardInterrupt:
        state.update(status='interrupted', failed_stage=stage, message='Inspect the last stage before rerunning setup')
        raise
    finally:
        write_json(record, state)
    return state


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skills-dir', type=Path, required=True)
    parser.add_argument('--knowledge-root', type=Path, help='Reuse an existing KB without source updates; missing LFS objects must be restored there first')
    parser.add_argument('--replace', action='store_true', help='Replace installed Skills; clean temporary backups after successful verification')
    args = parser.parse_args()
    try:
        setup(ROOT, args.skills_dir, args.knowledge_root, args.replace)
    except (FlowError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print('Complete local installation ready. Restart the Agent session to discover Skills.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
