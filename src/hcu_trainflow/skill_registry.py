"""Canonical Skill IDs shared by runtime dispatch and local installation.

Internal task modes/stage codes are stable protocol values, not folder names.
"""
STAGE_SKILLS = {
    'adapt': 'hcu-train-check-and-adapt',
    'optimize': 'hcu-train-analyze-and-optimize',
    'fault-tolerance': 'hcu-train-scale-and-stability',
}

WIKI_SEARCH_SKILL = 'hcu-trainflow-wiki-search'
WIKI_UPDATE_SKILL = 'hcu-trainflow-wiki-skill-update'

WORKFLOW_SKILLS = (
    'hcu-trainflow',
    *STAGE_SKILLS.values(),
    WIKI_SEARCH_SKILL,
    WIKI_UPDATE_SKILL,
)
