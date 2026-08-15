# PadelVision AI v0.3 — Database-Connected Coach

PadelVision v0.3 connects three layers:

1. **Video analysis** — MediaPipe detects 33 body landmarks.
2. **Binary movement database** — each comparable body point has an expected six-bit direction vector for each stroke phase.
3. **Coaching agent** — retrieves database rows and combines them with the user's measured mismatches before answering.

## Start on Windows

Extract the ZIP and double-click:

`START_HERE.bat`

Keep the terminal window open while using the app.

## What is new in v0.3

- The binary movement database is included in the project under `data/`.
- 33 pose landmarks are converted into observed binary movement vectors.
- Observed vectors are compared with expected database vectors.
- Results are summarized by movement phase, body segment, and individual landmark.
- The chatbot is now a database-connected coaching agent.
- The app has a cleaner conversational interface.
- Optional advanced LLM mode can use an OpenAI API key; the local grounded coach works without one.

## Binary vector order

`[X_Right, X_Left, Y_Forward, Y_Backward, Z_Up, Z_Down]`

Example:

- Right + Forward: `101000`
- Up + Forward: `001010`
- Stable: `000000`

## Important current limitations

This is still a research prototype.

- The seven stroke phases are currently estimated by dividing a single-stroke clip into equal time sections.
- The player coordinate conversion assumes a rear or front camera view and is not a full calibrated 3D court reconstruction.
- The movement database is marked **Needs coach validation**.
- Racket and ball tracking are not implemented yet.

These limitations should be fixed before treating the score as a validated padel technique assessment.

## Recommended video

- One complete stroke per clip.
- Full body visible.
- Stable camera.
- Rear view is currently preferred.
- 3–10 second clips work best for this prototype.


## Strategy-first video analysis

In v0.5 the player-facing AI no longer reports raw body landmarks, binary vectors,
angle values, movement-match percentages, or point-by-point placement.

The internal movement database is still used for diagnosis, but the result is converted into:

1. Overall movement pattern
2. Tactical consequence during a rally
3. Safer match strategy to use immediately
4. Movement rebuild sequence
5. One simple coaching cue
6. One practical training drill

This is deliberately different from a biomechanics dashboard. The technical matrix is an
internal reasoning layer; the player receives actionable padel strategy.

