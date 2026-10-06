---
name: clip-sourcing
description: Search YouTube with yt-dlp for real footage and download only Creative Commons clips, logging attribution. Use for any shot of kind clip.
---

# Clip sourcing

    python scripts/clip_search.py "observatory dome opening timelapse" --max 15 --out work/<slug>/clips/

The script searches, keeps only videos whose license field says Creative Commons, downloads them, and appends title, uploader, URL, and license to clips/LICENSES.md.

Pick the best few seconds (extract frames to judge) and record in and out points on the shot in shots.yaml. Put attribution in the end card and description. If nothing CC fits, fall back to a generated shot. Never use non-CC footage.
