"""OpenRouter client: model list, image keyframes, image-to-video.

Image generation uses the chat completions endpoint with modalities ["image","text"].
Video generation endpoints on OpenRouter are newer; on first run Claude Code should
check https://openrouter.ai/docs and adjust video() if the route or payload differs.
"""
import argparse, base64, json, os, sys, time
from pathlib import Path
import requests
from common import CFG, log_spend

BASE = CFG["openrouter"]["base_url"]
HDR = {"Authorization": f"Bearer {os.environ.get('OPENROUTER_API_KEY','')}",
       "Content-Type": "application/json"}


def data_url(path):
    mime = "image/png" if str(path).endswith(".png") else "image/jpeg"
    return f"data:{mime};base64," + base64.b64encode(Path(path).read_bytes()).decode()


def models():
    r = requests.get(f"{BASE}/models", headers=HDR, timeout=60); r.raise_for_status()
    for m in r.json()["data"]:
        mods = m.get("architecture", {}).get("output_modalities", [])
        if any(x in mods for x in ("image", "video", "audio")):
            print(m["id"], mods)


def image(prompt, refs, out, workdir="."):
    content = [{"type": "text", "text": prompt + "\nAspect ratio 16:9. Match the reference images' style and subjects exactly."}]
    content += [{"type": "image_url", "image_url": {"url": data_url(r)}} for r in refs]
    body = {"model": CFG["openrouter"]["keyframe_image"], "modalities": ["image", "text"],
            "messages": [{"role": "user", "content": content}]}
    r = requests.post(f"{BASE}/chat/completions", headers=HDR, json=body, timeout=300); r.raise_for_status()
    j = r.json()
    imgs = j["choices"][0]["message"].get("images") or []
    if not imgs:
        sys.exit("No image returned: " + json.dumps(j)[:500])
    b64 = imgs[0]["image_url"]["url"].split(",", 1)[1]
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_bytes(base64.b64decode(b64))
    log_spend(workdir, {"kind": "image", "model": body["model"], "out": out, "usage": j.get("usage")})
    print("wrote", out)


def video(model_key, img, prompt, out, seconds=6, workdir="."):
    model = CFG["openrouter"][model_key]
    res = "720p" if "seedance-2.5" in model else "1080p"   # seedance 2.5 tops out at 720p
    body = {"model": model, "prompt": prompt, "duration": seconds, "resolution": res, "aspect_ratio": "16:9",
            "generate_audio": False,   # no generated sound in our videos
            "frame_images": [{"type": "image_url", "image_url": {"url": data_url(img)}, "frame_type": "first_frame"}]}
    r = requests.post(f"{BASE}/videos", headers=HDR, json=body, timeout=120); r.raise_for_status()
    job = r.json()
    jid = job.get("id")
    print("job:", jid)   # printed first so a failed download can be retried without paying again
    while job.get("status") not in ("completed", "succeeded", "failed"):
        time.sleep(10)
        job = requests.get(f"{BASE}/videos/{jid}", headers=HDR, timeout=60).json()
        print("status:", job.get("status"))
    if job.get("status") == "failed":
        sys.exit("Video failed: " + json.dumps(job)[:500])
    download(job, out)
    log_spend(workdir, {"kind": "video", "model": model, "out": out, "job": jid, "cost": (job.get("usage") or {}).get("cost")})
    print("wrote", out, "cost", (job.get("usage") or {}).get("cost"))


def download(job, out):
    url = (job.get("unsigned_urls") or [None])[0] or f"{BASE}/videos/{job['id']}/content?index=0"
    hdr = HDR if url.startswith("https://openrouter.ai/api/") else None
    resp = requests.get(url, headers=hdr, timeout=300); resp.raise_for_status()
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_bytes(resp.content)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("models")
    a = sub.add_parser("image"); a.add_argument("--prompt", required=True); a.add_argument("--ref", action="append", default=[]); a.add_argument("--out", required=True); a.add_argument("--workdir", default=".")
    v = sub.add_parser("video"); v.add_argument("--model-key", default="video_default"); v.add_argument("--image", required=True); v.add_argument("--prompt", required=True); v.add_argument("--seconds", type=int, default=6); v.add_argument("--out", required=True); v.add_argument("--workdir", default=".")
    x = ap.parse_args()
    if x.cmd == "models": models()
    elif x.cmd == "image": image(x.prompt, x.ref, x.out, x.workdir)
    else: video(x.model_key, x.image, x.prompt, x.out, x.seconds, x.workdir)
