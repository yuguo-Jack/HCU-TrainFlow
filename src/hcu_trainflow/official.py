"""Public upstream discovery, PR source pages and immutable code navigation.

Acquisition pages are explicitly source-reported. They never stand in for an
authored mechanism/case or runtime validation. Ordinary reads remain private.
"""
import base64
import fnmatch
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import re
from urllib.parse import quote, urlencode

import yaml

from . import wiki
from .core import FlowError, atomic_write, child, digest, fingerprint, read_json, safe_id, utc, write_json


def repo_name(repo):
    repo = repo.removeprefix('https://github.com/').removesuffix('.git').rstrip('/')
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repo) or any(x in {'.', '..'} for x in repo.split('/')):
        raise FlowError('Expected public GitHub owner/repository')
    return repo


def api(repo, suffix, token=None):
    return wiki._get_json('https://api.github.com/repos/' + repo_name(repo) + suffix, token)


def source_for(project, identity):
    return next((s for s in read_json(Path(project)/'knowledge/sources.json') if s['id'] == identity), None)


def engine_repos(project, engine=None, source=None, repos=()):
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
    terms = re.findall(r'[\w./+-]+', query, re.UNICODE)[:20]
    if not terms:
        raise FlowError('No search terms')
    if not repos:
        return {'status':'scope-required', 'results':[], 'instruction':'Select an engine, source or repository.'}
    result = {'query':query, 'queried_at':utc(), 'results':[], 'coverage':[]}
    for repo in dict.fromkeys(repo_name(r) for r in repos):
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
    result['artifact'] = store.put(json.dumps(result,ensure_ascii=False).encode())
    return result


def annotate_prs(project, result):
    for row in result.get('results',[]):
        path=Path(project)/'knowledge/prs'/row['repository'].replace('/','--')/f'PR-{row["number"]}.md'
        meta,_=wiki.parse_page(path) if path.exists() else ({},'')
        row['locally_retained']=bool(meta)
        row['local_page_id']=meta.get('id')
        row['upstream_changed']=meta.get('updated_at')!=row['updated_at'] if meta else None
        row['discussion_recheck_required']=True
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


def read_pr(store, repo, number, token=None, max_pages=20):
    repo=repo_name(repo)
    if number <= 0 or not 1 <= max_pages <= 100:
        raise FlowError('Positive PR number and max-pages 1..100 required')
    base=f'https://api.github.com/repos/{repo}/pulls/{number}'
    detail,_=wiki._get_json(base,token)
    data={'repository':repo,'number':number,'detail':detail,'coverage':{},'observed_at':utc()}
    urls={'issue_comments':f'https://api.github.com/repos/{repo}/issues/{number}/comments',
          'inline_comments':base+'/comments','reviews':base+'/reviews','files':base+'/files'}
    for key,url in urls.items():
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
    data['coverage']['diff_complete']=len(data['files'])==detail.get('changed_files') and all(f.get('patch') for f in data['files'])
    data['refs']={side:{'repository':(detail.get(side,{}).get('repo') or {}).get('full_name'),
                        'commit':detail.get(side,{}).get('sha')} for side in ('head','base')}
    sha=store.put(json.dumps(data,ensure_ascii=False).encode())
    return {'artifact':sha,'repository':repo,'number':number,'title':detail.get('title'),'body':detail.get('body'),
            'refs':data['refs'],'coverage':data['coverage'],
            'files':[{'path':f['filename'],'old_path':f.get('previous_filename',f['filename']),'status':f.get('status')} for f in data['files']],
            'status':'collected-not-reviewed' if all(v['complete'] for v in data['coverage'].values() if isinstance(v,dict)) else 'partial',
            'instruction':'Read retained artifact for all reviews; inspect exact head/base file, callers and tests. No runtime validation implied.'}


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
    for page in (Path(project)/'knowledge').rglob('*.md'):
        meta,_=wiki.parse_page(page)
        if meta.get('kind') in {'source-pr','source-map','source-document'}:continue
        if identity in meta.get('pr_sources',[]) or any(r['source'] in source_ids for r in meta.get('sources',[])):
            affected[page.relative_to(project).as_posix()]=digest(page.read_bytes())
    # Removing a citation cannot silently approve the surviving prose.
    for name in previous:
        page=child(project,name)
        if page.is_file():affected.setdefault(name,digest(page.read_bytes()))
    return affected


def retain_pr(store, project, result, engine, token=None):
    """Explicitly publish public source material, never arbitrary private artifacts."""
    data=json.loads(store.artifact(result['artifact']))
    repo=repo_name(data['repository']); number=data['number']
    info,_=api(repo,'',token)
    if info.get('private') is not False:
        raise FlowError('Public Wiki accepts verified public repositories only')
    if any(not v['complete'] for v in data['coverage'].values() if isinstance(v,dict)):
        raise FlowError('Incomplete discussion pagination; keep prior published page and retry')
    slug=repo.replace('/','--'); pid=f'pr-{slug.lower()}-{number}'
    path=Path(project)/'knowledge/prs'/slug/f'PR-{number}.md'
    old_meta,_=wiki.parse_page(path) if path.exists() else ({},'')
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
        for row in data[key]:
            author=(row.get('user') or {}).get('login','unknown')
            body+=f'- {author} · {row.get("state", "comment")} · {row.get("submitted_at",row.get("created_at",""))} · [source]({row.get("html_url",d["html_url"])})\n\n'
            if row.get('path'):body+=f'File: `{row["path"]}` · line {row.get("line",row.get("original_line"))}\n\n'
            body+=(row.get('body') or '(No body; status only.)')+'\n\n'
    body+='## Changed files and fixed code\n\n'
    for row in data['files']:
        body+=f'- `{row["filename"]}` · {row.get("status")} · additions {row.get("additions")} / deletions {row.get("deletions")}\n'
        for side,ref in data['refs'].items():
            name=row.get('previous_filename',row['filename']) if side=='base' else row['filename']
            if ref['repository'] and ref['commit']:
                body+=f'  - [{side}](https://github.com/{ref["repository"]}/blob/{ref["commit"]}/{quote(name,safe="/")})\n'
    body+='\n## Evidence and interpretation boundary\n\n'
    rel='../../evidence/prs/'+slug+'/'+raw.name
    body+=f'[Original JSON, discussions and patches]({rel}) · SHA-256 `{raw_sha}`.\n\n'
    body+=f'Diff complete: {data["coverage"]["diff_complete"]}. Missing/binary/truncated patches require pinned source inspection. This is a source page, not an independently verified optimization case. Open, merged and released are different states; recheck the deployed dependency.\n'
    meta={'id':pid,'title':d['title'],'engine':engine,'stages':['adapt','optimize','fault-tolerance'],
          'kind':'source-pr','coverage':'upstream-body-and-discussions','review_level':'source-reported','runtime_validated':False,
          'repository':repo,'pr_number':number,'updated_at':d['updated_at'],'artifact_sha256':raw_sha,
          'artifact_path':raw.relative_to(project).as_posix(),'sources':[]}
    generated_page(path,meta,body)
    pointer=store.root/'wiki/pr-review'/f'{pid}.json'
    prior=read_json(pointer) if pointer.exists() else {}
    affected=pr_page_hashes(project,pid,repo,prior.get('affected_pages',[]))
    reviewed={p:d['page_sha256'] for p,d in prior.get('decisions',{}).get('pages',{}).items()}
    invalidated=prior.get('status')=='content-reviewed' and reviewed!=affected
    if old_meta.get('artifact_sha256')!=raw_sha or not prior or invalidated or set(prior.get('affected_pages',[]))!=set(affected):
        write_json(pointer,{'id':pid,'artifact_sha256':raw_sha,'affected_pages':sorted(affected),
                    'page':path.relative_to(project).as_posix(),
                    'status':'pending-content-review','reason':'PR evidence or related authored pages changed'})
    return {'id':pid,'page':path.relative_to(project).as_posix(),'artifact':raw_sha,'updated_at':d['updated_at']}


def review_pr(store, project, identity, decisions):
    safe_id(identity)
    pointer=store.root/'wiki/pr-review'/f'{identity}.json'
    pending=read_json(pointer)
    if pending['artifact_sha256']!=decisions.get('artifact_sha256'):raise FlowError('Review must address current retained PR artifact')
    if pending.get('page'):
        source_page=child(project,pending['page'])
        meta,_=wiki.parse_page(source_page)
    else:
        # Receipts created before project page bindings remain reviewable.
        matches=[(page,meta) for page in (Path(project)/'knowledge/prs').rglob('*.md')
                 if (meta:=wiki.parse_page(page)[0]).get('id')==identity]
        if len(matches)!=1:raise FlowError('Current retained PR source page is missing or ambiguous')
        source_page,meta=matches[0]
    if meta.get('id')!=identity or meta.get('artifact_sha256')!=pending['artifact_sha256']:
        raise FlowError('Current retained PR artifact changed; collect it again before review')
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
        generated_page(Path(project)/'knowledge/source-maps'/f'{source_id}.md',meta,body)
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
    """Bounded resumable refresh, preserving failed records and discussion audits."""
    if not 1<=max_prs<=100:raise FlowError('max-prs must be 1..100')
    source=source_for(project,source_id)
    if not source or source.get('kind')=='web':raise FlowError('Select registered Git source')
    repo=repo_name(source['repository']); engine=source.get('engine',source_id)
    ledger_path=Path(project)/'knowledge/catalog/pr-ledgers'/f'{source_id}.json'
    ledger=read_json(ledger_path) if ledger_path.exists() else {'records':{},'scope':'registered PR sources plus recent updated discovery'}
    # Explicitly retained older PRs are also refreshed, even outside the discovery window.
    for page in (Path(project)/'knowledge/prs'/repo.replace('/','--')).glob('PR-*.md'):
        meta,_=wiki.parse_page(page)
        ledger['records'].setdefault(str(meta['pr_number']),{'id':meta['id'],'updated_at':meta['updated_at']})
    state_path=store.root/'wiki/pr-sync'/f'{source_id}.json'
    state=read_json(state_path) if state_path.exists() else {}
    if not state.get('pending'):
        cutoff=since or ((datetime.fromisoformat(ledger['discovered_through'])-timedelta(days=1)).isoformat() if ledger.get('discovered_through') else (datetime.now(timezone.utc)-timedelta(days=30)).isoformat())
        cutoff_dt=datetime.fromisoformat(cutoff.replace('Z','+00:00'))
        if cutoff_dt.tzinfo is None:raise FlowError('since requires timezone')
        started=utc(); audit_before=datetime.now(timezone.utc)-timedelta(days=7)
        pending={int(n) for n,r in ledger['records'].items() if not r.get('checked_at') or datetime.fromisoformat(r['checked_at'])<audit_before}
        page=1; exhausted=False
        while page<=20:
            rows,links=api(repo,f'/pulls?state=all&sort=updated&direction=desc&per_page=100&page={page}',token)
            if not isinstance(rows,list):raise FlowError('Expected PR list')
            for row in rows:
                retained=ledger['records'].get(str(row['number']),{})
                if datetime.fromisoformat(row['updated_at'].replace('Z','+00:00'))>=cutoff_dt and retained.get('updated_at')!=row['updated_at']:
                    pending.add(row['number'])
            if not rows or datetime.fromisoformat(rows[-1]['updated_at'].replace('Z','+00:00'))<cutoff_dt or 'rel="next"' not in links:
                exhausted=True;break
            page+=1
        if not exhausted:raise FlowError('Discovery exceeds bounded range; narrow --since; cursor unchanged')
        state={'pending':sorted(pending,reverse=True),'started':started,'since':cutoff,'errors':[]}
        write_json(state_path,state)
    errors=[]; processed=[]
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
    state['errors']=errors
    if not state['pending']:
        ledger['discovered_through']=state['started'];ledger['discovery_since']=state['since'];write_json(ledger_path,ledger)
    write_json(state_path,state)
    review_pending=[]
    for row in ledger['records'].values():
        pointer=store.root/'wiki/pr-review'/f'{row["id"]}.json'
        if pointer.exists() and read_json(pointer)['status']=='pending-content-review':review_pending.append(row['id'])
    return {'source':source_id,'processed':processed,'pending':len(state['pending']),'errors':errors,'review_pending':review_pending,
            'status':'partial' if state['pending'] or errors else 'collected-not-reviewed',
            'scope_since':state['since'],'instruction':'Review related topics/cases; collection is not synthesis. Repeat the same command to resume.'}


def apply_refresh(store, project, stage_id):
    safe_id(stage_id)
    stage=read_json(store.root/'wiki/staging'/f'{stage_id}.json')
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
    source['baseline_commit']=stage['commit'];source['baseline_files']=stage['files']
    lock_path=Path(project)/'knowledge/source-lock.json'
    lock=read_json(lock_path)
    records={(r['repo'],r['commit'],r['path']):r for r in lock['files']}
    for name,row in stage['files'].items():
        records[(stage['repository'],stage['commit'],name)]={'repo':stage['repository'],'commit':stage['commit'],
            'ref':stage['ref'],'path':name,**row}
    lock['files']=list(records.values());lock['observed_on']=utc()[:10]
    write_json(lock_path,lock);write_json(Path(project)/'knowledge/sources.json',registry)
    return {'status':'content-applied','source':stage['source'],'commit':stage['commit'],
            'workflow_pending':receipt.get('workflow_deferred',[]),'runtime_validated':False}


def sync_documents(store, project, source_id, token=None, max_documents=40):
    """Discover documents from the complete fixed tree; retry incomplete batches."""
    if not 1<=max_documents<=500:raise FlowError('max-documents must be 1..500')
    source=source_for(project,source_id)
    if not source or source.get('kind')=='web':raise FlowError('Select Git source')
    repo=repo_name(source['repository'])
    info,_=api(repo,'',token)
    if info.get('private') is not False:raise FlowError('Only public repository documents may be retained')
    tree_path=Path(project)/'knowledge/catalog/repositories'/f'{source_id}.json'
    if not tree_path.exists():raise FlowError('Run wiki-inventory --retain first')
    tree=read_json(tree_path);sha=tree['commit']
    patterns=source.get('document_globs',['README*','docs/*.md','docs/*.rst'])
    paths=sorted(p for p,r in tree['entries'].items() if r['type']=='blob' and
                 Path(p).suffix.lower() in {'.md','.rst','.mdx','.txt'} and any(fnmatch.fnmatchcase(p,g) for g in patterns))
    ledger_path=Path(project)/'knowledge/catalog/document-ledgers'/f'{source_id}.json'
    ledger=read_json(ledger_path) if ledger_path.exists() else {'records':{}}
    def needs_copy(p):
        old=ledger['records'].get(p,{})
        return old.get('blob')!=tree['entries'][p]['sha'] or not old.get('page') or not child(project,old['page']).is_file()
    pending=[p for p in paths if needs_copy(p)]
    errors=[];processed=[]
    for path in pending[:max_documents]:
        try:
            result=read_code(store,repo,sha,path,token,max_chars=1000000)
            raw=store.artifact(result['artifact'])
            target=Path(project)/'knowledge/upstream-docs'/source_id/(path+'.md')
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
    ledger.update(commit=sha,patterns=patterns,discovered=len(paths),historical_paths=sorted(set(ledger['records'])-set(paths)))
    for name,row in ledger['records'].items():
        page=child(project,row['page'])
        if not page.exists():continue
        meta,body=wiki.parse_page(page)
        state='current-scan' if name in paths else 'outside-current-scan' if name in tree['entries'] else 'removed-from-latest-tree'
        if name in paths and row.get('blob')!=tree['entries'][name]['sha']:state='pending-newer-content'
        if meta.get('source_state')!=state:
            meta['source_state']=state
            try:generated_page(page,meta,body)
            except (OSError,ValueError) as exc:errors.append({'path':name,'error':str(exc)[:240]})
    write_json(ledger_path,ledger)
    remaining=[p for p in paths if needs_copy(p)]
    return {'source':source_id,'status':'partial' if remaining or errors else 'collected-not-reviewed',
            'processed':processed,'pending':len(remaining),'errors':errors,'patterns':patterns,'discovered':len(paths)}


def catalog(project):
    root=Path(project)/'knowledge'
    body='# 官方来源覆盖目录\n\n此页由来源目录和已保留页面重建。完整路径、文档采集和内容精读是不同覆盖层；没有逐模型或硬件验证的隐含承诺。\n\n'
    for source in read_json(root/'sources.json'):
        sid=source['id'];tree=root/'catalog/repositories'/f'{sid}.json'
        docs=root/'catalog/document-ledgers'/f'{sid}.json'
        body+='## '+sid+'\n\n'
        body+='来源：'+source['repository']+'\n\n'
        if tree.exists():
            value=read_json(tree)
            body+=f'- [源码目录](../source-maps/{sid}.md)：{len(value["entries"])} 路径，固定 `{value["commit"]}`，目录覆盖。\n'
        if docs.exists():
            value=read_json(docs)
            body+=f'- [文档目录](../upstream-docs/{sid}/)：扫描发现 {value["discovered"]} 份；保留 {len(value["records"])} 份（包含历史）；历史范围 {len(value.get("historical_paths",[]))} 份。扫描模式见 sources.json，pending 由更新运行报告给出。\n'
        if source.get('kind')!='web':
            for page in sorted((root/'prs'/source['repository'].replace('/','--')).glob('PR-*.md')):
                meta,_=wiki.parse_page(page)
                body+=f'- [PR #{meta["pr_number"]}：{meta["title"]}](../{page.relative_to(root).as_posix()})\n'
        body+='\n'
    generated_page(root/'catalog/README.md',{'id':'official-source-catalog','title':'官方源码 文档 PR 覆盖与更新索引',
        'kind':'source-map','engine':'cross-engine','review_level':'inventory-only','runtime_validated':False,'sources':[]},body)
    return {'status':'catalogued','source_count':len(read_json(root/'sources.json'))}


def update_source(store, project, source_id, token=None, max_prs=10, max_documents=40, since=None):
    source=source_for(project,source_id)
    if not source:raise FlowError('Unknown source')
    result={'source':source_id,'stages':{},'errors':[]}
    steps=([('inventory',lambda:inventory(store,project,source_id,token,True)),
            ('documents',lambda:sync_documents(store,project,source_id,token,max_documents)),
            ('prs',lambda:sync_prs(store,project,source_id,token,max_prs,since))] if source.get('kind')!='web' else [])
    steps.append(('content',lambda:wiki.refresh_source(store,project,source_id,token)))
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
