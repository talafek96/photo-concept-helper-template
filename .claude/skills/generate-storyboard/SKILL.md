---
name: generate-storyboard
description: Generate AI storyboard frames for a concept with the real model's likeness (Nano Banana Pro; fal.ai Seedream with the safety checker off for spicy/bold content Google refuses; OpenRouter last), then review every frame for identity drift, continuity and fake architecture and regenerate what's wrong. Use whenever concepts need images, the photographer says "show me", "remake frame N", "this doesn't look like her", or a board needs visuals.
---

# Generate the storyboard

Playbook with providers, keys, identity rules and known refusals: `references/image-generation.md`. Read it.

## Run
```bash
python3 scripts/gen.py shoots/<id>/concepts/<slug>.json                  # frame 1 (anchor) then the rest, 4 in parallel
python3 scripts/gen.py shoots/<id>/concepts/<slug>.json 3,5 --force      # redo frames 3 and 5
python3 scripts/gen.py shoots/<id>/concepts/<slug>.json --strict         # Nano Banana Pro only, fail instead of falling back
python3 scripts/gen.py shoots/<id>/concepts/<slug>.json --provider openrouter --strict  # same model, no Google daily limit
python3 scripts/gen.py shoots/<id>/concepts/<slug>.json --provider fal   # last resort: weaker coherence, say so first
```
Each frame gets `NN.png.src` naming the provider that made it; check it before showing frames (`cat
boards/<slug>/*.src`). The chain is Google → OpenRouter (same model) → fal, and a fallback prints `!! fell back`.
Google limits: a monthly **spend cap** (raise at https://ai.studio/spend, on the key's project) and a separate
**daily request limit** (Tier 1: 250 image requests/day per model, failed calls count; resets next day). Read
the 429 text to tell them apart, then switch to `--provider openrouter`. Run frames of one concept at a time
when the quota is tight.
Several concepts → at most **2 Google concepts at a time** (each already runs 4 frames in parallel; 8 concepts at once hit the Gemini quota and fell through to fal, which rejected the refs). Queue the rest sequentially in one background job; fal concepts can run alongside.
Spicy/boudoir/swimwear concepts: try Nano Banana Pro first (lingerie as outerwear usually passes); on a
refusal, soften the wording of that frame (a front view, "walks toward the camera", no "from behind") before
moving to fal. fal Seedream is visibly less coherent (the photographer noticed at once): never run whole
concepts on it without saying so. On fal, describe light effects only: it draws named gear (strobe, octa, LED
panel) into the shot even with "no stands in frame".
Prereq: `models/<name>/refs/` has photos (else run `study-model`).

## Review (mandatory before the photographer sees anything)
1. `python3 scripts/sheet.py shoots/<id>/boards/<slug>` and read the sheet.
2. Open every frame full size. Check:
   - **Face**: is it her (eyes, brows, freckles, septum ring, hair, tattoos)? Wide shots and profiles drift.
   - **Continuity**: same outfit, hair (style too: updo vs loose), props **and prop count** (one suitcase
     stays one), room/street, colour grade as frame 1. Outfits only change where the concept says so,
     and only into items she owns or the concept specifies.
   - **Real place, not a generic room**: an interior that is a real rental/venue must come from its listing
     photos as `loc_refs`; a generic white bedroom is a failure even if pretty.
   - **Tattoos**: same shape/size **and placement** every frame (fal moves them onto belly/hips/arms); models invent letters or glyphs, so describe abstract
     tattoos as "abstract brush strokes, no letters".
   - **Tattoos on the right body part, not on clothes**: they vanish under skirts/overalls (fal painted them onto yellow overalls; Google put them on knees below a pencil skirt and on the backs of legs in shots from behind). Say where they are hidden in the wardrobe text.
   - **One person**: no duplicated model in a frame.
   - **Forced perspective**: the far object stays far and small; models tend to move it next to her.
   - **Owned garment details**: two-piece stays two-piece, etc.
   - **Place**: matches the real location (no fake signs, foreign/exotic decor, wrong skyline, extra towers/arches).
   - **Story**: does the frame show its action clearly? Would someone get the sequence without text?
   - **Season & light**: props in season; light matches the plan/diagram (no light patches that have no source).
   - **Light physics** ("the shadows and the lights here make absolutely no sense"): find every source;
     highlights and shadows point away from it; a gel colours what it HITS and the shadow is where that colour
     is MISSING (never a red shadow on a white wall); shadows attach at the feet; no sunbeams through a solid
     ceiling; no lighting gear visible in frame.
   - **Set as found**: props and set pieces exactly as in the real photos (a few stacked tables, not a
     mountain of debris; thin fabric drapes, not a net). Describe them literally in `setting`.
   - **Composition variety**: every frame has its own shot size (wide / medium / tight close-up) written in
     its text; otherwise frames copy the anchor's composition.
   - **Anatomy & taste**: hands, limbs; nothing revealing.
   - **Independent check:** after your own pass, a fresh agent audits identity and light physics of every
     frame (frames + location photos, not your conclusions).
3. Regenerate failures: tighten that frame's text (closer framing, "face clearly visible, facing camera",
   restate the outfit) or fix frame 1 and redo all. Two failed tries on Google refusal → `--provider fal`.
4. Only then present: show the sheet (and key frames) in chat or go straight to `publish-board`.
Never say a frame is "good" or "fixed" as a verdict; say what changed and show it. Taste is the photographer's call.

## Web copies
`python3 scripts/sheet.py shoots/<id>/boards/<slug> --web shoots/<id>/board/img <slug>` (1600px, q82).
