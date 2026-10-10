"""Install six workflow, three kernel and two bound HCU knowledge Skills."""
import argparse
import hashlib
from pathlib import Path
import shutil
import datetime
import sys
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from hcu_trainflow.dependencies import knowledge_ready, require_checkout
from hcu_trainflow.core import FlowError

NAMES = ('hcu-trainflow','hcu-train-adapt','hcu-train-optimize','hcu-train-fault-tolerance','hcu-engine-wiki-search','hcu-engine-wiki-skill-update')
RENAMED = {'hcu-train-prepare': 'hcu-train-adapt', 'hcu-train-operate': 'hcu-train-fault-tolerance', 'hcu-engine-wiki-update': 'hcu-engine-wiki-skill-update'}
KERNEL_NAMES = ('hygon-hip-baseline-generator', 'hygon-hip-kernel-optimizer', 'hygon-triton-kernel-optimizer')
KNOWLEDGE_NAMES = ('hcu-knowledge-search', 'hcu-knowledge-update')

def tree_hash(path):
    return {p.relative_to(path).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in path.rglob('*') if p.is_file() and '__pycache__' not in p.parts}

def checked_destination(target, name):
    path=target/name
    if path.is_symlink() or path.resolve()!=path or path.resolve().parent!=target:
        raise FlowError('Refusing redirected destination: '+str(path))
    if path.exists() and not path.is_dir():
        raise FlowError('Skill destination is not a directory: '+str(path))
    return path

def managed_backup_root(target):
    backup_root=target.parent/'trainflow-skill-backups'
    if backup_root.is_symlink() or backup_root.resolve()!=backup_root or backup_root.is_relative_to(target):
        raise FlowError('Backup directory must be unredirected and outside scanned Skills')
    return backup_root


def backup_directory(target, path):
    # Recheck resolved boundaries immediately before moving a whole directory.
    path=checked_destination(target,path.name)
    backup_root=managed_backup_root(target)
    backup=backup_root/datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')/path.name
    if not backup.resolve().is_relative_to(backup_root):
        raise FlowError('Backup must remain under its managed root')
    backup.parent.mkdir(parents=True,exist_ok=True)
    path.rename(backup)
    print(path.name+': backed up to '+str(backup))
    return backup


def cleanup_backups(target, backups):
    """Remove only this successful invocation's backups, never sweep history."""
    def check(backup):
        root=managed_backup_root(target)
        if (not backup.is_absolute() or backup.parent.parent!=root
                or backup.name not in {*NAMES, *KERNEL_NAMES, *KNOWLEDGE_NAMES, *RENAMED}
                or backup.is_symlink() or backup.resolve()!=backup or not backup.is_dir()):
            raise FlowError('Refusing unsafe backup cleanup: '+str(backup))
        for child in backup.rglob('*'):
            if child.is_symlink() or child.resolve()!=child:
                raise FlowError('Retaining backup with redirected content: '+str(backup))

    # Validate the whole set, then recheck each path immediately before deletion.
    for backup in backups:
        check(backup)
    for backup in backups:
        check(backup)
        shutil.rmtree(backup)
        if not any(backup.parent.iterdir()):
            backup.parent.rmdir()
        print(backup.name+': verified replacement; temporary backup removed')

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--target',type=Path,required=True,help='Agent skills directory; installation is explicit')
    parser.add_argument('--replace',action='store_true',help='Replace installed Skills; clean temporary backups only after all copies and bindings verify')
    parser.add_argument('--with-kernel-skills',action='store_true',help=argparse.SUPPRESS)
    parser.add_argument('--workflow-only',action='store_true',help='Developer-only six-Skill refresh; not a complete TrainFlow installation')
    args=parser.parse_args()
    sources={name: ROOT/'skills'/name for name in NAMES}
    knowledge = None
    if not args.workflow_only:
        try:
            checkout, _ = require_checkout(ROOT, 'cuda-optimized-skill')
            knowledge, _ = require_checkout(ROOT, 'hcu-knowledge')
        except FlowError as exc:
            parser.error(str(exc))
        sources.update({name: checkout/'skills'/name for name in KERNEL_NAMES})
        sources.update({name: knowledge/'skills'/name for name in KNOWLEDGE_NAMES})
        result = subprocess.run([sys.executable, '-X', 'utf8', str(knowledge/'tools/setup_workspace.py'), 'doctor'],
                                cwd=knowledge, capture_output=True, text=True, encoding='utf-8', errors='replace')
        if not knowledge_ready(result):
            parser.error('HCU-Knowledge is not locally ready; run scripts/setup_trainflow.py first')
    target=args.target.expanduser().resolve()
    expected = {name: tree_hash(source) for name, source in sources.items()}
    # Runtime bindings belong to installed Skills, never their portable source.
    bindings = {name: (json.dumps({'project_root':str(ROOT.resolve())},ensure_ascii=False,indent=2)+'\n').encode()
                for name in NAMES}
    if knowledge:
        binding=(json.dumps({'root':str(knowledge)},ensure_ascii=False,indent=2)+'\n').encode()
        for name in KNOWLEDGE_NAMES:
            bindings[name]=binding
    for name, binding in bindings.items():
        expected[name]['workspace.json']=hashlib.sha256(binding).hexdigest()
    # Validate all destinations before any mutation.
    for name, source in sources.items():
        if not (source/'SKILL.md').is_file():parser.error('Missing source Skill: '+str(source))
        dest=checked_destination(target,name)
        if dest.is_relative_to(source.resolve()) or source.resolve().is_relative_to(dest):parser.error('Install outside source Skills: '+name)
        if dest.exists() and tree_hash(dest)!=expected[name] and not args.replace:
            parser.error('Existing different installation; inspect it then use --replace: '+name)
    for old in RENAMED:
        dest=checked_destination(target,old)
        if dest.exists() and not args.replace:
            parser.error('Obsolete Skill entry found; inspect it then use --replace to install current names: '+old)
    backups=[]
    for old in RENAMED:
        dest=checked_destination(target,old)
        if dest.exists():backups.append(backup_directory(target,dest))
    for name, source in sources.items():
        dest=checked_destination(target,name)
        if dest.exists():
            if tree_hash(dest)==expected[name]:print(name+': already current');continue
            # Retain originals on any install/verification failure.
            backups.append(backup_directory(target,dest))
        shutil.copytree(source,dest,ignore=shutil.ignore_patterns('__pycache__'))
        if name in bindings:
            (dest/'workspace.json').write_bytes(bindings[name])
        print(name+': installed')
    for name in sources:
        dest=checked_destination(target,name)
        if tree_hash(dest)!=expected[name]:
            raise FlowError('Installed Skill verification failed; backups retained: '+name)
    print(f'Verified {len(sources)} installed Skills and their bindings')
    cleanup_backups(target,backups)

if __name__=='__main__':main()
