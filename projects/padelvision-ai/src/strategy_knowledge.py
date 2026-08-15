from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StrokeStrategy:
    objective: str
    safe_pattern: str
    pressure_pattern: str
    avoid: str
    recovery: str


STROKE_STRATEGIES = {
    "Forehand Groundstroke": StrokeStrategy(
        "Build a repeatable neutral ball that protects court position.",
        "Use margin, depth and a balanced contact before trying to accelerate.",
        "Attack more aggressively only when you arrive early and create space.",
        "Do not force pace from a crowded or late position.",
        "Recover immediately according to where your ball sends the opponents.",
    ),
    "Backhand Groundstroke": StrokeStrategy(
        "Use a compact backhand to defend, reset or redirect the rally.",
        "Prioritise early preparation, spacing and a stable target.",
        "Change direction only when the body is organised before contact.",
        "Avoid reaching with the arm when your feet have not created space.",
        "Reset the racket and recover your defensive position quickly.",
    ),
    "Forehand Volley": StrokeStrategy(
        "Use a compact volley to maintain pressure at the net.",
        "Let the feet create the contact and keep the racket action short.",
        "Add angle or pace only from a balanced net position.",
        "Avoid a large backswing that delays recovery.",
        "Return the racket to the ready position immediately.",
    ),
    "Backhand Volley": StrokeStrategy(
        "Control the middle/net space with a short stable volley.",
        "Move behind the ball and use the opponent's pace.",
        "Attack the open space when the contact is comfortably in front.",
        "Avoid reaching or swinging hard from poor spacing.",
        "Recover to an active net position after contact.",
    ),
    "Serve": StrokeStrategy(
        "Start the point with a repeatable legal serve that supports the next shot.",
        "Choose placement and depth before speed.",
        "Use more pace only when the bounce, contact and balance are repeatable.",
        "Do not chase an ace at the cost of consistency or recovery.",
        "Move into the correct position for the return immediately.",
    ),
    "Bandeja": StrokeStrategy(
        "Protect the net after an opponent lob while keeping the rally under control.",
        "Get behind the ball and prioritise depth and placement.",
        "Increase pressure only when you are balanced and can recover forward.",
        "Avoid treating every bandeja like a power smash.",
        "Recover the net as soon as the shot allows it.",
    ),
    "Vibora": StrokeStrategy(
        "Create controlled attacking pressure with spin and direction.",
        "Position first and use a repeatable spinning contact.",
        "Add speed after the contact window and recovery are stable.",
        "Avoid accelerating while falling backward.",
        "Close the net again after the overhead.",
    ),
    "Flat Smash": StrokeStrategy(
        "Attack a suitable lob with power generated from positioning and extension.",
        "Use the smash only when you can contact high and in front.",
        "Accelerate when the tactical situation justifies the risk.",
        "Avoid maximum power from a poor contact window.",
        "Recover according to the rebound and opponent response.",
    ),
    "Kick Smash / X3": StrokeStrategy(
        "Use height, spin and court position to attack the ball out of court.",
        "Choose the X3 only when the lob creates the correct contact window.",
        "Accelerate upward with spin when you are set and balanced.",
        "Avoid the X3 from a poor position because a weak attack exposes the team.",
        "Be ready to follow the ball or defend if it stays in play.",
    ),
    "Forehand Lob": StrokeStrategy(
        "Regain time and push the opponents away from the net.",
        "Prioritise height and depth over a low risky trajectory.",
        "Use an aggressive lob only from a balanced contact.",
        "Avoid a short lob from a rushed position.",
        "Move forward together when the lob succeeds.",
    ),
    "Backhand Lob": StrokeStrategy(
        "Escape pressure and create space to recover or take the net.",
        "Use enough height and depth to force the opponents back.",
        "Attack the available overhead space when your contact is stable.",
        "Avoid flicking only with the wrist from a crowded position.",
        "Advance when the lob is good; otherwise recover defensively.",
    ),
}

PHASE_STRATEGY = {
    "Ready_Setup": (
        "The movement starts reactively instead of proactively.",
        "You arrive late to the next phase and are forced to improvise.",
        "Be ready before you need to swing.",
        "Play controlled rallies where the goal is to split step before every opponent contact.",
    ),
    "Preparation": (
        "The stroke is being organised too late or without a clear early preparation.",
        "The rest of the swing becomes rushed and direction changes become risky.",
        "Prepare early so the hit can stay simple.",
        "Use slow feeds and say 'turn' as soon as you identify the shot, then hit at 60% speed.",
    ),
    "Loading_Positioning": (
        "The main issue is arriving without enough spacing or balance.",
        "Even a good swing becomes unreliable when the body is crowded or still moving.",
        "Position first, hit second.",
        "Use fed balls and exaggerate two or three adjustment steps before each stroke.",
    ),
    "Acceleration": (
        "The stroke loses efficiency when speed is added.",
        "You may create pace but the target becomes less repeatable.",
        "Smooth first, fast second.",
        "Hit 10 balls at 50%, 10 at 65%, then 10 at 80%, increasing only while control stays stable.",
    ),
    "Contact": (
        "The movement pattern breaks down around the hitting moment.",
        "Direction, depth and control become inconsistent, especially under pressure.",
        "Win the contact before trying to win the point.",
        "Use a large target and hit at 60% pace, counting clean balanced contacts rather than winners.",
    ),
    "Follow_Through": (
        "The shot finishes without enough balance or control.",
        "Recovery becomes late and the next ball is harder.",
        "Finish under control, then reset immediately.",
        "Freeze for one second in a balanced finish after each practice shot, then recover.",
    ),
    "Recovery": (
        "The player does not reorganise quickly enough after the shot.",
        "A good first shot can still lose the rally because the next court position is weak.",
        "Your next shot starts when this one ends.",
        "Add a mandatory recovery target after every practice ball.",
    ),
}


def _weakest_phases(report: dict, limit: int = 2) -> list[str]:
    scores = report.get("binary_analysis", {}).get("phase_scores", {})
    return [name for name, _ in sorted(scores.items(), key=lambda x: x[1])[:limit]] if scores else []


def build_strategy_analysis(report: dict) -> str:
    stroke = report.get("stroke", "Forehand Groundstroke")
    if float(report.get("detection_rate", 0)) < 0.65:
        return "### Strategy analysis\n\nThe recording was not tracked consistently enough for a reliable strategy diagnosis. Re-record the full body with a stable camera."

    strategy = STROKE_STRATEGIES.get(stroke, STROKE_STRATEGIES["Forehand Groundstroke"])
    phase = (_weakest_phases(report, 1) or ["Preparation"])[0]
    pattern, consequence, cue, drill = PHASE_STRATEGY.get(phase, PHASE_STRATEGY["Preparation"])
    return (
        f"### Strategy analysis\n\n"
        f"**Overall movement pattern**  \n{pattern} {consequence}\n\n"
        f"**Tactical objective**  \n{strategy.objective}\n\n"
        f"**Match strategy for now**\n1. {strategy.safe_pattern}\n2. {strategy.avoid}\n3. {strategy.recovery}\n\n"
        f"**How to rebuild it**\n1. Reduce speed and organise the weak phase first.\n2. Repeat the movement with a larger target and stable balance.\n3. {strategy.pressure_pattern}\n\n"
        f"**One cue:** {cue}\n\n**Training drill:** {drill}"
    )


def build_short_strategy_summary(report: dict) -> str:
    stroke = report.get("stroke", "your stroke")
    phase = (_weakest_phases(report, 1) or ["Preparation"])[0]
    pattern, _, cue, _ = PHASE_STRATEGY.get(phase, PHASE_STRATEGY["Preparation"])
    strategy = STROKE_STRATEGIES.get(stroke, STROKE_STRATEGIES["Forehand Groundstroke"])
    return f"I analysed your **{stroke}** as a complete movement pattern. {pattern} For now: **{strategy.safe_pattern}** Cue: **{cue}**"
