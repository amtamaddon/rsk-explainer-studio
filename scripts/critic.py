"""Hostile QA pass: loudness, silence, black frames, speech accuracy, per-shot visual match."""
import base64, json, os, re, subprocess, sys
from pathlib import Path
import jiwer, requests
import opentimelineio as otio
from faster_whisper import WhisperModel
from common import CFG, parse_script

wd, video = Path(sys.argv[1]), Path(sys.argv[2])
fails, notes = [], []

def ff(filters):
    return subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(video), *filters, "-f", "null", "-"],
                          capture_output=True, text=True).stderr

# 1. loudness
log = ff(["-af", "ebur128=peak=true"])
I = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", log)[-1]); tp = float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", log)[-1])
notes.append(f"Loudness {I} LUFS, true peak {tp} dBTP")
if abs(I + 16) > 1: fails.append(f"Integrated loudness {I} LUFS; target -16. Re-run loudnorm in assembly.")
if tp > -1: fails.append(f"True peak {tp} dBTP over -1. Lower TP target in loudnorm.")

# 2. dead air and black frames
for m in re.finditer(r"silence_start: ([\d.]+)[\s\S]*?silence_duration: ([\d.]+)", ff(["-af", "silencedetect=n=-45dB:d=2.5"])):
    fails.append(f"{float(m.group(1)):.1f}s: {float(m.group(2)):.1f}s of silence. Tighten the gap or add VO.")
for m in re.finditer(r"black_start:([\d.]+) black_end:([\d.]+)", ff(["-vf", "blackdetect=d=0.5:pix_th=0.05", "-an"])):
    fails.append(f"{float(m.group(1)):.1f}s to {float(m.group(2)):.1f}s: black frames. Check the shot at this time.")

# 3. speech accuracy
paras = [p for p in parse_script(wd / "script.md") if p["tag"] != "silent"]   # silent paragraphs only hold the end card
segs, _ = WhisperModel(CFG["asr"]["model"], compute_type="auto").transcribe(str(video))
hyp = " ".join(s.text for s in segs)
norm = jiwer.Compose([jiwer.ToLowerCase(), jiwer.RemovePunctuation(), jiwer.RemoveMultipleSpaces(), jiwer.Strip()])
wer = jiwer.wer(norm(" ".join(p["text"] for p in paras)), norm(hyp))
notes.append(f"WER vs script: {wer:.1%}")
if wer > 0.05: fails.append(f"WER {wer:.1%} over 5%. Diff script.md against the transcript and re-record the worst paragraphs.")

# 4. visual match per shot
tl_path = next(wd.glob("timeline_final.otio"), None) or next(wd.glob("timeline_*.otio"))
tl = otio.adapters.read_from_file(str(tl_path))
ptext = {p["id"]: p["text"] for p in paras}
import yaml
vo_of = {s["id"]: s["vo"] for s in yaml.safe_load(open(wd / "shots.yaml", encoding="utf-8"))}
frames = wd / "critic_frames"; frames.mkdir(exist_ok=True)
t = 0.0
for clip in tl.video_tracks()[0]:
    d = clip.duration().to_seconds(); mid = t + d / 2; t += d
    png = frames / f"{clip.name}.png"
    subprocess.run(["ffmpeg", "-y", "-ss", f"{mid:.2f}", "-i", str(video), "-frames:v", "1", str(png)], capture_output=True)
    narration = ptext.get(vo_of.get(clip.name, ""), "")
    body = {"model": CFG["openrouter"]["vision_critic"], "response_format": {"type": "json_object"},
            "messages": [{"role": "user", "content": [
                {"type": "text", "text": "You are a skeptical film editor paid per defect found. Narration at this moment: "
                 f"\"{narration}\". Return JSON {{\"matches_narration\": bool, \"defects\": [str], \"fix\": str}}. "
                 "Defects include garbled text, warped anatomy, artifacts, style drift, irrelevant imagery, captions over key content."},
                {"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(png.read_bytes()).decode()}}]}]}
    try:
        r = requests.post(f"{CFG['openrouter']['base_url']}/chat/completions", json=body, timeout=120,
                          headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"})
        v = json.loads(r.json()["choices"][0]["message"]["content"])
        if not v.get("matches_narration") or v.get("defects"):
            fails.append(f"{mid:.1f}s shot {clip.name}: {'; '.join(v.get('defects', [])) or 'does not match narration'}. Fix: {v.get('fix','')}")
    except Exception as e:
        notes.append(f"Vision check skipped for {clip.name}: {e}")

report = ["# Critique", "", f"Result: {'FAIL' if fails else 'PASS'}", "", "## Measurements", *[f"- {n}" for n in notes],
          "", "## Failures", *([f"- {f}" for f in fails] or ["- none"])]
(wd / "critique.md").write_text("\n".join(report))
print("\n".join(report))
sys.exit(1 if fails else 0)
