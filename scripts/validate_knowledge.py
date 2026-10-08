"""Validate Wiki IDs, pinned source hashes/paths and maintenance targets offline."""
import json
from pathlib import Path
import sys
from hcu_trainflow.wiki import parse_page

def validate(root):
    errors=[];ids=set()
    lock=json.loads((root/'knowledge/source-lock.json').read_text())
    registry=json.loads((root/'knowledge/sources.json').read_text())
    sources={x['id']:x for x in registry}
    records={(x['repo'],x['commit'],x['path']):x for x in lock['files']}
    for path in (root/'knowledge').rglob('*.md'):
        meta,_=parse_page(path)
        if not meta.get('id') or meta['id'] in ids:errors.append(str(path)+': absent/duplicate id')
        ids.add(meta.get('id'))
        for s in meta.get('sources',[]):
            source=sources.get(s['source'],{})
            record=records.get((source.get('repository'),s['commit'],s['path']))
            if not record or record['sha256']!=s['sha256']:errors.append(str(path)+': source missing/hash mismatch')
            if s['path'] not in source.get('paths',[]):errors.append(str(path)+': source not monitored')
    for rule in json.loads((root/'knowledge/maintenance.json').read_text()):
        if rule['source'] not in sources:errors.append('Unknown maintenance source')
        for target in rule['targets']:
            if not (root/target).is_file():errors.append('Missing maintenance target '+target)
    return {'pages':len(ids),'sources':len(sources),'errors':errors}

if __name__=='__main__':
    result=validate(Path(__file__).resolve().parents[1]);print(json.dumps(result,ensure_ascii=False,indent=2));sys.exit(bool(result['errors']))
