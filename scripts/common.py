import json, os, re, subprocess, time
from pathlib import Path
import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
CFG = yaml.safe_load(open(ROOT / "config/models.yaml"))


def run(cmd, **kw):
    print("+", " ".join(map(str, cmd)))
    return subprocess.run(list(map(str, cmd)), check=True, text=True, **kw)


def probe_duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "default=nw=1:nk=1", str(path)], capture_output=True, text=True)
    return float(out.stdout.strip())


def parse_script(path):
    """Return [{'id','tag','text'}] from '## p01 [tag]' blocks."""
    text = Path(path).read_text()
    blocks = re.split(r"^## ", text, flags=re.M)[1:]
    paras = []
    for b in blocks:
        head, _, body = b.partition("\n")
        m = re.match(r"(\S+)\s*(?:\[(.*?)\])?", head.strip())
        paras.append({"id": m.group(1), "tag": (m.group(2) or "").strip(), "text": body.strip()})
    return paras


def log_spend(workdir, record):
    record["ts"] = time.time()
    with open(Path(workdir) / "spend.jsonl", "a") as f:
        f.write(json.dumps(record) + "\n")


def shot_plan(shots, paras, timing, gap=0.4):
    """[(shot, duration, offset_in_paragraph)] in script order. A shot with `seconds` gets that fixed
    length; the paragraph's remaining time is split evenly among the other shots that cover it."""
    by_vo = {}
    for s in shots: by_vo.setdefault(s["vo"], []).append(s)
    plan = []
    for p in paras:
        group = by_vo.get(p["id"]) or [{"id": f"card_{p['id']}", "kind": "still", "vo": p["id"]}]
        total = timing[p["id"]] + gap
        fixed = sum(s.get("seconds", 0) for s in group)
        free = [s for s in group if not s.get("seconds")]
        each = (total - fixed) / len(free) if free else 0
        off = 0.0
        for s in group:
            d = s.get("seconds") or each
            plan.append((s, d, off)); off += d
    return plan
