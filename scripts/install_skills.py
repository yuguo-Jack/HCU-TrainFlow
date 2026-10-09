"""Install workflow Skills and optionally the three pinned Hygon kernel Skills."""
import argparse
import hashlib
from pathlib import Path
import shutil
import datetime
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from hcu_trainflow.dependencies import require_checkout
from hcu_trainflow.core import FlowError

NAMES = ('hcu-train-prepare','hcu-train-optimize','hcu-train-operate','hcu-engine-wiki-search','hcu-engine-wiki-update')
KERNEL_NAMES = ('hygon-hip-baseline-generator', 'hygon-hip-kernel-optimizer', 'hygon-triton-kernel-optimizer')

def tree_hash(path):
    return {p.relative_to(path).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in path.rglob('*') if p.is_file()}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--target',type=Path,required=True,help='Agent skills directory; installation is explicit')
    parser.add_argument('--replace',action='store_true',help='Back up an existing different skill before replacement')
    parser.add_argument('--with-kernel-skills',action='store_true',help='Also install the three Hygon Skills from the locked thirdparty checkout')
    args=parser.parse_args()
    sources={name: ROOT/'skills'/name for name in NAMES}
    if args.with_kernel_skills:
        try:
            checkout, _ = require_checkout(ROOT, 'cuda-optimized-skill')
        except FlowError as exc:
            parser.error(str(exc))
        sources.update({name: checkout/'skills'/name for name in KERNEL_NAMES})
    target=args.target.expanduser().resolve()
    # Validate all destinations before any mutation.
    for name, source in sources.items():
        if not (source/'SKILL.md').is_file():parser.error('Missing source Skill: '+str(source))
        dest=target/name
        if dest.is_symlink():parser.error('Refusing symlink destination: '+str(dest))
        if dest.exists() and tree_hash(dest)!=tree_hash(source) and not args.replace:
            parser.error('Existing different installation; inspect it then use --replace: '+name)
    for name, source in sources.items():
        dest=target/name
        if dest.exists():
            if tree_hash(dest)==tree_hash(source):print(name+': already current');continue
            # Backups outside the scanned skills directory avoid duplicate discovery.
            backup=target.parent/'trainflow-skill-backups'/datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')/name
            backup.parent.mkdir(parents=True,exist_ok=True)
            dest.rename(backup)
        shutil.copytree(source,dest)
        print(name+': installed')

if __name__=='__main__':main()
