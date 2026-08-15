from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


STROKE_ALIASES = {
    "Forehand": "Forehand Groundstroke",
    "Backhand": "Backhand Groundstroke",
    "Serve": "Serve",
    "Forehand Volley": "Forehand Volley",
    "Backhand Volley": "Backhand Volley",
    "Bandeja": "Bandeja",
    "Vibora": "Vibora",
    "Flat Smash": "Flat Smash",
    "Kick Smash / X3": "Kick Smash / X3",
    "Forehand Lob": "Forehand Lob",
    "Backhand Lob": "Backhand Lob",
}

PHASES = [
    "Ready_Setup",
    "Preparation",
    "Loading_Positioning",
    "Acceleration",
    "Contact",
    "Follow_Through",
    "Recovery",
]

LANDMARK_TO_SEGMENT = {
    0: "Head", 1: "Head", 2: "Head", 3: "Head", 4: "Head", 5: "Head",
    6: "Head", 7: "Head", 8: "Head", 9: "Head", 10: "Head",
    11: "Left_Shoulder", 12: "Right_Shoulder",
    13: "Left_Elbow", 14: "Right_Elbow",
    15: "Left_Wrist", 16: "Right_Wrist", 17: "Left_Wrist", 18: "Right_Wrist",
    19: "Left_Wrist", 20: "Right_Wrist", 21: "Left_Wrist", 22: "Right_Wrist",
    23: "Pelvis", 24: "Pelvis",
    25: "Left_Knee", 26: "Right_Knee",
    27: "Left_Foot", 28: "Right_Foot", 29: "Left_Foot", 30: "Right_Foot",
    31: "Left_Foot", 32: "Right_Foot",
}


@dataclass(frozen=True)
class MovementReference:
    lookup_key: str
    stroke: str
    phase: str
    landmark_id: int
    landmark_name: str
    body_segment: str
    expected_direction: str
    comparable: bool
    expected_bits: tuple[int, int, int, int, int, int] | None
    expected_binary_vector: str
    ground_truth_status: str


class MovementDatabase:
    """Read-only retrieval layer over the binary movement reference database."""

    def __init__(self, csv_path: str | Path | None = None) -> None:
        project_root = Path(__file__).resolve().parents[1]
        self.csv_path = Path(csv_path or project_root / "data" / "binary_point_reference.csv")
        if not self.csv_path.exists():
            raise FileNotFoundError(f"Movement database not found: {self.csv_path}")

        self.references: list[MovementReference] = []
        self.by_key: dict[str, MovementReference] = {}
        self._load()

    def _load(self) -> None:
        with self.csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                comparable = str(row.get("Comparable", "0")).strip() in {"1", "true", "True"}
                bits = None
                if comparable:
                    try:
                        bits = tuple(int(row[name]) for name in (
                            "Exp_X_Pos", "Exp_X_Neg", "Exp_Y_Pos", "Exp_Y_Neg", "Exp_Z_Pos", "Exp_Z_Neg"
                        ))
                    except (TypeError, ValueError, KeyError):
                        comparable = False
                        bits = None

                ref = MovementReference(
                    lookup_key=row["Lookup_Key"],
                    stroke=row["Stroke"],
                    phase=row["Phase"],
                    landmark_id=int(row["Landmark_ID"]),
                    landmark_name=row["Landmark_Name"],
                    body_segment=row["Body_Segment"],
                    expected_direction=row["Expected_Direction"],
                    comparable=comparable,
                    expected_bits=bits,
                    expected_binary_vector=row["Expected_Binary_Vector"],
                    ground_truth_status=row.get("Ground_Truth_Status", "Prototype"),
                )
                self.references.append(ref)
                self.by_key[ref.lookup_key] = ref

    @property
    def strokes(self) -> list[str]:
        return sorted({ref.stroke for ref in self.references})

    def normalize_stroke(self, stroke: str) -> str:
        clean = stroke.strip()
        return STROKE_ALIASES.get(clean, STROKE_ALIASES.get(clean.title(), clean))

    def get_reference(self, stroke: str, phase: str, landmark_id: int) -> MovementReference | None:
        stroke_name = self.normalize_stroke(stroke)
        return self.by_key.get(f"{stroke_name}|{phase}|{landmark_id}")

    def get_phase_references(self, stroke: str, phase: str) -> list[MovementReference]:
        stroke_name = self.normalize_stroke(stroke)
        return [r for r in self.references if r.stroke == stroke_name and r.phase == phase]

    def query(
        self,
        *,
        stroke: str | None = None,
        phase: str | None = None,
        body_segment: str | None = None,
        landmark_name: str | None = None,
        comparable_only: bool = False,
        limit: int = 20,
    ) -> list[MovementReference]:
        stroke_name = self.normalize_stroke(stroke) if stroke else None
        results: list[MovementReference] = []
        for ref in self.references:
            if stroke_name and ref.stroke != stroke_name:
                continue
            if phase and ref.phase != phase:
                continue
            if body_segment and body_segment.lower() not in ref.body_segment.lower():
                continue
            if landmark_name and landmark_name.lower() not in ref.landmark_name.lower():
                continue
            if comparable_only and not ref.comparable:
                continue
            results.append(ref)
            if len(results) >= limit:
                break
        return results

    def search_text(self, question: str, stroke: str | None = None, limit: int = 12) -> list[MovementReference]:
        q = question.lower()
        phase = next((p for p in PHASES if p.lower().replace("_", " ") in q or p.lower() in q), None)

        keyword_segments = {
            "wrist": "Wrist", "hand": "Wrist", "racket": "Wrist",
            "elbow": "Elbow", "arm": "Elbow",
            "shoulder": "Shoulder", "chest": "Shoulder",
            "hip": "Pelvis", "pelvis": "Pelvis", "rotation": "Pelvis",
            "knee": "Knee", "leg": "Knee",
            "foot": "Foot", "feet": "Foot", "stance": "Foot",
            "head": "Head", "eyes": "Head", "look": "Head",
        }
        segment = next((value for key, value in keyword_segments.items() if key in q), None)

        candidates = self.references
        if stroke:
            stroke_name = self.normalize_stroke(stroke)
            candidates = [r for r in candidates if r.stroke == stroke_name]
        if phase:
            candidates = [r for r in candidates if r.phase == phase]
        if segment:
            filtered = [r for r in candidates if segment.lower() in r.body_segment.lower()]
            if filtered:
                candidates = filtered

        if "right" in q:
            right_side = [r for r in candidates if "right" in r.body_segment.lower() or "right" in r.landmark_name.lower()]
            if right_side:
                candidates = right_side
        elif "left" in q:
            left_side = [r for r in candidates if "left" in r.body_segment.lower() or "left" in r.landmark_name.lower()]
            if left_side:
                candidates = left_side

        candidates = sorted(candidates, key=lambda r: (not r.comparable, r.phase, r.landmark_id))
        return candidates[:limit]

    @staticmethod
    def serialize(refs: Iterable[MovementReference]) -> list[dict]:
        return [
            {
                "stroke": r.stroke,
                "phase": r.phase,
                "landmark_id": r.landmark_id,
                "landmark_name": r.landmark_name,
                "body_segment": r.body_segment,
                "expected_direction": r.expected_direction,
                "expected_binary_vector": r.expected_binary_vector,
                "comparable": r.comparable,
                "ground_truth_status": r.ground_truth_status,
            }
            for r in refs
        ]
