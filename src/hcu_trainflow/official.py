"""Public upstream discovery, PR source pages and immutable code navigation.

Acquisition pages are explicitly source-reported. They never stand in for an
authored mechanism/case or runtime validation. Ordinary reads remain private.
"""
import base64
import fnmatch
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import re
from urllib.parse import quote, urlencode

import yaml

from . import wiki
from . import knowledge_layout as layout
from .core import FlowError, atomic_write, child, digest, fingerprint, read_json, safe_id, utc, write_json


def repo_name(repo):
    repo = repo.removeprefix('https://github.com/').removesuffix('.git').rstrip('/')
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repo) or any(x in {'.', '..'} for x in repo.split('/')):
        raise FlowError('Expected public GitHub owner/repository')
    return repo


def api(repo, suffix, token=None):
    return wiki._get_json('https://api.github.com/repos/' + repo_name(repo) + suffix, token)


def source_for(project, identity):
    layout.require_local_owner(project, identity)
    source=next((s for s in read_json(Path(project)/'knowledge/sources.json') if s['id'] == identity), None)
    if source:
        layout.require_local_owner(project, source['repository'])
    return source


def engine_repos(project, engine=None, source=None, repos=()):
    if source:
        layout.require_local_owner(project, source)
    registry = read_json(Path(project)/'knowledge/sources.json')
    ids = set()
    if engine:
        for path in (Path(project)/'knowledge').rglob('*.md'):
            meta, _ = wiki.parse_page(path)
            if meta.get('engine') == engine:
                ids.update(s['source'] for s in meta.get('sources', []))
    selected = [s['repository'] for s in registry if s.get('kind') != 'web'
                and (s['id'] == source if source else (engine and (s.get('engine')==engine or (not s.get('engine') and s['id'] in ids))))]
    if source and not selected:
        raise FlowError('Select a registered Git source')
    return list(dict.fromkeys(repo_name(r) for r in [*selected, *repos]))


def search_prs(store, query, repos, token=None, limit=10, state='all', branch=None, page=1):
    if not query.strip() or len(query) > 240 or not 1 <= limit <= 100 or not 1 <= page <= 10:
        raise FlowError('Use concise terms, limit 1..100 and page 1..10')
    if state not in {'all','open','closed','merged'}:
        raise FlowError('Invalid PR state')
    from .capture_policy import public_query_risk
    if public_query_risk(query):
        return {'status':'public-query-required','results':[],'coverage':[],
                'instruction':'Extract public mechanism or symbol terms; pasted private context was kept local.'}
    terms = re.findall(r'[\w./+-]+', query, re.UNICODE)[:20]
    if not terms:
        raise FlowError('No search terms')
    if not repos:
        return {'status':'scope-required', 'results':[], 'instruction':'Select an engine, source or repository.'}
    repositories=list(dict.fromkeys(repo_name(repo) for repo in repos))
    result = {'query':query, 'queried_at':utc(), 'results':[], 'coverage':[],
              'query_scope':{'repositories':repositories,'state':state,'branch':branch,'page':page,'limit':limit}}
    for repo in repositories:
        q = f'is:pr repo:{repo} ' + ' '.join('"'+t+'"' for t in terms)
        if state != 'all': q += ' is:' + state
        if branch: q += ' base:"' + branch.replace('"','') + '"'
        report = {'repository':repo, 'complete':False}
        result['coverage'].append(report)
        try:
            data, links = wiki._get_json('https://api.github.com/search/issues?' + urlencode({'q':q,'per_page':limit,'page':page}), token)
            more = bool(re.search(r'rel="next"',links))
            report.update(total=data['total_count'],complete=not more and not data.get('incomplete_results'),
                          next_page=page+1 if more else None,platform_incomplete=data.get('incomplete_results',False))
            for rank, row in enumerate(data['items']):
                result['results'].append({'repository':repo,'number':row['number'],'title':row['title'],
                    'url':row['html_url'],'state':row['state'],'updated_at':row['updated_at'],'rank':rank,
                    'next':['wiki-pr',repo,str(row['number'])]})
        except (FlowError, OSError, ValueError) as exc:
            report['error'] = str(exc)[:240]
    result['display_truncated'] = len(result['results']) > limit
    result['results'] = sorted(result['results'],key=lambda r:r['rank'])[:limit]
    result['status'] = 'ok' if all(c['complete'] for c in result['coverage']) and not result['display_truncated'] else 'partial'
    if result['display_truncated']:
        result['instruction']='Combined result limit reached; query individual repositories to inspect omitted candidates.'
    payload={key:value for key,value in result.items() if key!='queried_at'}
    result['artifact'] = store.put(json.dumps(payload,ensure_ascii=False,sort_keys=True).encode())
    return result


def annotate_prs(project, result):
    for row in result.get('results',[]):
        path=layout.pr_root(project,row['repository'])/f'PR-{row["number"]}.md'
        meta,_=wiki.parse_page(path) if path.exists() else ({},'')
        row['locally_retained']=bool(meta)
        row['local_page_id']=meta.get('id')
        row['upstream_changed']=meta.get('updated_at')!=row['updated_at'] if meta else None
        row['discussion_recheck_required']=False
        row['discussion_reading']='on-demand'
    return result


def read_code(store, repo, commit, path, token=None, max_chars=24000):
    repo = repo_name(repo)
    if not re.fullmatch('[0-9a-f]{40}',commit):
        raise FlowError('Code reads require full fixed commit SHA')
    if not path or path.startswith('/') or '\\' in path or any(x in {'','..','.'} for x in path.split('/')) or '\n' in path:
        raise FlowError('Expected repository-relative path')
    if not 1 <= max_chars <= 1000000:
        raise FlowError('max-chars must be 1..1000000')
    key = fingerprint([repo,commit,path])
    pointer = store.root/'wiki/code'/f'{key}.json'
    if pointer.exists():
        retained = read_json(pointer)
        data = store.artifact(retained['artifact'])
    else:
        info, _ = api(repo,'/contents/'+quote(path,safe='/')+'?ref='+commit,token)
        if not isinstance(info,dict) or info.get('encoding') != 'base64':
            raise FlowError('Content API unavailable for this path; use pinned Git checkout for large files/submodules')
        data = base64.b64decode(info['content'])
        if b'\0' in data:
            raise FlowError('Binary source; use an appropriate original viewer')
        retained={'repository':repo,'commit':commit,'path':path,'artifact':store.put(data),
                  'url':f'https://github.com/{repo}/blob/{commit}/'+quote(path,safe='/')}
        write_json(pointer,retained)
    text=data.decode('utf-8')
    return {**retained,'content':text[:max_chars],'truncated':len(text)>max_chars,'lines':len(text.splitlines())}


def read_pr(store, repo, number, token=None, max_pages=20, *, discussions=None, files=None):
    repo=repo_name(repo)
    if number <= 0 or not 1 <= max_pages <= 100:
        raise FlowError('Positive PR number and max-pages 1..100 required')
    base=f'https://api.github.com/repos/{repo}/pulls/{number}'
    detail,_=wiki._get_json(base,token)
    # None preserves old internal callers. The user-facing CLI explicitly
    # requests body/pins only unless deeper reading is selected.
    discussions = True if discussions is None else discussions
    files = True if files is None else files
    data={'repository':repo,'number':number,'detail':detail,'coverage':{},'observed_at':utc()}
    urls={'issue_comments':f'https://api.github.com/repos/{repo}/issues/{number}/comments',
          'inline_comments':base+'/comments','reviews':base+'/reviews','files':base+'/files'}
    for key,url in urls.items():
        if not (files if key == 'files' else discussions):
            data[key]=[]
            data['coverage'][key]={'complete':False,'requested':False,'pages':0,
                                   'next_url':None,'error':None,'reason':'on demand'}
            continue
        rows=[]; pages=0; error=None; seen=set(); url+='?per_page=100'
        while url and pages<max_pages:
            try:
                if url in seen: raise FlowError('Nonadvancing pagination')
                seen.add(url)
                body,links=wiki._get_json(url,token)
                if not isinstance(body,list): raise FlowError('Expected paginated array')
                rows.extend(body); pages+=1
                match=re.search(r'<([^>]+)>; rel="next"',links)
                url=match[1] if match else None
            except (FlowError,OSError,ValueError) as exc:
                error=str(exc)[:240];break
        data[key]=rows
        data['coverage'][key]={'complete':not url,'pages':pages,'next_url':url,'error':error}
    data['coverage']['diff_complete']=bool(files and len(data['files'])==detail.get('changed_files') and all(f.get('patch') for f in data['files']))
    data['scope']={'body':True,'discussions':discussions,'files':files}
    data['refs']={side:{'repository':(detail.get(side,{}).get('repo') or {}).get('full_name'),
                        'commit':detail.get(side,{}).get('sha')} for side in ('head','base')}
    observed_at=data.pop('observed_at')
    sha=store.put(json.dumps(data,ensure_ascii=False,sort_keys=True).encode())
    return {'artifact':sha,'repository':repo,'number':number,'title':detail.get('title'),'body':detail.get('body'),
            'refs':data['refs'],'coverage':data['coverage'],
            'scope':data['scope'],'observed_at':observed_at,'url':detail.get('html_url',f'https://github.com/{repo}/pull/{number}'),
            'files':[{'path':f['filename'],'old_path':f.get('previous_filename',f['filename']),'status':f.get('status')} for f in data['files']],
            'status':'collected-not-reviewed' if all(v['complete'] for v in data['coverage'].values() if isinstance(v,dict) and v.get('requested',True)) else 'partial',
            'instruction':'Open the original PR page as needed. Discussions and files are optional; use exact head/base code, callers and tests for implementation claims. No runtime validation implied.'}


def markdown(meta, body):
    return '---\n'+yaml.safe_dump(meta,allow_unicode=True,sort_keys=False)+'---\n\n'+body


def generated_page(path, meta, body):
    # GitHub descriptions and upstream documents may contain mixed CRLF/CR.
    # parse_page uses universal newlines; hash the same canonical representation.
    body=body.replace('\r\n','\n').replace('\r','\n').strip()+'\n'
    if path.exists():
        previous, previous_body=wiki.parse_page(path)
        if previous.get('generated_body_sha256') != digest(previous_body.encode()):
            raise FlowError('Generated page has manual edits; preserve commentary in a separate topic: '+str(path))
    meta['generated_body_sha256']=digest(body.strip().encode())
    atomic_write(path,markdown(meta,body))


def pr_page_hashes(project, identity, repository, previous=()):
    source_ids={s['id'] for s in read_json(Path(project)/'knowledge/sources.json')
                if s.get('repository','').lower()==repository.lower()}
    affected={}
    for page in layout.review_page_candidates(project):
        meta,_=wiki.parse_page(page)
        if meta.get('kind') in {'source-pr','source-map','source-document'}:continue
        if identity in meta.get('pr_sources',[]) or any(r['source'] in source_ids for r in meta.get('sources',[])):
            affected[page.relative_to(project).as_posix()]=digest(page.read_bytes())
    # Removing a citation cannot silently approve the surviving prose.
    for name in previous:
        name=layout.current_path(project,name)
        page=child(project,name)
        if page.is_file():affected.setdefault(name,digest(page.read_bytes()))
    return affected


def retain_pr(store, project, result, engine, token=None):
    """Explicitly publish public source material, never arbitrary private artifacts."""
    project=Path(project).resolve()
    data=json.loads(store.artifact(result['artifact']))
    repo=repo_name(data['repository']); number=data['number']
    layout.require_local_owner(project,repo)
    info,_=api(repo,'',token)
    if info.get('private') is not False:
        raise FlowError('Public Wiki accepts verified public repositories only')
    if any(not v['complete'] for v in data['coverage'].values() if isinstance(v,dict) and v.get('requested',True)):
        raise FlowError('Incomplete discussion pagination; keep prior published page and retry')
    slug=repo.replace('/','--'); pid=f'pr-{slug.lower()}-{number}'
    path=layout.pr_root(project,repo)/f'PR-{number}.md'
    old_meta,old_body=wiki.parse_page(path) if path.exists() else ({},'')
    from .capture_policy import discovery_project, semantic_pr_fingerprint
    if discovery_project(project,repo) and old_meta.get('artifact_path'):
        from . import source_evidence
        original=source_evidence.read_json(project,old_meta['artifact_path'],expected_sha=old_meta['artifact_sha256'])
        if semantic_pr_fingerprint(original,data['coverage'])==semantic_pr_fingerprint(data,data['coverage']):
            if old_meta.get('generated_body_sha256')!=digest(old_body.encode()):
                raise FlowError('Generated page has manual edits; preserve commentary in a separate topic: '+str(path))
            _track_pr_review(store,project,pid,path,old_meta['artifact_sha256'],old_meta,repo)
            return {'id':pid,'page':path.relative_to(project).as_posix(),'artifact':old_meta['artifact_sha256'],
                    'updated_at':old_meta['updated_at'],'unchanged':True,
                    'scope':'Existing richer fixed evidence retained; new observation did not change requested semantics'}
    retained={k:v for k,v in data.items() if k!='observed_at'}
    raw_bytes=json.dumps(retained,ensure_ascii=False,sort_keys=True,indent=2).encode()
    raw_sha=digest(raw_bytes)
    raw=Path(project)/'knowledge/evidence/prs'/slug/f'{number}-{raw_sha}.json'
    atomic_write(raw,raw_bytes)
    d=data['detail']
    body=f'# {d["title"]}\n\n[Upstream PR]({d["html_url"]}) · state: {d["state"]} · merged: {d.get("merged",False)}\n\n'
    body+='## Original PR description\n\n'+(d.get('body') or 'No upstream description; do not infer motivation from title.')+'\n\n'
    body+='## Review and discussion\n\n'
    for key in ('reviews','issue_comments','inline_comments'):
        body+='### '+key+'\n\n'
        if not data['coverage'].get(key,{}).get('requested',True):
            body+='Not requested; open the original PR page if this discussion is needed.\n\n'
        for row in data[key]:
            author=(row.get('user') or {}).get('login','unknown')
            body+=f'- {author} · {row.get("state", "comment")} · {row.get("submitted_at",row.get("created_at",""))} · [source]({row.get("html_url",d["html_url"])})\n\n'
            if row.get('path'):body+=f'File: `{row["path"]}` · line {row.get("line",row.get("original_line"))}\n\n'
            body+=(row.get('body') or '(No body; status only.)')+'\n\n'
    body+='## Changed files and fixed code\n\n'
    if not data['coverage'].get('files',{}).get('requested',True):
        body+='File list and patches were not requested. Read the original PR or exact head/base code as needed.\n\n'
    for row in data['files']:
        body+=f'- `{row["filename"]}` · {row.get("status")} · additions {row.get("additions")} / deletions {row.get("deletions")}\n'
        for side,ref in data['refs'].items():
            name=row.get('previous_filename',row['filename']) if side=='base' else row['filename']
            if ref['repository'] and ref['commit']:
                body+=f'  - [{side}](https://github.com/{ref["repository"]}/blob/{ref["commit"]}/{quote(name,safe="/")})\n'
    body+='\n## Evidence and interpretation boundary\n\n'
    rel=Path(os.path.relpath(raw,path.parent)).as_posix()
    body+=f'[Original JSON, discussions and patches]({rel}) · SHA-256 `{raw_sha}`.\n\n'
    body+=f'Diff complete: {data["coverage"]["diff_complete"]}. Missing/binary/truncated patches require pinned source inspection. This is a source page, not an independently verified optimization case. Open, merged and released are different states; recheck the deployed dependency.\n'
    meta={'id':pid,'title':d['title'],'engine':engine,'stages':['adapt','optimize','fault-tolerance'],
          'kind':'source-pr','coverage':('upstream-body; discussions/files on demand' if any(not v.get('requested',True) for v in data['coverage'].values() if isinstance(v,dict)) else 'upstream-body-and-discussions'),'review_level':'source-reported','runtime_validated':False,
          'repository':repo,'pr_number':number,'updated_at':d['updated_at'],'artifact_sha256':raw_sha,
          'artifact_path':raw.relative_to(project).as_posix(),'sources':[]}
    generated_page(path,meta,body)
    _track_pr_review(store,project,pid,path,raw_sha,old_meta,repo)
    return {'id':pid,'page':path.relative_to(project).as_posix(),'artifact':raw_sha,'updated_at':d['updated_at']}


def _track_pr_review(store,project,pid,path,raw_sha,old_meta,repo):
    """Retaining identical source bytes still observes changed authored dependencies."""
    pointer=store.root/'wiki/pr-review'/f'{pid}.json'
    prior=read_json(pointer) if pointer.exists() else {}
    affected=pr_page_hashes(project,pid,repo,prior.get('affected_pages',[]))
    reviewed=layout.current_hashes(project,{p:d['page_sha256'] for p,d in prior.get('decisions',{}).get('pages',{}).items()})
    invalidated=prior.get('status')=='content-reviewed' and reviewed!=affected
    if old_meta.get('artifact_sha256')!=raw_sha or not prior or invalidated or set(prior.get('affected_pages',[]))!=set(affected):
        write_json(pointer,{'id':pid,'artifact_sha256':raw_sha,'affected_pages':sorted(affected),
                    'page':path.relative_to(project).as_posix(),
                    'status':'pending-content-review','reason':'PR evidence or related authored pages changed'})


def review_pr(store, project, identity, decisions):
    project=Path(project).resolve()
    safe_id(identity)
    pointer=store.root/'wiki/pr-review'/f'{identity}.json'
    pending=read_json(pointer)
    if pending['artifact_sha256']!=decisions.get('artifact_sha256'):raise FlowError('Review must address current retained PR artifact')
    if pending.get('page'):
        source_page=child(project,layout.current_path(project,pending['page']))
        pending['page']=source_page.relative_to(project).as_posix()
        meta,_=wiki.parse_page(source_page)
    else:
        # Receipts created before project page bindings remain reviewable.
        matches=[(page,meta) for page in (Path(project)/'knowledge/projects').rglob('PR-*.md')
                 if (meta:=wiki.parse_page(page)[0]).get('id')==identity]
        if len(matches)!=1:raise FlowError('Current retained PR source page is missing or ambiguous')
        source_page,meta=matches[0]
    if meta.get('id')!=identity or meta.get('artifact_sha256')!=pending['artifact_sha256']:
        raise FlowError('Current retained PR artifact changed; collect it again before review')
    pending['affected_pages']=[layout.current_path(project,name) for name in pending['affected_pages']]
    affected=pr_page_hashes(project,identity,meta['repository'],pending['affected_pages'])
    if set(affected)!=set(pending['affected_pages']):
        pending={**pending,'affected_pages':sorted(affected),'status':'pending-content-review',
                 'reason':'Related authored pages changed after PR capture'}
        write_json(pointer,pending)
    rows=decisions.get('pages',{})
    if set(rows)!=set(pending['affected_pages']):raise FlowError('Review every affected PR overview/topic/case')
    if not decisions.get('note'):raise FlowError('PR review requires an overall interpretation, including when no page is affected')
    for name,row in rows.items():
        if row.get('decision') not in {'updated','still-applicable','historical'} or not row.get('note'):
            raise FlowError('Substantive per-page decision required')
        if digest(child(project,name).read_bytes())!=row.get('page_sha256'):raise FlowError('Reviewed page changed')
    receipt={**pending,'status':'content-reviewed','decisions':decisions,'reviewed_at':utc(),'runtime_validated':False}
    write_json(store.root/'wiki/pr-review-history'/f'{fingerprint(receipt)}.json',receipt)
    write_json(pointer,receipt)
    return receipt


def inventory(store, project, source_id, token=None, retain=False):
    project=Path(project).resolve()
    source=source_for(project,source_id)
    if not source or source.get('kind')=='web':raise FlowError('Select registered Git source')
    repo=repo_name(source['repository'])
    info,_=api(repo,'',token)
    if retain and info.get('private') is not False:raise FlowError('Cannot publish private source inventory')
    commit,_=api(repo,'/commits/'+quote(source['ref'],safe=''),token)
    sha=commit['sha']
    tree,_=api(repo,f'/git/trees/{sha}?recursive=1',token)
    if tree.get('truncated'):raise FlowError('Repository tree truncated; no complete inventory or deletion inference')
    records={row['path']:{'sha':row['sha'],'type':row['type'],'mode':row['mode']} for row in tree['tree']}
    previous_path=Path(project)/'knowledge/catalog/repositories'/f'{source_id}.json'
    previous=read_json(previous_path) if previous_path.exists() else {'entries':{}}
    changed=sorted(p for p in records.keys() | previous['entries'].keys() if records.get(p)!=previous['entries'].get(p))
    data={'source':source_id,'repository':repo,'ref':source['ref'],'commit':sha,'entries':records,'observed_at':utc(),
          'coverage':'complete-path-and-blob-inventory; not complete content review'}
    artifact=store.put(json.dumps(data,ensure_ascii=False).encode())
    report={'artifact':artifact,'source':source_id,'commit':sha,'previous_commit':previous.get('commit'),'changed_paths':changed,
            'new_paths':sorted(records.keys()-previous['entries'].keys()),'removed_paths':sorted(previous['entries'].keys()-records.keys())}
    pending_path=store.root/'wiki/inventory-pending'/f'{source_id}.json'
    pending=read_json(pending_path) if pending_path.exists() else {'paths':[]}
    pending={'source':source_id,'commit':sha,'paths':sorted(set(pending['paths'])|set(changed))}
    write_json(pending_path,pending)
    report['pending_paths']=pending['paths']
    write_json(store.root/'wiki/inventory'/f'{source_id}.json',report)
    if retain:
        write_json(previous_path,data)
        groups={}
        for path,row in records.items():
            if row['type']!='tree':groups.setdefault(path.split('/')[0],[]).append((path,row))
        body=f'# {repo}: fixed source directory map\n\nCommit `{sha}` · ref `{source["ref"]}`. Full paths are discoverable; listing a file does not imply its contents were read.\n\n'
        body+='Use `wiki-code '+repo+' '+sha+' PATH` to inspect exact files, then follow callers/tests. A gitlink entry pins a child SHA, not its latest branch.\n\n'
        for group,entries in groups.items():
            body+='## '+group+'\n\n'
            body+='\n'.join(f'- [{p}](https://github.com/{repo}/blob/{sha}/{quote(p,safe="/")}) · {r["type"]} `{r["sha"]}`' for p,r in entries)+'\n\n'
        meta={'id':source_id+'-source-map','title':repo+' source directory map','kind':'source-map',
              'engine':source.get('engine',source_id),'review_level':'inventory-only','runtime_validated':False,
              'stages':['adapt','optimize','fault-tolerance'],'sources':[]}
        generated_page(layout.source_map(project,source_id),meta,body)
    return report


def triage_inventory(store, project, source_id, decisions):
    pending_path=store.root/'wiki/inventory-pending'/f'{source_id}.json'
    pending=read_json(pending_path)
    if decisions.get('commit')!=pending['commit']:raise FlowError('Inventory triage must address the latest fixed commit')
    rows=decisions.get('paths',{})
    if set(rows)-set(pending['paths']):raise FlowError('Unknown pending inventory paths')
    for path,row in rows.items():
        if row.get('decision') not in {'knowledge-added','not-relevant','deferred'} or not row.get('note'):
            raise FlowError('Each path needs a substantive inventory decision')
        if row['decision']=='knowledge-added':
            if not row.get('pages'):raise FlowError('Link added or revised knowledge pages')
            for page in row['pages']:
                if not child(project,page).is_file():raise FlowError('Missing linked knowledge page')
    for path,row in rows.items():
        if row['decision']!='deferred':pending['paths'].remove(path)
    receipt={'source':source_id,'commit':pending['commit'],'paths':rows,'reviewed_at':utc()}
    write_json(store.root/'wiki/inventory-reviews'/f'{fingerprint(receipt)}.json',receipt)
    write_json(pending_path,pending)
    return {'pending':len(pending['paths']),'runtime_validated':False}


def sync_prs(store, project, source_id, token=None, max_prs=10, since=None):
    """Resume bounded discovery before retention; paginated observations are not atomic."""
    project=Path(project).resolve()
    if not 1<=max_prs<=100:raise FlowError('max-prs must be 1..100')
    source=source_for(project,source_id)
    if not source or source.get('kind')=='web':raise FlowError('Select registered Git source')
    from .capture_policy import is_discovery
    if is_discovery(source,project):
        return discover_prs(store,source,token,max_prs,since)
    repo=repo_name(source['repository']); engine=source.get('engine',source_id)
    ledger_path=Path(project)/'knowledge/catalog/pr-ledgers'/f'{source_id}.json'
    ledger=read_json(ledger_path) if ledger_path.exists() else {'records':{},'scope':'registered PR sources plus recent updated discovery'}
    for record in ledger['records'].values():
        if record.get('page'):
            record['page']=layout.current_path(project,record['page'])
    # Explicitly retained older PRs are also refreshed, even outside the discovery window.
    for page in layout.pr_root(project,repo).glob('PR-*.md'):
        meta,_=wiki.parse_page(page)
        ledger['records'].setdefault(str(meta['pr_number']),{'id':meta['id'],'updated_at':meta['updated_at']})
    state_path=store.root/'wiki/pr-sync'/f'{source_id}.json'
    state=read_json(state_path) if state_path.exists() else {}
    if not state.get('pending') and not state.get('discovery'):
        cutoff=since or ((datetime.fromisoformat(ledger['discovered_through'])-timedelta(days=1)).isoformat() if ledger.get('discovered_through') else (datetime.now(timezone.utc)-timedelta(days=30)).isoformat())
        cutoff_dt=datetime.fromisoformat(cutoff.replace('Z','+00:00'))
        if cutoff_dt.tzinfo is None:raise FlowError('since requires timezone')
        started=utc(); audit_before=datetime.now(timezone.utc)-timedelta(days=7)
        pending={int(n) for n,r in ledger['records'].items() if not r.get('checked_at') or datetime.fromisoformat(r['checked_at'])<audit_before}
        state={'pending':sorted(pending,reverse=True),'started':started,'since':cutoff,'errors':[],
               'discovery':{'status':'in-progress','next_page':1}}
        # Persist before the first request too: even a page-one failure must
        # retain the fixed window and the seven-day discussion audit queue.
        write_json(state_path,state)
    errors=[]; processed=[]
    if state.get('discovery'):
        # Discovery takes precedence over an already nonempty pending queue.
        # Do not restart its window or reset started when a caller resumes.
        cutoff_dt=datetime.fromisoformat(state['since'].replace('Z','+00:00'))
        if cutoff_dt.tzinfo is None:raise FlowError('since requires timezone')
        pending={int(n) for n in state['pending']}
        for _ in range(20):
            page=state['discovery']['next_page']
            try:
                rows,links=api(repo,f'/pulls?state=all&sort=updated&direction=desc&per_page=100&page={page}',token)
                if not isinstance(rows,list):raise FlowError('Expected PR list')
                found=set(); updated=[]
                # Validate the complete page before checkpointing any of it.
                # An invalid response is not an empty page or an exhausted scan.
                for row in rows:
                    if (not isinstance(row,dict) or type(row.get('number')) is not int
                            or row['number']<=0 or not isinstance(row.get('updated_at'),str)):
                        raise FlowError('Expected numbered PR rows with updated_at')
                    observed=datetime.fromisoformat(row['updated_at'].replace('Z','+00:00'))
                    if observed.tzinfo is None:raise FlowError('PR updated_at requires timezone')
                    updated.append(observed)
                    retained=ledger['records'].get(str(row['number']),{})
                    if observed>=cutoff_dt and retained.get('updated_at')!=row['updated_at']:
                        found.add(row['number'])
                if not isinstance(links,str):raise FlowError('Expected PR pagination links')
            except (FlowError,OSError,ValueError) as exc:
                errors.append({'phase':'discovery','page':page,'error':str(exc)[:240]})
                break
            pending.update(found)
            state['pending']=sorted(pending,reverse=True)
            state['errors']=[]
            if not rows or updated[-1]<cutoff_dt or 'rel="next"' not in links:
                state.pop('discovery')
                write_json(state_path,state)
                break
            state['discovery']['next_page']=page+1
            write_json(state_path,state)
    if not state.get('discovery'):
        # Old states have only pending/started/since. Keep draining those
        # without a new discovery pass, while removing duplicate queue entries.
        state['pending']=sorted({int(n) for n in state['pending']},reverse=True)
        for number in state['pending'][:max_prs]:
            try:
                result=read_pr(store,repo,number,token)
                record=retain_pr(store,project,result,engine,token)
                ledger['records'][str(number)]={**record,'checked_at':utc()}
                write_json(ledger_path,ledger)
                state['pending'].remove(number)
                write_json(state_path,state)
                processed.append(number)
            except (FlowError,OSError,ValueError) as exc:errors.append({'number':number,'error':str(exc)[:240]})
        if not state['pending']:
            ledger['discovered_through']=state['started'];ledger['discovery_since']=state['since'];write_json(ledger_path,ledger)
    state['errors']=errors
    write_json(state_path,state)
    review_pending=[]
    for row in ledger['records'].values():
        pointer=store.root/'wiki/pr-review'/f'{row["id"]}.json'
        if pointer.exists() and read_json(pointer)['status']=='pending-content-review':review_pending.append(row['id'])
    discovery=state.get('discovery')
    return {'source':source_id,'processed':processed,'pending':len(state['pending']),'errors':errors,'review_pending':review_pending,
            'status':'partial' if discovery or state['pending'] or errors else 'collected-not-reviewed',
            'discovery_pending':bool(discovery),'next_page':discovery['next_page'] if discovery else None,
            'scope_since':state['since'],
            'instruction':('Discovery is incomplete; repeat the same command to resume its fixed window. No PRs were retained or public cursor advanced. GitHub pagination is not an atomic snapshot.'
                           if discovery else 'Review related topics/cases; collection is not synthesis. Repeat the same command to resume.')}


def discover_prs(store, source, token=None, limit=10, since=None):
    """Observe one recent PR listing; preserve old capture queues as history.

    Search covers longer-tail questions when needed. A successful bounded list
    is never presented as full-history/body/discussion coverage.
    """
    repo=repo_name(source['repository'])
    safe_id(source['id'])
    if type(limit) is not int or not 1<=limit<=100:raise FlowError('Discovery limit must be 1..100')
    cutoff=None
    if since:
        cutoff=datetime.fromisoformat(since.replace('Z','+00:00'))
        if cutoff.tzinfo is None:raise FlowError('since requires timezone')
    state_path=store.root/'wiki/pr-discovery'/f'{source["id"]}.json'
    previous=read_json(state_path) if state_path.exists() else {}
    result={'source':source['id'],'repository':repo,'processed':[],'pending':0,'captured':0,
            'review_pending':[],'history_complete':False,'discussion_audited':False,
            'scope':'one recent listing page; no automatic PR body/comments/reviews/files retention',
            'instruction':'Open a candidate URL or search the repository for the actual question; read body/code/discussion only as needed.'}
    try:
        rows,links=api(repo,f'/pulls?state=all&sort=updated&direction=desc&per_page={limit}&page=1',token)
        if not isinstance(rows,list) or not isinstance(links,str):raise FlowError('Expected PR list and pagination links')
        if len(rows)>limit:raise FlowError('PR response exceeds requested listing window')
        candidates=[]
        for row in rows:
            if (not isinstance(row,dict) or type(row.get('number')) is not int or row['number']<=0
                    or not isinstance(row.get('updated_at'),str)):
                raise FlowError('Expected numbered PR rows with updated_at')
            updated=datetime.fromisoformat(row['updated_at'].replace('Z','+00:00'))
            if updated.tzinfo is None:raise FlowError('PR updated_at requires timezone')
            if cutoff and updated<cutoff:continue
            candidates.append({'number':row['number'],'title':row.get('title') or f'PR #{row["number"]}',
                               'url':f'https://github.com/{repo}/pull/{row["number"]}',
                               'updated_at':row['updated_at'],'state':row.get('state','unknown'),
                               'status':'unreviewed','body_captured':False})
        queue={str(row['number']):row for row in previous.get('candidates',[])}
        queue.update((str(row['number']),row) for row in candidates)
        queue=sorted(queue.values(),key=lambda row:datetime.fromisoformat(row['updated_at'].replace('Z','+00:00')),reverse=True)[:1000]
        candidate_fp=fingerprint(queue)
        state={'source':source['id'],'repository':repo,'observed_at':utc(),'candidates':queue,
               'candidate_fingerprint':candidate_fp,'scope':result['scope'],'history_complete':False,
               'listing_has_more':bool(re.search(r'rel="next"',links)),'max_candidates':1000,'listing_limit':limit}
        write_json(state_path,state)
        result.update(status='discovered',errors=[],results=candidates[:limit],listed=len(rows),
                      candidate_count=len(queue),unchanged=previous.get('candidate_fingerprint')==candidate_fp,
                      discovery_pending=False,next_page=2 if state['listing_has_more'] else None,
                      observation_path=str(state_path))
    except (FlowError,OSError,ValueError) as exc:
        result.update(status='partial',errors=[{'phase':'discovery','error':str(exc)[:240]}],
                      results=[],candidate_count=len(previous.get('candidates',[])),discovery_pending=True,next_page=1)
    old_state=store.root/'wiki/pr-sync'/f'{source["id"]}.json'
    if old_state.exists():
        old=read_json(old_state)
        result['historical_capture']={'state_path':str(old_state),'pending':len(old.get('pending',[])),
                                      'status':'preserved; outside discovery scope'}
    return result


def apply_refresh(store, project, stage_id):
    safe_id(stage_id)
    stage=read_json(store.root/'wiki/staging'/f'{stage_id}.json')
    if stage.get('failures'):raise FlowError('Cannot apply incomplete source acquisition; retry failed registered paths')
    layout.require_local_owner(project, stage['source'])
    receipt=read_json(store.root/'wiki/reviews'/f'{stage_id}.json')
    reviewed_pages = receipt.get('page_hashes', {p: d['page_sha256'] for p, d in receipt['decisions'].items()})
    if wiki.source_page_hashes(project, stage['source']) != reviewed_pages:
        raise FlowError('Review stale; related pages changed or were added before applying source lock')
    for path, sha in receipt.get('content_hashes', reviewed_pages).items():
        if not child(project,path).is_file() or digest(child(project,path).read_bytes()) != sha:
            raise FlowError('Review stale; reviewed content changed before applying source lock')
    for path, sha in receipt.get('workflow_hashes', {}).items():
        if not child(project,path).is_file() or digest(child(project,path).read_bytes()) != sha:
            raise FlowError('Review stale; workflow changed before applying source lock')
    for path,decision in {**receipt['decisions'],**receipt['workflow_decisions']}.items():
        if digest(child(project,path).read_bytes())!=decision['page_sha256']:
            raise FlowError('Review stale; content changed before applying source lock')
    latest=read_json(store.root/'wiki/sources'/f'{stage["source"]}.json')
    if latest['commit']!=stage['commit']:raise FlowError('Newer acquisition exists')
    registry=read_json(Path(project)/'knowledge/sources.json')
    source=next(s for s in registry if s['id']==stage['source'])
    proofs=stage.get('absence_proofs',{})
    if any(not wiki.valid_absence_proof(proof,stage['commit'],name)
           or proof.get('repository')!=stage['repository'] for name,proof in proofs.items()):
        raise FlowError('Invalid fixed-path absence proof')
    from .capture_policy import is_discovery
    if source.get('kind')!='web' and is_discovery(source,project):
        if stage['repository']!=source['repository'] or stage['ref']!=source['ref']:
            raise FlowError('Source registration changed; refresh and review the selected repository/ref')
        if set(stage['files'])&set(proofs) or set(stage['files'])|set(proofs)!=set(source.get('paths',[])):
            raise FlowError('Source registration changed or staged path coverage is incomplete; refresh and review again')
    source['baseline_commit']=stage['commit'];source['baseline_files']=stage['files']
    if proofs or 'baseline_absent_files' in source:source['baseline_absent_files']=proofs
    lock_path=Path(project)/'knowledge/source-lock.json'
    lock=read_json(lock_path)
    historical=[row for row in lock['files'] if not isinstance(row,dict) or not all(key in row for key in ('repo','commit','path'))]
    records={(r['repo'],r['commit'],r['path']):r for r in lock['files'] if isinstance(r,dict) and all(key in r for key in ('repo','commit','path'))}
    for name,row in stage['files'].items():
        records[(stage['repository'],stage['commit'],name)]={'repo':stage['repository'],'commit':stage['commit'],
            'ref':stage['ref'],'path':name,**row,'status':'collected'}
    lock['files']=[*historical,*records.values()];lock['observed_on']=utc()[:10]
    if proofs or 'absences' in lock:
        prior_absences=lock.get('absences',[])
        historical_absences=[row for row in prior_absences if not isinstance(row,dict) or not all(key in row for key in ('repo','commit','path'))]
        absences={(row['repo'],row['commit'],row['path']):row for row in prior_absences
                  if isinstance(row,dict) and all(key in row for key in ('repo','commit','path'))}
        for name,proof in proofs.items():
            absences[(stage['repository'],stage['commit'],name)]={'repo':stage['repository'],'commit':stage['commit'],
                'ref':stage['ref'],'path':name,'status':'proven-absent','proof':proof}
        lock['absences']=[*historical_absences,*absences.values()]
    write_json(lock_path,lock);write_json(Path(project)/'knowledge/sources.json',registry)
    navigation=_maybe_catalog(store,project)
    return {'status':'content-applied','source':stage['source'],'commit':stage['commit'],
            'workflow_pending':receipt.get('workflow_deferred',[]),'runtime_validated':False,'catalog':navigation}


def document_exclusions(source):
    """Explicit, reviewed scope decisions; never infer relevance from keywords."""
    rules = source.get('document_exclusions', {})
    if not isinstance(rules, dict) or any(
        not isinstance(pattern, str) or not pattern.strip()
        or not isinstance(reason, str) or not reason.strip()
        for pattern, reason in rules.items()
    ):
        raise FlowError('document_exclusions must map nonempty path globs to review reasons')
    return rules


def select_document_paths(source, entries):
    patterns = source.get('document_globs', ['README*', 'docs/*.md', 'docs/*.rst'])
    rules = document_exclusions(source)
    candidates = sorted(p for p, row in entries.items() if row['type'] == 'blob'
                        and Path(p).suffix.lower() in {'.md', '.rst', '.mdx', '.txt'}
                        and any(fnmatch.fnmatchcase(p, g) for g in patterns))
    excluded = {p: reason for p in candidates for pattern, reason in rules.items()
                if fnmatch.fnmatchcase(p, pattern)}
    return [p for p in candidates if p not in excluded], excluded


def sync_documents(store, project, source_id, token=None, max_documents=40):
    """Discover documents from the complete fixed tree; retry incomplete batches."""
    project=Path(project).resolve()
    if not 1<=max_documents<=500:raise FlowError('max-documents must be 1..500')
    source=source_for(project,source_id)
    if not source or source.get('kind')=='web':raise FlowError('Select Git source')
    rules=document_exclusions(source)
    ledger_path=Path(project)/'knowledge/catalog/document-ledgers'/f'{source_id}.json'
    ledger=read_json(ledger_path) if ledger_path.exists() else {'records':{}}
    for record in ledger['records'].values():
        if record.get('page'):
            record['page']=layout.current_path(project,record['page'])
    retained_excluded=sorted(p for p in ledger['records'] if any(fnmatch.fnmatchcase(p,g) for g in rules))
    if retained_excluded:
        raise FlowError('Curate retained documents excluded by policy before syncing (pages, links and ledger): '
                        + ', '.join(retained_excluded))
    repo=repo_name(source['repository'])
    info,_=api(repo,'',token)
    if info.get('private') is not False:raise FlowError('Only public repository documents may be retained')
    tree_path=Path(project)/'knowledge/catalog/repositories'/f'{source_id}.json'
    if not tree_path.exists():raise FlowError('Run wiki-inventory --retain first')
    tree=read_json(tree_path);sha=tree['commit']
    patterns=source.get('document_globs',['README*','docs/*.md','docs/*.rst'])
    paths,excluded=select_document_paths(source,tree['entries'])
    def needs_copy(p):
        old=ledger['records'].get(p,{})
        entry=tree['entries'][p]
        # Contents API follows a symlink; its target can change without the link blob changing.
        stale_target=entry.get('mode')=='120000' and old.get('commit')!=sha
        return old.get('blob')!=entry['sha'] or stale_target or not old.get('page') or not child(project,old['page']).is_file()
    pending=[p for p in paths if needs_copy(p)]
    errors=[];processed=[]
    for path in pending[:max_documents]:
        try:
            result=read_code(store,repo,sha,path,token,max_chars=1000000)
            raw=store.artifact(result['artifact'])
            target=layout.document_root(project,source_id)/(path+'.md')
            body=f'# {repo} / {path}\n\n[Original at fixed commit]({result["url"]})\n\n'
            body+='Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.\n\n---\n\n'+raw.decode('utf-8')+'\n'
            meta={'id':'doc-'+source_id+'-'+fingerprint(path)[:20],'title':repo+' / '+path,'engine':source.get('engine',source_id),
                  'kind':'source-document','review_level':'source-reported','runtime_validated':False,
                  'stages':['adapt','optimize','fault-tolerance'],'repository':repo,'commit':sha,'path':path,
                  'raw_sha256':digest(raw),'sources':[]}
            generated_page(target,meta,body)
            ledger['records'][path]={'blob':tree['entries'][path]['sha'],'commit':sha,'sha256':digest(raw),
                                     'page':target.relative_to(project).as_posix(),'url':result['url']}
            write_json(ledger_path,ledger);processed.append(path)
        except (OSError,FlowError,UnicodeError,ValueError) as exc:errors.append({'path':path,'error':str(exc)[:240]})
    # Removed documents remain as historical records; never silently delete their content.
    ledger.update(commit=sha,patterns=patterns,excluded_paths=excluded,discovered=len(paths),historical_paths=sorted(set(ledger['records'])-set(paths)))
    for name,row in ledger['records'].items():
        page=child(project,row['page'])
        if not page.exists():continue
        meta,body=wiki.parse_page(page)
        state='current-scan' if name in paths else 'outside-current-scan' if name in tree['entries'] else 'removed-from-latest-tree'
        if name in paths and needs_copy(name):state='pending-newer-content'
        if meta.get('source_state')!=state:
            meta['source_state']=state
            try:generated_page(page,meta,body)
            except (OSError,ValueError) as exc:errors.append({'path':name,'error':str(exc)[:240]})
    write_json(ledger_path,ledger)
    remaining=[p for p in paths if needs_copy(p)]
    return {'source':source_id,'status':'partial' if remaining or errors else 'collected-not-reviewed',
            'processed':processed,'pending':len(remaining),'errors':errors,'patterns':patterns,'discovered':len(paths),
            'excluded_paths':excluded}


def catalog(project):
    project=Path(project).resolve()
    from .capture_policy import discovery_project
    if discovery_project(project):
        return _discovery_catalog(project)
    root=Path(project)/'knowledge'
    body='# 官方来源覆盖目录\n\n此页由来源目录和已保留页面重建。完整路径、文档采集和内容精读是不同覆盖层；没有逐模型或硬件验证的隐含承诺。\n\n'
    for source in read_json(root/'sources.json'):
        sid=source['id'];tree=root/'catalog/repositories'/f'{sid}.json'
        docs=root/'catalog/document-ledgers'/f'{sid}.json'
        body+='## '+sid+'\n\n'
        body+='来源：'+source['repository']+'\n\n'
        if source.get('document_scope'):
            body+='文档收录范围：'+source['document_scope']+'\n\n'
        if tree.exists():
            value=read_json(tree)
            link=Path(os.path.relpath(layout.source_map(project,sid),root/'catalog')).as_posix()
            body+=f'- [源码目录]({link})：{len(value["entries"])} 路径，固定 `{value["commit"]}`，目录覆盖。\n'
        if docs.exists():
            value=read_json(docs)
            link=Path(os.path.relpath(layout.document_root(project,sid),root/'catalog')).as_posix()
            body+=f'- [文档目录]({link}/)：扫描发现 {value["discovered"]} 份；保留 {len(value["records"])} 份（包含历史）；历史范围 {len(value.get("historical_paths",[]))} 份。扫描模式见 sources.json，pending 由更新运行报告给出。\n'
            if source.get('document_exclusions'):
                body+=f'- 按已复核范围排除 {len(value.get("excluded_paths",{}))} 份文档；规则与理由见 sources.json 的 document_exclusions。排除不代表上游删除，仍可按固定源码路径查阅。\n'
        if source.get('kind')!='web':
            for page in sorted(layout.pr_root(project,source['repository']).glob('PR-*.md')):
                meta,_=wiki.parse_page(page)
                title=meta['title'].replace('[','&#91;').replace(']','&#93;')
                body+=f'- [PR #{meta["pr_number"]}：{title}](../{page.relative_to(root).as_posix()})\n'
        body+='\n'
    generated_page(root/'catalog/README.md',{'id':'official-source-catalog','title':'官方源码 文档 PR 覆盖与更新索引',
        'kind':'source-map','engine':'cross-engine','review_level':'inventory-only','runtime_validated':False,'sources':[]},body)
    project_catalog(project)
    return {'status':'catalogued','source_count':len(read_json(root/'sources.json'))}


def _discovery_catalog(project):
    """Rebuild links, not a second mirror of upstream PR/tree inventories."""
    root=Path(project)/'knowledge'
    registry=read_json(root/'sources.json')
    body='# 官方来源与按需查阅\n\n此页只维护登记来源和阅读路由，不展开全部 PR、评论或完整源码路径。'
    body+='先查已有解释，长尾问题在线联搜原页；重要结论按实际版本读取源码与必要证据。历史采集台账不代表本轮刷新。\n\n'
    for source in registry:
        sid=source['id']
        url=source['repository'] if source.get('kind')=='web' else 'https://github.com/'+repo_name(source['repository'])
        body+=f'## {sid}\n\n[官方入口]({url})'
        if source.get('kind')!='web':
            body+=f' · [PR 入口]({url}/pulls) · 登记分支 `{source["ref"]}`'
        body+='\n\n'
        if source.get('document_scope'):body+='文档选择范围：'+source['document_scope']+'\n\n'
        mapping=layout.source_map(project,sid)
        if mapping.is_file():
            link=Path(os.path.relpath(mapping,root/'catalog')).as_posix()
            body+=f'- [固定源码阅读入口]({link})；按固定 commit 查文件、调用者和测试。\n'
        docs=layout.document_root(project,sid)
        if docs.is_dir() and any(docs.rglob('*.md')):
            link=Path(os.path.relpath(docs,root/'catalog')).as_posix()
            body+=f'- [选定文档原文]({link}/)；保留原版本和适用范围。\n'
        body+='\n'
    generated_page(root/'catalog/README.md',{'id':'official-source-catalog','title':'官方来源与按需查阅入口',
        'kind':'source-map','engine':'cross-engine','review_level':'navigation-only','runtime_validated':False,'sources':[]},body)
    project_catalog(project)
    return {'status':'catalogued','source_count':len(registry),'profile':'discovery-first',
            'scope':'registered routes and selected authored knowledge; no full PR/tree expansion'}


def project_catalog(project):
    """Rebuild navigation, keeping authored mechanisms separate from source copies."""
    project=Path(project).resolve()
    root=Path(project)/'knowledge'
    from .capture_policy import discovery_project
    lite=discovery_project(project)
    coverage=root/'coverage.json'
    groups={r['id']:r for r in read_json(coverage).get('projects',[])} if coverage.exists() else {}
    registry=read_json(root/'sources.json')
    identities={layout.project_id(project,source=s['id']) for s in registry}
    if (root/'projects').exists():
        identities.update(p.name for p in (root/'projects').iterdir() if p.is_dir())
    index='# 官方工程 Wiki\n\n按工程归属组织。每个工程内 `upstream/` 保存来源，`local/` 保存经过整理的解释；来源数量不表示内容已全部复核。\n\n'
    for identity in sorted(identities):
        directory=root/'projects'/identity
        group=groups.get(identity,{})
        body=f'# {identity}\n\n'
        if group.get('entry'):
            target=Path(project)/group['entry']
            title=wiki.parse_page(target)[0].get('title',identity)
            link=Path(os.path.relpath(target,directory)).as_posix()
            body+=f'从[工程总览：{title}]({link})进入。\n\n'
        body+='## 整理后的知识\n\n'
        listed=set()
        for section,label in [('overview','定位与代码地图'),('guides','安装、运行与测试'),('topics','机制专题'),('cases','优化案例'),('changes','版本与更新')]:
            pages=sorted((directory/'knowledgebase/local'/section).rglob('*.md'))
            if not pages:continue
            body+='### '+label+'\n\n'
            for page in pages:
                title=wiki.parse_page(page)[0].get('title',page.stem)
                body+=f'- [{title}]({page.relative_to(directory).as_posix()})\n'
                listed.add(page.relative_to(project).as_posix())
            body+='\n'
        related=[name for name in group.get('related_pages',[]) if name not in listed]
        if related:
            body+='### 关联阅读\n\n'
            for name in related:
                page=child(project,name)
                if page.is_file():
                    title=wiki.parse_page(page)[0].get('title',page.stem)
                    body+=f'- [{title}]({Path(os.path.relpath(page,directory)).as_posix()})\n'
            body+='\n'
        body+='## 上游资料\n\n'
        for source in registry:
            if layout.project_id(project,source=source['id'])!=identity:continue
            sid=source['id']
            url=source['repository'] if source.get('kind')=='web' else 'https://github.com/'+source['repository']
            body+=f'- [{sid}]({url})\n'
        sections=([('docs','选定官方文档原文'),('prs','已选定 PR 与固定证据'),('source-map','固定源码阅读入口')] if lite
                  else [('docs','官方文档原文'),('prs','PR 描述、review 与固定代码'),('source-map','完整源码路径')])
        for kind,label in sections:
            path=directory/'knowledgebase/upstream'/kind
            if path.is_dir() and (not lite or any(path.rglob('*.md'))):body+=f'- [{label}]({path.relative_to(directory).as_posix()}/)\n'
        if lite:
            body+='\n普通 PR 通过官方原页联搜，正文、代码和讨论按需读取；已选定页面链接固定原件，历史材料由既有固定 Git 基线按需恢复。'
        else:
            body+='\n原始 PR JSON 集中保存在 [evidence/prs](../../evidence/prs/)；每篇 PR 原文页链接其固定原件。'
        body+='局部 Wiki 不重复维护 HCU 仓，参见[知识分工](../../../docs/knowledge-architecture.md#hcu-仓库知识的分工)。\n'
        generated_page(directory/'README.md',{'id':'project-'+identity,'title':identity+' 官方工程 Wiki 导航',
            'kind':'source-map','review_level':'navigation-only','runtime_validated':False,'sources':[]},body)
        index+=f'- [{identity}]({identity}/README.md)\n'
    generated_page(root/'projects/README.md',{'id':'official-projects-index','title':'官方工程 Wiki 目录',
        'kind':'source-map','review_level':'navigation-only','runtime_validated':False,'sources':[]},index)


def _navigation_inputs(project):
    """Fingerprint exactly the small inputs used by lite link navigation.

    Source document/PR bodies and historical ledgers are deliberately excluded:
    the hub links their selected directories, rather than expanding each item.
    """
    project=Path(project).resolve()
    root=project/'knowledge'
    registry=read_json(root/'sources.json')
    coverage=root/'coverage.json'
    groups=read_json(coverage).get('projects',[]) if coverage.is_file() else []
    identities={layout.project_id(project,source=source['id']) for source in registry}
    if (root/'projects').is_dir():identities.update(path.name for path in (root/'projects').iterdir() if path.is_dir())
    titles={}
    def title(path):
        if not path.resolve().is_relative_to(root.resolve()):raise FlowError('Navigation page link escapes knowledge root')
        if path.is_file():
            meta,_=wiki.parse_page(path)
            titles[path.relative_to(project).as_posix()]=meta.get('title',path.stem)
    selected=[]
    for identity in sorted(identities):
        directory=root/'projects'/identity
        for section in ['overview','guides','topics','cases','changes']:
            for page in sorted((directory/'knowledgebase/local'/section).rglob('*.md')):title(page)
        selected.append((identity,[(kind,any((directory/'knowledgebase/upstream'/kind).rglob('*.md')))
                                    for kind in ['docs','prs','source-map']]))
    for group in groups:
        for name in [group.get('entry'),*group.get('related_pages',[])]:
            if name:title(child(project,name))
    sources=[]
    for source in registry:
        value={key:source.get(key) for key in ['id','repository','kind','ref','knowledge_project','document_scope']}
        value['source_map_present']=layout.source_map(project,source['id']).is_file()
        value['selected_documents_present']=any(layout.document_root(project,source['id']).rglob('*.md'))
        sources.append(value)
    signature=fingerprint({'sources':sources,'groups':groups,'titles':titles,'selected_sections':selected})
    outputs=[root/'catalog/README.md',root/'projects/README.md',
             *(root/'projects'/identity/'README.md' for identity in sorted(identities))]
    return signature,outputs


def _maybe_catalog(store,project):
    from .capture_policy import discovery_project
    if not discovery_project(project):return {'status':'not-managed','rebuilt':False}
    project=Path(project).resolve()
    signature,outputs=_navigation_inputs(project)
    path=store.root/'wiki/catalog-checks'/f'{fingerprint(str(project))}.json'
    previous=read_json(path) if path.is_file() else {}
    hashes={page.relative_to(project).as_posix():digest(page.read_bytes()) if page.is_file() else None for page in outputs}
    if previous.get('input')==signature and previous.get('outputs')==hashes and all(hashes.values()):
        return {'status':'unchanged','rebuilt':False}
    catalog(project)
    # catalog() may create the canonical project directories on its first run.
    signature,outputs=_navigation_inputs(project)
    hashes={page.relative_to(project).as_posix():digest(page.read_bytes()) for page in outputs}
    write_json(path,{'project':str(project),'input':signature,'outputs':hashes})
    return {'status':'catalogued','rebuilt':True,'scope':'registered routes and selected-page navigation only'}


def update_source(store, project, source_id, token=None, max_prs=10, max_documents=40, since=None):
    source=source_for(project,source_id)
    if not source:raise FlowError('Unknown source')
    from .capture_policy import is_discovery
    if is_discovery(source,project) and source.get('kind')!='web':
        return _update_discovery_source(store,project,source,token,max_prs,since)
    result={'source':source_id,'stages':{},'errors':[]}
    steps=([('inventory',lambda:inventory(store,project,source_id,token,True)),
            ('documents',lambda:sync_documents(store,project,source_id,token,max_documents)),
            ('prs',lambda:sync_prs(store,project,source_id,token,max_prs,since))] if source.get('kind')!='web' else [])
    def refresh_content():
        inventory_commit = result['stages'].get('inventory', {}).get('commit')
        if inventory_commit:
            return wiki.refresh_source(store,project,source_id,token,fixed_commit=inventory_commit)
        return wiki.refresh_source(store,project,source_id,token)
    steps.append(('content',refresh_content))
    steps.append(('catalog',lambda:catalog(project)))
    for name,action in steps:
        if name=='documents' and 'inventory' not in result['stages']:
            result['errors'].append({'stage':name,'error':'Skipped: latest complete source inventory unavailable'})
            continue
        try:result['stages'][name]=action()
        except (OSError,ValueError) as exc:result['errors'].append({'stage':name,'error':str(exc)[:240]})
    result['status']='partial' if result['errors'] or any(x.get('status')=='partial' for x in result['stages'].values()) else 'pending-content-review'
    result['instruction']='Review changed source paths and related overviews/topics/cases. Explicitly defer site workflow reviews if necessary; no automatic task dependency upgrade.'
    write_json(store.root/'wiki/update-runs'/f'{source_id}-{fingerprint(result)[:16]}.json',result)
    return result


def _locked_source_commit(project,source):
    """Reuse only the complete, hash-bound baseline that was actually applied.

    The lock keeps historical and partial observations. Their latest timestamps
    or status fields do not select the current reviewed baseline.
    """
    commit=source.get('baseline_commit')
    files=source.get('baseline_files')
    absent=source.get('baseline_absent_files',{})
    if (not isinstance(commit,str) or not re.fullmatch(r'[0-9a-f]{40}',commit)
            or not isinstance(files,dict) or not isinstance(absent,dict)):
        return None
    watched=set(source.get('paths',[]))
    if set(files)&set(absent) or set(files)|set(absent)!=watched:
        return None
    path=Path(project)/'knowledge/source-lock.json'
    lock=read_json(path) if path.is_file() else {}
    repositories={repo_name(repo).lower() for repo in [source['repository'],*source.get('repository_aliases',[])]}
    rows=[row for row in lock.get('files',[]) if isinstance(row,dict)
          and str(row.get('repo','')).lower() in repositories and row.get('commit')==commit]
    for name,expected in files.items():
        sha=expected.get('sha256') if isinstance(expected,dict) else None
        if not isinstance(sha,str) or not re.fullmatch(r'[0-9a-f]{64}',sha):return None
        matches=[row for row in rows if row.get('path')==name]
        # Old native apply rows had no status; exact applied hash bindings make
        # them compatible. Explicit failed/partial records never become passes.
        if not matches or any(row.get('sha256')!=sha or row.get('status') not in {None,'collected'} for row in matches):
            return None
    for name,proof in absent.items():
        if not wiki.valid_absence_proof(proof,commit,name):return None
        if str(proof.get('repository','')).lower() not in repositories:return None
        matches=[row for row in lock.get('absences',[]) if isinstance(row,dict) and row.get('commit')==commit and row.get('path')==name
                 and str(row.get('repo','')).lower() in repositories]
        if not matches or any(row.get('proof')!=proof or row.get('status')!='proven-absent' for row in matches):return None
    return commit


def _update_discovery_source(store,project,source,token,max_prs,since):
    """Check fixed monitored inputs; discover long-tail material when needed."""
    result={'source':source['id'],'stages':{},'errors':[],
            'scope':'branch check and registered paths only; PR URL discovery; no full-tree/document/discussion sweep'}
    try:
        repo=repo_name(source['repository'])
        commit,_=api(repo,'/commits/'+quote(source['ref'],safe=''),token)
        sha=commit.get('sha')
        if not isinstance(sha,str) or not re.fullmatch(r'[0-9a-f]{40}',sha):raise FlowError('Unexpected commit SHA')
        locked=_locked_source_commit(project,source)
        result['stages']['check']={'commit':sha,'locked_commit':locked,'observed_at':utc(),
                                   'status':'unchanged' if sha==locked else 'changed'}
        if sha==locked:
            result['stages']['content']={'status':'unchanged','commit':sha,'body_read':False,
                                          'meaning':'Fixed inputs reused; authored facts and runtime behavior were not revalidated'}
        else:
            # The old full update verified this through inventory(). A light
            # update must retain that public boundary before staging bytes.
            info,_=api(repo,'',token)
            if info.get('private') is not False:raise FlowError('Only verified public repository content may be retained')
            result['stages']['content']=wiki.refresh_source(store,project,source['id'],token,fixed_commit=sha)
    except (OSError,ValueError) as exc:
        result['errors'].append({'stage':'content','error':str(exc)[:240]})
    try:
        result['stages']['prs']=sync_prs(store,project,source['id'],token,max_prs,since)
    except (OSError,ValueError) as exc:
        result['errors'].append({'stage':'prs','error':str(exc)[:240]})
    try:
        result['stages']['catalog']=_maybe_catalog(store,project)
    except (OSError,ValueError) as exc:
        result['errors'].append({'stage':'catalog','error':str(exc)[:240]})
    partial=result['errors'] or any(stage.get('status')=='partial' for stage in result['stages'].values())
    content=result['stages'].get('content',{})
    result['status']='partial' if partial else ('unchanged' if content.get('status')=='unchanged' else 'pending-content-review')
    result['instruction']='Review only actual changed inputs and affected knowledge; use online PR links and source code on demand. No automatic task dependency upgrade.'
    write_json(store.root/'wiki/source-checks'/f'{source["id"]}.json',result)
    return result
