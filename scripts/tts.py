"""Gemini TTS, one WAV per paragraph, emotion steered by the paragraph tag."""
import json, os, sys, wave
from pathlib import Path
import re, subprocess
import yaml
from common import CFG, parse_script, probe_duration, run

LEX_PATH = Path(__file__).resolve().parent.parent / "config/pronunciations.yaml"
LEX = yaml.safe_load(LEX_PATH.read_text()) if LEX_PATH.exists() else {}


def spoken(text):
    """Swap written forms for spoken ones (e.g. 835 -> eight thirty-five) before synthesis."""
    for k, v in (LEX or {}).items():
        text = re.sub(rf"(?<![\w-]){re.escape(str(k))}(?![\w-])", str(v), text)
    return text


def synth(client, text, tag, out):
    from google.genai import types
    # gemini-3.8-flash-tts speaks any style direction aloud and rejects system instructions,
    # so send the narration alone and set the lecture pace afterwards with tts.tempo.
    resp = client.models.generate_content(
        model=CFG["tts"]["model"],
        contents=text,
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=CFG["tts"]["voice"])))))
    pcm = resp.candidates[0].content.parts[0].inline_data.data
    with wave.open(str(out), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(pcm)
    tempo = CFG["tts"].get("tempo", 1.0)
    if tempo != 1.0:
        tmp = Path(out).with_suffix(".raw.wav"); Path(out).replace(tmp)
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-af", f"atempo={tempo}", out]); tmp.unlink()


def synth_edge(text, tag, out):
    """Keyless STAND-IN (no GEMINI_API_KEY): Microsoft Edge neural voice via edge-tts.
    No natural-language style steering is possible here, so the paragraph tag only nudges rate and pitch.
    Replace with Gemini TTS for the real emotive read."""
    import asyncio, edge_tts
    t = tag.lower(); rate, pitch = "-6%", "-2Hz"
    if any(k in t for k in ("quiet", "reflective", "closing")): rate, pitch = "-10%", "-4Hz"
    if any(k in t for k in ("building", "curious", "amused")): rate, pitch = "-3%", "+0Hz"
    tmp = str(out) + ".mp3"
    comm = edge_tts.Communicate(text, os.environ.get("TTS_VOICE") or CFG["tts"].get("fallback_voice", "en-GB-RyanNeural"), rate=rate, pitch=pitch)
    asyncio.run(comm.save(tmp))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-ar", "24000", "-ac", "1", str(out)], check=True)
    os.remove(tmp)


if __name__ == "__main__":
    script, outdir = Path(sys.argv[1]), Path(sys.argv[2])
    only = sys.argv[3] if len(sys.argv) > 3 else None   # e.g. p01 for an audition
    outdir.mkdir(parents=True, exist_ok=True)
    key = os.environ.get("GEMINI_API_KEY") if CFG["tts"].get("provider") == "gemini" else None
    if key:
        from google import genai
        client = genai.Client(api_key=key)
    else:
        client = None
        print(f"Using edge-tts voice {os.environ.get('TTS_VOICE') or CFG['tts'].get('fallback_voice')}; emotion tags only nudge rate/pitch.")
    tfile = outdir / "timing.json"
    timing = json.loads(tfile.read_text()) if (only and tfile.exists()) else {}
    for p in parse_script(script):
        if only and p["id"] != only: continue
        out = outdir / f"{p['id']}.wav"
        text = spoken(p["text"])
        (synth(client, text, p["tag"], out) if client else synth_edge(text, p["tag"], out))
        timing[p["id"]] = probe_duration(out)
        print(p["id"], f"{timing[p['id']]:.1f}s")
    (outdir / "timing.json").write_text(json.dumps(timing, indent=2))
