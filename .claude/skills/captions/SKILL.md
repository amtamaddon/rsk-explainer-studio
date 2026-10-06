---
name: captions
description: Produce word-level timed subtitles from the final audio with faster-whisper and burn them in. Use after the final cut renders.
---

# Captions

    python scripts/captions.py out/<slug>_final.mp4 --script work/<slug>/script.md

- Transcribes with word timestamps, groups words into lines of at most 42 characters, and writes an .ass file that highlights each word as it is spoken, plus a plain .srt sidecar.
- Passes the script as the ASR initial prompt so proper nouns and terms come out right. Fix any remaining misspellings against script.md by hand.
- Burns in to out/<slug>_captioned.mp4.
