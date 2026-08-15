from __future__ import annotations
from typing import Any

SECTIONS = ['Home', 'Discover', 'Profile', 'Matches', 'Decision Studio', 'Copilot', 'Trust & Data']

SECTION_META = {
    'Home': ('Start with clarity', 'Understand the journey and choose where to begin.'),
    'Discover': ('Explore possibilities', 'Move from interests to fields and interdisciplinary directions.'),
    'Profile': ('Build your decision profile', 'Add the information that makes recommendations more useful.'),
    'Matches': ('Understand your options', 'See recommendations through different decision lenses.'),
    'Decision Studio': ('Compare and plan', 'Turn a shortlist into trade-offs, tasks and scenarios.'),
    'Copilot': ('Think with VeriPath', 'Ask grounded questions about your options and next steps.'),
    'Trust & Data': ('See the evidence', 'Understand data quality, limitations and methodology.'),
}

def profile_completeness(profile: dict[str, Any]) -> float:
    fields = [
        bool(profile.get('interests')), bool(profile.get('career_goal')), bool(profile.get('background')),
        bool(profile.get('preferred_domains')), bool(profile.get('preferred_countries')),
        float(profile.get('budget', 0) or 0) > 0, bool(profile.get('language')),
    ]
    return round(sum(fields) / len(fields), 3)

def next_action(profile: dict[str, Any], results, shortlist: list[str]) -> tuple[str, str, str]:
    if not profile.get('interests') and not profile.get('career_goal'):
        return ('Discover', 'Start by telling VeriPath what interests you.', 'You do not need to know the exact degree yet.')
    if not profile.get('preferred_domains'):
        return ('Discover', 'Choose a few study families to explore.', 'This makes the academic universe easier to navigate.')
    if profile_completeness(profile) < 0.57:
        return ('Profile', 'Complete the parts of your profile that affect trade-offs.', 'Academic background, budget, location and language matter.')
    if results is None or len(results) == 0:
        return ('Matches', 'Generate your first recommendation set.', 'Then inspect why each option appears and what remains unknown.')
    if len(shortlist) < 2:
        return ('Matches', 'Shortlist two or three serious options.', 'A shortlist gives you something concrete to compare.')
    return ('Decision Studio', 'Compare your shortlist and turn uncertainty into tasks.', 'This is where browsing becomes a decision process.')

def journey_progress(profile: dict[str, Any], results, shortlist: list[str]) -> float:
    milestones = [
        bool(profile.get('interests') or profile.get('career_goal')), bool(profile.get('preferred_domains')),
        profile_completeness(profile) >= 0.57, results is not None and len(results) > 0, len(shortlist) >= 2,
    ]
    return round(sum(milestones) / len(milestones), 3)
