"""Choose CI scope conservatively; no network or repository mutations."""
import argparse
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess

DATA_TESTS = [
    'tests/test_monitor_wiki.py', 'tests/test_official_experience.py',
    'tests/test_knowledge_layout.py', 'tests/test_knowledge_evidence.py',
    'tests/test_knowledge_consistency.py', 'tests/test_wiki_coverage.py',
    'tests/test_documentation.py', 'tests/test_skill_routing.py',
    'tests/test_full_setup.py', 'tests/test_ci_scope.py',
    'tests/test_official_lite.py', 'tests/test_wiki_index_lite.py',
    'tests/test_wiki_coverage_lite.py', 'tests/test_persistent_lite_contract.py',
    'tests/test_wiki_maintenance_branch.py', 'tests/test_wiki_search_policy.py',
    'tests/test_official_incremental_review.py',
]


def classify(paths):
    """Only known prose/data paths use the reduced lane; unknown paths run all."""
    paths = list(paths)
    full, categories = not paths, set()
    reasons = [] if paths else ['No trustworthy changed-file inventory']
    for name in paths:
        path = PurePosixPath(name)
        if (not name or '\\' in name or path.is_absolute() or '..' in path.parts
                or any(part.startswith('.') for part in path.parts)):
            full = True
            reasons.append(name + ': code, configuration or unknown path')
        elif name == 'knowledge/storage.json':
            full = True
            reasons.append(name + ': storage schema/reader contract')
        elif path.parts[0] == 'knowledge':
            categories.add('knowledge')
        elif path.parts[0] == 'docs' and path.suffix.lower() in {'.md', '.svg', '.png', '.jpg', '.jpeg', '.webp'}:
            categories.add('docs')
        elif path.parts[0] == 'skills' and path.suffix.lower() in {'.md', '.json', '.yaml', '.yml'}:
            categories.add('skills')
        elif len(path.parts) == 1 and name in {'README.md', 'CHANGELOG.md', 'findings.md', 'progress.md', 'task_plan.md'}:
            categories.add('docs')
        else:
            full = True
            reasons.append(name + ': software or unclassified contract')
    return {'full': full, 'knowledge': full or 'knowledge' in categories,
            'docs': full or 'docs' in categories, 'skills': full or 'skills' in categories,
            'changed_files': len(paths), 'reasons': reasons,
            'data_tests': DATA_TESTS}


def changed_paths(root, base, head, run=subprocess.run):
    if not all(re.fullmatch(r'[0-9a-fA-F]{40}', x or '') and set(x) != {'0'} for x in (base, head)):
        return None
    result = run(['git', 'diff', '--name-only', '--no-renames', '-z', base, head, '--'],
                 cwd=root, capture_output=True, check=False)
    if result.returncode:
        return None
    try:
        return [value.decode('utf-8', errors='strict') for value in result.stdout.split(b'\0') if value]
    except UnicodeDecodeError:
        return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', default=os.environ.get('CI_BASE', ''))
    parser.add_argument('--head', default=os.environ.get('CI_HEAD', ''))
    parser.add_argument('--test-targets', action='store_true')
    args = parser.parse_args()
    if args.test_targets:
        print(' '.join(DATA_TESTS))
        return
    paths = changed_paths(Path(__file__).resolve().parents[1], args.base, args.head)
    result = classify(paths or [])
    if paths is None:
        result['reasons'] = ['Missing/unreadable base or head; run full software matrix']
    output = os.environ.get('GITHUB_OUTPUT')
    if output:
        with Path(output).open('a', encoding='utf-8') as stream:
            for key in ['full', 'knowledge', 'docs', 'skills']:
                stream.write(f'{key}={str(result[key]).lower()}\n')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
