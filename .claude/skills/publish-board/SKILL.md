---
name: publish-board
description: Build and publish the shoot board the photographer shares with the producer and model - a claude.ai artifact in the board language (RTL or LTR) with one chapter per concept (storyboard, real location photos with credits, map links, styling, light, logistics) plus overview and shoot-day plan. Use when concepts are ready to show, when the photographer wants "an artifact / a board / something to send her", to add/remove/fix chapters, or to open a new board when one is full.
---

# Publish the board

## Rules (default lessons from earlier boards; the photographer's own corrections override them)
- **It's shared** with the producer and the model. No questions to the photographer, no "TBD", no notes-to-self, no
  "Questions for <model>" section, nothing unfinished. Uncertainties become production notes with an
  action ("check with the farm the week before"), never questions.
- **Language:** the board language from the brief, else `memory/user-photographer.md`. Set `lang` and `dir`
  in `board.json`; `build_board.py` has built-in UI strings for `he` and `en` and takes a `strings` override
  for any other language (see its docstring). English terms only where natural (gear names, "blue hour",
  "rim"); don't force them. Concept titles may be in the heritage language with a translation.
- **Label everything:** real photos carry the "real photo" tag + author + licence + year; AI frames carry the
  "AI sketch" tag (`real_tag` / `ai_tag`, translated to the board language).
  Never present AI scenery as a real place or invent a map.
- Don't write "bold outfits" or explain that something is bold; just show it.
- **Styling says whose it is.** Every garment/prop is either hers (from `profile.md` → What she owns) or
  listed under "to buy/borrow" with a price. Never let an AI frame's invented outfit imply she owns it.
- Map links on every location (`scripts/places.py pin`).
- Keep the approved design (`templates/board/board.css`): treatment-book layout (RTL or LTR), chapter accents in light
  and dark, contact strip + lightbox. Don't redesign without being asked.
- A board that gets long → open a new board (new artifact), link the old one in the intro.

## Build
1. Web images: per concept `python3 scripts/sheet.py shoots/<id>/boards/<slug> --web shoots/<id>/board/img <slug>`;
   real photos copied/resized to `shoots/<id>/board/img/ref-<place>-NN.jpg` (≤1600px).
2. Write/extend `shoots/<id>/board/board.json` (schema in the `scripts/build_board.py` docstring; a worked
   chapter: `templates/board/example-board.json`, built from `templates/concepts/example.json`). Per chapter:
   logline, "how it really looks" + photos + places + logistics, root, frames (title/action/camera, signature
   marks), the light plan of each lit frame on THAT frame (`frames[n]["light"]` + `light_text`), prod
   (styling · light with the photographer's gear · logistics/permits/cost). More than one area or day on the
   board → `"tabs"` (sticky tab bar, one panel per tab, chapter chips, #hash links), e.g. one tab per area,
   plus shoot-day plan and kit. Page: label line (team, handles,
   shoot window), intro, overview table, shoot-day plan, kit list, what not to bring.
3. `python3 scripts/build_board.py shoots/<id>` → fixes any MISSING images it reports.
4. Proofread the board language (reversed RTL sentences and typos slipped through before); grep for leftovers
   (`?` addressed to the photographer, "TODO", English placeholder text, words the memory forbids).

## Publish
Load the `artifact-design` skill first (house rules), then the Artifact tool: `file_path` =
`shoots/<id>/board/index.html`, `root` = `shoots/<id>/board`, `files` = the `img/...` list in `board/used.json`,
icon "camera" on first publish. Updates: same file path → same URL; use a `label` ("Old town as it looks
today"). New artifacts are private: tell the photographer to share from the Share menu. Record the URL + version in
`shoots/<id>/notes.md` and commit.
