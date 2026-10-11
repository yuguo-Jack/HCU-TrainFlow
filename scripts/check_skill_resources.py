"""Check local documentation links and reachability of Skill references, offline."""
import argparse
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


def check_resources(project):
    project = Path(project).resolve()
    pages = sorted([*(project/'skills').rglob('*.md'), *(project/'docs').rglob('*.md')])
    edges, issues = {}, []
    for page in pages:
        text = page.read_text(encoding='utf-8')
        # Fenced examples are not documentation dependencies.
        text = re.sub(r'^```[^\n]*\n.*?^```\s*$', '', text, flags=re.M | re.S)
        targets = []
        for raw in re.findall(r'!?\[[^\]\n]*\]\(([^)\n]+)\)', text):
            raw = raw.strip()
            raw = raw[1:raw.index('>')] if raw.startswith('<') and '>' in raw else raw.split(' "', 1)[0]
            url = urlsplit(raw)
            if url.scheme or url.netloc or not url.path:
                continue
            targets.append((page.parent/unquote(url.path)).resolve())
        # Entrypoints use root-relative code paths. Other docs also discuss paths
        # in external repositories, so only Markdown links are checked there.
        if page.name == 'SKILL.md':
            for raw in re.findall(r'`((?:docs|skills)/[^`\s<>*]+\.md)(?:#[^`]*)?`', text):
                targets.append((project/raw).resolve())
        edges[page] = set(targets)
        for target in targets:
            if not target.is_relative_to(project):
                issues.append(f'{page.relative_to(project)}: link leaves project: {target}')
            elif not target.exists():
                issues.append(f'{page.relative_to(project)}: missing {target.relative_to(project)}')
    entries = list((project/'skills').glob('*/SKILL.md'))
    if not entries:
        issues.append('No Skill entrypoints found')
    if not (project/'docs/skill-reading-map.md').is_file():
        issues.append('Missing docs/skill-reading-map.md')
    visited, pending = set(), list(entries)
    while pending:
        page = pending.pop()
        if page in visited:
            continue
        visited.add(page)
        pending.extend(edges.get(page, set()) - visited)
    for page in pages:
        if page.is_relative_to(project/'skills') and 'references' in page.relative_to(project).parts and page not in visited:
            issues.append(f'{page.relative_to(project)}: no reading route from a Skill entrypoint')
    return {'status': 'incomplete' if issues else 'current', 'pages': len(pages),
            'reachable_pages': len(visited), 'issues': sorted(set(issues))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, default=ROOT)
    args = parser.parse_args()
    result = check_resources(args.project)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['status'] == 'current' else 1


if __name__ == '__main__':
    raise SystemExit(main())
