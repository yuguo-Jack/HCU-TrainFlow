"""Bounded PR discovery when local candidates are weak or freshness matters."""
import re


STOP = {'how', 'what', 'why', 'does', 'the', 'for', 'and', 'with', 'from', 'into',
        'is', 'are', 'can', 'could', 'should', 'this', 'that', 'to', 'of', 'in', 'on',
        'a', 'an', 'pr', 'mr', 'latest', 'recent', 'new', '怎么', '如何', '是否', '什么'}
FRESH = re.compile(r'最新|最近|新增|新变化|新修复|相关\s*PR|相关\s*MR|'
                   r'\b(?:current|latest|recent|upstream|regression)\b|'
                   r'(?<![A-Za-z0-9_])(?:PR|MR)(?![A-Za-z0-9_])', re.I)


def adequate(results, query):
    from .wiki import terms
    tokens = set(terms(query)) - STOP
    wanted = {word for word in tokens if re.search('[a-zA-Z]', word) or len(word) > 1}
    if not wanted:
        return False
    for row in results:
        if row.get('review_state', '').startswith('local-page-changed'):
            continue
        text = ' '.join(str(row.get(k) or '') for k in ['title', 'excerpt', 'body'])
        found = wanted & set(terms(text))
        if len(found) / len(wanted) >= 0.8:
            return True
    return False


def augment(store, project, result, query, *, mode='auto', engine=None, source=None,
            repos=(), pr_query=None, limit=10):
    from . import official
    from .capture_policy import discovery_project
    if mode == 'off':
        result['online_pr'] = {'status': 'disabled'}
        return result
    lite = discovery_project(project)
    local = result.get('results', [])
    if not lite:
        # Preserve the pre-lite empty-result fallback for old projects.
        if mode == 'always' or not local:
            online = official.annotate_prs(project, official.search_prs(store, pr_query or query,
                official.engine_repos(project, engine, source, repos), limit=limit))
            result['online_pr'] = online
            if online.get('status') == 'partial':
                result['status'] = 'partial'
        return result
    enough = adequate(local, query)
    fresh = bool(FRESH.search(query))
    result['evidence_sufficiency'] = {'local_candidates': len(local), 'lexically_adequate': enough,
                                     'freshness_or_pr_intent': fresh, 'semantic_answer_verified': False}
    if mode != 'always' and enough and not fresh:
        result['online_pr'] = {'status': 'not-requested', 'reason': 'Local candidates still require reading'}
        return result
    explicit = bool(engine or source or repos)
    inferred_engines = []
    selected = official.engine_repos(project, engine, source, repos)
    if not explicit:
        inferred_engines = list(dict.fromkeys(row.get('metadata', {}).get('engine') for row in local
            if row.get('metadata', {}).get('engine') not in {None, '', 'cross-engine', 'unspecified', 'unknown'}))[:3]
        selected = list(dict.fromkeys(repo for name in inferred_engines
                                     for repo in official.engine_repos(project, engine=name)))[:6]
    if not selected:
        result['online_pr'] = {'status': 'scope-required', 'results': [],
            'instruction': 'Select the relevant --engine, --source or --repo; no arbitrary repository subset was searched.'}
        return result
    # Keep raw context intact until the existing public-query guard checks it.
    # Only an explicitly supplied --pr-query replaces it with public terms.
    online = official.annotate_prs(project, official.search_prs(store, pr_query or query, selected, limit=limit))
    online['scope_selection'] = {'explicit': explicit, 'repositories': selected,
                                 'inferred_engines': inferred_engines,
                                 'meaning': 'Only these repositories were searched; other scopes remain available explicitly'}
    result['online_pr'] = online
    if online.get('status') == 'partial':
        result['status'] = 'partial'
    return result
