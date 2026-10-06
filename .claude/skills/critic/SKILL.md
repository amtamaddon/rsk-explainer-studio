---
name: critic
description: Review a rendered video for audio and visual quality using frame screenshots, a vision model, and transcription. Use after every final render and before showing the user.
---

# Critic

    python scripts/critic.py work/<slug> out/<slug>_captioned.mp4

Checks and pass bars:
1. **Speech accuracy.** Transcribe and compare to script.md. Word error rate under 5%.
2. **Loudness.** Integrated -16 LUFS within 1 LU; true peak under -1 dBTP.
3. **Dead air and black frames.** No silence over 2.5 s; no black over 0.5 s except intended fades.
4. **Visual match.** A screenshot at each shot's midpoint goes to the vision model with that paragraph's narration. Does the frame show what is being said? Any garbled text, warped anatomy, flicker, or drift from refs?
5. **Captions.** Legible and not covering diagram content.

The script writes work/<slug>/critique.md with each failure, its timestamp, shot id, and a concrete fix. Read it as a hostile editor would. Fix, re-render, re-critique, at most three loops.
