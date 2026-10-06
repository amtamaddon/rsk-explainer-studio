"""Shared Manim kit for diagram shots. A scene subclasses Shot, sets SID, and writes build(),
calling self.cue("phrase") to wait until that phrase is spoken in the shot's paragraph.

    manim -qh --fps 30 work/<slug>/scenes/scenes.py S02    (or: python scripts/render_scenes.py work/<slug>)
"""
import json, sys
from pathlib import Path
import yaml
from manim import *

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import parse_script, shot_plan

BG, ACCENT, INK, DIM, PANEL, LINE, GOOD = "#0E1116", "#E07A1F", "#E6E9EF", "#8A93A6", "#161B24", "#2A3040", "#5FB49C"
FONT = "Segoe UI"
TOP, FLOOR = 3.5, -2.45     # keep content above FLOOR: burned-in captions sit below it


def T(s, size=30, color=INK, weight=NORMAL, **kw):
    return Text(s, font=FONT, font_size=size, color=color, weight=weight, **kw)


def card(label, w=2.6, h=1.2, color=INK, size=26, fill=PANEL, sub=None):
    txt = T(label, size, color, line_spacing=0.8)
    if sub:
        txt = VGroup(txt, T(sub, size - 8, DIM, line_spacing=0.8)).arrange(DOWN, buff=0.12)
    box = RoundedRectangle(corner_radius=0.14, width=max(w, txt.width + 0.4), height=max(h, txt.height + 0.3),
                           stroke_color=color, stroke_width=3, fill_color=fill, fill_opacity=1)
    return VGroup(box, txt.move_to(box))


def arrow(a, b, color=DIM):
    return Arrow(a.get_right(), b.get_left(), buff=0.1, color=color, stroke_width=3, max_tip_length_to_length_ratio=0.2)


def heading(s):
    return T(s, 30, DIM).to_corner(UL, buff=0.5)


def table(rows, widths, size=24, header_color=DIM, row_h=0.62):
    """rows[0] is the header. Returns VGroup of row VGroups (each a VGroup of cells)."""
    out = VGroup()
    for r, row in enumerate(rows):
        cells = VGroup()
        x = 0
        for c, val in enumerate(row):
            t = T(str(val), size, header_color if r == 0 else INK, weight=BOLD if r == 0 else NORMAL)
            t.move_to([x + 0.15 + t.width / 2, -r * row_h, 0]); cells.add(t)
            x += widths[c]
        out.add(cells)
    rules = VGroup(*[Line([0, -(r + 0.5) * row_h, 0], [sum(widths), -(r + 0.5) * row_h, 0], color=LINE, stroke_width=1.5) for r in range(len(rows) - 1)])
    g = VGroup(out, rules)
    g.rows = out
    return g


class Shot(Scene):
    SID = None

    def setup(self):
        wd = Path(sys.modules[self.__class__.__module__].__file__).resolve().parent.parent
        shots = yaml.safe_load(open(wd / "shots.yaml"))
        paras = {p["id"]: p for p in parse_script(wd / "script.md")}
        timing = json.loads((wd / "vo/timing.json").read_text())
        for s, d, off in shot_plan(shots, list(paras.values()), timing):
            if s["id"] == self.SID:
                self.D, self.off, self.para = d, off, paras[s["vo"]]["text"]
                self.speech = timing[s["vo"]]
        self.camera.background_color = BG

    def now(self):
        return self.renderer.time

    def cue(self, phrase, lead=0.25):
        """Wait until `phrase` is spoken (estimated from its position in the paragraph)."""
        i = self.para.find(phrase)
        if i < 0:
            raise ValueError(f"{self.SID}: cue phrase not in paragraph: {phrase!r}")
        t = i / len(self.para) * self.speech - self.off - lead
        if t > self.now() + 0.05:
            self.wait(t - self.now())

    def construct(self):
        self.build()
        rest = self.D - self.now() - 0.6
        if rest > 0.05:
            self.wait(rest)
        if self.mobjects:
            self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.5)
        if self.D - self.now() > 0.04:
            self.wait(self.D - self.now())

    def build(self):
        raise NotImplementedError


def acro(abbr, expansion, color=ACCENT, w=None):
    """An acronym chip: the letters large, the expansion beneath."""
    a = T(abbr, 40, color, weight=BOLD)
    e = T(expansion, 22, DIM)
    g = VGroup(a, e).arrange(DOWN, buff=0.12)
    box = RoundedRectangle(corner_radius=0.14, width=max(w or 0, g.width + 0.5, 2.2), height=g.height + 0.4,
                           stroke_color=color, stroke_width=2.5, fill_color=PANEL, fill_opacity=1)
    return VGroup(box, g.move_to(box))
