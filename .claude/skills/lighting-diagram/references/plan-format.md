# Plan JSON format (`scripts/blockout.py`)

Units are metres; x = right, z = away from the camera, y = up. Floor points are `[x, z]`, and 3D points are
`[x, z, y]`. A complete real plan is in `assets/example-plan.json`.

| Key | Fields | Notes |
|---|---|---|
| `name` | string | output prefix: `<name>_layout_pov.png`, `<name>_layout_side.png` |
| `floor` | `[[x, z], ...]` | walkable ground polygon. Leave no-go areas (water, air past a railing) out of it |
| `walls[]` | `from`, `to` `[x, z]`; `height`; `fill` [r,g,b]; `label`; `label_t` (0-1 along the wall); `label_y` (m) | one entry per flat wall face |
| `walls[].features[]` | arch: `type:"arch"`, `at` (0-1 along the wall), `width`, `spring` (m), `rise` (m) · rect: `t` [t0,t1], `y` [y0,y1], `filled` · both: `label`, `label_y` | doors, arches, mosaics, windows, plinths |
| `boxes[]` | `x` [x0,x1], `z` [z0,z1], `h`, `label` | steps, benches, cars, a bed |
| `subjects[]` | `at`, `height` (top of head), `pose` stand/kneel/lie, `label` | |
| `props[]` | `at`, `height`, `label`, `in_frame_ok` | fogger, chair, fan |
| `haze[]` | `at`, `radius`, `height`, `label` | where the cloud will be: beams/rays only exist inside it |
| `lights[]` | `at`, `height` (head), `modifier` octa/umbrella/softbox/bare, `size` (m, modifier diameter), `aim` [x,z,y], `color` (orange, amber, blue, red, green, cyan, purple, white), `spread` (beam half-width at the target, m), `label`, `in_frame_ok` | the label names the unit, modifier, gel and height |
| `camera` | `at`, `height`, `look` [x,z,y], `focal_mm`, `orientation` portrait/landscape, `settings` | `look` = the point at the centre of the frame |
| `pov_vfov` | degrees, default 80 | widen it if a light falls outside the POV blockout |
| `side_view` | `eye` [x,z,y], `look` [x,z,y], `vfov` | overview camera. The default sits about 7.5 m behind and 6 m above the subject, slightly left. Set it by hand for a clear read: look down at 35-45°, from the side where no wall blocks the view. In an alley or corridor, put the eye above the centre line. |

`in_frame_ok` takes a reason, e.g. `"hidden behind his back"` or `"retouched out"`. Without one, the frame check
fails (exit 1) when any part of the stand, head or modifier is inside the lens frame. The check has no occlusion
model, so the review must confirm the reason in the real frame. A margin under 2° is flagged TIGHT: at 6 m that
is about 20 cm, less than a stand leg's spread.
