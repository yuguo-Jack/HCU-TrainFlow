"""Check the source distribution contract with the real build backend offline."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile


def test_sdist_retains_declared_evidence_assets_and_excludes_local_checkouts(tmp_path):
    root=Path(__file__).resolve().parents[1]
    project=tmp_path/'project';project.mkdir()
    for name in ('pyproject.toml','MANIFEST.in','README.md','LICENSE','CHANGELOG.md','CONTRIBUTING.md','THIRD_PARTY_NOTICES.md'):
        shutil.copy2(root/name,project/name)
    module=project/'src/hcu_trainflow/__init__.py';module.parent.mkdir(parents=True)
    module.write_text('"""Source distribution fixture."""\n')
    files={
        'docs/assets/workflow-overview.png':b'fixture image',
        'thirdparty/KNOWLEDGE-NOTICES.md':b'Upstream knowledge attribution\n',
        'thirdparty/licenses/upstream/LICENSE':b'Original upstream license\n',
        'thirdparty/licenses/upstream/NOTICE':b'Original upstream notice\n',
        'knowledge/sites/site/evidence/result.csv':b'bandwidth,unit\n1,GB/s\n',
        'knowledge/sites/site/evidence/network.json.gz':b'compressed fixture',
        'knowledge/sites/site/evidence/all-ranks.zip':b'archive fixture',
        'knowledge/sites/site/evidence/rank-00.stdout':b'output fixture',
        'knowledge/sites/site/evidence/hostfile_slots':b'host slots=1\n',
        'knowledge/sites/site/evidence/probe.py':b'# retained probe\n',
        'knowledge/sites/site/evidence/site-env.sh':b'# retained environment\n',
        'knowledge/experiments/final/evidence/final-result.bin':b'final milestone fixture',
    }
    for name,data in files.items():
        path=project/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    for section,name in [('sites','site'),('experiments','final')]:
        base=project/'knowledge'/section/name
        rows=[{'path':str(Path(p).relative_to(base.relative_to(project))).replace('\\','/'),
               'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),
               'source':'fixture','representation':'original','source_sha256':hashlib.sha256(data).hexdigest()}
              for p,data in files.items() if p.startswith(base.relative_to(project).as_posix()+'/')]
        (base/'manifest.json').write_text(json.dumps({'schema_version':1,'files':rows}))
    omitted=['.work/private.json','thirdparty/TraceLens/private.json','thirdparty/cuda-optimized-skill/private.json','thirdparty/HCU-Knowledge/private.json']
    for name in omitted:
        path=project/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text('{}')
    out=tmp_path/'out';out.mkdir()
    command=[sys.executable,'-c','import sys; import setuptools.build_meta as b; b.build_sdist(sys.argv[1])',str(out)]
    result=subprocess.run(command,cwd=project,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=60)
    assert result.returncode==0,result.stdout+result.stderr
    archives=list(out.glob('*.tar.gz'));assert len(archives)==1
    with tarfile.open(archives[0]) as archive:
        prefix=archive.getnames()[0].split('/')[0]
        members={name.removeprefix(prefix+'/'):name for name in archive.getnames()}
        for name,data in files.items():
            assert name in members,'Source distribution lost declared evidence or linked asset: '+name
            assert archive.extractfile(members[name]).read()==data
        assert all(name not in members for name in omitted)
