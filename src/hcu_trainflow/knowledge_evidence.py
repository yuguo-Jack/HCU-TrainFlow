"""Offline integrity checks for repository-owned site/case evidence.

Checks declared bytes and safe paths, not measurement quality or permissions.
"""
import hashlib
import json
from pathlib import Path, PurePosixPath
import re


def _linked_below(path, root):
    """Reject links in every component below the chosen repository root."""
    for part in (path, *path.parents):
        if part == root:
            break
        if part.is_symlink() or getattr(part, 'is_junction', lambda: False)():
            return True
    return False


def validate_manifests(project):
    root = Path(project).resolve()
    errors = []
    manifests = []
    for section in ('sites', 'experiments'):
        manifests.extend(sorted((root / 'knowledge' / section).glob('*/manifest.json')))
    for manifest in manifests:
        try:
            if _linked_below(manifest, root) or not manifest.resolve().is_relative_to(root):
                raise ValueError('linked manifest/site directory is not portable')
            value = json.loads(manifest.read_text(encoding='utf-8'))
            if not isinstance(value, dict) or value.get('schema_version') != 1:
                raise ValueError('expected manifest schema_version 1')
            rows = value.get('files')
            if not isinstance(rows, list) or not rows:
                raise ValueError('manifest files must be a nonempty list')
            seen = set()
            for row in rows:
                if not isinstance(row, dict):
                    raise ValueError('invalid file declaration')
                name = row.get('path')
                if not isinstance(name, str) or not name or '\\' in name or ':' in name:
                    raise ValueError('expected a relative POSIX path')
                rel = PurePosixPath(name)
                if rel.is_absolute() or '..' in rel.parts or name != rel.as_posix():
                    raise ValueError('unsafe or noncanonical evidence path')
                if name.casefold() in seen:
                    raise ValueError('duplicate evidence path')
                seen.add(name.casefold())
                path = manifest.parent / name
                base = manifest.parent.resolve()
                if _linked_below(path, root):
                    raise ValueError('symlink evidence is not portable')
                if not path.resolve().is_relative_to(base) or not path.is_file():
                    raise ValueError('missing or escaped evidence: ' + name)
                if not isinstance(row.get('sha256'), str) or not re.fullmatch('[0-9a-f]{64}', row['sha256']):
                    raise ValueError('invalid evidence SHA256: ' + name)
                if type(row.get('bytes')) is not int or row['bytes'] < 0:
                    raise ValueError('invalid evidence byte count: ' + name)
                if any(not isinstance(row.get(k), str) or not row[k].strip()
                       for k in ('source', 'representation', 'source_sha256')):
                    raise ValueError('missing evidence provenance: ' + name)
                if not re.fullmatch('[0-9a-f]{64}', row['source_sha256']):
                    raise ValueError('invalid original source SHA256: ' + name)
                raw = path.read_bytes()
                if len(raw) != row['bytes'] or hashlib.sha256(raw).hexdigest() != row['sha256']:
                    errors.append(str(manifest) + ': evidence bytes/hash mismatch: ' + name)
        except (OSError, ValueError, TypeError) as exc:
            errors.append(str(manifest) + ': ' + str(exc))
    return errors
