"""Validate Wiki IDs, pinned source hashes/paths and maintenance targets offline."""
import json
import os
from pathlib import Path
import sys
import hashlib
import re
import fnmatch
from urllib.parse import unquote, urlsplit
from hcu_trainflow.wiki import parse_page
from hcu_trainflow.knowledge_evidence import validate_manifests
from hcu_trainflow.official import document_exclusions
from hcu_trainflow.core import FlowError

GENERATED_KINDS = {'source-pr', 'source-map', 'source-document'}


def repository_name(value):
    """Compare registered GitHub repository identities, not branch names."""
    return str(value).lower().removeprefix('https://github.com/').removeprefix('git@github.com:').rstrip('/').removesuffix('.git')


def source_repositories(source):
    return {repository_name(x) for x in [source.get('repository', ''), *source.get('repository_aliases', [])]}


def local_path(root, name):
    path = (root / name).resolve()
    return path if path.is_relative_to(root.resolve()) else None


def validate_baselines(sources, records):
    errors = []
    for sid, source in sources.items():
        for name, row in source.get('baseline_files', {}).items():
            record = records.get((source.get('repository'), source.get('baseline_commit'), name))
            if not record or record.get('sha256') != row.get('sha256'):
                errors.append(f'{sid}: baseline source missing/hash mismatch: {name}')
            if name not in source.get('paths', []):
                errors.append(f'{sid}: baseline path not monitored: {name}')
    return errors


def validate_catalog(root, sources, pages):
    """Check generated metadata against its own inventory, including old documents."""
    errors = []
    for path in (root / 'knowledge/catalog/repositories').glob('*.json'):
        data = json.loads(path.read_text(encoding='utf-8'))
        sid = path.stem
        source = sources.get(sid)
        if not source or data.get('source') != sid or repository_name(data.get('repository')) not in source_repositories(source):
            errors.append(f'{path}: catalog source identity mismatch')
        from hcu_trainflow.knowledge_layout import source_map
        mapping = source_map(root, sid).resolve()
        if mapping not in pages:
            errors.append(f'{path}: missing generated source map')
        else:
            meta, body = pages[mapping]
            commit = re.search(r'\bCommit `([^`]+)`', body)
            if meta.get('kind') != 'source-map' or not commit or commit.group(1) != data.get('commit'):
                errors.append(f'{mapping}: source map/catalog commit mismatch')
    for path in (root / 'knowledge/catalog/document-ledgers').glob('*.json'):
        data = json.loads(path.read_text(encoding='utf-8'))
        source = sources.get(path.stem)
        if not source:
            errors.append(f'{path}: unknown document ledger source')
            continue
        for name, row in data.get('records', {}).items():
            page = local_path(root, row.get('page', ''))
            meta = pages.get(page, ({}, ''))[0]
            if (meta.get('kind') != 'source-document' or meta.get('path') != name
                    or repository_name(meta.get('repository')) not in source_repositories(source)
                    or meta.get('commit') != row.get('commit') or meta.get('raw_sha256') != row.get('sha256')):
                errors.append(f'{path}: document page/ledger identity or hash mismatch: {name}')
            # A retained document may predate the inventory even when unchanged.
            # Compare its record, never require every document to match the newest tree.
    return errors


def validate_dependency_sources(root, sources, pages):
    """Explicit current coverage is distinct from historical page citations.

    thirdparty/manifest.json may declare dependency_sources entries with dependency,
    source and current_pages. Only those authored pages must cite that source at the
    dependency commit. A registry branch/tag may differ while identifying the same
    commit. This check is offline and does not change checkouts or version locks.
    """
    path = root / 'thirdparty/manifest.json'
    if not path.is_file():
        return []
    manifest = json.loads(path.read_text(encoding='utf-8'))
    dependencies = {row['id']: row for row in manifest.get('dependencies', [])}
    errors = []
    seen = set()
    bindings = manifest.get('dependency_sources', [])
    if not isinstance(bindings, list):
        return [f'{path}: dependency_sources must be an array']
    for binding in bindings:
        if not isinstance(binding, dict):
            errors.append(f'{path}: invalid dependency source binding')
            continue
        did, sid = binding.get('dependency'), binding.get('source')
        label = f'dependency {did} / source {sid}'
        if did in seen:
            errors.append(f'{label}: duplicate dependency source binding')
        seen.add(did)
        dependency, source = dependencies.get(did), sources.get(sid)
        if not dependency or not source:
            errors.append(f'{label}: unknown dependency or Wiki source')
            continue
        if repository_name(dependency.get('url')) not in source_repositories(source):
            errors.append(f'{label}: repository mismatch')
        commit = dependency.get('commit')
        if not commit or source.get('baseline_commit') != commit:
            errors.append(f'{label}: Wiki baseline differs from dependency commit')
        if not source.get('baseline_files'):
            errors.append(f'{label}: current source baseline has no acquired files')
        current_pages = binding.get('current_pages')
        if not isinstance(current_pages, list) or not current_pages:
            errors.append(f'{label}: current_pages must name current authored coverage')
            continue
        for name in current_pages:
            page = local_path(root, name) if isinstance(name, str) else None
            meta = pages.get(page, ({}, ''))[0]
            refs = [row for row in meta.get('sources', []) if row.get('source') == sid]
            if not meta or meta.get('kind') in GENERATED_KINDS or not refs:
                errors.append(f'{label}: missing current authored source coverage: {name}')
            elif any(row.get('commit') != commit for row in refs):
                errors.append(f'{label}: current page cites a different commit: {name}')
        catalog = root / 'knowledge/catalog/repositories' / (sid + '.json')
        if not catalog.is_file() or json.loads(catalog.read_text(encoding='utf-8')).get('commit') != commit:
            errors.append(f'{label}: current source inventory differs from dependency commit')
    return errors


def validate_authored_links(root, path, body):
    """Source copies retain upstream-relative links; only authored local links count."""
    body = re.sub(r'```.*?```|~~~.*?~~~', '', body, flags=re.S)
    simple = r'!?\[[^\]\n]*\]\((<[^>\n]+>|[^\s)\n]+)(?:\s+[^)]*)?\)'
    nested = r'!?\[(?:[^\[\]\n]|\[[^\[\]\n]*\](?!\())*\]\((<[^>\n]+>|[^\s)\n]+)(?:\s+[^)]*)?\)'
    links = list(dict.fromkeys(re.findall(simple, body) + re.findall(nested, body)))
    errors = []
    for link in links:
        target = urlsplit(link.strip('<>'))
        if target.scheme or target.netloc or not target.path:
            continue
        # Preserve authored spelling before resolve() canonicalizes case on
        # Windows. A link that works there can still break in a Linux clone.
        spelled = Path(os.path.abspath(path.parent / unquote(target.path)))
        dest = spelled.resolve()
        if not spelled.is_relative_to(root.resolve()) or not dest.is_relative_to(root.resolve()) or not dest.exists():
            errors.append(f'{path}: broken local knowledge link: {link}')
        else:
            parent = root.resolve()
            for part in spelled.relative_to(parent).parts:
                if part not in {child.name for child in parent.iterdir()}:
                    errors.append(f'{path}: local knowledge link case mismatch: {link}')
                    break
                parent = parent / part
    return errors


def validate(root):
    root = Path(root).resolve()
    errors=[];ids=set();pr_refs=[];pages={};kinds={}
    lock=json.loads((root/'knowledge/source-lock.json').read_text(encoding='utf-8'))
    registry=json.loads((root/'knowledge/sources.json').read_text(encoding='utf-8'))
    sources={x['id']:x for x in registry}
    exclusion_rules={}
    for sid,source in sources.items():
        try:
            exclusion_rules[sid]=document_exclusions(source)
        except FlowError as exc:
            errors.append(f'{sid}: {exc}')
    records={(x['repo'],x['commit'],x['path']):x for x in lock['files']}
    if len(sources) != len(registry):errors.append('Duplicate source registry id')
    if len(records) != len(lock['files']):errors.append('Duplicate source lock record')
    for path in (root/'knowledge').rglob('*.md'):
        meta,body=parse_page(path)
        pages[path.resolve()] = (meta, body)
        if not meta.get('id') or meta['id'] in ids:errors.append(str(path)+': absent/duplicate id')
        ids.add(meta.get('id'))
        kinds[meta.get('id')] = meta.get('kind')
        pr_refs.extend((path,pid) for pid in meta.get('pr_sources',[]))
        if meta.get('kind') in GENERATED_KINDS:
            if meta.get('generated_body_sha256')!=hashlib.sha256(body.encode()).hexdigest():errors.append(str(path)+': generated source page modified')
            if meta.get('runtime_validated') is not False:errors.append(str(path)+': generated source material cannot claim runtime validation')
            if meta.get('kind')=='source-document':
                for sid,source in sources.items():
                    if repository_name(meta.get('repository')) in source_repositories(source):
                        for pattern,reason in exclusion_rules.get(sid,{}).items():
                            if fnmatch.fnmatchcase(meta.get('path',''),pattern):
                                errors.append(f'{path}: document excluded by {sid} policy ({reason}); curate page, links and ledger')
        else:
            errors.extend(validate_authored_links(root, path, body))
        if meta.get('review_level') == 'navigation-only' or meta.get('id') == 'official-source-catalog':
            errors.extend(validate_authored_links(root, path, body))
        if meta.get('kind')=='source-pr':
            raw=(root/meta.get('artifact_path','')).resolve()
            if not raw.is_relative_to((root/'knowledge/evidence/prs').resolve()) or not raw.is_file():errors.append(str(path)+': missing PR evidence')
            elif hashlib.sha256(raw.read_bytes()).hexdigest()!=meta.get('artifact_sha256'):errors.append(str(path)+': PR evidence hash mismatch')
            else:
                artifact = json.loads(raw.read_text(encoding='utf-8'))
                if repository_name(artifact.get('repository')) != repository_name(meta.get('repository')) or artifact.get('number') != meta.get('pr_number'):
                    errors.append(str(path)+': PR evidence identity mismatch')
        for s in meta.get('sources',[]):
            source=sources.get(s['source'],{})
            record=records.get((source.get('repository'),s['commit'],s['path']))
            if not record or record['sha256']!=s['sha256']:errors.append(str(path)+': source missing/hash mismatch')
            if s['path'] not in source.get('paths',[]):errors.append(str(path)+': source not monitored')
    for path,pid in pr_refs:
        if kinds.get(pid) != 'source-pr':errors.append(str(path)+': missing related PR source '+pid)
    for rule in json.loads((root/'knowledge/maintenance.json').read_text(encoding='utf-8')):
        if rule['source'] not in sources:errors.append('Unknown maintenance source')
        elif any(name not in sources[rule['source']].get('paths', []) for name in rule.get('paths', [])):
            errors.append('Unmonitored maintenance path for '+rule['source'])
        for target in rule['targets']:
            if not (root/target).is_file():errors.append('Missing maintenance target '+target)
    errors.extend(validate_baselines(sources, records))
    errors.extend(validate_catalog(root, sources, pages))
    errors.extend(validate_dependency_sources(root, sources, pages))
    errors.extend(validate_project_layout(root, sources, pages))
    errors.extend(validate_manifests(root))
    return {'pages':len(ids),'sources':len(sources),'errors':errors}


def validate_project_layout(root, sources, pages):
    """Check ownership and paths without turning directory checks into review."""
    from hcu_trainflow import knowledge_layout as layout
    errors = []
    for sid, source in sources.items():
        try:
            layout.require_local_owner(root, sid)
            layout.require_local_owner(root, source['repository'])
        except FlowError as exc:
            errors.append(str(exc))
        if not source.get('knowledge_project'):
            errors.append(f'{sid}: missing knowledge_project')
        entry = root / 'knowledge/projects' / layout.project_id(root, source=sid) / 'README.md'
        if not entry.is_file():
            errors.append(f'{sid}: missing project README')
    for path, (meta, _) in pages.items():
        kind = meta.get('kind')
        expected = None
        if kind in {'source-pr', 'source-document'}:
            try:
                layout.require_local_owner(root, meta.get('repository', ''))
            except FlowError as exc:
                errors.append(str(exc))
        if kind == 'source-pr':
            expected = layout.pr_root(root, meta['repository']) / path.name
        elif kind == 'source-document':
            registered = next((s for s in sources.values() if s.get('repository') == meta.get('repository')), None)
            if registered:
                expected = layout.document_root(root, registered['id']) / (meta['path'] + '.md')
        if expected and path != expected.resolve():
            errors.append(f'{path}: source material outside owning project')
    for row in layout.external_routes(root):
        if row['id'] in sources:
            errors.append(f'{row["id"]}: external knowledge must not be locally collected')
        for name in [row['entry'], *row.get('targets', [])]:
            target = local_path(root, name)
            if not target or not target.is_file():
                errors.append(f'{row["id"]}: missing external route/maintenance target {name}')
    manifest = root / 'thirdparty/manifest.json'
    if manifest.is_file():
        data = json.loads(manifest.read_text(encoding='utf-8'))
        deps = {d['id']:d for d in data.get('dependencies', [])}
        for contract in data.get('integration_contracts', []):
            dependency = deps.get(contract['dependency'], {})
            if not dependency or dependency.get('commit') != contract.get('reviewed_commit'):
                errors.append(f'{contract["dependency"]}: integration contract needs dependency-version review')
            if not contract.get('documents'):
                errors.append(f'{contract["dependency"]}: missing integration documents')
            for name in contract.get('documents', []):
                target = local_path(root, name)
                if not target or not target.is_file():
                    errors.append(f'Missing integration contract {name}')
    return errors

if __name__=='__main__':
    result=validate(Path(__file__).resolve().parents[1]);print(json.dumps(result,ensure_ascii=False,indent=2));sys.exit(bool(result['errors']))
