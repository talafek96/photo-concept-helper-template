---
name: study-model
description: Learn who a model is before designing for her - her look (face, hair, tattoos, piercings, build), her style and genres, her personality and what she likes shooting - from her Instagram (posts, highlights, DMs), the WhatsApp chat and photos she sent, then write models/<name>/profile.md, identity.txt and 5-6 identity reference photos. Use for every new model or Instagram handle the photographer mentions, when refs are missing, when "it doesn't look like her", or when the photographer says "understand her style / personality".
---

# Study the model

Every later step leans on this: concepts are built around her personality, and the AI storyboards only
look like her if the refs and identity text are right. Spend the time here.

Output: `models/<name>/profile.md`, `identity.txt`, `refs/01_face.jpg ...` (5-6 photos). Raw material in
`models/<name>/ig/` and `wa/` (gitignored).

## 1. Gather
- **Instagram** → `read-instagram` skill: posts (enough to go past her latest phase - if the last month
  is one trip or one theme, go further back), highlights, and the DM thread with the photographer.
- **Chats** → `read-chats` skill, **every source the photographer named** (WhatsApp AND Instagram DMs: one
  doesn't replace the other; the real details often sit in WhatsApp) for the window they name; photos she
  sent of things she owns, references, voice notes. No WhatsApp MCP set up → say so and ask them to paste or
  export what matters.
- Photos the photographer drops into the conversation.

## 2. Look, properly
Open the contact sheet, then the strongest 10-15 posts full size. Write down:
- **Look:** face shape, eyes, brows, lips, skin tone, freckles/marks, hair (colour, length, styles she
  repeats), tattoos (where, what, colours), piercings, build, height feel.
- **Style:** genres she shoots (street, boudoir, cosplay, fitness, fine art...), palettes, light (flash,
  natural, gels), makeup, wardrobe she repeats, poses and expressions she's good at.
- **Personality:** captions, how she talks in the chat, what she's proud of, humour, energy (calm /
  playful / fierce). This decides which stories suit her.
- **Range:** soft ↔ spicy content she already publishes (incl. paid platforms if the photographer mentions them):
  this sets the boldness range the concepts may use. It's her existing range, not a target to exceed.
- **Signals:** which posts got the most likes/comments; what she says she wants to try.
- **Her references** (things she sent): technique, composition, palette, styling, mood, props.

## 3. Identity refs
Pick 5-6 sharp, varied, recent photos where it's clearly her and alone: frontal face, close-up, 3/4 or
profile, full body, each tattooed area. Crop out other people. Save as `refs/01_face.jpg`... (jpg ≤2000px).
Recent matters: hair and tattoos change, and the generator copies what it sees.

## 4. Write
- `identity.txt` (template `templates/model/identity.txt`): one paragraph describing face, hair, skin, marks,
  piercings, tattoos, build; "keep her exact face; not a generic model".
- `profile.md` (template `templates/model/profile.md`): look · style · personality · range · what she owns
  (with photo files) · her references · facts to ASK rather than invent (heritage, comfort level).
- **Likeness test:** one portrait frame with `scripts/gen.py` from a throwaway concept. If it isn't her,
  change refs/identity before any storyboard work - fixing likeness later costs every frame twice.

Commit `profile.md` + `identity.txt` (`model <name>: profile`). Photos stay local.
