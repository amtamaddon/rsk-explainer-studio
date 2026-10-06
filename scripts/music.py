"""ElevenLabs music bed."""
import argparse, os
from pathlib import Path
import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

ap = argparse.ArgumentParser()
ap.add_argument("--prompt", required=True); ap.add_argument("--seconds", type=float, required=True); ap.add_argument("--out", required=True)
a = ap.parse_args()
Path(a.out).parent.mkdir(parents=True, exist_ok=True)
if not os.environ.get("ELEVENLABS_API_KEY"):
    # STAND-IN: no key, so synthesize a sparse ambient pad locally (slow chord drones, soft noise). Replace with ElevenLabs.
    import numpy as np, subprocess
    print("WARNING: ELEVENLABS_API_KEY not set. Synthesizing a local ambient pad instead.")
    sr, n = 48000, int(a.seconds * 48000); t = np.arange(n) / sr; y = np.zeros(n)
    chords = [[220, 261.6, 329.6, 392], [174.6, 220, 261.6, 329.6], [196, 246.9, 293.7, 349.2], [164.8, 196, 246.9, 329.6]]
    seg = 12.0
    for i in range(int(np.ceil(a.seconds / seg))):
        s0, s1 = int(i * seg * sr), min(n, int((i + 1) * seg * sr)); tt = t[s0:s1] - t[s0]
        env = np.minimum(1, tt / 3.0) * np.minimum(1, (tt[-1] - tt) / 3.0 + 0.02)
        for f in chords[i % 4]:
            for det in (-1.5, 0, 1.5):
                y[s0:s1] += 0.08 * env * np.sin(2 * np.pi * (f + det * 0.3) * tt + np.random.rand() * 6) * (1 + 0.15 * np.sin(2 * np.pi * 0.11 * tt))
    y += 0.01 * np.convolve(np.random.randn(n), np.ones(400) / 400, "same")
    y *= 0.5 / np.max(np.abs(y))
    raw = str(Path(a.out).with_suffix(".f32"))
    y.astype(np.float32).tofile(raw)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "f32le", "-ar", str(sr), "-ac", "1", "-i", raw,
                    "-af", "lowpass=f=1800,afade=t=in:d=3,afade=t=out:st=%f:d=4" % max(0, a.seconds - 4), "-b:a", "160k", a.out], check=True)
    os.remove(raw); print("wrote", a.out, "(local stand-in)"); raise SystemExit
r = requests.post("https://api.elevenlabs.io/v1/music",
                  headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"]},
                  json={"prompt": a.prompt, "music_length_ms": int(a.seconds * 1000)}, timeout=600)
r.raise_for_status()
Path(a.out).parent.mkdir(parents=True, exist_ok=True)
Path(a.out).write_bytes(r.content)
print("wrote", a.out)
