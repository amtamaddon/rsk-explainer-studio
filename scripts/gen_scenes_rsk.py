"""Generate the style-C scene stills for work/rsk-explainer-v2 (character sheet + style frame A as references)."""
import subprocess, sys
from concurrent.futures import ThreadPoolExecutor

WD = "work/rsk-explainer-v2"
REFS = [f"{WD}/keyframes/s00_character_sheet.png", f"{WD}/style/A_flat_illustration.png"]
STYLE = ("Flat vector illustration matching the reference images exactly: the same outline weight, the same simple faces, flat fills "
         "and minimal shading, and the characters exactly as drawn on the character sheet. Bright whites and warm light neutrals "
         "(cream, light sand, soft warm gray), lighter and warmer than the references. Navy and orange appear only as tiny accents on "
         "screens or small objects, never on walls, furniture or clothing. Paper documents show only blank gray lines, never letters. "
         "No text, no logos, no labels anywhere. The administrator always wears her glasses. No cartoon effects such as sigh puffs or "
         "motion marks. Monitors obey real geometry: a screen is visible only from the side it faces. 16:9 widescreen.")
SCENES = {
    "s01": "Wide shot of a busy neighborhood urgent care front desk in the morning. The administrator (woman in her 40s, shoulder-length "
           "brown hair, glasses, beige cardigan) stands behind the front desk checking in a patient at the counter while holding a desk "
           "phone receiver to her ear, the phone cord running behind the monitor, never in front of it. The monitor faces the administrator only: its screen points toward her, and the patient at the counter and the viewer see only the plain gray back of the monitor and its stand, with no screen visible from their side. The patient at the counter looks "
           "clearly different from the administrator: a younger man with short curly black hair in a dark green zip-up jacket; on the desk a monitor, a keyboard and a stack of paper EOB statements. A small waiting area with two "
           "seated patients, and the nurse in light-teal scrubs walking past an exam room door. Window daylight.",
    "s04": "Medium shot of the RSK team member (man in his 30s, short dark hair, headset with microphone, light-blue shirt) seated at a "
           "workstation, seen from the side so his focused face is clearly visible in profile. His monitor is turned three-quarters toward "
           "him: we see the screen at an angle, showing simple abstract table rows with one row outlined in orange, and the screen faces "
           "him, not the viewer. Bright open office with a window and plants. He and the monitor fill the left two-thirds of the frame; "
           "keep the right third as clean empty wall for a data card added later.",
    "s10": "Medium shot of the RSK team member (man in his 30s, short dark hair, headset, light-blue shirt) at his desk presenting on a "
           "video call. His large monitor shows a screen share: a neat stack of simple claim cards on the left and a plain logo-free "
           "video window with a generic blank avatar on the right. He gestures toward the screen, calm and confident. The room matches his workstation office: a window with daylight on the left wall and a potted plant beside the desk. Nobody else in the room.",
    "s11": "A single frame split vertically into two equal vignettes in the same style, separated by a thin white gap. Left: a neighborhood "
           "urgent care front desk and a small waiting area. Right: a calm behavioral health therapy office with two armchairs facing "
           "each other, a side table with a plant and a tissue box, soft daylight from a window. No people.",
    "s13": "Over-the-shoulder medium shot from behind and slightly to the right of the administrator (woman in her 40s, shoulder-length "
           "brown hair, glasses, beige cardigan) seated at the front desk. We see her shoulder and a three-quarter profile of her face, "
           "eyes open, glasses on, with a slight relieved smile. Her monitor faces her and therefore also faces the viewer; its screen "
           "is a plain light blank panel. A closed file folder rests flat on the desk beside the keyboard. Beyond the desk on the left, "
           "a calm waiting room with one patient reading.",
}


def gen(sid):
    cmd = [sys.executable, "scripts/openrouter.py", "image", "--workdir", WD, "--out", f"{WD}/keyframes/{sid}.png",
           "--prompt", f"{SCENES[sid]} {STYLE}"]
    for r in REFS:
        cmd += ["--ref", r]
    p = subprocess.run(cmd, capture_output=True, text=True)
    return sid, "ok" if p.returncode == 0 else "FAILED " + (p.stderr.strip().splitlines() or [""])[-1]


if __name__ == "__main__":
    ids = sys.argv[1:] or list(SCENES)
    with ThreadPoolExecutor(5) as ex:
        for sid, status in ex.map(gen, ids):
            print(sid, status)
