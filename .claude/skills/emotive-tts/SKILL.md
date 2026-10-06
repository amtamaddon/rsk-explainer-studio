---
name: emotive-tts
description: Generate expressive narration audio with Gemini TTS, steering emotion per paragraph. Use whenever narration, voiceover, or spoken audio is needed for a video.
---

# Emotive TTS

## First run: finish building this skill from the live API
Gemini TTS is steered by natural-language style instructions. Before first use, fetch the current Gemini speech-generation docs, confirm the model ID in config/models.yaml, list the available voices, and update scripts/tts.py and this file with anything that differs (voice names, style-prompt syntax, multi-speaker support, sample rate). Audition three voices on paragraph p01 and let the user pick. Then delete this section.

## Use
    python scripts/tts.py work/<slug>/script.md work/<slug>/vo/

The script turns each paragraph's bracketed tag into a style instruction:
- base persona, always prepended: "Read as a warm, unhurried university lecturer speaking to a small room. Natural pauses at commas. Never rushed, never theatrical."
- tag appended: "Tone for this passage: <tag>."

One WAV per paragraph keeps retakes cheap. vo/timing.json records each duration for assembly.

## Pronunciation
config/pronunciations.yaml maps written forms to spoken ones and is applied only to the TTS input, so captions still show "835". It is read as "eight thirty-five", never "eight hundred thirty-five". Add any term a voice misreads.

## Quality bar
Render p01 alone first. If the read sounds sing-song or overacted, soften the tag wording instead of adding emotion words.
