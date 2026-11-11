---
name: develop-concepts
description: The creative core - design original, continuous-story photo concepts (one real location, 6-10 causally linked frames, styling, light with the photographer's gear, signature shots) tailored to the model's personality and range, and write each as concept JSON ready for storyboards. Use for any request for concepts, ideas, themes or directions - "give me 10 concepts", "more ideas", "bolder / spicier / softer / cheaper", "with gels", "street" - and when remaking a concept the photographer didn't like.
---

# Develop concepts

Read first: `shoots/<id>/brief.md`, `models/<name>/profile.md`, `memory/user-photographer.md`,
`references/creative-principles.md`, `references/gear.md`, `references/seasonality-<region>.md`,
`references/<region>-locations.md` (region from `user-photographer.md`), the shoot's `notes.md` (what was
already proposed/rejected), and the injected memory rules.

## Two formats: pick by what the photographer wants
- **Image-first (default for striking portfolio work; `memory/feedback-image-first-concepts.md`):** an
  interesting real place + ONE killer image that works without a caption, ~5 frames around it, at most one
  twist; boldness the way the photographer defined it; light physics written into `look`. This is what landed
  after five rejected boards of clever stories.
- **Short film (6-10 causally linked frames, steps 1-3 below):** when they ask for a story-driven series.
Taste misses twice in a row → stop guessing: ask what they mean, with concrete options, before a 3rd try, and
save the answer to memory.

## Process
0. **Outdoor / no-space brief → location-first.** Run `scout-locations` for a long list (~20) of places with
   character, pick ~10, then write the story each place suggests (steps 1-7 per place).
1. **Mine for roots.** List 15-20 raw seeds before choosing: real folktales, poems, sayings, crafts, foods,
   childhood rituals, slang, art forms, the meaning of her name, things from her Instagram/WhatsApp, the
   references she sent, what's in season, what's lying around the shoot area. Discard the clichés.
2. **Pick the strongest 3-5** that are genuinely different from each other (and from `notes.md`).
   For "more ideas" requests, default to a spread: one poetic, one bold, one cheap-in-a-room, one
   public location, unless the photographer specified ("bold", "cheap", "gels", "street").
3. **Shape each as a short film:** inciting event → decision → consequence → development → climax →
   ending. Write the 6-10 frames so each one visibly follows from the last. Kill the concept if the middle
   frames are interchangeable poses.
4. **Ground it:** a real location type you can actually find (or a known place from
   `<region>-locations.md`); in-season props; one outfit; what we bring vs what's there; cost; permits.
   Then run **`scout-locations`** for the specific place.
5. **Light it** with the photographer's kit (`gear.md`: every light they own, a gel colour, haze where legal).
   Every lit frame gets a plan on real ground (`lighting-diagram`). Write the physics into `look` as effects
   from unseen sources: what each light hits, the colour of the shadow, where haze is. Haze needs a still,
   sheltered space; say honestly when a place is open and the smoke will blow away.
6. **Boring test** (`references/creative-principles.md`): one-line hook with want + turn + payoff for each.
   Kill: no turn; "she does her hobby somewhere pretty"; a genre she already posts a lot; anything needing a
   venue, rig or rental the photographer doesn't have (pole, studio, room) unless they asked. Replace killed
   ideas; list them in `notes.md` so they never come back. Also kill anything that needs set dressing or props
   they'd have to hunt down: use the location as found. Her statement pieces are not banned; use them.
   The most eye-catching concepts lead the board.
7. **Self-critique pass** before generating: Does the story read from images alone? One location? Is she
   doing something, not posing? Would it stop a scroll? Is anything fake about the place? In season? Could the
   team's known vetoes (brief, `user-photographer.md`) kill it? Is it cheaper than it needs to be? Fix, then
   write the JSON.

## Concept JSON
`shoots/<id>/concepts/<slug>.json`. Schema and a full worked example: `templates/concepts/example.json`
(a free public location, direct flash + one gel, 8 causally linked frames). `scripts/gen.py` reads these keys:
```json
{"slug": "...", "title": "Night Swim (a title in another language gets a translation)", "model": "<folder under models/>",
 "tag": "soft | editorial | bold | spicy",
 "premise": "root + our version, the whole arc in 3-4 sentences",
 "setting": "the REAL place as it looks today, every frame",
 "wardrobe": "one outfit, layers spelled out (sheer over opaque)",
 "look": "photographic technique, grain, palette, lens feel",
 "frames": ["establishing...", "SIGNATURE ...", "..."],
 "loc_refs": ["shoots/<id>/locations/<place>/03.jpg"], "provider": "google", "aspect": "3:2"}
```
Required: slug, title, model, premise, setting, wardrobe, look, frames. Optional: tag (for the board),
loc_refs, provider (`google` | `fal` | `openrouter`), aspect (`3:2` default, `2:3`, `1:1`).
Also keep for the board: translation of the title, logline, root (quote + explanation),
per-frame title/action/camera, styling, props (there vs bring), light, logistics, signature frames.

## Bold, spicy, cheap, gels: the default meanings (the photographer's own words override them)
- **The range is set by the model**, from `profile.md` → Range, and capped by the photographer's limits
  (`user-photographer.md` → Boldness). A model who already publishes boudoir can get spicy concepts; a model
  who doesn't gets bold-but-dressed ones. When the photographer asks for "all the options", spread the set
  across a scale and tag each concept: **soft · editorial · bold · spicy**.
- **Bold** = expressions, attitude, fashion with more skin (latex, harness, bodice, slip, body paint, bare
  legs/shoulders), hard light, confrontational eye contact. Not stunts (no haircut).
- **Spicy** = lingerie, boudoir, wet-look, swimwear, sheets and mirrors, sensual poses and gaze. Still a
  story, still coherent and tasteful. No nudity, no explicit acts: the board is shared and the frames are
  of a real person.
- Don't write "bold outfits"/"spicy" as a selling line on the board; the images say it.
- **Cheap/easy** = one room or a free public spot, market props, ≤1 assistant, no rentals beyond a night.
- **Gels** = one colour per concept when asked for gel ideas; the colour should mean something in the story.

## Then
Generate (`generate-storyboard`), review, add to the board (`publish-board`), and append the concepts with
status to `shoots/<id>/notes.md`. Commit.
