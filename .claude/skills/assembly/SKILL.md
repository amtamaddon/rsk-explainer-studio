---
name: assembly
description: Assemble shots, voiceover, and music into a timeline with OpenTimelineIO and render with ffmpeg. Use for the animatic and the final cut.
---

# Assembly

    python scripts/assemble.py work/<slug> --mode animatic   # keyframe stills over VO
    python scripts/assemble.py work/<slug> --mode final

- Writes timeline.otio (video, VO, and music tracks), so the edit is inspectable and opens in Resolve or Premiere via OTIO adapters.
- Each shot is trimmed or held to its paragraph's VO duration.
- Renders out/<slug>_<mode>.mp4 at 1080p30, music sidechain-ducked under VO, loudness normalized to -16 LUFS.
