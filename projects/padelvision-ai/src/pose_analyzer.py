from __future__ import annotations

import math
import urllib.request
from collections import defaultdict
from pathlib import Path
from typing import Iterable

import cv2
import mediapipe as mp
import numpy as np

from src.feedback import build_feedback
from src.movement_database import LANDMARK_TO_SEGMENT, PHASES, MovementDatabase

MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "pose_landmarker/pose_landmarker_full/float16/latest/pose_landmarker_full.task"
)

LEFT_SHOULDER, RIGHT_SHOULDER = 11, 12
LEFT_ELBOW, RIGHT_ELBOW = 13, 14
LEFT_WRIST, RIGHT_WRIST = 15, 16
LEFT_HIP, RIGHT_HIP = 23, 24
LEFT_KNEE, RIGHT_KNEE = 25, 26
LEFT_ANKLE, RIGHT_ANKLE = 27, 28

POSE_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 7), (0, 4), (4, 5), (5, 6), (6, 8),
    (9, 10), (11, 12), (11, 13), (13, 15), (12, 14), (14, 16),
    (15, 17), (15, 19), (15, 21), (16, 18), (16, 20), (16, 22),
    (11, 23), (12, 24), (23, 24), (23, 25), (25, 27), (27, 29),
    (29, 31), (27, 31), (24, 26), (26, 28), (28, 30), (30, 32), (28, 32),
]


def calculate_angle(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> float:
    ba = a - b
    bc = c - b
    denominator = np.linalg.norm(ba) * np.linalg.norm(bc)
    if denominator == 0:
        return float("nan")
    cosine = float(np.dot(ba, bc) / denominator)
    return math.degrees(math.acos(float(np.clip(cosine, -1.0, 1.0))))


def safe_mean(values: Iterable[float], default: float = 0.0) -> float:
    clean = [v for v in values if not math.isnan(v)]
    return float(np.mean(clean)) if clean else default


def movement_bits(delta: np.ndarray, threshold: float) -> tuple[int, int, int, int, int, int]:
    dx, dy, dz = (float(delta[0]), float(delta[1]), float(delta[2]))
    return (
        int(dx > threshold), int(dx < -threshold),
        int(dy > threshold), int(dy < -threshold),
        int(dz > threshold), int(dz < -threshold),
    )


def direction_match(observed: tuple[int, ...], expected: tuple[int, ...]) -> float:
    """Direction-aware binary similarity; avoids rewarding shared inactive zero bits."""
    observed_active = {i for i, value in enumerate(observed) if value}
    expected_active = {i for i, value in enumerate(expected) if value}
    if not expected_active:
        return 1.0 if not observed_active else 0.0
    union = observed_active | expected_active
    return len(observed_active & expected_active) / len(union) if union else 1.0


class PoseAnalyzer:
    def __init__(
        self,
        model_path: str | Path | None = None,
        database: MovementDatabase | None = None,
    ) -> None:
        project_root = Path(__file__).resolve().parents[1]
        self.model_path = Path(model_path or project_root / "models" / "pose_landmarker_full.task")
        self.database = database or MovementDatabase()
        self._ensure_model()

    def _ensure_model(self) -> None:
        if self.model_path.exists():
            return
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = self.model_path.with_suffix(".download")
        try:
            urllib.request.urlretrieve(MODEL_URL, temp_path)
            temp_path.replace(self.model_path)
        except Exception as exc:
            temp_path.unlink(missing_ok=True)
            raise RuntimeError(
                "Could not download the MediaPipe pose model. Check your internet connection and run again."
            ) from exc

    @staticmethod
    def _phase_for_frame(frame_index: int, total_frames: int) -> str:
        if total_frames <= 1:
            return PHASES[0]
        ratio = min(max(frame_index / max(total_frames - 1, 1), 0.0), 0.999999)
        return PHASES[min(int(ratio * len(PHASES)), len(PHASES) - 1)]

    @staticmethod
    def _player_coordinates(landmarks, camera_view: str) -> np.ndarray:
        xyz = np.array([[lm.x, lm.y, lm.z] for lm in landmarks], dtype=np.float32)
        shoulder_width = np.linalg.norm(xyz[RIGHT_SHOULDER] - xyz[LEFT_SHOULDER])
        scale = max(float(shoulder_width), 1e-4)
        xyz = xyz / scale
        camera_sign = -1.0 if camera_view == "Front of player" else 1.0
        player_x = xyz[:, 0] * camera_sign
        player_y = xyz[:, 2] * camera_sign
        player_z = -xyz[:, 1]
        return np.column_stack([player_x, player_y, player_z])

    def process_video(
        self,
        input_path: Path,
        output_path: Path,
        handedness: str,
        stroke: str,
        camera_view: str = "Behind player",
        motion_threshold: float = 0.04,
    ) -> dict:
        capture = cv2.VideoCapture(str(input_path))
        if not capture.isOpened():
            raise ValueError("OpenCV could not open the uploaded video.")

        fps = capture.get(cv2.CAP_PROP_FPS) or 30.0
        width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        if width <= 0 or height <= 0:
            capture.release()
            raise ValueError("The uploaded video has invalid dimensions.")

        writer = cv2.VideoWriter(str(output_path), cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))

        options = mp.tasks.vision.PoseLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=str(self.model_path)),
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
            num_poses=1,
            min_pose_detection_confidence=0.5,
            min_pose_presence_confidence=0.5,
            min_tracking_confidence=0.5,
        )

        elbow_angles: list[float] = []
        knee_angles: list[float] = []
        stance_ratios: list[float] = []
        binary_records: list[dict] = []
        detected_frames = 0
        processed_frames = 0
        previous_player_points: np.ndarray | None = None
        stroke_name = self.database.normalize_stroke(stroke)

        with mp.tasks.vision.PoseLandmarker.create_from_options(options) as landmarker:
            frame_index = 0
            while True:
                ok, frame = capture.read()
                if not ok:
                    break
                processed_frames += 1
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
                timestamp_ms = int((frame_index / fps) * 1000)
                result = landmarker.detect_for_video(mp_image, timestamp_ms)

                elbow_angle = float("nan")
                knee_angle = float("nan")
                phase = self._phase_for_frame(frame_index, total_frames or processed_frames)
                frame_match_scores: list[float] = []

                if result.pose_landmarks:
                    detected_frames += 1
                    image_landmarks = result.pose_landmarks[0]
                    world_landmarks = result.pose_world_landmarks[0] if getattr(result, "pose_world_landmarks", None) else image_landmarks
                    image_points = np.array([[lm.x * width, lm.y * height] for lm in image_landmarks], dtype=np.float32)
                    player_points = self._player_coordinates(world_landmarks, camera_view)

                    shoulder_i, elbow_i, wrist_i = (
                        (LEFT_SHOULDER, LEFT_ELBOW, LEFT_WRIST)
                        if handedness == "left"
                        else (RIGHT_SHOULDER, RIGHT_ELBOW, RIGHT_WRIST)
                    )
                    elbow_angle = calculate_angle(image_points[shoulder_i], image_points[elbow_i], image_points[wrist_i])
                    left_knee_angle = calculate_angle(image_points[LEFT_HIP], image_points[LEFT_KNEE], image_points[LEFT_ANKLE])
                    right_knee_angle = calculate_angle(image_points[RIGHT_HIP], image_points[RIGHT_KNEE], image_points[RIGHT_ANKLE])
                    knee_angle = min(left_knee_angle, right_knee_angle)

                    shoulder_width_px = np.linalg.norm(image_points[LEFT_SHOULDER] - image_points[RIGHT_SHOULDER])
                    ankle_width_px = np.linalg.norm(image_points[LEFT_ANKLE] - image_points[RIGHT_ANKLE])
                    if shoulder_width_px > 1:
                        stance_ratios.append(float(ankle_width_px / shoulder_width_px))

                    elbow_angles.append(elbow_angle)
                    knee_angles.append(knee_angle)

                    if previous_player_points is not None:
                        deltas = player_points - previous_player_points
                        for landmark_id in range(min(33, len(player_points))):
                            ref = self.database.get_reference(stroke_name, phase, landmark_id)
                            observed = movement_bits(deltas[landmark_id], motion_threshold)
                            if ref and ref.comparable and ref.expected_bits is not None:
                                score = direction_match(observed, ref.expected_bits)
                                frame_match_scores.append(score)
                                status = "Correct" if score == 1.0 else ("Partial" if score >= 0.5 else "Incorrect")
                                binary_records.append({
                                    "frame": frame_index,
                                    "timestamp_ms": timestamp_ms,
                                    "phase": phase,
                                    "landmark_id": landmark_id,
                                    "landmark_name": ref.landmark_name,
                                    "body_segment": ref.body_segment,
                                    "observed_bits": "".join(map(str, observed)),
                                    "expected_bits": ref.expected_binary_vector,
                                    "expected_direction": ref.expected_direction,
                                    "match_score": round(score, 3),
                                    "status": status,
                                })
                    previous_player_points = player_points
                    self._draw_pose(frame, image_landmarks, width, height)
                    self._draw_metrics(frame, elbow_angle, knee_angle, handedness, stroke_name, phase, safe_mean(frame_match_scores, default=float("nan")))

                writer.write(frame)
                frame_index += 1

        capture.release()
        writer.release()
        if processed_frames == 0:
            raise ValueError("No frames could be read from the video.")

        detection_rate = detected_frames / processed_frames
        valid_elbows = [v for v in elbow_angles if not math.isnan(v)]
        elbow_min = min(valid_elbows) if valid_elbows else 0.0
        elbow_max = max(valid_elbows) if valid_elbows else 0.0

        metrics = {
            "elbow_angle_mean_deg": round(safe_mean(elbow_angles), 1),
            "elbow_angle_min_deg": round(elbow_min, 1),
            "elbow_angle_max_deg": round(elbow_max, 1),
            "elbow_range_deg": round(elbow_max - elbow_min, 1),
            "knee_angle_mean_deg": round(safe_mean(knee_angles), 1),
            "stance_width_ratio_mean": round(safe_mean(stance_ratios), 2),
            "frames_processed": processed_frames,
            "estimated_total_frames": total_frames,
        }

        binary_analysis = self._summarize_binary(binary_records)
        findings, heuristic_score = build_feedback(metrics=metrics, detection_rate=detection_rate, stroke=stroke_name, handedness=handedness)

        if binary_analysis["comparable_points"]:
            movement_match = binary_analysis["overall_match"] * 100
            prototype_score = round(0.35 * heuristic_score + 0.65 * movement_match)
        else:
            prototype_score = heuristic_score

        return {
            "version": "0.5",
            "stroke": stroke_name,
            "handedness": handedness,
            "camera_view": camera_view,
            "score": int(max(0, min(100, prototype_score))),
            "detection_rate": detection_rate,
            "metrics": metrics,
            "findings": findings,
            "binary_analysis": binary_analysis,
            "phase_method": "Equal-time seven-phase segmentation (prototype)",
            "database_ground_truth_status": "Needs coach validation",
        }

    @staticmethod
    def _summarize_binary(records: list[dict]) -> dict:
        if not records:
            return {
                "overall_match": 0.0,
                "comparable_points": 0,
                "phase_scores": {},
                "worst_segments": [],
                "worst_landmarks": [],
                "sample_mismatches": [],
            }

        overall = float(np.mean([r["match_score"] for r in records]))
        by_phase: dict[str, list[float]] = defaultdict(list)
        by_segment: dict[str, list[float]] = defaultdict(list)
        by_landmark: dict[str, list[float]] = defaultdict(list)
        for record in records:
            by_phase[record["phase"]].append(record["match_score"])
            by_segment[record["body_segment"]].append(record["match_score"])
            by_landmark[record["landmark_name"]].append(record["match_score"])

        phase_scores = {phase: round(float(np.mean(scores)), 3) for phase, scores in by_phase.items()}
        worst_segments = sorted(
            ({"body_segment": k, "match_score": round(float(np.mean(v)), 3)} for k, v in by_segment.items()),
            key=lambda x: x["match_score"],
        )[:6]
        worst_landmarks = sorted(
            ({"landmark_name": k, "match_score": round(float(np.mean(v)), 3)} for k, v in by_landmark.items()),
            key=lambda x: x["match_score"],
        )[:8]
        mismatches = sorted(records, key=lambda r: r["match_score"])[:12]
        return {
            "overall_match": round(overall, 3),
            "comparable_points": len(records),
            "phase_scores": phase_scores,
            "worst_segments": worst_segments,
            "worst_landmarks": worst_landmarks,
            "sample_mismatches": mismatches,
        }

    @staticmethod
    def _draw_pose(frame, landmarks, width: int, height: int) -> None:
        points = [(int(lm.x * width), int(lm.y * height), float(lm.visibility)) for lm in landmarks]
        for start, end in POSE_CONNECTIONS:
            x1, y1, v1 = points[start]
            x2, y2, v2 = points[end]
            if v1 > 0.35 and v2 > 0.35:
                cv2.line(frame, (x1, y1), (x2, y2), (240, 240, 240), 2)
        for x, y, visibility in points:
            if visibility > 0.35:
                cv2.circle(frame, (x, y), 4, (90, 220, 150), -1)

    @staticmethod
    def _draw_metrics(frame, elbow_angle, knee_angle, handedness, stroke, phase, frame_match) -> None:
        lines = [f"{stroke}", f"Movement phase: {phase.replace('_', ' ')}"]
        y = 30
        for line in lines:
            cv2.putText(frame, line, (20, y), cv2.FONT_HERSHEY_SIMPLEX, 0.60, (20, 20, 20), 4, cv2.LINE_AA)
            cv2.putText(frame, line, (20, y), cv2.FONT_HERSHEY_SIMPLEX, 0.60, (255, 255, 255), 1, cv2.LINE_AA)
            y += 26
