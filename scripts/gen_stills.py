"""Generate the still for every `generated` shot in a work dir's shots.yaml (skips ones that already exist).
    python scripts/gen_stills.py work/<slug> "<style suffix>"
"""
import subprocess, sys
from pathlib import Path
import yaml
wd, style = Path(sys.argv[1]), sys.argv[2]
for s in yaml.safe_load(open(wd / "shots.yaml", encoding="utf-8")):
    if s.get("kind") != "generated": continue
    out = wd / "keyframes" / f"{s['id']}.png"
    if out.exists(): continue
    r = subprocess.run([sys.executable, "scripts/openrouter.py", "image", "--prompt", f"{s['prompt']}. {style}", "--out", str(out), "--workdir", str(wd)],
                       capture_output=True, text=True)
    print(s["id"], "ok" if r.returncode == 0 else "FAILED: " + (r.stderr.strip().splitlines() or [""])[-1])
