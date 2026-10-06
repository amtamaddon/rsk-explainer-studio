---
name: motion-graphics
description: Build diagrams, equations, and kinetic type for explainers with Manim, Motion Canvas, or Hyperframes. Use for any shot of kind manim or html.
---

# Motion graphics

Pick the tool by the job:
- **Manim** (Python): geometry, plots, equations, anything in the 3Blue1Brown idiom. `manim -qh scenes/<id>.py Scene -o <id>.mp4`
- **Motion Canvas** (TypeScript): HTML-grounded diagrams, UI, timelines, typographic sequences.
- **Hyperframes**: when the shot is easiest to express as an HTML page animated over time. Read its current docs before first use.

Rules:
- Match duration to the paragraph length in vo/timing.json.
- Background #0E1116, one accent color, generous negative space.
- Build the diagram in the order the narration explains it. Animate the idea, not decoration.
- Export 1920x1080, 30 fps, H.264, to shots/<id>.mp4.
