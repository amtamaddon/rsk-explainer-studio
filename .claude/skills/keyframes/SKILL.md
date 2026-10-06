---
name: keyframes
description: Create reference images and per-shot keyframes with the configured image model via OpenRouter, keeping style and subjects consistent. Use before any video generation and to build the animatic.
---

# Keyframes

1. **Reference sheet first.** From shots.yaml collect every recurring subject, location, and the overall look. Generate one reference image per item into refs/ (ref_style.png, ref_sky.png...). Show them to the user; they anchor the whole video.
2. **Keyframes.** For each generated or still shot:
   `python scripts/openrouter.py image --prompt "..." --ref refs/ref_style.png --ref refs/<subject>.png --out keyframes/<id>.png`
   Always pass the style ref plus the subject refs listed on the shot.
3. **Consistency check.** Build a contact sheet (`ffmpeg -pattern_type glob -i 'keyframes/*.png' -vf tile=4x3 contact.png`) and judge the set together. Regenerate outliers before moving on.
4. 16:9 at 1920x1080 or the nearest size the model supports.
