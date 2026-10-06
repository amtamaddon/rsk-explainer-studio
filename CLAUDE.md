# Explainer Studio

You produce 3Blue1Brown-style explainer videos end to end. Run this in Claude Code, not the Claude app: the pipeline needs a real shell, API keys, ffmpeg, and long-running renders.

## RSK house rules (hard rules, override anything below)

@docs/rsk-video-rules.md

For RSK videos the audience is busy practice leaders, so keep narration plain and conversational rather than lecture-style; the Claudism rules below still apply. A finished worked example (script, shot list, character sheet, style frames, approved keyframes) is in examples/rsk-explainer-v2/

## Pipeline (run in order, one stage at a time, write every artifact under work/<slug>/)

1. **Plan the script** with the `script-planning` skill. Output: script.md and shots.yaml.
2. **Voice** with `emotive-tts`. Output: vo/*.wav plus vo/timing.json.
3. **Reference images, then keyframes** with `keyframes`. Output: refs/ and keyframes/.
4. **Animatic.** Assemble keyframes as stills against the voiceover with `assembly` (mode: animatic). Show it to the user and get approval before spending on video generation.
5. **Generated shots** with `video-gen`. Seedance for motion-heavy shots, Veo for everything else.
6. **Motion graphics** with `motion-graphics` (Manim for math, Motion Canvas or Hyperframes for HTML-grounded diagrams and type).
7. **Real-world clips** with `clip-sourcing` (yt-dlp, Creative Commons only, license logged).
8. **Music bed:** skipped. No music (see Audio).
9. **Assemble** with `assembly` (OpenTimelineIO timeline, then ffmpeg render).
10. **Captions** with `captions` (word-level timed, burned in plus a sidecar .srt).
11. **Critique** with `critic`. If it fails, fix the named shots and re-run steps 9 to 11. Max three loops, then report to the user.

## Narration voice (hard rule)

Narrate like a university professor giving a well-prepared lecture to curious adults. Full, connected sentences that carry an idea from cause to consequence. Avoid Claudisms:
- no strings of short punchy sentences ("It's simple. It's elegant. It's wrong.")
- no number-stuffing; use a figure only when the argument needs it, and at most one per paragraph
- no "Here's the thing", "Let's dive in", "But here's the twist", rhetorical question chains, or rule-of-three lists
- no em dashes or en dashes in the script
Prefer analogy, a concrete image, then the abstraction.

## Audio (user preference, hard rule)

Narrate with the Edge neural voice (tts.provider: edge in config/models.yaml), not Gemini. Skip the music step: no music bed and no sound effects. Assembly adds music only if work/<slug>/music.mp3 exists, so never create it.

## Model routing

All model IDs live in config/models.yaml. Never hardcode them. Image and video generation go through OpenRouter with one key (scripts/openrouter.py). If a model ID returns 404, list current models (`python scripts/openrouter.py models`) and ask the user before substituting.

## Budget discipline

- Generate keyframes before video. Never call a video model for a shot without an approved keyframe.
- Video gen is the expensive step; log every call with cost to work/<slug>/spend.jsonl.

## Setup

    cp .env.example .env   # fill in your own OpenRouter key and set a credit limit on it
    pip install -r requirements.txt
    winget install ffmpeg yt-dlp   # Windows; or brew / apt
    npm i -g @motion-canvas/cli   # optional, for HTML motion graphics

Start with: copy briefs/rsk-template.md to briefs/<slug>.md, fill it in, then say "Make the video in briefs/<slug>.md." Always start a fresh session per video.
