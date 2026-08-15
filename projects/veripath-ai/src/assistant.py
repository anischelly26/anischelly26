from __future__ import annotations
from typing import Any


def _rows(results, limit=6):
    if results is None or len(results) == 0:
        return []
    return [row.to_dict() for _, row in results.head(limit).iterrows()]


def respond(question: str, profile: dict[str, Any], results, shortlist: list[str], **_) -> dict[str, Any]:
    """Grounded deterministic copilot: answer only from loaded profile/results and keep uncertainty visible."""
    q = question.strip().lower()
    tops = _rows(results)
    if not q:
        return {'text': 'Ask about your recommendations, affordability, unknown requirements, shortlist or next step.'}

    if 'profile' in q:
        return {'text': f"Saved interests: {', '.join(profile.get('interests', [])) or 'none yet'}. Preferred domains: {', '.join(profile.get('preferred_domains', [])) or 'not set'}. Budget: €{float(profile.get('budget', 0) or 0):,.0f}."}

    if any(x in q for x in ['cheaper', 'budget', 'affordable']):
        if not tops:
            return {'text': 'Generate recommendations first so I can compare known tuition data.'}
        rows = sorted(tops, key=lambda r: float(r.get('tuition_eur', 10**9) or 10**9))[:3]
        return {'text': 'Lower-cost options in the current result set: ' + '; '.join(f"{r.get('title')} ({'tuition unknown' if not r.get('tuition_eur') else '€'+format(float(r.get('tuition_eur')), ',.0f')})" for r in rows) + '. Verify official fees before making a decision.'}

    if any(x in q for x in ['missing', 'unknown', 'verify']):
        if not tops:
            return {'text': 'I need recommendation results before I can identify programme-specific unknowns.'}
        unknowns = tops[0].get('unknowns', []) or ['No explicit unknowns recorded']
        return {'text': f"For {tops[0].get('title')}, still verify: {', '.join(map(str, unknowns))}. VeriPath does not fill missing admissions facts with guesses."}

    if any(x in q for x in ['why', 'recommended']):
        if not tops:
            return {'text': 'Generate recommendations first.'}
        row = tops[0]
        why = ' '.join(row.get('why', [])) or 'The current weighted compatibility components produced the ranking.'
        caution = ' '.join(row.get('why_not', [])) or 'No major known conflict is recorded.'
        return {'text': f"{row.get('title')} appears because: {why} Caution: {caution} Compatibility is decision support, not admission probability."}

    if any(x in q for x in ['compare', 'versus', ' vs ']):
        if len(tops) < 2:
            return {'text': 'I need at least two recommendation results to compare.'}
        a, b = tops[:2]
        return {'text': f"{a.get('title')} scores {a.get('compatibility_score',0):.1f}/100 compatibility versus {b.get('title')} at {b.get('compatibility_score',0):.1f}/100. Compare affordability, data quality, known checks and unknowns separately rather than treating either score as an admission chance."}

    if any(x in q for x in ['next', 'what should i do']):
        if results is None or len(results) == 0:
            return {'text': 'Complete the profile, then generate a recommendation set.'}
        if len(shortlist) < 2:
            return {'text': 'Open the strongest options, inspect unknowns, then shortlist at least two serious choices.'}
        return {'text': 'Compare the shortlist, verify official requirements and turn every unknown into a concrete application task.'}

    if tops:
        row = tops[0]
        return {'text': f"Your current leading result is {row.get('title')} at {row.get('institution')} with compatibility {row.get('compatibility_score',0):.1f}/100. Ask why it ranks there, what is unknown, or for cheaper alternatives."}
    return {'text': 'I only answer from information loaded inside VeriPath. If the evidence is missing, I will tell you instead of inventing it.'}


def answer(question: str, profile: dict[str, Any], results, shortlist: list[str], **kwargs) -> str:
    return respond(question, profile, results, shortlist, **kwargs)['text']
