"""Render a lighting plan (JSON, metres) as two perspective layout blockouts and check the frame.

Usage:
  python3 .claude/skills/lighting-diagram/scripts/blockout.py <plan.json> <out_dir>
Writes <out_dir>/<name>_layout_pov.png   - from the camera position, wider than the lens, the real lens frame dashed
       <out_dir>/<name>_layout_side.png  - elevated 3/4 overview with the camera's view wedge
and prints a FRAME CHECK: for every light, stand and prop, whether any part is inside the lens frame. Exit code 1
if something is in frame without an "in_frame_ok" reason (e.g. "hidden behind the couple", "retouched out").
It does not model occlusion: a reason is a claim the review must check in the real frame.

The blockouts are crude on purpose: they are layout references for scripts/diagram3d.py so the image model copies
positions and perspective instead of inventing them. Plan format: references/plan-format.md; worked plan: assets/example-plan.json.
Coordinates: x = right, z = away from the camera, y = up; the camera usually sits near (0, 0).
"""
import json, math, os, sys
from PIL import Image, ImageDraw, ImageFont

try:
    FONT = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 22)
except OSError:
    FONT = ImageFont.load_default()
PAPER = (245, 238, 222)
COLORS = {"orange": (255, 150, 50), "amber": (255, 180, 60), "blue": (80, 140, 255), "red": (240, 60, 60),
          "green": (70, 200, 90), "cyan": (60, 210, 230), "purple": (170, 90, 240), "white": (255, 245, 210)}
SENSOR = (36.0, 24.0)
NEAR = 0.1
TIGHT_DEG = 2.0   # less margin than this to the frame edge is reported as TIGHT
W, H = 1200, 1500


def sub(a, b): return [a[i] - b[i] for i in range(3)]
def add(a, b): return [a[i] + b[i] for i in range(3)]
def mul(a, s): return [c * s for c in a]
def dot(a, b): return sum(a[i] * b[i] for i in range(3))
def cross(a, b): return [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]]
def norm(a): l = math.sqrt(dot(a, a)) or 1.0; return [c / l for c in a]
def v3(p, h=0.0): return [p[0], h, p[1]] if len(p) == 2 else [p[0], p[2], p[1]]   # plan (x, z[, y]) -> (x, y, z)


class Cam:
    """Pinhole camera. eye/look are plan points (x, z, y)."""
    def __init__(self, eye, look, vfov):
        self.e, t = v3(eye), v3(look)
        self.f = norm(sub(t, self.e))
        self.r = norm(cross([0, 1, 0], self.f))
        self.u = cross(self.f, self.r)
        self.k = (H / 2) / math.tan(math.radians(vfov) / 2)

    def local(self, p):
        d = sub(p, self.e)
        return dot(d, self.r), dot(d, self.u), dot(d, self.f)

    def __call__(self, p):
        x, y, z = self.local(p)
        z = max(z, NEAR)
        return (W / 2 + self.k * x / z, H / 2 - self.k * y / z)

    def clip(self, pts):
        """Clip a 3D polygon (or segment) to the near plane before projecting, so geometry behind the eye
        (a light aimed back at the camera, a wall passing the camera) doesn't smear across the image."""
        loc = [(p, self.local(p)[2]) for p in pts]
        out = []
        n = len(loc) if len(loc) > 2 else 1
        for i in range(n):
            (a, za), (b, zb) = loc[i], loc[(i + 1) % len(loc)]
            if za >= NEAR:
                out.append(a)
            if (za >= NEAR) != (zb >= NEAR):
                t = (NEAR - za) / (zb - za)
                out.append(add(a, mul(sub(b, a), t)))
        if len(loc) == 2 and loc[1][1] >= NEAR:
            out.append(loc[1][0])
        return [self(p) for p in out]


PLACED = []


def poly(d, P, pts, **kw):
    q = P.clip(pts)
    if len(q) >= 3:
        d.polygon(q, **kw)


def dashed(d, a, b, fill="black", width=2, dash=14):
    n = max(1, int(math.dist(a, b) / dash))
    for i in range(0, n, 2):
        t0, t1 = i / n, min(1, (i + 1) / n)
        d.line([(a[0] + (b[0]-a[0])*t0, a[1] + (b[1]-a[1])*t0), (a[0] + (b[0]-a[0])*t1, a[1] + (b[1]-a[1])*t1)],
               fill=fill, width=width)


def label(d, xy, text, fill="black"):
    w = d.textlength(text, font=FONT)
    x = min(max(xy[0] + 8, 10), W - w - 10)
    y = min(max(xy[1] - 30, 10), H - 40)
    for _ in range(12):          # nudge down until it doesn't overlap a label already placed
        box = (x - 4, y - 2, x + w + 4, y + 26)
        if not any(box[0] < b[2] and b[0] < box[2] and box[1] < b[3] and b[1] < box[3] for b in PLACED):
            break
        y = min(y + 28, H - 40)
    PLACED.append((x - 4, y - 2, x + w + 4, y + 26))
    d.text((x, y), text, fill=fill, font=FONT)


def lens_half(cam):
    f = cam["focal_mm"]
    long_, short = SENSOR
    hw, hh = (short, long_) if cam.get("orientation", "portrait") == "portrait" else (long_, short)
    return hw / 2 / f, hh / 2 / f          # tan of half angles (horizontal, vertical)


def frame_check(plan):
    c = plan["camera"]
    cam = Cam([c["at"][0], c["at"][1], c["height"]], c["look"], 60)
    tx, ty = lens_half(c)
    report, bad = [], False

    def inside(p):
        x, y, z = cam.local(p)
        return z > 0 and abs(x / z) <= tx and abs(y / z) <= ty

    def past(p):
        """degrees outside the frame, and which edge (negative = inside)."""
        x, y, z = cam.local(p)
        if z <= 0:
            return 90.0, "behind the camera"
        hx = math.degrees(math.atan(abs(x) / z) - math.atan(tx))
        hy = math.degrees(math.atan(abs(y) / z) - math.atan(ty))
        edge = ("right" if x > 0 else "left") if hx >= hy else ("top" if y > 0 else "bottom")
        return max(hx, hy), edge

    def check(name, pts, must_hide, why=""):
        nonlocal bad
        hit = [p for p in pts if inside(p)]
        if hit:
            hmin = min(p[1] for p in hit)
            msg = f"IN FRAME (visible from {hmin:.1f} m up)" if must_hide else f"in frame (allowed{': ' + why if why else ''})"
            bad |= must_hide
        else:
            deg, edge = min(past(p) for p in pts)
            msg = f"outside: {deg:.1f} deg past the {edge} edge"
            if deg < TIGHT_DEG:
                msg += f"  TIGHT: under {TIGHT_DEG:.0f} deg, a small move or a wider crop puts it in frame"
        report.append(f"  {name:<28} {msg}")

    for L in plan.get("lights", []):
        x, z = L["at"]
        stand = [v3([x, z, L["height"] * s / 10]) for s in range(11)] + modifier_ring(L)
        check(L["label"], stand, not L.get("in_frame_ok"), L.get("in_frame_ok", ""))
    for p in plan.get("props", []):
        check(p["label"], [v3([*p["at"], p.get("height", 0.3) * s / 4]) for s in range(5)], not p.get("in_frame_ok"), p.get("in_frame_ok", ""))
    return report, bad


def draw_scene(d, P, plan):
    floor = plan.get("floor")
    if floor:
        poly(d, P, [v3(p) for p in floor], fill=(232, 226, 210), outline=(0, 0, 0))
    for wall in plan.get("walls", []):
        a, b, h = wall["from"], wall["to"], wall.get("height", 3.0)
        poly(d, P, [v3(a), v3(b), v3(b, h), v3(a, h)], fill=tuple(wall.get("fill", (215, 209, 193))), outline=(0, 0, 0))
        on = lambda t, y: P(v3([a[0] + (b[0]-a[0])*t, a[1] + (b[1]-a[1])*t], y))
        if wall.get("label"):
            label(d, on(wall.get("label_t", 0.15), wall.get("label_y", h - 0.3)), wall["label"])
        for f in wall.get("features", []):
            if f["type"] == "arch":
                c, w, sh = f["at"], f["width"] / 2 / math.dist(a, b), f.get("spring", 1.6)
                rise = f.get("rise", 0.85)
                pts = [on(c - w, 0), on(c - w, sh)] + [on(c - w*math.cos(k/20*math.pi), sh + rise*math.sin(k/20*math.pi)) for k in range(21)] + [on(c + w, 0)]
                d.polygon(pts, fill=(40, 40, 40))
            else:   # rect on the wall: t range along the wall, y range
                (t0, t1), (y0, y1) = f["t"], f["y"]
                q = [on(t0, y0), on(t1, y0), on(t1, y1), on(t0, y1)]
                d.polygon(q, fill=(20, 20, 20)) if f.get("filled") else d.polygon(q, outline=(70, 70, 150), width=3)
            if f.get("label"):
                label(d, on(f.get("at", sum(f.get("t", [0, 0])) / 2), f.get("label_y", 0.5)), f["label"])
    for bx in plan.get("boxes", []):          # steps, benches, cars: x range, z range, height
        (x0, x1), (z0, z1), h = bx["x"], bx["z"], bx["h"]
        poly(d, P, [v3([x0, z0], h), v3([x1, z0], h), v3([x1, z1], h), v3([x0, z1], h)], fill=(30, 30, 30, 220))
        poly(d, P, [v3([x0, z0]), v3([x1, z0]), v3([x1, z0], h), v3([x0, z0], h)], fill=(50, 50, 50, 220))
        if bx.get("label"):
            label(d, P(v3([(x0+x1)/2, z0], h)), bx["label"])


def light_axes(L):
    head = v3([L["at"][0], L["at"][1], L["height"]])
    aim = norm(sub(v3(L["aim"]), head))
    r1 = norm(cross(aim, [0, 1, 0])) if abs(aim[1]) < 0.99 else [1, 0, 0]
    return head, aim, r1, cross(r1, aim)


def modifier_ring(L):
    """3D outline of the modifier face (octa 8, umbrella 16, softbox 4 corners; bare = a 15 cm head)."""
    head, aim, r1, r2 = light_axes(L)
    n = {"octa": 8, "umbrella": 16, "softbox": 4}.get(L.get("modifier", "bare"), 4)
    R = L.get("size", 0.15) / 2
    return [add(head, add(mul(r1, R*math.cos(2*math.pi*k/n + math.pi/n)), mul(r2, R*math.sin(2*math.pi*k/n + math.pi/n)))) for k in range(n)]


def draw_light(d, P, L):
    col = COLORS.get(L.get("color", "white"), (255, 245, 210))
    x, z = L["at"]
    base = v3([x, z])
    head, aim, r1, r2 = light_axes(L)
    R = L.get("size", 0.15) / 2
    d.line(P.clip([base, head]), fill="black", width=4)
    for s in (-0.3, 0.3):
        d.line(P.clip([base, add(base, [s, 0, -0.2])]), fill="black", width=3)
    if L.get("modifier", "bare") in ("octa", "umbrella", "softbox"):
        poly(d, P, modifier_ring(L), fill=(255, 255, 255), outline=(0, 0, 0), width=3)
    else:
        hp = P(head)
        d.rectangle([hp[0]-12, hp[1]-10, hp[0]+12, hp[1]+10], fill=(15, 15, 15))
    seg = P.clip([head, v3(L["aim"])])
    if len(seg) < 2:
        label(d, P(add(head, [0, 0.35, 0])), L["label"]); return
    a, t = seg
    rad = max(10, math.dist(P(head), P(add(head, mul(r1, max(R, 0.08))))))
    dx, dy = t[0]-a[0], t[1]-a[1]; l = math.hypot(dx, dy) or 1; px, py = -dy/l, dx/l
    spread = L.get("spread", 0.35)
    rt = math.dist(t, P(add(v3(L["aim"]), [spread, 0, 0])))
    d.polygon([(a[0]+px*rad, a[1]+py*rad), (a[0]-px*rad, a[1]-py*rad), (t[0]-px*rt, t[1]-py*rt), (t[0]+px*rt, t[1]+py*rt)],
              fill=col + (110,))
    label(d, P(add(head, [0, 0.35, 0])), L["label"])


def draw_subject(d, P, s):
    x, z = s["at"]; h = s.get("height", 1.7)
    if s.get("pose") == "lie":
        a, b = P(v3([x - 0.8, z], 0.2)), P(v3([x + 0.8, z], 0.2))
        d.line([a, b], fill=(110, 110, 110), width=18)
        top = b
    else:
        b, t = P(v3([x, z])), P(v3([x, z], h - 0.2))
        d.line([b, t], fill=(110, 110, 110), width=max(8, int(abs(b[1]-t[1]) / 4)))
        hd = P(v3([x, z], h - 0.08)); r = max(10, abs(b[1]-t[1]) / 7)
        d.ellipse([hd[0]-r, hd[1]-r, hd[0]+r, hd[1]+r], fill=(110, 110, 110))
        top = b
    label(d, (top[0] - 80, top[1] + 40), s["label"])


def draw_haze(d, P, hz):
    """A soft cloud: stacked translucent rings, so the image model knows where the haze (and the rays) are."""
    x, z = hz["at"]; r = hz.get("radius", 1.0); top = hz.get("height", 2.0)
    for i in range(6):
        y = top * (i + 0.5) / 6; rr = r * (1 - 0.25 * abs(i - 2.5) / 2.5)
        ring = [v3([x + rr*math.cos(a/12*2*math.pi), z + rr*math.sin(a/12*2*math.pi)], y) for a in range(12)]
        poly(d, P, ring, fill=(150, 150, 160, 28))
    label(d, P(v3([x + r, z], top)), hz.get("label", "HAZE"))


def draw_prop(d, P, p):
    b, t = P(v3(p["at"])), P(v3(p["at"], p.get("height", 0.3)))
    d.rectangle([b[0]-7, t[1], b[0]+7, b[1]], fill=(15, 15, 15))
    label(d, (b[0] - 60, b[1] + 30), p["label"])


def render(plan, P, eye, out, frame=None, cam_drawn=False):
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im, "RGBA")
    PLACED.clear()
    draw_scene(d, P, plan)
    items = [(s["at"], draw_subject, s) for s in plan.get("subjects", [])]
    items += [(p["at"], draw_prop, p) for p in plan.get("props", [])]
    items += [(L["at"], draw_light, L) for L in plan.get("lights", [])]
    items += [(h["at"], draw_haze, h) for h in plan.get("haze", [])]
    e = v3(eye)
    items.sort(key=lambda it: -math.dist([it[0][0], it[0][1]], [e[0], e[2]]))   # far first
    for _, fn, obj in items:
        fn(d, P, obj)
    c = plan["camera"]
    if frame:
        x0, y0, x1, y1 = frame
        for a, b in [((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))]:
            dashed(d, a, b, width=4)
        label(d, (x0, y0 + 38), f"{c['focal_mm']}mm FRAME")
    if cam_drawn:
        cp3 = v3([c["at"][0], c["at"][1], c["height"]])
        cp = P(cp3)
        d.rectangle([cp[0]-30, cp[1]-18, cp[0]+30, cp[1]+18], fill=(15, 15, 15))
        d.text((cp[0] + 40, cp[1] - 10), f"CAMERA {c['height']} m up, {c['focal_mm']} mm", fill="black", font=FONT)
        look = v3(c["look"]); dist = math.dist(cp3, look)
        cc = Cam([c["at"][0], c["at"][1], c["height"]], c["look"], 60)
        tx, ty = lens_half(c)
        for sx in (-1, 1):
            for sy in (-1, 1):
                ray = add(cc.f, add(mul(cc.r, sx*tx), mul(cc.u, sy*ty)))
                end = P.clip([cp3, add(cp3, mul(ray, dist * 1.3))])
                if len(end) == 2:
                    dashed(d, *end)
    im.save(out)


def main(plan_path, out_dir):
    plan = json.load(open(plan_path))
    name = plan.get("name", os.path.splitext(os.path.basename(plan_path))[0])
    os.makedirs(out_dir, exist_ok=True)
    c = plan["camera"]
    eye = [c["at"][0], c["at"][1], c["height"]]
    vfov = plan.get("pov_vfov", 80)          # wider than the lens so the lights outside the frame show
    P = Cam(eye, c["look"], vfov)
    tx, ty = lens_half(c)
    fw, fh = P.k * tx, P.k * ty
    pov = os.path.join(out_dir, f"{name}_layout_pov.png")
    render(plan, P, eye, pov, frame=(W/2 - fw, H/2 - fh, W/2 + fw, H/2 + fh))
    sv = plan.get("side_view", {})
    look = c["look"]
    # default: above and a little left of the camera axis, high enough to see over side walls (alleys, corridors)
    side_eye = sv.get("eye", [look[0] - 2.0, look[1] - 7.5, 6.0])
    S = Cam(side_eye, sv.get("look", [look[0] + 0.5, look[1] - 1.0, 1.0]), sv.get("vfov", 60))
    side = os.path.join(out_dir, f"{name}_layout_side.png")
    render(plan, S, side_eye, side, cam_drawn=True)
    report, bad = frame_check(plan)
    print(pov); print(side)
    print(f"FRAME CHECK ({c['focal_mm']} mm {c.get('orientation', 'portrait')}):")
    print("\n".join(report))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(*sys.argv[1:])
