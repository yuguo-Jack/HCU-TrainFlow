"""Portable fixed website originals, independent of a private task Store.

Only explicitly applied registered documents are retained. Historical receipts
remain immutable; the undated index points to deduplicated, hash-named bytes.
"""
from pathlib import Path
import re
from urllib.parse import urlsplit

from .core import FlowError, atomic_write, child, digest, read_json, write_json
from . import knowledge_layout as layout


INDEX = 'knowledge/catalog/web-originals.json'
REPRESENTATIONS = {'original': '.html', 'extracted_text': '.txt'}


def _sha(value):
    return isinstance(value, str) and re.fullmatch(r'[0-9a-f]{64}', value)


def _url(value):
    if not isinstance(value, str):
        return False
    parsed = urlsplit(value)
    return (parsed.scheme == 'https' and parsed.hostname == 'docs.nvidia.com'
            and not parsed.username and not parsed.password and parsed.port in (None, 443))


def _path(project, relative):
    root = Path(project).resolve()
    path = root / relative
    for part in (path, *path.parents):
        if part == root:
            break
        if part.is_symlink() or getattr(part, 'is_junction', lambda: False)():
            raise FlowError('Linked website evidence is not portable')
    return child(root, relative)


def _key(row):
    # HTML can change without changing the extracted-text revision. Preserve
    # those original observations too, rather than replacing historical bytes.
    return (row['source'], row['revision'], row['path'], row['url'],
            row['original']['sha256'], row['extracted_text']['sha256'])


def _validate_row(row):
    if not isinstance(row, dict) or any(not isinstance(row.get(k), str) or not row[k].strip()
                                       for k in ('source', 'path')):
        raise FlowError('Invalid website original identity')
    if not _sha(row.get('revision')) or not _url(row.get('url')):
        raise FlowError('Website original requires a fixed fingerprint and canonical URL')
    for name, suffix in REPRESENTATIONS.items():
        value = row.get(name)
        if (not isinstance(value, dict) or not _sha(value.get('sha256'))
                or type(value.get('bytes')) is not int or value['bytes'] < 0
                or value.get('file') != f'knowledge/evidence/web/{value["sha256"]}{suffix}'):
            raise FlowError('Invalid hash-named website evidence declaration')


def _bytes(project, declaration):
    path = _path(project, declaration['file'])
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise FlowError('Missing shared website original: ' + declaration['file']) from exc
    if len(data) != declaration['bytes'] or digest(data) != declaration['sha256']:
        raise FlowError('Shared website evidence bytes/hash mismatch: ' + declaration['file'])
    return data


def originals(project, *, verify=True):
    """Read the live index and compatible dated receipts, without network I/O."""
    directory = Path(project) / 'knowledge/catalog'
    paths = [directory / 'web-originals.json', *sorted(directory.glob('web-originals-*.json'))]
    rows = {}
    for path in paths:
        if not path.exists():
            continue
        value = read_json(_path(project, path.relative_to(Path(project)).as_posix()))
        if not isinstance(value, dict) or value.get('schema') != 1 or not isinstance(value.get('originals'), list):
            raise FlowError('Invalid shared website originals index: ' + path.name)
        for row in value['originals']:
            _validate_row(row)
            key = _key(row)
            if key in rows and rows[key] != row:
                raise FlowError('Conflicting website original declarations')
            rows[key] = row
    if verify:
        for row in rows.values():
            for name in REPRESENTATIONS:
                _bytes(project, row[name])
    return list(rows.values())


def _write_index(project, rows):
    path = _path(project, INDEX)
    value = {'schema': 1,
             'scope': 'Applied registered official website responses and extracted text; historical originals retained.',
             'copyright_notice': 'Official NVIDIA material; preserve attribution and thirdparty/KNOWLEDGE-NOTICES.md.',
             'originals': sorted(rows, key=_key)}
    if not path.is_file() or read_json(path) != value:
        write_json(path, value)
    return INDEX


def migrate_index(project):
    """Adopt existing verified dated records without copying their objects."""
    rows = originals(project)
    if not rows:
        return None
    return _write_index(project, rows)


def retain_stage(store, project, source, stage):
    """Verify all inputs before sharing bytes or advancing any source lock."""
    if (source.get('kind') != 'web' or stage['repository'] != source['repository']
            or stage['ref'] != 'registered-official-pages' or stage.get('absence_proofs')
            or set(stage['files']) != set(source.get('paths', []))):
        raise FlowError('Website source registration changed; refresh and review again')
    rows = {_key(row): row for row in originals(project)}
    payloads = {}
    for name, value in stage['files'].items():
        url = source.get('documents', {}).get(name)
        if (not _url(url) or value.get('url') != url
                or not _sha(value.get('sha256')) or not _sha(value.get('raw_sha256'))):
            raise FlowError('Website source registration or fixed evidence changed; refresh and review again')
        row = {'source': source['id'], 'revision': stage['commit'], 'path': name, 'url': url}
        for representation, field in [('original', 'raw_sha256'), ('extracted_text', 'sha256')]:
            sha = value[field]
            data = store.artifact(sha)
            if digest(data) != sha:
                raise FlowError('Website acquisition artifact hash mismatch')
            relative = f'knowledge/evidence/web/{sha}{REPRESENTATIONS[representation]}'
            declaration = {'file': relative, 'sha256': sha, 'bytes': len(data)}
            target = _path(project, relative)
            if target.exists():
                _bytes(project, declaration)
            row[representation] = declaration
            payloads[relative] = data
        _validate_row(row)
        rows[_key(row)] = row
    # Preflight above includes every new object and every retained declaration.
    # An interrupted publish may leave reusable hash-named objects, never an
    # applied lock pointing to unavailable private-only bytes.
    for relative, data in payloads.items():
        target = _path(project, relative)
        if not target.exists():
            atomic_write(target, data)
    for row in rows.values():
        for representation in REPRESENTATIONS:
            _bytes(project, row[representation])
    index = _write_index(project, list(rows.values()))
    return {'index': index, 'objects': len(payloads), 'originals': len(stage['files'])}


def read_original(project, source_id, name, *, revision=None, text=False, max_chars=24000):
    """Read verified shared bytes, including history, with no Store or fetch."""
    if not 1 <= max_chars <= 1000000:
        raise FlowError('max-chars must be 1..1000000')
    layout.require_local_owner(project, source_id)
    registry = read_json(Path(project) / 'knowledge/sources.json')
    source = next((row for row in registry if row['id'] == source_id), None)
    if not source or source.get('kind') != 'web':
        raise FlowError('Select a registered website source')
    layout.require_local_owner(project, source['repository'])
    revision = revision or source.get('baseline_commit')
    if not _sha(revision):
        raise FlowError('Website original requires a full content fingerprint')
    lock = read_json(Path(project) / 'knowledge/source-lock.json')
    selected = [row for row in lock.get('files', []) if row.get('repo') == source['repository']
                and row.get('commit') == revision and row.get('path') == name]
    if len(selected) != 1:
        raise FlowError('No unambiguous fixed website source lock for this path/revision')
    bound = selected[0]
    matches = [row for row in originals(project, verify=False)
               if row['source'] == source_id and row['revision'] == revision and row['path'] == name
               and row['url'] == bound.get('url') and row['original']['sha256'] == bound.get('raw_sha256')
               and row['extracted_text']['sha256'] == bound.get('sha256')]
    if len(matches) != 1:
        raise FlowError('Fixed website original is not shared; no source was refreshed or missing bytes inferred')
    row = matches[0]
    # Verify both representations even when displaying just one.
    values = {key: _bytes(project, row[key]) for key in REPRESENTATIONS}
    representation = 'extracted_text' if text else 'original'
    declaration = row[representation]
    content = values[representation].decode('utf-8')
    return {'source': source_id, 'revision': revision, 'path': name, 'url': row['url'],
            'representation': representation, 'local_path': str(_path(project, declaration['file'])),
            'sha256': declaration['sha256'], 'bytes': declaration['bytes'],
            'content': content[:max_chars], 'truncated': len(content) > max_chars,
            'status': 'shared-fixed-original', 'source_refreshed': False}


def validate(project):
    """Check declared bytes and current web bindings; do not certify old gaps."""
    try:
        rows = originals(project)
        registry = read_json(Path(project) / 'knowledge/sources.json')
        lock = read_json(Path(project) / 'knowledge/source-lock.json')
        for source in registry:
            if source.get('kind') != 'web':
                continue
            for name, value in source.get('baseline_files', {}).items():
                matches = [record for record in lock.get('files', [])
                           if record.get('repo') == source['repository']
                           and record.get('commit') == source.get('baseline_commit') and record.get('path') == name]
                if len(matches) != 1 or any(matches[0].get(key) != value.get(key)
                                            for key in ('sha256', 'raw_sha256', 'url')):
                    raise FlowError(f'{source["id"]}: current website lock differs from baseline: {name}')
                if not any(row['source'] == source['id'] and row['revision'] == source.get('baseline_commit')
                           and row['path'] == name and row['url'] == value.get('url')
                           and row['original']['sha256'] == value.get('raw_sha256')
                           and row['extracted_text']['sha256'] == value.get('sha256') for row in rows):
                    raise FlowError(f'{source["id"]}: current website baseline lacks shared fixed bytes: {name}')
        return []
    except (OSError, ValueError, TypeError, KeyError) as exc:
        return ['Website originals: ' + str(exc)]
