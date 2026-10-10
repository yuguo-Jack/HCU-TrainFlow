"""Validated, scoped technical summaries for the generated board, never gates."""
import html
import json
import re

from .core import FlowError


SECTIONS = {
    'environment': '环境与测试预期 / 结果',
    'configuration': '配置、并行与显存取舍',
    'analysis': '性能分析与归因',
    'operators': '热点算子、模型与优化空间',
    'experiments': '参数与 Kernel 实验',
    'recovery': '扩容与恢复验证',
    'training': '持续训练观测',
    'review': 'RLCR 决策与验收缺口',
}
QUALIFICATIONS = {
    'not-measured': '未实测 / 待验证',
    'source-only': '仅源码分析 / 未实测',
    'local-tested': '本地测试 / 非硬件验收',
    'measured': '实测 / 仅所述范围',
}
MAX_BYTES = 256 * 1024


def text(value, label, limit, *, single_line=False):
    if (not isinstance(value, str) or not value.strip() or len(value) > limit
            or any(ord(c) < 32 and c not in '\n\t' or ord(c) == 127 for c in value)
            or single_line and '\n' in value):
        raise FlowError(f'{label} must be nonempty text up to {limit} characters' +
                        (' on one line' if single_line else ''))


def evidence(store, value):
    if (not isinstance(value, list) or len(value) > 64
            or any(not isinstance(sha, str) or not re.fullmatch(r'[0-9a-f]{64}', sha) for sha in value)):
        raise FlowError('Board evidence must be a list of at most 64 retained artifact IDs')
    for sha in value:
        store.artifact(sha)


def _qualification(value, proof):
    if not isinstance(value, str) or value not in QUALIFICATIONS:
        raise FlowError('Technical qualification must be not-measured, source-only, local-tested or measured')
    if value != 'not-measured' and not proof:
        raise FlowError('Source analysis, tests and measurements require retained evidence')


def validate(store, sections, *, patch=False):
    if not isinstance(sections, dict) or set(sections) - SECTIONS.keys():
        raise FlowError('Unknown technical section; use ' + ', '.join(SECTIONS))
    required = {'summary', 'scope', 'qualification', 'columns', 'rows', 'notes', 'evidence'}
    for name, section in sections.items():
        if section is None and patch:
            continue
        if not isinstance(section, dict) or set(section) != required:
            raise FlowError(f'Technical section {name} requires ' + ', '.join(sorted(required)))
        text(section['summary'], 'Technical summary', 2000)
        text(section['scope'], 'Technical scope', 2000)
        evidence(store, section['evidence'])
        _qualification(section['qualification'], section['evidence'])
        columns = section['columns']
        if not isinstance(columns, list) or not 1 <= len(columns) <= 10:
            raise FlowError('Technical tables require 1 to 10 columns')
        for column in columns:
            text(column, 'Technical column', 100, single_line=True)
        if len(set(columns)) != len(columns):
            raise FlowError('Technical column names must be unique')
        if not isinstance(section['rows'], list) or len(section['rows']) > 100:
            raise FlowError('Technical sections allow at most 100 rows; split or summarize explicitly')
        for row in section['rows']:
            if not isinstance(row, dict) or set(row) != {'cells', 'qualification', 'evidence'}:
                raise FlowError('Technical rows require cells, qualification and evidence')
            if not isinstance(row['cells'], list) or len(row['cells']) != len(columns):
                raise FlowError('Technical row cells must match the columns')
            for cell in row['cells']:
                text(cell, 'Technical cell', 2000)
            evidence(store, row['evidence'])
            _qualification(row['qualification'], row['evidence'] or section['evidence'])
        if not isinstance(section['notes'], list) or len(section['notes']) > 20:
            raise FlowError('Technical notes allow at most 20 items')
        for note in section['notes']:
            text(note, 'Technical note', 2000)
    if len(json.dumps(sections, ensure_ascii=False).encode('utf8')) > MAX_BYTES:
        raise FlowError('Combined technical board exceeds 256 KiB; summarize explicitly')


def fresh(body, task):
    return (bool(body) and body.get('context') == task['context']
            and body.get('context_epoch') == task['context_epoch'])


def merge(previous, update, task):
    """Replace named sections; omission preserves only the same context epoch."""
    sections = dict(previous.get('technical', {})) if fresh(previous, task) else {}
    for name, section in update.items():
        if section is None:
            sections.pop(name, None)
        else:
            sections[name] = section
    return sections


def plain(value):
    """Render author text literally; only the renderer can create links or HTML."""
    escaped = html.escape(value, quote=True)
    escaped = re.sub(r'([\\`*_{}\[\]()#+.!~-])', r'\\\1', escaped)
    return escaped.replace('|', '&#124;').replace('\n', '<br>').replace('\t', '    ')


def render(sections, link):
    if not sections:
        return []
    lines = ['', '## 技术详情', '',
             '下列内容是带范围的观察与判断；源码、本地测试和硬件实测分别标记，不自动通过任何验收。']
    for name, title in SECTIONS.items():
        if name not in sections:
            continue
        section = sections[name]
        lines += ['', '### ' + title, '', plain(section['summary']), '',
                  '**范围：** ' + plain(section['scope']), '',
                  '**结论依据：** ' + QUALIFICATIONS[section['qualification']], '']
        if section['evidence']:
            lines += ['栏目证据：' + ' · '.join(link(sha) for sha in section['evidence']), '']
        if section['rows']:
            lines += ['| ' + ' | '.join([*(plain(c) for c in section['columns']), '依据 / 验证范围', '证据']) + ' |',
                      '| ' + ' | '.join(['---'] * (len(section['columns']) + 2)) + ' |']
            for row in section['rows']:
                proof = ' · '.join(link(sha) for sha in row['evidence'])
                if not proof:
                    proof = '见栏目证据' if section['evidence'] else '未提供'
                lines += ['| ' + ' | '.join([*(plain(c) for c in row['cells']),
                           QUALIFICATIONS[row['qualification']], proof]) + ' |']
        if section['notes']:
            lines += [''] + ['- ' + plain(note) for note in section['notes']]
    return lines
