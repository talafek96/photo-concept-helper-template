---
name: lighting-diagram
description: Plan and draw the photographer's lighting diagrams - a physically honest light plan with their real gear (references/gear.md) rendered as two 3D illustrated diagrams (camera POV with the real lens frame + elevated overview), built from one metric 3D plan and a layout blockout so positions are exact, then checked against the frame and the real location. Use for every flash, gel or haze concept and every recreated reference image; whenever the photographer asks "how do I light this", "where do the lights go", "show me the setup", "lighting diagram / light plan"; and whenever they say a light, shadow, backlight or beam doesn't make sense or the diagram and photo disagree - even if they don't say "diagram".
---

# Lighting diagram

The photographer will stand in the real place with these exact lights and copy the diagram. A diagram that looks
right but puts a stand in the air, in frame, or on the wrong side wastes the shoot. The standard is: **one metric
plan per frame, rendered precisely, checked against reality.**

Why it is this strict: the first diagrams were vague chapter-level sketches. One put a rim light "behind her" on a
bridge where behind her was a railing and air ("HOW AM I SUPPOSED TO PUT THE LIGHT BEHIND HER? IN THE AIR?"),
others weren't tied to any frame, and AI frames showed red shadows on a white wall.

Style: `references/diagram-style/` (the photographer's chosen look; the default is cream paper, ink line-art in
perspective, realistic grey gear, translucent coloured beams, bold uppercase labels with dashed arrows).
Gear: `references/gear.md` only.

## Deliverables per lit frame
1. **The light plan in words**, in the concept's light section and under the frame on the board.
2. **POV diagram**: from the camera position, with the real lens frame dashed, so it's obvious what's in frame
   and that every light stands outside it.
3. **Overview diagram**: elevated 3/4, about 35° down, so front/behind and distances read at a glance (a single
   eye-level view once hid that the backlight was behind the subject).
4. **The AI photo of that frame**, matching both diagrams.

One plan, one named frame: the diagrams sit under the frame they light (`frames[n]["light"]` +
`frames[n]["light_text"]` in board.json), never as a vague chapter-level image.

## Workflow

### 1. Read the light you must reproduce
If there is a reference (painting, mood image), read its light first: where highlights sit, which way shadows
fall, colour of key vs rim, rays and haze, **and the camera height** (a painting lit from above, upper right and
seen from the ground got both wrong in the first plan). Without a reference, decide what the background does
(stays black, glows, carries a shadow) and design toward that.

### 2. Map the real ground in metres
From the real, dated location photos (not the AI frame): walls, corners, steps, railings, doors, and where
nothing can stand (air past a railing, water, drops, traffic). x = right, z = away from the camera, y = up,
camera near (0, 0). Estimate sizes from known objects (door ≈ 2.1 m, step ≈ 15-18 cm, paving tiles).
**Every feature in the plan must be visible in the real photos.** A plan once invented a "side opening" for the
fogger that the real alley didn't have.

### 3. Write the plan as JSON and run the blockout
Copy `assets/example-plan.json` to `shoots/<id>/board/plans/<slug>.json` and edit it (format:
`references/plan-format.md`).
```bash
python3 .claude/skills/lighting-diagram/scripts/blockout.py shoots/<id>/board/plans/<slug>.json shoots/<id>/board/plans
```
It writes `<name>_layout_pov.png` and `<name>_layout_side.png` and prints a **FRAME CHECK**: each stand and prop
in frame or how far outside. It exits 1 if anything is in frame without an `"in_frame_ok"` reason. Fix the plan
until it passes, then **look at both blockouts**: the image model will copy them.

Physics while you edit (every rule here was broken on a delivered board):
- No beams without haze. Haze needs a still, enclosed or sheltered space: say honestly when a place is open at
  both ends and the smoke will blow away.
- A small flash can't light or colour a building 15 m away in daylight.
- No boom means no light from directly above (a tall stand in front, tilted down, is the honest version).
- A gel colours what it HITS; the shadow is where that colour is MISSING (red flash → red wall, dark shadow; never
  a red shadow on a white wall). Shadows attach at the feet.

### 4. Generate the photo (if the frame needs one)
Text plus the real location photos only (`generate-storyboard`). **Never attach a diagram or blockout to the photo
generation**: it mirrored the pose and invented architecture. In the concept's `look`, describe the light's
EFFECT from "an unseen source outside the frame", never gear names: image models draw a named strobe, octa or
LED panel into the shot.

### 5. Draw the two diagrams
One prompt file per view, from `references/prompt-template.md`. Keep the OBJECTS and LABELS blocks identical in
both, so they can't disagree. Labels are precise (unit, modifier, gel, height, angle; body, lens @ mm,
ISO/f/shutter/WB, camera distance and height) and in English.
```bash
python3 scripts/diagram3d.py shoots/<id>/boards/<slug>/diagram_pov.png shoots/<id>/board/plans/<slug>_diagram_pov.txt \
    --layout shoots/<id>/board/plans/<slug>_layout_pov.png --photo shoots/<id>/boards/<slug>/NN.png \
    --loc shoots/<id>/locations/<real>.jpg [--gear references/gear-photos/<item>.jpg] [--provider openrouter]
# same for diagram_side.png with <slug>_layout_side.png
```
If the geometry is wrong (a light on the wrong side, a beam over their heads, a wrong wall), fix the plan or
prompt and **regenerate fresh**: edits keep a bad draft's geometry (that happened three times in a row). Once
the geometry is right, fix small things with `--edit <draft.png>` (pass a crop of the real frame as `--photo`
for a pose; text alone didn't fix the knees). Delete failed versions.

### 6. Review, then an independent check
Go through `references/review-checklist.md` with **all images of the frame side by side**. Then a fresh
general-purpose agent with a skeptical gaffer brief gets the plan JSON, the blockouts, both diagrams, the photo
and the real location photos (not your conclusions), and returns PASS/FIX with numbers. Fix every FIX before the
photographer sees it. Report what changed, never just "fixed"; name any residual flaw you left.

### 7. Commit
Commit the plan JSON and prompt files (`shoot <name>: ...`). Generated images (blockouts, diagrams) stay
gitignored. New lessons go to `PITFALLS.md` / `memory/`.

## When the image providers are down
`diagram3d.py` uses `gen.py`: Google → OpenRouter (same Nano Banana Pro, no Google daily limit) → fal. If all
fail, say which one needs what (spend cap at ai.studio/spend, daily limit reset, top-up). Meanwhile show the two
blockouts (precise if plain), or the flat SVG (`references/flat-svg.md`).

## Files
- `scripts/blockout.py`: plan JSON → POV and overview blockouts + the frame check.
- `assets/example-plan.json`: a complete real plan (courtyard corner, octa key, bare rim, fogger, low camera).
- `references/plan-format.md`, `prompt-template.md`, `review-checklist.md`, `flat-svg.md`.
- `scripts/diagram3d.py` (repo root): the style renderer; `references/diagram-style/`, `references/gear-photos/`.
