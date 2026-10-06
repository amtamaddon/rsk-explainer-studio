"""Search YouTube, keep only Creative Commons videos, download, log attribution."""
import argparse
from pathlib import Path
import yt_dlp

ap = argparse.ArgumentParser()
ap.add_argument("query"); ap.add_argument("--max", type=int, default=15); ap.add_argument("--out", required=True); ap.add_argument("--keep", type=int, default=3)
a = ap.parse_args()
out = Path(a.out); out.mkdir(parents=True, exist_ok=True)

with yt_dlp.YoutubeDL({"quiet": True, "skip_download": True}) as y:
    res = y.extract_info(f"ytsearch{a.max}:{a.query}", download=False)

cc = [e for e in res["entries"] if e and "creative commons" in (e.get("license") or "").lower()]
print(f"{len(cc)} of {len(res['entries'])} results are Creative Commons")
opts = {"outtmpl": str(out / "%(id)s.%(ext)s"), "format": "bv*[height<=1080]+ba/b[height<=1080]",
        "merge_output_format": "mp4", "quiet": True}
with yt_dlp.YoutubeDL(opts) as y, open(out / "LICENSES.md", "a") as log:
    for e in cc[: a.keep]:
        y.download([e["webpage_url"]])
        log.write(f"- {e['id']}.mp4: \"{e['title']}\" by {e.get('uploader')} ({e['webpage_url']}), {e['license']}\n")
        print("got", e["id"], e["title"])
