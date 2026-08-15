# PadelVision AI v0.5 — Strategy-First AI Padel Coach

PadelVision is a sports-AI research prototype that turns a short padel-stroke video into **player-facing tactical coaching** rather than a wall of biomechanics numbers.

## System

```text
Stroke video
   ↓
MediaPipe pose estimation (33 landmarks)
   ↓
Player-centred movement deltas
   ↓
7-phase stroke segmentation
   ↓
Movement-reference comparison
   ↓
Internal diagnosis
   ↓
Movement pattern → tactical consequence → match strategy → rebuild → cue → drill
```

The app combines:

- **Video analysis** with MediaPipe + OpenCV
- **Movement reference retrieval** using six-bit directional vectors
- **Strategy-first coaching** that hides raw coordinates/landmark noise from the player
- **Official-rules retrieval** for padel-rule questions
- **Local coaching mode** that works without an API key
- **Optional OpenAI mode** for richer grounded conversation

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

On Windows, `START_HERE.bat` is also included.

## Strategy-first design

The player-facing AI does **not** lead with raw body landmark IDs, binary vectors, angle values or point-by-point placement.

Instead, the internal movement analysis is translated into:

1. Overall movement pattern
2. Tactical consequence during the rally
3. Safer match strategy to use immediately
4. Movement rebuild sequence
5. One simple coaching cue
6. One practical training drill

## Important limitations

This is a research prototype, not a validated coaching/medical system.

- Stroke phases are currently estimated using equal-time segmentation.
- Player-centred coordinates are not a calibrated 3D court reconstruction.
- The movement-reference data is explicitly marked **Needs coach validation**.
- Racket and ball tracking are not implemented in this build.
- Technique scores must not be treated as scientifically validated performance grades.

## GitHub source-mirror note

The original saved release is **`PadelVision_AI_v0.5_STRATEGY.zip`**. It contains the complete movement dataset, rules source material, sample outputs and bundled project assets.

This GitHub folder mirrors the readable application/engine source and includes a small reference sample so the code structure can be explored and started without committing every large/binary source asset. See [`../SOURCE_RELEASES.md`](../SOURCE_RELEASES.md) for release provenance and SHA-256 verification.

---

**Anis Chelly // AI × Software Engineering // Sports AI R&D**
