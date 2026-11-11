# Diagram prompt template (one file per view)

`scripts/diagram3d.py` adds the style text, the style refs and a list naming each attached image. Your prompt
file only describes **this view**. Write it in English, even when the board is in Hebrew: the image model spells
English labels far more reliably.

Both views (POV and overview) share the same OBJECTS and LABELS blocks word for word, so the two images can't
disagree. Copy them between the files; change only VIEW and STRICT.

```
VIEW: <CAMERA POV | OVERVIEW>. <POV: "Drawn from just behind the camera, which is <on the ground / at eye level>,
looking <up/level/down>, exactly like the layout blockout. Draw the dashed rectangle as a clean thin dashed
rectangle labelled '<45>mm FRAME', so it is clear every light stands OUTSIDE it."
| OVERVIEW: "From above and to the front-<left/right>, looking down about 35 degrees, exactly like the layout
blockout. The camera is small, seen from behind, with two thin dashed lines on the floor showing its field of
view (every stand outside these lines), labelled 'CAMERA VIEW'.">

PLACE: <the real geometry in plain words: which wall is where, corners, steps, railings, doors, what the
background is made of. Name only what is really there.>

PEOPLE: <exact pose copied from the photo: who kneels/stands/sits, which knee is down, where each hand is,
where the head points, what touches the ground>.

OBJECTS (all standing on the floor):
- KEY = <unit> in <modifier with size> <+ gel> on a <tall/short> stand <where, relative to the subject and the
  camera>, head at <h> m, tilted <deg> down, pointing at <exactly what>; <colour> translucent beam from the
  <modifier face> ENDING on <what it lights>.
- RIM / FILL / BACKGROUND = ... (same pattern)
- HAZE = <fogger> on the ground <where>, haze rising <where>; rays only where a light passes through it.
- CAMERA = <where, height>, drawn from behind, lens pointing <into the scene / up at them>.

STRICT: <the 2-4 things the model got wrong last time or is most likely to: "both lights are on the RIGHT side",
"the speedlight AND its whole stand are right of the frame edge", "he is NOT standing", "the fogger has no cable">.

LABELS (exact text; bold uppercase heading + regular lines; thin dashed arrow to each object; each label ONCE):
"KEY LIGHT" / "<unit, exactly as in references/gear.md>" / "<modifier + gel>" / "<where · height · angle>"
"RIM LIGHT" / "<unit>" / "<modifier + gel or WB effect>" / "<where · height · aim>"
"SMOKE MACHINE" / "<fogger model>" / "<where · puff timing>" / "<condition>"
"CAMERA & LENS:" / "<body> · <lens> @ <mm>" / "ISO <> · f/<> · 1/<> · WB <>K" / "<where · height · tilt>"
Spell every label exactly. Exactly <N> lights. No other text.
```

Worked plan: `assets/example-plan.json` (a courtyard corner, octa key, bare rim, fogger hidden behind the subject, low camera).

## Edit files (`--edit`)
List only the changes, numbered, each with its target and its end state, and end with "No other changes."
```
1. Redraw the couple, same place and size, in EXACTLY the pose of the attached photo crop: <pose>.
2. Change the lines under "SMOKE MACHINE" to exactly: "<...>".
No other changes.
```
Pass `--photo <crop of the real frame>` when fixing a pose: text alone did not fix the knees.
