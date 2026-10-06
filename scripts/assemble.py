"""Build timeline.otio from shots.yaml + VO timing, then render with ffmpeg.

animatic: keyframe stills (or title cards) held for each paragraph's VO.
final:    generated / manim / clip shots, falling back to stills where missing.
"""
import argparse, json
from pathlib import Path
import opentimelineio as otio
import yaml
from common import run, parse_script, shot_plan, ROOT

FPS, W, H, GAP = 30, 1920, 1080, 0.4
ap = argparse.ArgumentParser(); ap.add_argument("workdir"); ap.add_argument("--mode", choices=["animatic", "final"], default="animatic")
a = ap.parse_args()
wd = Path(a.workdir); slug = wd.name
shots = yaml.safe_load(open(wd / "shots.yaml"))
timing = json.loads((wd / "vo/timing.json").read_text())
paras = parse_script(wd / "script.md")
seg = wd / f"seg_{a.mode}"; seg.mkdir(exist_ok=True)

plan = [(s, d) for s, d, _ in shot_plan(shots, paras, timing, GAP)]

def source(s):
    vid, key = wd / f"shots/{s['id']}.mp4", wd / f"keyframes/{s['id']}.png"
    if a.mode == "final" and s.get("kind") == "clip" and s.get("clip"):
        return wd / "clips" / s["clip"], s.get("in", 0)
    if a.mode == "final" and vid.exists(): return vid, 0
    if key.exists(): return key, None
    return None, None

vf = f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=0x0E1116,fps={FPS},format=yuv420p"
tl = otio.schema.Timeline(name=f"{slug}_{a.mode}")
vtrack = otio.schema.Track(name="V1", kind=otio.schema.TrackKind.Video)
listfile = seg / "list.txt"
with open(listfile, "w") as lf:
    for s, d in plan:
        out = seg / f"{s['id']}.mp4"
        src, start = source(s)
        if src is None:   # title card so gaps are visible in the animatic
            label = s["id"].replace(":", " ")
            run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"color=c=0x0E1116:s={W}x{H}:r={FPS}:d={d}",
                 "-vf", f"drawtext=text='{label} ({s.get('kind','?')})':fontcolor=white:fontsize=48:x=(w-tw)/2:y=(h-th)/2",
                 "-pix_fmt", "yuv420p", str(out)])
        elif start is None:   # still image
            run(["ffmpeg", "-y", "-loop", "1", "-i", src, "-t", f"{d:.3f}", "-vf", vf, "-an", str(out)])
        else:                 # video: trim, or hold last frame if short
            run(["ffmpeg", "-y", "-ss", str(start), "-i", src, "-vf", vf + f",tpad=stop_mode=clone:stop_duration={d}",
                 "-t", f"{d:.3f}", "-an", str(out)])
        lf.write(f"file '{out.resolve()}'\n")
        vtrack.append(otio.schema.Clip(name=s["id"],
            media_reference=otio.schema.ExternalReference(target_url=str(out.resolve())),
            source_range=otio.opentime.TimeRange(otio.opentime.RationalTime(0, FPS), otio.opentime.RationalTime(round(d * FPS), FPS))))
tl.tracks.append(vtrack)

# VO track: paragraphs in order, each followed by a short gap
atrack = otio.schema.Track(name="VO", kind=otio.schema.TrackKind.Audio)
ins, fc = [], []
for i, p in enumerate(paras):
    f = wd / f"vo/{p['id']}.wav"; ins += ["-i", f]
    fc.append(f"[{i}]aresample=48000,apad=pad_dur={GAP}[a{i}]")
    atrack.append(otio.schema.Clip(name=p["id"], media_reference=otio.schema.ExternalReference(target_url=str(f.resolve())),
        source_range=otio.opentime.TimeRange(otio.opentime.RationalTime(0, FPS), otio.opentime.RationalTime(round((timing[p['id']] + GAP) * FPS), FPS))))
fc.append("".join(f"[a{i}]" for i in range(len(paras))) + f"concat=n={len(paras)}:v=0:a=1[vo]")
vo_full = wd / "vo_full.wav"
run(["ffmpeg", "-y", *ins, "-filter_complex", ";".join(fc), "-map", "[vo]", vo_full])
tl.tracks.append(atrack)

music = wd / "music.mp3"
if music.exists():
    mtrack = otio.schema.Track(name="MUSIC", kind=otio.schema.TrackKind.Audio)
    mtrack.append(otio.schema.Clip(name="music", media_reference=otio.schema.ExternalReference(target_url=str(music.resolve()))))
    tl.tracks.append(mtrack)
otio.adapters.write_to_file(tl, str(wd / f"timeline_{a.mode}.otio"))

video_only = seg / "video.mp4"
run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", listfile, "-c", "copy", video_only])
outdir = ROOT / "out"; outdir.mkdir(exist_ok=True)
final = outdir / f"{slug}_{a.mode}.mp4"
if music.exists():
    mix = ("[1]asplit=2[vo][sc];[2]volume=0.35[m];[m][sc]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400[duck];"
           "[vo][duck]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-16:TP=-2:LRA=11[aout]")
    run(["ffmpeg", "-y", "-i", video_only, "-i", vo_full, "-i", music, "-filter_complex", mix,
         "-map", "0:v", "-map", "[aout]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", final])
else:
    run(["ffmpeg", "-y", "-i", video_only, "-i", vo_full, "-af", "loudnorm=I=-16:TP=-2:LRA=11",
         "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", final])
print("rendered", final)
