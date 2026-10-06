---
name: video-gen
description: Turn approved keyframes into short generated video shots with Veo or Seedance through OpenRouter. Use only after the animatic is approved.
---

# Video generation

- Route by the shot's `motion` field: `high` goes to Seedance (stronger on camera moves and physical motion), everything else to Veo.
- Always image-to-video from the approved keyframe, plus reference images where the API accepts them. Never text-only.
- Keep clips 4 to 8 seconds; assembly trims to the voiceover.
- Prompt for camera and motion only. The keyframe already carries content and style.
- `python scripts/openrouter.py video --model-key video_motion --image keyframes/<id>.png --prompt "slow push in, stars faintly twinkle" --out shots/<id>.mp4`
- Every call is logged to spend.jsonl. Stop and ask the user if spend passes the brief's budget.
