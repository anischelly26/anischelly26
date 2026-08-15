from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RuleSection:
    title: str
    content: str
    source: str = "FIP Rules of Padel — application 01.01.2026"


class RulesDatabase:
    """Offline retrieval layer for the official FIP padel rules bundled with the full release."""

    RULE_QUERY_TERMS = {
        "rule", "rules", "legal", "illegal", "allowed", "fault", "serve", "service",
        "score", "scoring", "deuce", "golden point", "star point", "tie-break", "let",
        "net", "bounce", "wall", "glass", "fence", "out of court", "point lost",
        "double hit", "touch net", "racket", "ball", "court", "coach", "receiver",
    }

    def __init__(self, text_path: str | Path | None = None) -> None:
        root = Path(__file__).resolve().parents[1]
        self.text_path = Path(text_path or root / "data" / "rules" / "fip_rules_2026.txt")
        self.raw_text = self.text_path.read_text(encoding="utf-8", errors="ignore") if self.text_path.exists() else ""
        self.sections = self._parse_sections(self.raw_text) if self.raw_text else []

    @property
    def version_label(self) -> str:
        return "Official FIP Rules of Padel — application 01.01.2026"

    def is_rule_question(self, question: str) -> bool:
        q = question.lower()
        technique = ("how to hit", "improve my", "technique", "movement", "drill", "teach me")
        if any(x in q for x in technique):
            return False
        return any(term in q for term in self.RULE_QUERY_TERMS)

    def search(self, query: str, limit: int = 5) -> list[RuleSection]:
        terms = {t for t in re.findall(r"[a-z0-9-]+", query.lower()) if len(t) > 2}
        scored = []
        for section in self.sections:
            hay = f"{section.title} {section.content}".lower()
            score = sum(8 if t in section.title.lower() else hay.count(t) for t in terms)
            if score:
                scored.append((score, section))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [s for _, s in scored[:limit]]

    def build_context(self, sections, max_chars: int = 9000) -> list[dict]:
        out, used = [], 0
        for section in sections:
            if used >= max_chars:
                break
            text = section.content[: max_chars - used]
            out.append({"title": section.title, "content": text, "source": section.source})
            used += len(text)
        return out

    def local_answer(self, question: str, sections=None) -> str:
        q = question.lower()
        if "serve" in q or "service" in q:
            return (
                "For a legal padel serve, bounce the ball in your service area, keep at least one foot behind the service line, "
                "strike at or below waist level with at least one foot on the ground, and send the ball diagonally into the correct service box. "
                "Use the bundled FIP rulebook for the exact fault/let wording."
            )
        if "touch" in q and "net" in q:
            return "While the ball is in play, touching the net or the opponent's court with your body, racket or equipment loses the point."
        if "double" in q and "hit" in q:
            return "A deliberate double hit loses the point; the official rules contain the exception for one continuous movement."
        sections = sections or self.search(question)
        if sections:
            return "\n\n".join(f"**{s.title}**\n{s.content[:700]}" for s in sections[:3])
        return "No matching section is available in this lightweight source mirror. See the full saved release for the complete bundled FIP rules text."

    @staticmethod
    def _parse_sections(text: str) -> list[RuleSection]:
        pattern = re.compile(r"(?m)^\s*(RULE\s+\d+\.\s+[^\n]+)\s*$")
        matches = list(pattern.finditer(text.replace("\r", "")))
        sections = []
        for i, match in enumerate(matches):
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            content = re.sub(r"\s+", " ", text[match.end():end]).strip()
            sections.append(RuleSection(match.group(1).strip(), content))
        return sections
