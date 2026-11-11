---
name: lighting-diagram
description: Draw a physically honest top-down lighting diagram (inline SVG, theme-aware) for a concept using the photographer's actual gear - lights, gels, modifiers, angles, distances, walls, flags, haze, camera and lens settings. Use for every flash/gel/haze concept on a board, and whenever the photographer says the light doesn't make sense or asks how to light something.
---

# Lighting diagram

Origin: on an earlier black-studio concept the photographer said: "the light composition doesn't make sense
for that one, so add a light diagram image and take the wall into account." The AI frames had light patches on
a wall with no source.

## Think it through first (in words, in the concept's light section)
- Where is the background (wall/sky/hallway) and how far behind her? Should it stay black, glow, or carry a
  shadow? Decide, then place lights so that happens (flags, grids, distance falloff).
- Each light: unit (by name, from `references/gear.md`), gel, modifier (grid, softbox, bare), height, angle, power role
  (key / rim / kicker / fill / background), what it must NOT hit.
- Ambient: daylight/blue hour/practicals and the shutter speed that keeps them. Haze: beams only exist
  where there is haze and a light pointing through it.
- Camera: lens (from `gear.md`), aperture, shutter, sync (rear-curtain for motion), position.
- The AI frames must agree with this. If they don't, regenerate them or change the plan.

## Draw it
```python
import sys; sys.path.insert(0, "scripts")
from diagram import svg, person, camera, wall, dist, AMBER, RED, BLUE
s = svg({"aria": "Lighting diagram: <title>",
         "beams": [(150, 285, 310, 215, AMBER, 16)],
         "extra": [wall(40, "Black wall", "stays black: no light hits it"), dist(560, 50, 560, 210, "~3 m", 585, 135),
                   person(310, 210, "<model>"), camera(310, 390, "70-200 · f/4 · 1/200", "Camera")],
         "lights": [(150, 285, 310, 210, AMBER, "Strobe · amber gel", "key · grid · 45°", -10, 40)]})
```
Examples: `python3 scripts/diagram.py` renders three worked plans (black-studio key + rim, single red gel with a
wall shadow, blue hallway backlight) to `scratch/diag_preview.html`. Labels in the board language (the examples
are in English; translate every label, including the `camera()` title). Put the SVG string in the chapter's `"diagram"` in `board.json`.
Check it renders in light and dark (it uses `var(--ink)`, `var(--muted)`, `var(--surface)`).
