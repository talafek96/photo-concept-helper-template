# PITFALLS

Things that went wrong while running this agent, and the fix, so they never happen twice.
Injected into every session by `.claude/hooks/inject-memory.sh`. The entries below shipped with the template
(learned on another photographer's shoots); add this photographer's own as they happen.

**How to maintain this file**
- Add an entry the moment something fails or the photographer has to step in: a tool error you had to work
  around, a wrong assumption, a step you skipped that they had to ask for, a result they rejected.
- Each entry: `symptom → cause → fix → where it's fixed`. The fix must live in a skill, script or
  memory file too, so the pitfall can't recur; this file is the index that points there.
- Keep it short. When a fix is permanent in code (the failure can no longer happen), shrink the entry to one
  line; delete it after a few clean shoots.
- Commit it with the fix (`pitfall: <short>`).

## Setup
- **A session started in the shared template checkout** → work committed there can't be pushed and would
  leak into the template → the SessionStart hook warns when origin is `photo-concept-helper-template`;
  create your own repo with "Use this template" → `.claude/hooks/inject-memory.sh`, README.
- **An optional tool isn't set up (no WhatsApp MCP, no fal key, OpenCLI extension not connected)** → say
  which one in one line, use the fallback (Instagram DMs / pasted chat; next provider; ask to open Chrome),
  never guess the content → `user-photographer.md` → Tools available; `onboard` lists setup steps.

## Instagram
- **Every post saved the same images, incl. other people's photos** → `<img>` scraping picked up the
  profile grid / "more posts" → read the JSON the post page embeds → `read-instagram/scripts/grab.py` + `post.js`.
- **`ig.me/m/<handle>` doesn't open the thread reliably** → open profile → Message button → popup's
  `/direct/t/<id>` link → `read-instagram/scripts/dm.py`.
- **Clicking inbox rows opened the public "New note" composer / someone else's thread (marked seen)** →
  never click inbox rows or the note composer; only the profile Message button and URLs → `read-instagram` SKILL.md.
- **Testing on a random DM thread** → only ever open the thread of the person the photographer named.
- **Story highlights weren't scripted** → `read-instagram/scripts/highlights.py` reads the embedded reel
  JSON per highlight URL (no clicks, nothing marked seen).
- **grab.py got 24 of 90 posts; scrolling did nothing** → Instagram loads the grid only while the tab is
  visible, and the Mac was locked overnight (`visibilityState: hidden`); the web API endpoints 404 →
  grab.py now warns; use highlights for the older period, rerun at the Mac → `read-instagram` SKILL.md.
- **`opencli instagram user/profile` → 429** → use the browser-bridge scripts, not the API adapters.

## WhatsApp
- **Chat had only an old message; newest DB message hours old** → the WhatsApp bridge wasn't running (the
  MCP only reads its DB) → start it in the background from `$WHATSAPP_BRIDGE_DIR` and wait for the sync →
  `read-chats` SKILL.md step 4.
- **Read the Instagram DMs but not WhatsApp (or skipped the photos)** → when the photographer names both,
  read both, and view + download every photo in the window → `read-chats` SKILL.md; `study-model` step 1 now
  says every named source, WhatsApp AND Instagram.

## Identity and wardrobe
- **Tattoos crawled onto belly, hips, arms and calves (mostly fal)** → identity.txt didn't state placement
  as a strict "only here, nowhere else" → `models/<name>/identity.txt` names the exact place and lists the
  forbidden ones; review checks placement per frame → `generate-storyboard` checklist.
- **fal invented an outfit (a latex suit) the board implied she owned; boots rendered as a different style** →
  styling must come from what she owns (or be listed to buy with a price); pass product photos of owned items
  as `loc_refs` → `publish-board` rules, `image-generation.md`.

## Boards
- **Titles and TOC links carried the wrong `lang`** → `build_board.py` had a hardcoded `title_lang` default
  from an earlier shoot → defaults now come from the board's `lang`; UI labels come from `STRINGS` / `strings`
  → `scripts/build_board.py`.

## Concepts and locations
- **"Wheel against the sunrise" on a promenade that faces north-west** → sun geometry not checked → every
  outdoor concept states the sun azimuth/time vs camera direction → `scout-locations` SKILL.md step 5.
- **Whole board rejected as boring (two rounds): yoga, pole, her own lingerie set, "she does X at a nice place"**
  → concepts recycled her content categories and had no turn → boring test (one-line hook: want + turn +
  payoff; kill hobby-somewhere-pretty and copies of her feed) → `references/creative-principles.md`,
  `develop-concepts` step 6, `memory/feedback-boring-test.md`.
- **Brief turned "she has no indoor space" into "rent an Airbnb / pole studio / tattoo studio"** → constraint
  was bought away instead of designed for → no space = outdoor, free public places, location-first; rentals
  only when the photographer asks → `new-shoot`, `scout-locations`, `memory/feedback-producible-with-own-means.md`.
- **Concepts needed a pole and lighting the photographer doesn't have** → gear check against
  `references/gear.md` in the boring test → `develop-concepts` step 6.
- **Planned the location radius around the photographer instead of the least mobile person** (the model had no
  car and the shoot fell on a no-transit rest day) → intake never asked where she lives, how she travels or what
  weekday it is → radius centred on the least mobile person; rest-day status + parking per place → `new-shoot`
  step 7, `scout-locations`, `memory/feedback-plan-around-least-mobile.md`.

## Scouting
- **`scripts/commons/search.py` crashed (UnboundLocalError) on repeated Commons 429s** → longer retries, skip the term instead of crashing → fixed in the script.
- **Google place photos carry no date** → date a place from dated reviews/Commons; never call an undated photo "recent" → `scout-locations`.

## Image generation
- **Abstract tattoos rendered as letters/glyphs; "calligraphic" in a prompt wrote characters on paper** →
  describe tattoos as "abstract brush strokes, no letters" in identity.txt and add "no writing" to the setting
  → `generate-storyboard` review checklist.
- **Frames drifted on prop count (two suitcases), hair style (updo vs loose), outfits she doesn't own, and a
  generic room instead of the real rental** → checklist items + always `loc_refs` from the listing →
  `generate-storyboard` SKILL.md review step 2.
- **Ten concepts generated at once → Gemini quota errors, fal fallback rejected refs, 15 frames missing** → max 2
  Google concepts concurrently, queue the rest → `generate-storyboard` SKILL.md.
- **Tattoos painted on overalls / on knees under a pencil skirt / on backs of legs; duplicated model; forced-perspective
  object moved close; black two-piece rendered as one-piece** → review checklist items + say where tattoos are hidden
  in the wardrobe text → `generate-storyboard` review step 2.

## Process
- **Ended a turn with "waiting on X" while the job had already finished or no watcher was armed → run stalled
  until someone pinged** → before ending a turn, check that a running background job or Monitor will wake
  you (`pgrep -f scripts/gen.py`, a Monitor whose exit condition can actually fire); otherwise keep working.
  Waiter loops that grep for a success line hang forever when the step fails: match the failure lines too.
- **`gen.py` fal/OpenRouter fallback failed with "Broken pipe"** → full-size anchor PNGs sent inline → refs now
  downscaled to ≤1536px JPEG in `data_uri` (`scripts/gen.py`).
- **Built the skills by hand without skill-creator practices** → descriptions now state when to trigger,
  rules explain why, single-skill scripts are bundled in the skill folder. Use `/skill-creator` for new skills.
- **Two sessions share this checkout** → `git add` only the files you changed (never `git add -A` while
  another session works here), `git pull --rebase` before push.
- **Needed a manager to catch: skipped source, impossible sun direction, invented outfits, tattoo drift** →
  all now in skills/checklists; before reporting done, run the request check point by point (CLAUDE.md).
