"""Install five Skills; preserve existing different installations unless --replace."""
import argparse
import hashlib
from pathlib import Path
import shutil
import datetime

NAMES = ('hcu-train-prepare','hcu-train-optimize','hcu-train-operate','hcu-engine-wiki-search','hcu-engine-wiki-update')

def tree_hash(path):
    return {p.relative_to(path).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in path.rglob('*') if p.is_file()}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--target',type=Path,required=True,help='Agent skills directory; installation is explicit')
    parser.add_argument('--replace',action='store_true',help='Back up an existing different skill before replacement')
    args=parser.parse_args()
    source=Path(__file__).resolve().parents[1]/'skills'
    target=args.target.expanduser().resolve()
    # Validate all destinations before any mutation.
    for name in NAMES:
        dest=target/name
        if dest.is_symlink():parser.error('Refusing symlink destination: '+str(dest))
        if dest.exists() and tree_hash(dest)!=tree_hash(source/name) and not args.replace:
            parser.error('Existing different installation; inspect it then use --replace: '+name)
    for name in NAMES:
        dest=target/name
        if dest.exists():
            if tree_hash(dest)==tree_hash(source/name):print(name+': already current');continue
            # Backups outside the scanned skills directory avoid duplicate discovery.
            backup=target.parent/'trainflow-skill-backups'/datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')/name
            backup.parent.mkdir(parents=True,exist_ok=True)
            dest.rename(backup)
        shutil.copytree(source/name,dest)
        print(name+': installed')

if __name__=='__main__':main()
