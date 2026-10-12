"""Check authored Wiki reading routes, never infer factual or runtime coverage."""
import json
from pathlib import Path
import sys

DIMENSIONS = {
    'scope', 'structure', 'installation', 'run_test', 'contracts',
    'call_chain', 'performance_memory', 'diagnosis_recovery', 'versions_prs',
}
ROLES = {'engine', 'library', 'ecosystem', 'tool', 'method'}


def validate_coverage(root):
    root = Path(root).resolve()
    manifest = root / 'knowledge/coverage.json'
    errors = []
    if not manifest.is_file():
        return ['Missing knowledge/coverage.json']
    data = json.loads(manifest.read_text(encoding='utf-8'))
    registry = json.loads((root / 'knowledge/sources.json').read_text(encoding='utf-8'))
    sources = {x['id'] for x in registry}
    covered, identities = set(), set()

    for source in registry:
        parent = source.get('parent_gitlink')
        if not parent:
            continue
        sid, name = parent.get('source'), parent.get('path')
        catalog = root / 'knowledge/catalog/repositories' / (str(sid) + '.json')
        if sid not in sources or not name or not catalog.is_file():
            errors.append(f'{source["id"]}: missing parent gitlink inventory')
            continue
        entry = json.loads(catalog.read_text(encoding='utf-8')).get('entries', {}).get(name, {})
        if (entry.get('type') != 'commit' or source.get('ref') != entry.get('sha')
                or source.get('baseline_commit') != entry.get('sha')):
            errors.append(f'{source["id"]}: parent gitlink changed; review the child at the pinned commit')

    def page(value, label):
        if not isinstance(value, str) or not value:
            errors.append(f'{label}: missing page')
            return
        path = (root / value).resolve()
        if not path.is_relative_to(root / 'knowledge') or not path.is_file() or path.suffix != '.md':
            errors.append(f'{label}: invalid knowledge page {value}')
        elif any(part in {'upstream-docs', 'source-maps', 'prs'} for part in path.relative_to(root / 'knowledge').parts):
            errors.append(f'{label}: generated sources do not replace authored explanations')

    for row in data.get('projects', []):
        identity = row.get('id', '')
        if not identity or identity in identities:
            errors.append(f'Duplicate or empty coverage identity: {identity}')
        identities.add(identity)
        if row.get('role') not in ROLES:
            errors.append(f'{identity}: invalid role')
        registered = set(row.get('sources', []))
        if not registered or registered - sources:
            errors.append(f'{identity}: missing/unknown registered sources {sorted(registered - sources)}')
        if registered & covered:
            errors.append(f'{identity}: source assigned to multiple coverage groups')
        covered.update(registered)
        page(row.get('entry'), identity)
        dimensions = row.get('dimensions', {})
        if set(dimensions) != DIMENSIONS:
            errors.append(f'{identity}: missing/unknown dimensions {sorted(DIMENSIONS ^ set(dimensions))}')
        for name, pages in dimensions.items():
            if not isinstance(pages, list) or not pages:
                errors.append(f'{identity}/{name}: no reading route')
                continue
            for value in pages:
                page(value, identity + '/' + name)
        mechanisms = row.get('mechanisms', [])
        if row.get('role') in {'engine', 'library', 'ecosystem'} and len(mechanisms) < 2:
            errors.append(f'{identity}: at least two explained mechanisms required')
        for mechanism in mechanisms:
            if not mechanism.get('topic'):
                errors.append(f'{identity}: mechanism needs a concrete topic')
            page(mechanism.get('page'), identity + '/mechanism')
        if not row.get('limits'):
            errors.append(f'{identity}: explicit reading/runtime limits required')
    if sources - covered:
        errors.append('Registered sources without authored route: ' + ', '.join(sorted(sources - covered)))
    return errors


if __name__ == '__main__':
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
    failures = validate_coverage(root)
    print(json.dumps({'ok': not failures, 'errors': failures,
                      'scope': 'organization only; source review and hardware evidence remain separate'}, ensure_ascii=False, indent=2))
    raise SystemExit(bool(failures))
