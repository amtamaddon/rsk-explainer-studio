"""Word-level captions with faster-whisper: karaoke .ass + .srt, burned in."""
import argparse, re
from pathlib import Path
from faster_whisper import WhisperModel
from common import CFG, run, parse_script

ap = argparse.ArgumentParser(); ap.add_argument("video"); ap.add_argument("--script")
ap.add_argument("--theme", choices=["dark", "light"], default="dark")   # light: white text on a navy box, for light-background videos
a = ap.parse_args()
video = Path(a.video)
prompt = " ".join(p["text"] for p in parse_script(a.script))[:900] if a.script else None

model = WhisperModel(CFG["asr"]["model"], compute_type="auto")
segments, _ = model.transcribe(str(video), word_timestamps=True, initial_prompt=prompt)
words = [w for s in segments for w in s.words]

# The script is ground truth for spelling, capitalization and punctuation: align the ASR words to the
# script's words and take the script's form wherever they match (timings stay from ASR).
if a.script:
    import difflib
    from types import SimpleNamespace
    key = lambda s: re.sub(r"[^a-z0-9$]", "", s.lower())
    ref = [tok for p in parse_script(a.script) if p["tag"] != "silent" for tok in p["text"].split()]
    sm = difflib.SequenceMatcher(None, [key(w.word) for w in words], [key(r) for r in ref], autojunk=False)
    fixed = []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        src = words[i1:i2]
        if op == "equal" or (op == "replace" and i2 - i1 == j2 - j1):   # same count: take the script's words
            fixed += [SimpleNamespace(word=ref[j], start=w.start, end=w.end) for w, j in zip(src, range(j1, j2))]
        elif op == "replace" and j2 - j1 == 1:                          # ASR split one script word (e.g. look-back)
            fixed.append(SimpleNamespace(word=ref[j1], start=src[0].start, end=src[-1].end))
        else:                                                            # anything else: keep what was heard
            fixed += [SimpleNamespace(word=w.word, start=w.start, end=w.end) for w in src]
    words = fixed

lines, cur = [], []
for w in words:
    text = " ".join(x.word.strip() for x in cur + [w])
    if cur and (len(text) > (34 if a.theme == 'light' else 42) or w.start - cur[-1].end > 0.6 or re.search(r"[.?!]$", cur[-1].word)):
        lines.append(cur); cur = []
    cur.append(w)
if cur: lines.append(cur)

def ts(t, ass=False):
    h, m, s = int(t // 3600), int(t % 3600 // 60), t % 60
    return f"{h}:{m:02d}:{s:05.2f}" if ass else f"{h:02d}:{m:02d}:{int(s):02d},{int(t % 1 * 1000):03d}"

srt = []
ass = ["[Script Info]", "ScriptType: v4.00+", "PlayResX: 1920", "PlayResY: 1080", "",
       "[V4+ Styles]",
       "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
       ("Style: Default,Segoe UI Semibold,72,&H001874F4,&H00FFFFFF,&H00741500,&H00741500,0,0,0,0,100,100,0,0,3,18,0,2,80,80,50,1"
        if a.theme == "light" else
        "Style: Default,Arial,54,&H0000D7FF,&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,3,0,2,80,80,70,1"),
       "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
for i, ln in enumerate(lines, 1):
    start, end = ln[0].start, ln[-1].end
    srt += [str(i), f"{ts(start)} --> {ts(end)}", " ".join(w.word.strip() for w in ln), ""]
    tag = "k" if a.theme == "light" else "kf"   # light: whole-word color switch, no mid-word sweep
    kara = "".join(f"{{\\{tag}{max(1, round((w.end - w.start) * 100))}}}{w.word.strip()} " for w in ln)
    ass.append(f"Dialogue: 0,{ts(start, True)},{ts(end, True)},Default,,0,0,0,,{kara.strip()}")

base = video.with_suffix("")
Path(f"{base}.srt").write_text("\n".join(srt))
Path(f"{base}.ass").write_text("\n".join(ass))
out = str(base).replace("_final", "") + "_captioned.mp4"
# run from the video's folder with relative paths: ffmpeg filter args choke on "C:" drive colons
run(["ffmpeg", "-y", "-i", video.name, "-vf", f"ass={base.name}.ass", "-c:a", "copy", Path(out).name], cwd=video.parent)
print("wrote", out)
