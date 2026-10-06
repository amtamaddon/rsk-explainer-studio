"""Burn a drawn title and/or label onto a generated clip (ffmpeg drawtext is unusable on this Windows build).

    python scripts/clip_overlay.py work/<slug> s04
Reads `title` / `label` from the shot in shots.yaml. Keeps the untouched clip in clips_raw/<id>.mp4 and writes shots/<id>.mp4.
"""
import shutil, subprocess, sys
from pathlib import Path
import yaml
from PIL import Image, ImageDraw, ImageFont

NAVY, WHITE, CREAM = (0, 21, 116, 255), (255, 255, 255, 255), (247, 243, 238, 235)
BOLD = "C:/Windows/Fonts/segoeuib.ttf"


def overlay_png(title, label, out, W=1920, H=1080):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if title:
        f = ImageFont.truetype(BOLD, 66); x, y = 70, 56
        bw = d.textlength(title, font=f)
        d.rounded_rectangle([x - 24, y - 12, x + bw + 24, y + 86], radius=16, fill=CREAM)
        d.text((x, y), title, font=f, fill=NAVY)
    if label:
        f = ImageFont.truetype(BOLD, 40); x, y = 70, H - 300
        bw = d.textlength(label, font=f)
        d.rounded_rectangle([x - 20, y - 8, x + bw + 20, y + 56], radius=12, fill=NAVY)
        d.text((x, y - 2), label, font=f, fill=WHITE)
    im.save(out)


if __name__ == "__main__":
    wd, sid = Path(sys.argv[1]), sys.argv[2]
    shot = next(s for s in yaml.safe_load(open(wd / "shots.yaml", encoding="utf-8")) if s["id"] == sid)
    raw = wd / "clips_raw" / f"{sid}.mp4"
    raw.parent.mkdir(exist_ok=True)
    if not raw.exists():
        shutil.copy(wd / "shots" / f"{sid}.mp4", raw)
    png = wd / "clips_raw" / f"{sid}_overlay.png"
    overlay_png(shot.get("title"), shot.get("label"), png)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-i", str(png), "-filter_complex",
                    "[0]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2[v];[v][1]overlay=0:0,format=yuv420p",
                    "-an", "-c:v", "libx264", "-crf", "18", str(wd / "shots" / f"{sid}.mp4")], check=True)
    print(sid, "overlaid")
