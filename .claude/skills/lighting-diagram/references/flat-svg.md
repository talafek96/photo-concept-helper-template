# Flat SVG diagram (fallback only)

Use it when no image provider works (all three failed at once in Nov 2026), or as a small inline diagram in the
HTML board next to the 3D image. It is a top-down plan, so it shows ground and no-go zones well but not heights.

```python
import sys; sys.path.insert(0, "scripts")
from diagram import svg, person, camera, wall, dist, zone, ground, line, AMBER, RED, BLUE
s = svg({"aria": "Lighting diagram: <title>",
         "beams": [(150, 285, 310, 215, AMBER, 16)],
         "extra": [wall(40, "Black wall", "stays black: no light hits it"), dist(560, 50, 560, 210, "~3 m", 585, 135),
                   zone(440, 60, 160, 120, "Air past the railing", "nothing can stand here"),
                   person(310, 210, "<model>"), camera(310, 390, "70-200 · f/4 · 1/200", "Camera")],
         "lights": [(150, 285, 310, 210, AMBER, "Strobe · amber gel", "key · grid · 45°", -10, 40)]})
```
- `zone()` draws where nothing can stand (air past a railing, water, drops, traffic); `ground()` the walkable area.
- Examples: `python3 scripts/diagram.py` renders three worked plans to `scratch/diag_preview.html`.
- Labels in the board language. Put the SVG + text rows on the frame it lights (`frames[n]["light"]`,
  `frames[n]["light_text"]` = [[heading, text], ...]).
- Render with headless Chrome to check labels don't collide or clip (RTL: anchor labels middle, not end), in light
  and dark (it uses `var(--ink)`, `var(--muted)`, `var(--surface)`).
