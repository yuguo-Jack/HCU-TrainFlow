"""Canonical Skill IDs shared by runtime dispatch and local installation.

Internal task modes/stage codes are stable protocol values, not folder names.
"""
STAGE_SKILLS = {
    'adapt': 'hcu-train-environment-check-and-adapt',
    'optimize': 'hcu-train-analyze-and-optimize',
    'fault-tolerance': 'hcu-train-scale-and-stability',
}

WORKFLOW_SKILLS = (
    'hcu-trainflow',
    *STAGE_SKILLS.values(),
    'hcu-engine-wiki-search',
    'hcu-engine-wiki-skill-update',
)
