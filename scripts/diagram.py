"""Top-down lighting diagrams as inline SVG (theme-aware: uses the board's --ink/--muted/--surface vars).

The photographer asked for these after a concept's light made no physical sense: every concept with flash/gels gets one,
and it must respect the real space - walls, distances, where spill lands, what the haze shows.

Library use (write a small spec per concept, then paste the SVG into board.json "diagram"):
    from diagram import svg, person, camera, wall, dist, AMBER, RED, BLUE
    s = svg({"aria": "...", "beams": [(x, y, tx, ty, COLOR, spread)], "extra": [wall(...), person(...), camera(...)],
             "lights": [(x, y, tx, ty, COLOR, "Strobe · amber gel", "role · modifier · angle", label_dx, label_dy)]})
Canvas 620x440, camera at the bottom, background wall at the top. Write every label in the board language
(person() and camera() take their label/title as arguments). Light names come from references/gear.md.
Run this file directly to render three worked examples to scratch/diag_preview.html.
"""
import math, json, sys

def beam(x, y, tx, ty, color, spread=18, length=None):
    a = math.atan2(ty - y, tx - x)
    L = length or math.hypot(tx - x, ty - y) + 20
    s = math.radians(spread)
    p1 = (x + L * math.cos(a - s), y + L * math.sin(a - s))
    p2 = (x + L * math.cos(a + s), y + L * math.sin(a + s))
    return f'<path d="M{x},{y} L{p1[0]:.0f},{p1[1]:.0f} L{p2[0]:.0f},{p2[1]:.0f} Z" fill="{color}" fill-opacity="0.22"/>'

def light(x, y, tx, ty, color, label, sub, lx=0, ly=0):
    a = math.degrees(math.atan2(ty - y, tx - x))
    return (f'<g transform="translate({x},{y}) rotate({a:.0f})"><rect x="-14" y="-10" width="22" height="20" rx="3" fill="{color}" stroke="var(--ink)" stroke-width="1.5"/>'
            f'<rect x="8" y="-13" width="5" height="26" fill="var(--ink)"/></g>'
            f'<text x="{x+lx}" y="{y+ly}" class="dl">{label}</text><text x="{x+lx}" y="{y+ly+16}" class="ds">{sub}</text>')

def svg(spec):
    W, H = 620, 440
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{spec["aria"]}" xmlns="http://www.w3.org/2000/svg" class="diagram">',
           '<style>.dl{font:700 14px Assistant,Arial,sans-serif;fill:var(--ink);text-anchor:middle}.ds{font:400 12px Assistant,Arial,sans-serif;fill:var(--muted);text-anchor:middle}.dm{stroke:var(--muted);stroke-width:1;stroke-dasharray:4 4;fill:none}</style>']
    for b in spec.get("beams", []):
        out.append(beam(*b))
    for el in spec.get("extra", []):
        out.append(el)
    for l in spec["lights"]:
        out.append(light(*l))
    out.append('</svg>')
    return "".join(out)

def person(x, y, label="Model"):
    return (f'<circle cx="{x}" cy="{y}" r="16" fill="var(--surface)" stroke="var(--ink)" stroke-width="2"/>'
            f'<circle cx="{x}" cy="{y-6}" r="5" fill="var(--ink)"/><text x="{x}" y="{y+36}" class="dl">{label}</text>')

def camera(x, y, sub, title="Camera"):
    return (f'<rect x="{x-16}" y="{y-11}" width="32" height="22" rx="4" fill="var(--ink)"/><rect x="{x-7}" y="{y-21}" width="14" height="11" fill="var(--ink)"/>'
            f'<text x="{x}" y="{y+30}" class="dl">{title}</text><text x="{x}" y="{y+46}" class="ds">{sub}</text>')

def wall(y, label, sub, color="var(--ink)"):
    return (f'<rect x="40" y="{y-10}" width="540" height="14" fill="{color}"/><text x="310" y="{y-18}" class="dl">{label}</text>'
            f'<text x="310" y="{y+24}" class="ds">{sub}</text>')

def dist(x1, y1, x2, y2, label, tx, ty):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="dm"/><text x="{tx}" y="{ty}" class="ds">{label}</text>'

AMBER = "#E3A23B"; RED = "#D23A3A"; BLUE = "#4B8FD6"

def examples():
    D = {}
    # Black-studio lacquer look: gridded key, flag keeps the wall black, rim from behind
    D["studio"] = svg({"aria": "Lighting diagram: black studio, amber key + rim",
      "beams": [(150, 285, 310, 215, AMBER, 16), (470, 130, 325, 205, AMBER, 9)],
      "extra": [wall(40, "Black wall", "stays fully black: no light reaches it"),
                '<rect x="186" y="150" width="8" height="70" fill="var(--ink)" transform="rotate(-35 190 185)"/><text x="232" y="138" class="ds">black flag: blocks spill on the wall</text>',
                dist(560, 50, 560, 210, "~3 m", 585, 135), person(310, 210, "Model on a stool"), camera(310, 390, "70-200 · f/4 · 1/200")],
      "lights": [(150, 285, 310, 210, AMBER, "Strobe · amber gel", "key · grid · 45° left, high", -10, 40),
                 (470, 130, 310, 210, AMBER, "Speedlight · amber gel", "rim from behind-right", 30, -28)]})
    # Single red gel: one hard light throws her giant shadow on a concrete wall; fan for wind, low haze
    D["redwall"] = svg({"aria": "Lighting diagram: single red gel, shadow on a concrete wall",
      "beams": [(470, 300, 300, 215, RED, 20, 330)],
      "extra": [wall(40, "Concrete wall", "her giant shadow falls on it, left", "var(--muted)"),
                '<ellipse cx="190" cy="80" rx="70" ry="16" fill="var(--ink)" fill-opacity="0.18"/><text x="190" y="110" class="ds">shadow on the wall</text>',
                '<circle cx="110" cy="230" r="18" fill="none" stroke="var(--ink)" stroke-width="2"/><path d="M128,230 l60,-6 M128,236 l58,4 M128,224 l56,-14" stroke="var(--muted)" stroke-width="1.5"/><text x="110" y="268" class="dl">Fan / blower</text><text x="110" y="284" class="ds">wind from the left</text>',
                '<rect x="370" y="150" width="30" height="18" rx="3" fill="var(--muted)"/><text x="385" y="140" class="ds">low smoke machine: dust</text>',
                dist(560, 50, 560, 210, "~4 m", 585, 135), person(300, 215), camera(300, 395, "28mm · low · 1/250")],
      "lights": [(470, 300, 300, 215, RED, "Strobe · red gel", "single · hard · high right", 20, 42)]})
    # Blue hallway: backlight from the end of a corridor, weak fill by the camera
    D["hallway"] = svg({"aria": "Lighting diagram: blue backlight down a hallway",
      "beams": [(310, 70, 310, 380, BLUE, 14, 330), (380, 360, 315, 230, BLUE, 12)],
      "extra": ['<rect x="230" y="40" width="10" height="370" fill="var(--ink)"/><rect x="380" y="40" width="10" height="370" fill="var(--ink)"/><text x="190" y="225" class="ds">hallway wall</text><text x="440" y="225" class="ds">hallway wall</text>',
                '<g fill="var(--surface)" stroke="var(--muted)" stroke-width="1"><ellipse cx="290" cy="160" rx="6" ry="3"/><ellipse cx="330" cy="130" rx="6" ry="3"/><ellipse cx="300" cy="110" rx="6" ry="3"/><ellipse cx="320" cy="180" rx="6" ry="3"/></g><text x="310" y="98" class="ds">trail of feathers</text>',
                person(310, 230), camera(310, 400, "50mm · f/2.8 · 1/250")],
      "lights": [(310, 70, 310, 230, BLUE, "Strobe · blue gel", "backlight from the hallway end · feathers glow", 0, -12),
                 (380, 360, 310, 230, BLUE, "Speedlight · blue gel", "weak fill near the camera", 70, 10)]})
    return D


if __name__ == "__main__":
    import os
    os.makedirs("scratch", exist_ok=True)
    D = examples()
    open("scratch/diag_preview.html", "w").write("<style>:root{--ink:#1A1E1B;--muted:#5B635C;--surface:#F7F8F5}body{background:#ECEEE9}</style>" + "".join(f"<div style='width:620px'>{v}</div>" for v in D.values()))
    print("scratch/diag_preview.html")
