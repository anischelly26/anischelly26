from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CoachingPlan:
    stroke: str
    title: str
    steps: tuple[str, ...]
    key_cue: str
    drill: str


STROKE_PLANS: dict[str, CoachingPlan] = {
    "Forehand Groundstroke": CoachingPlan(
        stroke="Forehand Groundstroke",
        title="Build a clean forehand from preparation to recovery",
        steps=(
            "Start in a balanced ready position with the racket in front and make a small split step as your opponent strikes the ball.",
            "Turn your shoulders early and take the racket back with the body turn instead of pulling the arm back on its own.",
            "Use small adjustment steps so the ball is not too close to your body, then settle into a stable hitting base.",
            "Begin the forward swing smoothly from the legs and trunk, then let the hitting arm follow the rotation.",
            "Meet the ball comfortably in front of you and keep your eyes on the contact area through the hit.",
            "Finish the swing naturally, then bring the racket back in front and recover immediately for the next ball.",
        ),
        key_cue="Turn early, create space, contact in front, recover fast.",
        drill="Do 3 sets of 10 slow shadow forehands. Pause at preparation, contact and finish. Then repeat with easy fed balls at 50% speed.",
    ),
    "Backhand Groundstroke": CoachingPlan(
        stroke="Backhand Groundstroke",
        title="Build a compact, stable backhand",
        steps=(
            "Split step and recognise the backhand early so you can turn before the ball reaches you.",
            "Rotate your shoulders as a unit and prepare the racket compactly on the backhand side.",
            "Adjust with the feet until you have enough distance from the ball to swing without being crowded.",
            "Start the forward movement from a stable base and rotate through the shot instead of pushing only with the arms.",
            "Contact the ball in front of the body with a stable racket path.",
            "Finish under control, recover the racket in front and return to your tactical position.",
        ),
        key_cue="Early turn, good spacing, stable contact, quick recovery.",
        drill="Alternate 10 shadow backhands with 10 controlled fed backhands. Focus only on early preparation and spacing before adding speed.",
    ),
    "Forehand Volley": CoachingPlan(
        stroke="Forehand Volley",
        title="Make the forehand volley shorter and more efficient",
        steps=(
            "Stay in a low, active ready position with the racket in front.",
            "Turn slightly toward the forehand side but keep the preparation compact; do not make a full backswing.",
            "Move your feet toward the ball and organise your body before the hit.",
            "Guide the racket forward with a firm, controlled structure rather than swinging hard.",
            "Contact the ball in front and use the opponent's pace whenever possible.",
            "Keep the finish short and recover the racket immediately to the ready position.",
        ),
        key_cue="Compact preparation, step to the ball, short finish.",
        drill="Stand near the net and have a partner feed 20 easy balls. Your goal is to finish every volley with the racket still in front of your body.",
    ),
    "Backhand Volley": CoachingPlan(
        stroke="Backhand Volley",
        title="Make the backhand volley compact and stable",
        steps=(
            "Start with the racket high and in front in an active net position.",
            "Turn the shoulders slightly toward the backhand side without taking the racket too far behind you.",
            "Use the feet to get your body behind the ball instead of reaching with the arm.",
            "Move the racket forward on a short path with a stable wrist and controlled racket face.",
            "Contact in front of the body and keep the head quiet through the hit.",
            "Finish compactly and reset immediately for the next volley.",
        ),
        key_cue="Move your feet first; the volley swing stays short.",
        drill="Hit 3 rounds of 15 backhand volleys with no backswing beyond the shoulder line. Prioritise clean contact over power.",
    ),
    "Serve": CoachingPlan(
        stroke="Serve",
        title="Build a repeatable legal padel serve",
        steps=(
            "Set up calmly in the correct service position and choose your target before starting the motion.",
            "Bounce the ball consistently in front of your hitting side so the contact point is repeatable.",
            "Prepare the racket with a relaxed arm and keep the motion simple rather than trying to create power with a large swing.",
            "Transfer your weight forward while striking the ball at or below waist level with at least one foot on the ground.",
            "Send the ball diagonally into the correct service box with control and enough depth to make the return difficult.",
            "Recover immediately into the court and prepare for the third shot.",
        ),
        key_cue="Consistent bounce, simple swing, legal contact, recover forward.",
        drill="Place a towel-sized target deep in the service box. Hit 30 serves at 60% speed and count only serves that are both legal and land in the target zone.",
    ),
    "Bandeja": CoachingPlan(
        stroke="Bandeja",
        title="Use the bandeja to keep control and protect the net",
        steps=(
            "Recognise the lob early and turn side-on immediately.",
            "Move back with adjustment steps until the ball is comfortably in front of your hitting shoulder.",
            "Raise the racket early and keep the non-hitting arm involved in tracking the ball.",
            "Stay balanced and strike with a controlled, slicing action rather than trying to hit a maximum-power smash.",
            "Send the ball deep with margin, ideally toward the corners or difficult defensive zones.",
            "Move forward again after the shot and recover your net position quickly.",
        ),
        key_cue="Get behind the lob, control the contact, then take the net again.",
        drill="Have a partner feed 15 lobs. Your objective is not to win the point; land every bandeja deep and recover inside the service line after each shot.",
    ),
    "Vibora": CoachingPlan(
        stroke="Vibora",
        title="Create a faster attacking overhead without losing control",
        steps=(
            "Turn early and move behind the ball so you are not hitting while falling backward.",
            "Prepare high with the body side-on and track the ball with the non-hitting arm.",
            "Accelerate with trunk rotation and a compact arm action rather than a long tennis-style swing.",
            "Contact high and slightly in front, then brush around the outside of the ball to create side spin.",
            "Direct the shot with depth and angle rather than relying only on speed.",
            "Recover your balance immediately and close the net again.",
        ),
        key_cue="Position first, spin second, power third.",
        drill="Hit sets of 10 víboras at 60% pace aiming deep to one corner. Increase speed only after you can recover forward after every shot.",
    ),
    "Flat Smash": CoachingPlan(
        stroke="Flat Smash",
        title="Build power from positioning and full extension",
        steps=(
            "Read the lob early, turn and move so the ball is in front rather than directly above or behind you.",
            "Load the legs while preparing the hitting arm high.",
            "Drive upward from the ground and rotate the trunk before accelerating the arm.",
            "Reach fully at contact and strike through the ball with a fast but controlled racket head.",
            "Land balanced and know your tactical objective before choosing maximum power.",
            "Recover according to the result of the smash instead of admiring the shot.",
        ),
        key_cue="Get under the ball, extend fully, stay balanced.",
        drill="Perform 10 shadow smashes focusing on footwork, then 15 fed smashes at 70% power while trying to land balanced inside the court.",
    ),
    "Kick Smash / X3": CoachingPlan(
        stroke="Kick Smash / X3",
        title="Create the upward spin needed for an attacking kick smash",
        steps=(
            "Move early so the ball is high and comfortably in front of you.",
            "Load the legs and prepare with the racket high while keeping the body side-on.",
            "Drive upward and accelerate the racket from below the contact path.",
            "Contact at maximum comfortable reach and brush up and around the ball to create topspin and side spin.",
            "Choose the target based on court position; the X3 is a tactical shot, not only a power test.",
            "Recover immediately because an unsuccessful attacking smash can leave your team exposed.",
        ),
        key_cue="Early feet, upward acceleration, high spinning contact.",
        drill="Start with kick-smash shadow swings, then hit 20 controlled overheads focusing on spin and high rebound before attempting to send the ball out of court.",
    ),
    "Forehand Lob": CoachingPlan(
        stroke="Forehand Lob",
        title="Use the forehand lob to regain time and net position",
        steps=(
            "Prepare early and move so you can contact the ball without being jammed.",
            "Lower your base slightly and keep the racket path simple.",
            "Use the legs and a smooth upward swing to lift the ball rather than flicking only with the wrist.",
            "Contact in front with enough height and margin to clear the opponents comfortably.",
            "Aim for depth first; a short lob is easier to attack than a slightly higher deep lob.",
            "Move forward when the lob succeeds and your opponents are forced away from the net.",
        ),
        key_cue="Lift with the whole movement, aim high and deep, then advance.",
        drill="Place a target zone near the opponent's back glass and hit 20 lobs. Score one point only when the ball lands deep without being an easy overhead.",
    ),
    "Backhand Lob": CoachingPlan(
        stroke="Backhand Lob",
        title="Create a reliable defensive backhand lob",
        steps=(
            "Turn early and create enough space on the backhand side.",
            "Stay balanced and let the legs help lower your position under the ball.",
            "Swing smoothly forward and upward instead of trying to lift the ball with the hands alone.",
            "Contact in front with a stable racket face and give the ball enough height to pass the net players safely.",
            "Prioritise depth and recovery over a perfect winner.",
            "Advance only when the lob actually pushes the opponents back.",
        ),
        key_cue="Stable base, smooth lift, high margin, deep target.",
        drill="Hit alternating backhand lobs from defensive positions. The goal is 8 out of 10 balls landing in the final third of the opponent's court.",
    ),
}


PHASE_FOCUS = {
    "Ready_Setup": "Start by improving your ready position and first reaction before changing the swing itself.",
    "Preparation": "Your priority is earlier, simpler preparation. Make the turn before the ball arrives so you are not rushing the swing.",
    "Loading_Positioning": "Your priority is footwork and spacing. Get into position first; do not try to repair poor spacing with the arm at the last second.",
    "Acceleration": "Your priority is sequencing. Let the lower body and trunk start the action, then allow the hitting arm to accelerate naturally.",
    "Contact": "Your priority is repeatable contact. Slow the drill down until you can meet the ball in a comfortable contact zone consistently.",
    "Follow_Through": "Your priority is a controlled finish. Do not stop the racket abruptly or over-swing after contact.",
    "Recovery": "Your priority is recovery. Finish the shot, reset the racket and move back to the correct tactical position immediately.",
}


SEGMENT_CUES = {
    "Wrist": "Keep the hand and racket connected to the larger swing. Avoid trying to manufacture the whole shot with a late wrist flick.",
    "Elbow": "Keep the arm structure relaxed and coordinated with the shoulder turn. Avoid locking the arm or forcing the elbow independently.",
    "Shoulder": "Use an early shoulder turn and let the upper body organise the stroke before the arm accelerates.",
    "Pelvis": "Use the hips as part of the turn and weight transfer instead of hitting only with the upper body.",
    "Knee": "Stay athletic through the legs so you can load, adjust and recover without becoming upright and static.",
    "Foot": "Fix the feet before the swing. Small adjustment steps create better spacing and make the racket action much simpler.",
    "Head": "Track the ball early and keep the head quiet around contact instead of looking up too soon.",
}


def get_plan(stroke: str) -> CoachingPlan:
    return STROKE_PLANS.get(stroke, STROKE_PLANS["Forehand Groundstroke"])


def targeted_steps(stroke: str, phase: str | None, body_segment: str | None) -> tuple[str, list[str], str]:
    plan = get_plan(stroke)
    focus = PHASE_FOCUS.get(phase or "", "Build the movement slowly from preparation to recovery before adding speed.")
    segment_key = next((key for key in SEGMENT_CUES if body_segment and key.lower() in body_segment.lower()), None)
    segment_cue = SEGMENT_CUES.get(segment_key or "", "Keep the movement simple, balanced and repeatable.")

    phase_to_step_indexes = {
        "Ready_Setup": [0, 1],
        "Preparation": [0, 1, 2],
        "Loading_Positioning": [1, 2, 3],
        "Acceleration": [2, 3, 4],
        "Contact": [2, 3, 4],
        "Follow_Through": [3, 4, 5],
        "Recovery": [4, 5],
    }
    indexes = phase_to_step_indexes.get(phase or "", [0, 1, 2, 3, 4, 5])
    selected = [plan.steps[i] for i in indexes if i < len(plan.steps)]
    steps = [focus, segment_cue, *selected]
    steps = list(dict.fromkeys(steps))[:5]
    return plan.title, steps, plan.drill
