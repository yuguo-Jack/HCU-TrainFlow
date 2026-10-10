"""Validate Wiki IDs, pinned source hashes/paths and maintenance targets offline."""
import json
from pathlib import Path
import sys
import hashlib
from hcu_trainflow.wiki import parse_page
from hcu_trainflow.knowledge_evidence import validate_manifests

def validate(root):
    errors=[];ids=set();pr_refs=[]
    lock=json.loads((root/'knowledge/source-lock.json').read_text())
    registry=json.loads((root/'knowledge/sources.json').read_text())
    sources={x['id']:x for x in registry}
    records={(x['repo'],x['commit'],x['path']):x for x in lock['files']}
    for path in (root/'knowledge').rglob('*.md'):
        meta,body=parse_page(path)
        if not meta.get('id') or meta['id'] in ids:errors.append(str(path)+': absent/duplicate id')
        ids.add(meta.get('id'))
        pr_refs.extend((path,pid) for pid in meta.get('pr_sources',[]))
        if meta.get('kind') in {'source-pr','source-map','source-document'}:
            if meta.get('generated_body_sha256')!=hashlib.sha256(body.encode()).hexdigest():errors.append(str(path)+': generated source page modified')
        if meta.get('kind')=='source-pr':
            raw=(root/meta.get('artifact_path','')).resolve()
            if not raw.is_relative_to((root/'knowledge/evidence/prs').resolve()) or not raw.is_file():errors.append(str(path)+': missing PR evidence')
            elif hashlib.sha256(raw.read_bytes()).hexdigest()!=meta.get('artifact_sha256'):errors.append(str(path)+': PR evidence hash mismatch')
        for s in meta.get('sources',[]):
            source=sources.get(s['source'],{})
            record=records.get((source.get('repository'),s['commit'],s['path']))
            if not record or record['sha256']!=s['sha256']:errors.append(str(path)+': source missing/hash mismatch')
            if s['path'] not in source.get('paths',[]):errors.append(str(path)+': source not monitored')
    for path,pid in pr_refs:
        if pid not in ids:errors.append(str(path)+': missing related PR source '+pid)
    for rule in json.loads((root/'knowledge/maintenance.json').read_text()):
        if rule['source'] not in sources:errors.append('Unknown maintenance source')
        for target in rule['targets']:
            if not (root/target).is_file():errors.append('Missing maintenance target '+target)
    errors.extend(validate_manifests(root))
    return {'pages':len(ids),'sources':len(sources),'errors':errors}

if __name__=='__main__':
    result=validate(Path(__file__).resolve().parents[1]);print(json.dumps(result,ensure_ascii=False,indent=2));sys.exit(bool(result['errors']))
