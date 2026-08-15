from __future__ import annotations


def build_feedback(
    metrics: dict,
    detection_rate: float,
    stroke: str,
    handedness: str,
) -> tuple[list[dict], int]:
    """
    Build transparent prototype feedback from measured pose features.

    These are screening heuristics, not validated biomechanical rules.
    They are deliberately simple so the system does not pretend to know
    more than it actually measured.
    """
    findings: list[dict] = []
    penalties = 0

    if detection_rate < 0.65:
        findings.append({
            "severity": "high",
            "title": "Recording quality needs improvement",
            "message": "The system lost your body in too many frames, so the movement measurements are not reliable enough for strong technique conclusions.",
            "drill": "Record from farther away, keep your full body in frame, use good lighting, and avoid another player crossing in front of you.",
        })
        penalties += 30
    else:
        findings.append({
            "severity": "good",
            "title": "Body tracking quality is usable",
            "message": f"Your pose was detected in {detection_rate:.0%} of analysed frames.",
            "drill": "Keep using a stable camera angle for consistent comparisons.",
        })

    elbow_range = metrics["elbow_range_deg"]
    if elbow_range < 28:
        findings.append({
            "severity": "medium",
            "title": "Playing arm looks relatively rigid",
            "message": f"The measured {handedness} elbow changed by only about {elbow_range:.1f}°. This can indicate a limited arm movement pattern, although racket tracking is needed before making a definitive padel diagnosis.",
            "drill": "Practise slow shadow swings while keeping the shoulder, elbow and hand moving as one coordinated chain rather than locking the arm.",
        })
        penalties += 15
    else:
        findings.append({
            "severity": "good",
            "title": "The playing arm shows clear movement",
            "message": f"The elbow moved through a measurable range of about {elbow_range:.1f}°.",
            "drill": "Next versions will check whether this movement happens at the correct moment relative to the racket and ball.",
        })

    knee_angle = metrics["knee_angle_mean_deg"]
    if knee_angle > 164:
        findings.append({
            "severity": "medium",
            "title": "Athletic base may be too upright",
            "message": f"Your mean measured knee angle was about {knee_angle:.1f}°. Across this clip, the legs appear relatively straight.",
            "drill": "Use a slightly lower ready position: soften the knees, keep your weight active on the front of the feet, and recover to that position after every shot.",
        })
        penalties += 12
    else:
        findings.append({
            "severity": "good",
            "title": "You show some knee flexion",
            "message": f"Your mean measured knee angle was about {knee_angle:.1f}°, suggesting a more active lower-body position.",
            "drill": "Maintain that athletic base before and after contact.",
        })

    stance_ratio = metrics["stance_width_ratio_mean"]
    if 0 < stance_ratio < 0.85:
        findings.append({
            "severity": "medium",
            "title": "Stance may be narrow",
            "message": "Your ankle-to-shoulder width ratio was relatively small in the analysed frames.",
            "drill": "Start in a balanced ready position with enough base width to move in either direction without crossing your feet immediately.",
        })
        penalties += 10
    elif stance_ratio > 2.7:
        findings.append({
            "severity": "medium",
            "title": "Stance may be excessively wide",
            "message": "Your measured stance was very wide relative to shoulder width in this clip.",
            "drill": "Avoid getting stuck in a static wide base. Keep the feet active and recover to a balanced position after the shot.",
        })
        penalties += 8
    elif stance_ratio > 0:
        findings.append({
            "severity": "good",
            "title": "Stance width looks broadly balanced",
            "message": f"The average stance-width ratio was {stance_ratio:.2f} relative to shoulder width.",
            "drill": "The next step is to analyse foot timing, not only stance width.",
        })

    score = max(20, min(95, 90 - penalties))

    if stroke == "serve":
        findings.append({
            "severity": "medium",
            "title": "Serve-specific contact analysis is not active yet",
            "message": "v0.1 can measure body pose, but it cannot yet verify ball bounce, racket path, contact height or legal serve mechanics.",
            "drill": "For the next model, record the full body, racket and ball from a side-diagonal angle.",
        })

    return findings, score
