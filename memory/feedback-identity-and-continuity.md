---
name: feedback-identity-and-continuity
description: "Every frame must look like the actual model (face, hair, tattoo placement) in what she owns, same set; storyboards on Nano Banana Pro, never silently on a weaker model; explicit shot sizes"
metadata:
  type: feedback
  origin: template-default
  modified: 2026-11-12
---
Same face, hair (style too), build; tattoos in the **exact placement** (identity.txt says "only here, nowhere
else"); same wardrobe, props and prop count unless the story changes them. Outfits come from what she owns, or
the board lists them as to buy. Review every frame full size (sheet + singles) before the photographer sees
it; regenerate drift, wrong skylines, fake signage/lettering, generic rooms instead of the real place.
**Model:** storyboards = Nano Banana Pro (Google, or the same model via OpenRouter when Google's daily limit is
spent). fal Seedream is visibly less coherent ("which model did you use? the coherence is significantly
lower"): never run whole concepts on it silently. Use `gen.py --strict`; if only fal works, say so first.
Give every frame an explicit shot size (wide / medium / tight close-up) or Nano Banana copies the anchor frame.
**Why:** frames drifted on face, outfit and hair; a foreign skyline over the real city; fal moved thigh tattoos
onto belly, arms and calves and invented clothes she doesn't own.
**How to apply:** `generate-storyboard` review step every time; owned items as `loc_refs`.
