"""Check current authored documentation against local files and CLI, offline.

Historical logs and pinned upstream material are not current usage instructions.
This checks navigability and declared interfaces, not the truth of every claim.
"""
import argparse
from collections import Counter
from contextlib import redirect_stderr, redirect_stdout
import io
import json
import os
from pathlib import Path
import re
import shlex
import sys
import unicodedata
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'scripts'))
HISTORY = {'CHANGELOG.md', 'task_plan.md', 'findings.md', 'progress.md'}
FENCE = re.compile(r'^ {0,3}(`{3,}|~{3,})([^\n]*)\n.*?^ {0,3}\1[ \t]*$', re.M | re.S)


def prose(text):
    return FENCE.sub(lambda m: '\n' * m[0].count('\n'), text)


def pages(project):
    """Only controlled documentation roots; never traverse third-party checkouts."""
    result = [p for p in project.glob('*.md') if p.name not in HISTORY]
    for folder in ('docs', 'skills'):
        result.extend((project / folder).rglob('*.md'))
    result.extend((project / 'thirdparty').glob('*.md'))
    result.extend(p for p in (project / 'knowledge').rglob('*.md')
                  if 'upstream' not in p.relative_to(project / 'knowledge').parts)
    return sorted(set(result))


def links(text):
    body = prose(text)
    pattern = r'!?\[[^\]\n]*\]\((<[^>\n]+>|[^\s)\n]+)(?:\s+[^)]*)?\)'
    result = re.findall(pattern, body)
    # Reference-style destinations are checked even if their label is unused.
    result.extend(re.findall(r'^ {0,3}\[[^\]\n]+\]:\s*(<[^>\n]+>|\S+)', body, re.M))
    return [value.strip('<>') for value in result]


def anchors(text):
    body = prose(text)
    result = set(re.findall(r'(?:id|name)=[\"\x27]([^\"\x27]+)', body))
    seen = Counter()
    headings = re.findall(r'^ {0,3}#{1,6}\s+(.+?)\s*#*$', body, re.M)
    headings.extend(re.findall(r'^([^\n]+)\n(?:={3,}|-{3,})\s*$', body, re.M))
    for heading in headings:
        heading = re.sub(r'\[([^]]+)\]\([^)]+\)', r'\1', heading)
        heading = re.sub(r'<[^>]+>', '', heading).strip().lower()
        slug = ''.join(c for c in heading if c in '_- ' or unicodedata.category(c)[0] in 'LNM').replace(' ', '-')
        number = seen[slug]
        result.add(slug + ('-' + str(number) if number else ''))
        seen[slug] += 1
    return result


def cli_examples(text):
    for block in FENCE.finditer(text):
        if block[2].strip() not in {'', 'bash', 'sh', 'shell', 'powershell', 'console'}:
            continue
        body = block[0].split('\n', 1)[1].rsplit('\n', 1)[0]
        body = re.sub(r'[\\`]\s*\n\s*', ' ', body)
        for line in body.splitlines():
            if line.strip().startswith('hcu-trainflow '):
                yield line.strip()


def check_documentation(project, cli_parser=None):
    project = Path(project).resolve()
    docs = pages(project)
    texts = {p: p.read_text(encoding='utf-8') for p in docs}
    issues, incoming, children, heading_cache = [], Counter(), {}, {}
    examples_checked, json_checked = 0, 0
    if cli_parser is None:
        from hcu_trainflow.cli import parser
        cli_parser = parser()
    from install_skills import RENAMED
    for page, text in texts.items():
        name = page.relative_to(project).as_posix()
        destinations = [(raw, page.parent) for raw in links(text)]
        if page.name == 'SKILL.md':
            destinations.extend((raw, project) for raw in re.findall(
                r'`((?:docs|skills)/[^`\s<>*]+\.md(?:#[^`]*)?)`', prose(text)))
        for raw, base in destinations:
            url = urlsplit(raw)
            # Current self-links should also work in this checkout. Pinned links
            # refer to historical trees and must not be interpreted as HEAD.
            own = 'https://github.com/yuguo-Jack/HCU-TrainFlow/blob/main/'
            if raw.startswith(own):
                url = urlsplit(raw[len(own):])
                base = project
            else:
                if url.scheme or url.netloc:
                    continue
            target = Path(os.path.abspath(base / unquote(url.path))) if url.path else page
            if not target.is_relative_to(project) or not target.resolve().is_relative_to(project):
                issues.append(f'{name}: link leaves project: {raw}')
                continue
            if not target.exists():
                issues.append(f'{name}: missing link target: {raw}')
                continue
            parent = project
            for part in target.relative_to(project).parts:
                if parent not in children:
                    children[parent] = {child.name for child in parent.iterdir()}
                if part not in children[parent]:
                    issues.append(f'{name}: link case mismatch: {raw}')
                    break
                parent = parent / part
            if target != page:
                incoming[target] += 1
            if target.suffix.lower() == '.md' and url.fragment:
                if target not in heading_cache:
                    heading_cache[target] = anchors(target.read_text(encoding='utf-8'))
                if unquote(url.fragment) not in heading_cache[target]:
                    issues.append(f'{name}: missing heading anchor: {raw}')
        # Stable Wiki IDs and explicitly documented installer migration names
        # are valid. Only executable invocations of retired Skills are rejected.
        for old, new in RENAMED.items():
            if re.search(r'\$' + re.escape(old) + r'(?![\w-])', text):
                issues.append(f'{name}: retired Skill invocation {old}; use {new}')
        for command in cli_examples(text):
            examples_checked += 1
            err = io.StringIO()
            try:
                with redirect_stderr(err), redirect_stdout(io.StringIO()):
                    cli_parser.parse_args(shlex.split(command, comments=True)[1:])
            except (SystemExit, ValueError) as exc:
                if isinstance(exc, SystemExit) and exc.code == 0:
                    continue
                detail = err.getvalue().strip().splitlines()
                issues.append(f'{name}: invalid CLI example: {command} ({detail[-1] if detail else exc})')
        for block in FENCE.finditer(text):
            if block[2].strip() == 'json':
                json_checked += 1
                body = block[0].split('\n', 1)[1].rsplit('\n', 1)[0]
                try:
                    json.loads(body)
                except ValueError as exc:
                    issues.append(f'{name}: invalid JSON example: {exc}')
    # User-facing docs need a reading route, rather than becoming forgotten stubs.
    for page in docs:
        standalone_root = page.parent == project and page.name not in {'README.md', 'AGENTS.md'}
        if (standalone_root or page.is_relative_to(project / 'docs')) and not incoming[page]:
            issues.append(f'{page.relative_to(project).as_posix()}: no incoming documentation link')
    pyproject = project / 'pyproject.toml'
    if pyproject.is_file():
        metadata = pyproject.read_text(encoding='utf-8')
        section = re.search(r'^\[project\]\s*\n(.*?)(?=^\[|\Z)', metadata, re.M | re.S)
        version = re.search(r'^version\s*=\s*"([^"]+)"', section[1], re.M) if section else None
        if version:
            readme = texts.get(project / 'README.md', '')
            advertised = re.search(r'当前版本[：:]\s*`([^`]+)`', readme)
            if not advertised or advertised[1] != version[1]:
                issues.append('README.md: current version must match pyproject.toml')
            init = project / 'src/hcu_trainflow/__init__.py'
            actual = re.search(r'__version__\s*=\s*"([^"]+)"', init.read_text(encoding='utf-8')) if init.is_file() else None
            if not actual or actual[1] != version[1]:
                issues.append('src/hcu_trainflow/__init__.py: version differs from pyproject.toml')
            for page, text in texts.items():
                if page == project / 'README.md' or page.is_relative_to(project / 'knowledge'):
                    continue
                # Do not treat DTK, Torch or upstream versions as our release.
                pattern = r'(?:HCU-TrainFlow[^\n]{0,40}|(?:可执行|工程版本|项目版本|当前版本)[：: ]*)`?v?(0\.\d+\.\d+(?:[-.][\w.]+)?)'
                if re.search(pattern, text, re.I):
                    issues.append(f'{page.relative_to(project).as_posix()}: project version belongs in README/package/CHANGELOG')
    notice = texts.get(project / 'THIRD_PARTY_NOTICES.md', '')
    expected = []
    registry = project / 'knowledge/sources.json'
    if registry.is_file():
        expected.extend(row['repository'] if row['repository'].startswith('http')
                        else 'https://github.com/' + row['repository']
                        for row in json.loads(registry.read_text(encoding='utf-8')))
    manifest = project / 'thirdparty/manifest.json'
    if manifest.is_file():
        for row in json.loads(manifest.read_text(encoding='utf-8')).get('dependencies', []):
            expected.extend([row['url'], *row.get('mirrors', {}).values()])
            if row.get('upstream_url'):
                expected.append(row['upstream_url'])
    destinations = {link.rstrip('/').removesuffix('.git') for link in links(notice)}
    for url in sorted(set(expected)):
        if url.rstrip('/').removesuffix('.git') not in destinations:
            issues.append(f'THIRD_PARTY_NOTICES.md: registered source not linked: {url}')
    return {'status': 'incomplete' if issues else 'current', 'pages': len(docs),
            'cli_examples': examples_checked, 'json_examples': json_checked, 'issues': sorted(set(issues)),
            'scope': 'Current authored Markdown; historical logs and pinned upstream bodies are excluded'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, default=ROOT)
    args = parser.parse_args()
    result = check_documentation(args.project)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['status'] == 'current' else 1


if __name__ == '__main__':
    raise SystemExit(main())
