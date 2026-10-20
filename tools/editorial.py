"""Editorial GitHub profile assets: text rendered as outlines, light + dark variants."""
import sys
from pathlib import Path
from html import escape
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

FONT_DIR, OUT = Path(sys.argv[1]), Path(sys.argv[2])
W = 1200
THEMES = {
    "light": dict(ink="#1B1F24", muted="#69707A", rule="#D5DAE0", accent="#2F55D4"),
    "dark":  dict(ink="#E8EAED", muted="#8B929C", rule="#30363D", accent="#8FA8FF"),
}
_fonts = {}

def font(weight):
    if weight not in _fonts:
        f = TTFont(FONT_DIR / f"IBMPlexSansKR-{weight}.ttf")
        _fonts[weight] = (f, f.getGlyphSet(), f.getBestCmap(), f["head"].unitsPerEm, f["hmtx"])
    return _fonts[weight]

def measure(text, weight, size, track=0):
    f, gs, cmap, upm, hmtx = font(weight)
    return sum(hmtx[cmap.get(ord(c), ".notdef")][0] for c in text) * size / upm + track * max(len(text) - 1, 0)

def text(t, x, y, weight, size, color, track=0, anchor="start"):
    f, gs, cmap, upm, hmtx = font(weight)
    if anchor == "end":
        x -= measure(t, weight, size, track)
    s = size / upm
    parts = []
    for c in t:
        name = cmap.get(ord(c))
        if name is None:
            raise SystemExit(f"missing glyph {c!r} in {weight}")
        pen = SVGPathPen(gs)
        gs[name].draw(pen)
        d = pen.getCommands()
        if d:
            parts.append(f'<path transform="translate({x:.2f} {y:.2f}) scale({s:.5f} {-s:.5f})" d="{d}"/>')
        x += hmtx[name][0] * s + track
    return f'<g fill="{color}">{"".join(parts)}</g>'

def wrap(t, weight, size, width):
    lines, cur = [], ""
    for word in t.split(" "):
        trial = f"{cur} {word}".strip()
        if cur and measure(trial, weight, size) > width:
            lines.append(cur); cur = word
        else:
            cur = trial
    return lines + [cur]

def svg(name, h, body, title):
    for theme, c in THEMES.items():
        inner = body(c)
        (OUT / f"{name}-{theme}.svg").write_text(
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img">'
            f'<title>{escape(title)}</title>{inner}</svg>\n', encoding="utf-8")

def rule(y, c):
    return f'<rect x="0" y="{y}" width="{W}" height="1.5" fill="{c["rule"]}"/>'

# Hero: the name is the one loud element; everything else stays quiet.
def hero(c):
    name_w = measure("김태용", "Light", 156, -6)
    out = [text("김태용", -6, 170, "Light", 156, c["ink"], -6),
           text("Kim Taeyong", name_w + 30, 170, "Regular", 26, c["muted"]),
           text("데이터를 이해하고, 모델로 실험하며,", 0, 262, "Regular", 36, c["ink"]),
           text("결과를 제품처럼 정리합니다.", 0, 312, "Regular", 36, c["ink"]),
           rule(368, c)]
    x = 0
    for s in ["Python", "PyTorch", "TensorFlow", "scikit-learn", "Pandas", "Jupyter"]:
        out.append(text(s, x, 412, "Regular", 22, c["muted"]))
        x += measure(s, "Regular", 22) + 40
    return "".join(out)

svg("hero", 430, hero, "김태용 Kim Taeyong — 데이터를 이해하고, 모델로 실험하며, 결과를 제품처럼 정리합니다. Python, PyTorch, TensorFlow, scikit-learn, Pandas, Jupyter")

# One linked row per project; rules separate rows (GitHub's heading underline already opens the list).
def row(name, title, tags, desc, last=False, desc_color="muted", accent_tail=None):
    lines = wrap(desc, "Regular", 23, 1000)
    h = 110 + 34 * (len(lines) - 1) + (0 if last else 22)
    def body(c):
        out = [text(title, 0, 62, "Medium", 34, c["ink"]),
               text(tags, W, 60, "Regular", 20, c["muted"], anchor="end")]
        for i, l in enumerate(lines):
            out.append(text(l, 0, 100 + 34 * i, "Regular", 23, c[desc_color]))
        if accent_tail:
            x = measure(lines[-1] + " ", "Regular", 23)
            out.append(text(accent_tail, x, 100 + 34 * (len(lines) - 1), "Medium", 23, c["accent"]))
        if not last:
            out.append(rule(h - 1.5, c))
        return "".join(out)
    svg(name, h, body, f"{title} — {desc}{' ' + accent_tail if accent_tail else ''}")

row("project-clearwrite", "Clearwrite", "Python   Desktop app",
    "원문·수정본·수정 이유를 한눈에. Codex·Claude CLI로 윤문하고 문체 점수와 실제 수정 비율을 확인하는 데스크톱 편집기.")
row("project-ship-paint", "Ship Paint Defect Classification", "Computer Vision",
    "선박 도장 결함 분류를 탐구하는 Computer Vision 프로젝트")
row("project-nids", "NIDS Competition", "Machine Learning",
    "네트워크 침입 탐지를 위한 머신러닝 분류 프로젝트")
row("project-seoul", "Seoul Commercial Analysis", "Data Analysis",
    "서울시 유동인구와 상권 매출을 연결한 창업 입지 분석", last=True)
row("kaggle", "Kaggriculture", "Kaggle   Bronze medal",
    "최종 10,148팀 중 557위,", last=True, desc_color="ink", accent_tail="약 상위 5.5%")

# A real sequence, so it reads left to right with arrows.
def flow(c):
    steps = ["Understand", "Build", "Validate", "Explain", "Improve"]
    size, gap = 40, 0
    words = sum(measure(s, "Light", size) for s in steps)
    arrow = measure("→", "Light", size)
    gap = (W - words - arrow * 4) / 8
    out, x = [], 0
    for i, s in enumerate(steps):
        out.append(text(s, x, 64, "Light", size, c["ink"]))
        x += measure(s, "Light", size) + gap
        if i < 4:
            out.append(text("→", x, 64, "Light", size, c["muted"]))
            x += arrow + gap
    return "".join(out)

svg("workflow", 90, flow, "Understand → Build → Validate → Explain → Improve")
print("done", sorted(p.name for p in OUT.glob("*-light.svg")))
