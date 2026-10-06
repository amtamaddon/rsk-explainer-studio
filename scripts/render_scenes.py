"""Render every manim shot in work/<slug>/shots.yaml from work/<slug>/scenes/scenes.py into shots/<id>.mp4.

    python scripts/render_scenes.py work/<slug> [s02 s03 ...]
"""
import shutil, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import yaml

wd = Path(sys.argv[1]).resolve()
only = set(sys.argv[2:])
ids = [s["id"] for s in yaml.safe_load(open(wd / "shots.yaml")) if s.get("kind") == "manim" and (not only or s["id"] in only)]
(wd / "shots").mkdir(exist_ok=True)


def render(sid):
    media = wd / "media" / sid
    r = subprocess.run(["manim", "-qh", "--fps", "30", "--disable_caching", "--media_dir", str(media), "-o", f"{sid}.mp4",
                        str(wd / "scenes/scenes.py"), sid.upper()], capture_output=True, text=True)
    (wd / f"log_{sid}.txt").write_text(r.stdout + r.stderr)
    if r.returncode:
        return f"{sid} FAILED (see log_{sid}.txt): {r.stderr.strip().splitlines()[-1] if r.stderr.strip() else ''}"
    out = next(media.rglob(f"{sid}.mp4"))
    shutil.copy(out, wd / "shots" / f"{sid}.mp4")
    return f"{sid} ok"


with ThreadPoolExecutor(4) as ex:
    for line in ex.map(render, ids):
        print(line)
