"""Correct ASR misspellings in out/<slug>_final.ass/.srt against the script, then re-burn the captions.

    python scripts/fix_captions.py scale-1-payers [...]
Fixes are whole-word, case-sensitive; edit FIXES when a new mishearing shows up.
"""
import re, subprocess, sys
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "out"
COMMON = {"pairs": "payers", "pair": "payer", "e -bit -dar": "EBITDA", "e-bit-dar": "EBITDA"}
FIXES = {
    "scale-1-payers": {"AISSO": "ERISA", "MAX": "MACs", "Senior Owns": "Cigna owns", "Etna": "Aetna", "Elevent": "Elevance",
                       "Centine": "Centene", "rule makings": "rulemakings"},
    "scale-2-providers": {"Xperity": "Experity", "care sense physicians": "care sends physicians"},
    "scale-3-money": {"prior orth": "prior auth", "ACO reaches": "ACO REACH,"},
    "scale-4-news": {"ACMS rule": "A CMS rule", "in appropriate": "inappropriate", "reprising company": "repricing company",
                     "Claritiv": "Claritev", "MHPAA": "MHPAEA", "Multiplan": "MultiPlan"},
    "scale-5-morning": {"Council": "Counsel", "Cardio Vascular": "Cardiovascular", "Asmansson": "Osmundson", "UNIO": "Unio",
                        "Andrew Mints": "Andrew Mintz", "United Dermatology Partners": "United Derm Partners",
                        "Cussrow": "Kusserow", "Women's Health Care": "Women's Healthcare", "like there's deal": "like theirs deal"},
}


def fix(slug):
    table = {**COMMON, **FIXES.get(slug, {})}
    for ext in ("ass", "srt"):
        p = OUT / f"{slug}_final.{ext}"
        s = p.read_text(encoding="utf-8")
        for a, b in table.items():
            # the .ass file wraps each word in karaoke tags, so allow tags between the words of a phrase
            parts = [re.escape(w) for w in a.split(" ")]
            pat = r"(?<![\w-])" + r"(\s*(?:\{[^}]*\})?\s*)".join(parts) + r"(?![\w-])"
            s = re.sub(pat, lambda m: b if len(parts) == 1 else _rejoin(m, b, len(parts)), s)
        p.write_text(s, encoding="utf-8")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{slug}_final.mp4", "-vf", f"ass={slug}_final.ass",
                    "-c:a", "copy", f"{slug}_captioned.mp4"], cwd=OUT, check=True)
    print(slug, "re-burned")


def _rejoin(m, replacement, n):
    """Keep the karaoke tags between words, swapping only the words themselves."""
    seps = [m.group(i) for i in range(1, n)]
    words = replacement.split(" ")
    if len(words) != n:
        return replacement
    return "".join(w + (seps[i] if i < len(seps) else "") for i, w in enumerate(words))


if __name__ == "__main__":
    for slug in sys.argv[1:]:
        fix(slug)
