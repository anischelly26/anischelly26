from __future__ import annotations

import json
import os
from typing import Any

from src.coaching_knowledge import get_plan
from src.movement_database import MovementDatabase
from src.rules_database import RulesDatabase
from src.strategy_knowledge import build_short_strategy_summary, build_strategy_analysis


class PadelCoachAgent:
    """Strategy-first padel coach grounded in video analysis, movement references and official rules."""

    def __init__(
        self,
        database: MovementDatabase | None = None,
        rules_database: RulesDatabase | None = None,
    ) -> None:
        self.database = database or MovementDatabase()
        self.rules_database = rules_database or RulesDatabase()

    def welcome(self, report: dict | None = None) -> str:
        if not report:
            return (
                "Hi — I’m your PadelVision coach. Upload a stroke video and I’ll turn the hidden movement analysis "
                "into a practical strategy: what pattern is limiting the shot, what to change in a match, "
                "how to rebuild the movement, and how to train it. You can also ask me about the official rules of padel."
            )
        return build_short_strategy_summary(report)

    def strategy_analysis(self, report: dict) -> str:
        return build_strategy_analysis(report)

    def coaching_plan(self, report: dict) -> str:
        return self.strategy_analysis(report)

    def answer(
        self,
        question: str,
        report: dict | None = None,
        history: list[dict] | None = None,
        api_key: str | None = None,
        model: str | None = None,
    ) -> str:
        is_rule_question = self.rules_database.is_rule_question(question)
        stroke = report.get("stroke") if report else self._infer_stroke(question)
        movement_refs = self.database.search_text(question, stroke=stroke, limit=12)
        rule_sections = self.rules_database.search(question, limit=5) if is_rule_question else []
        context = self._build_context(question, report, movement_refs, rule_sections)

        key = (api_key or os.getenv("OPENAI_API_KEY") or "").strip()
        if key:
            try:
                return self._answer_with_openai(
                    question=question,
                    context=context,
                    history=history or [],
                    api_key=key,
                    model=(model or os.getenv("OPENAI_MODEL") or "gpt-4.1-mini").strip(),
                )
            except Exception as exc:
                local = self._answer_locally(question, report, is_rule_question, rule_sections)
                return f"{local}\n\n*Advanced AI mode was unavailable, so I used the local strategy engine. ({type(exc).__name__})*"

        return self._answer_locally(question, report, is_rule_question, rule_sections)

    def _build_context(self, question: str, report: dict | None, refs, rule_sections) -> str:
        payload: dict[str, Any] = {
            "question": question,
            "movement_reference_rows_INTERNAL_ONLY": self.database.serialize(refs),
            "official_rules_sections": self.rules_database.build_context(rule_sections),
            "rules_source": self.rules_database.version_label,
        }
        if report:
            payload["video_analysis_INTERNAL_ONLY"] = {
                "stroke": report.get("stroke"),
                "handedness": report.get("handedness"),
                "detection_rate": report.get("detection_rate"),
                "binary_analysis": report.get("binary_analysis"),
                "metrics": report.get("metrics"),
                "phase_method": report.get("phase_method"),
                "database_ground_truth_status": report.get("database_ground_truth_status"),
            }
            payload["player_facing_strategy_analysis"] = build_strategy_analysis(report)
        return json.dumps(payload, indent=2, ensure_ascii=False)

    @staticmethod
    def _answer_with_openai(question, context, history, api_key, model) -> str:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        recent_history = history[-10:]
        input_payload = (
            "Conversation history:\n" + json.dumps(recent_history, ensure_ascii=False)
            + "\n\nGrounded PadelVision context:\n" + context
            + "\n\nUser question:\n" + question
        )
        response = client.responses.create(
            model=model,
            instructions=(
                "You are PadelVision Coach, a strategy-first expert padel coach. "
                "The user NEVER wants raw body points, landmark IDs, coordinates, binary vectors, angle values, "
                "movement-match percentages, database rows, or point-by-point placement explanations. "
                "Those data are internal diagnostic signals only. "
                "After a video analysis, explain the player's OVERALL MOVEMENT PATTERN and convert it into strategy. "
                "Your answer should normally cover: (1) what the overall movement pattern is causing, "
                "(2) the tactical consequence in a padel rally, (3) the safest match strategy to use now, "
                "(4) the sequence for rebuilding the movement, (5) one short cue, and (6) one practical drill. "
                "Do not say 'your right wrist should move X' or expose a body-point diagnosis unless the user explicitly asks for biomechanics. "
                "Even then, explain it in normal coaching language rather than coordinates or binary data. "
                "Do not invent video-specific errors that are absent from the supplied analysis. "
                "For official rule questions, answer only from the supplied FIP rules context and cite the relevant rule title/number when available. "
                "Keep rules and technique advice separate. The movement reference database is prototype coaching data, not a universal scientific ground truth."
            ),
            input=input_payload,
        )
        return response.output_text.strip()

    def _answer_locally(self, question: str, report: dict | None, is_rule_question: bool, rule_sections) -> str:
        q = question.lower().strip()
        if is_rule_question:
            return self.rules_database.local_answer(question, rule_sections)

        stroke = report.get("stroke") if report else self._infer_stroke(question)
        if not stroke:
            stroke = "Forehand Groundstroke"

        video_strategy_terms = (
            "analysis", "analyse", "analyze", "video", "strategy", "strategie",
            "what should i do", "what should i fix", "improve", "wrong",
            "match plan", "tactical", "tactic", "what did you see",
        )
        if report and any(term in q for term in video_strategy_terms):
            return self.strategy_analysis(report)

        if any(phrase in q for phrase in ["how to", "how do i", "steps", "teach me", "right technique", "correct technique"]):
            plan = get_plan(stroke)
            steps = "\n".join(f"{i}. {step}" for i, step in enumerate(plan.steps, start=1))
            return f"### {plan.title}\n\n{steps}\n\n**Simple cue:** {plan.key_cue}\n\n**Drill:** {plan.drill}"

        if report:
            return self.strategy_analysis(report)

        plan = get_plan(stroke)
        return (
            f"For **{stroke}**, the core idea is: **{plan.key_cue}**\n\n"
            "Upload a video and I’ll give you a strategic analysis of the complete movement, or ask me to teach the stroke step by step."
        )

    def _infer_stroke(self, question: str) -> str | None:
        q = question.lower()
        aliases = {
            "forehand volley": "Forehand Volley",
            "backhand volley": "Backhand Volley",
            "forehand lob": "Forehand Lob",
            "backhand lob": "Backhand Lob",
            "forehand": "Forehand Groundstroke",
            "backhand": "Backhand Groundstroke",
            "serve": "Serve",
            "service": "Serve",
            "bandeja": "Bandeja",
            "vibora": "Vibora",
            "víbora": "Vibora",
            "flat smash": "Flat Smash",
            "x3": "Kick Smash / X3",
            "kick smash": "Kick Smash / X3",
        }
        for token, stroke in aliases.items():
            if token in q:
                return stroke
        return None
