---
name: onboard
description: "First-run interview that sets this repo up for its photographer - who they are (name, Instagram, home region, languages, board language), what and how they shoot, their gear, usual team, boldness limits, budget habits and which tools are installed - then writes memory/user-photographer.md, references/gear.md and region references, fills the {{...}} placeholders in CLAUDE.md/README.md, reports missing tools with setup steps, and commits. Use it FIRST whenever memory/user-photographer.md still says `status: placeholder` or the SessionStart hook reports a first run - even if the photographer opens with \"new shoot with @someone\" or just \"hi\" - and also when they say \"set me up again\", \"update my profile/gear\", \"I moved\", or \"learn my style\"."
---

# Onboard the photographer

Every other skill reads what this one writes: `new-shoot` takes its defaults from the profile, `scout-locations`
centres on the home region and reads `<region>-locations.md`, `develop-concepts` and `lighting-diagram` design
only with `gear.md`, `publish-board` writes in the board language. A wrong or empty profile makes every later
board subtly wrong, so do this properly, but keep it light: it's a conversation, not a form.

## 0. Before saying anything
1. **Template check.** `git remote get-url origin`. If it contains `photo-concept-helper-template`, this is
   the shared template, not their repo: say so first and walk them through GitHub "Use this template" →
   new **private** repo → `git remote set-url origin <new url>` (or clone the new repo and restart there).
   Continue the interview, but do not commit until origin points at their own repo.
2. **Resume, don't restart.** Read `memory/user-photographer.md`, `references/gear.md`, `CLAUDE.md` and
   `README.md`. If some answers are already there (an earlier, interrupted onboarding), only ask the rest.
3. **Check tools silently** so you can tell them later instead of asking. Never print a key: use exit codes only.
   ```bash
   for k in photoprep-gemini-key fal-key openrouter-key; do
     security find-generic-password -s "$k" >/dev/null 2>&1 && echo "$k: yes" || echo "$k: MISSING"; done
   command -v opencli >/dev/null && opencli doctor 2>&1 | grep -i extension || echo "opencli: MISSING"
   grep -q '^GOOGLE_MAPS_API_KEY=' ~/.config/google-maps-mcp.env 2>/dev/null && echo "maps key: yes" || echo "maps key: MISSING"
   python3 -c "import PIL" 2>/dev/null && echo "Pillow: yes" || echo "Pillow: MISSING"
   command -v uv >/dev/null && echo "uv: yes" || echo "uv: MISSING"
   echo "WHATSAPP_BRIDGE_DIR=${WHATSAPP_BRIDGE_DIR:-unset}"
   ```
   WhatsApp: it is set up only if `mcp__whatsapp__*` tools exist in this session (look at your tool list).
   Google Maps MCP: same, `mcp__google-maps__*` (optional; the scripts use the key directly).

## 1. The interview
Greet them in one or two lines (what this repo does, that you'll ask a few things first, ~5 minutes), then ask
in **rounds of 2-4 questions**, one message per round. Why rounds: a 20-question form gets skimmed and
half-answered; short rounds get real answers and let later questions build on earlier ones.
Offer a default or examples in brackets wherever you can, accept "skip" / "don't know", and switch to the
language they answer in.

**Round 1: who**
- Name (what to call them) and Instagram handle.
- Home city / region / country (the default area for scouting).
- Languages they speak, and the language for boards (and so RTL/LTR).

**Round 2: their work**
- What they shoot (portraits, fashion, cosplay, boudoir, conceptual, street, weddings...).
- Their style in their own words: light, mood, palette, references they love.
- Offer: *"Want me to look through your Instagram to learn your style? It takes ~5 min in the background
  through your Chrome."* If yes and OpenCLI is connected, start `read-instagram` on their own handle (section
  "The photographer's own feed") as a **background job** and keep interviewing; fold the summary in at the
  end. If OpenCLI is missing, say it'll work once it's set up.

**Round 3: gear**
- Bodies, lenses, flashes/strobes/continuous lights (how many of each), modifiers, gels, haze/smoke,
  triggers, anything else they carry. Example to prompt them: *"e.g. a full-frame mirrorless body, 24-70 f/2.8, 85 f/1.8,
  2× speedlight, a 200Ws strobe, gels, grid, small softbox"*.
- Do they drive / have a car on shoot days?

**Round 4: how they work**
- Usual team: producer, MUA, stylist, assistant? Anything those people love or veto?
- Boldness: on the scale **soft · editorial · bold · spicy**, how far do they go, and anything they never
  shoot? (Nudity and explicit content are never generated here regardless.)
- Budget habits: free public spots only, cheap rentals OK up to roughly what, paid venues ever? Currency.
- Weekly rest days that close places or transit where they shoot (e.g. Shabbat, Sunday)?

**Round 5: the defaults (one message, quick)**
Tell them the agent arrives with habits learned from another photographer, and list the most opinionated
ones in one line each (from `memory/feedback-*.md`): one real location + one continuous story per concept;
the "boring test" (no hobby-somewhere-pretty); boards in their language with no questions/notes on them;
bold = skin/attitude/light, labelled soft→spicy; cheap and free places first, never long rentals; scouting
centred on the least mobile person; use their whole kit. Ask: *"Anything here that isn't you?"* Each
disagreement → rewrite or delete that memory file following `learn-from-feedback` → Template defaults.

**Round 6: tools** — only if something is unknown after step 0 (e.g. "Do you use WhatsApp with models? Want
to connect it later?"). Don't ask about what you already detected.

## 2. Write it down
- **`memory/user-photographer.md`**: replace the whole placeholder with their answers in the same sections;
  frontmatter `status: filled` and today's date in `modified`. Include region slug, currency, rest days,
  languages, board language + direction, tools available (yes/missing per tool), and the Instagram style
  summary. Their name and handle are fine here (private repo); never store their email, phone, or keys.
- **`references/gear.md`**: fill every section from their answers, delete the template comment and the
  `status: template` line, keep "Patterns that worked" but drop patterns their kit can't do. If they own
  more than one light, say so in bold: plans must use it.
- **Region files.** In Israel → keep `israel-locations.md` / `seasonality-israel.md`, region slug `israel`,
  and delete their "Example region file" note. Elsewhere → create `references/<region>-locations.md` and
  `references/seasonality-<region>.md` (kebab-case region, e.g. `lisbon`, `bavaria`) with
  the same structure as the Israel files and empty tables, a one-line header "verified items only, with
  month checked", and a daylight table for the current and next month computed for their home coordinates
  (never guessed). Leave the Israel files as examples; don't delete them unless asked.
- **Placeholders.** Replace every `{{...}}` in `CLAUDE.md` and `README.md` (`{{PHOTOGRAPHER_NAME}}`,
  `{{INSTAGRAM_HANDLE}}`, `{{HOME_BASE}}`, `{{LANGUAGES}}`, `{{BOARD_LANGUAGE}}`) and remove the
  "*(... filled by onboard / at onboarding)*" notes. Check with `grep -rn '{{' CLAUDE.md README.md`.
- **Places region (optional).** If they have a Maps key and `PLACES_REGION_CODE` isn't in
  `~/.config/google-maps-mcp.env`, offer to append it (their country's two-letter code); ask before editing a
  file outside the repo.

## 3. Tell them what's missing
One short list, only for what's missing, each with the one command or link to fix it (details in `README.md`
→ Prerequisites):
- No image key → `security add-generic-password -a "$USER" -s <photoprep-gemini-key|fal-key|openrouter-key> -w`
  (prompts for the key). Without any, storyboards can't be generated; Gemini + fal is the recommended pair.
- No OpenCLI / extension → `npm install -g @jackwener/opencli`, install its Chrome extension, `opencli doctor`.
  Without it: no Instagram reading; they can drop photos in instead.
- No WhatsApp MCP → optional; lharries/whatsapp-mcp style bridge + `WHATSAPP_BRIDGE_DIR`. Without it the
  agent reads Instagram DMs and whatever they paste.
- No Maps key → optional; pins and current place photos come from web search and Commons instead.
- No Pillow / uv → `brew install uv`, `python3 -m pip install --user Pillow` (or `brew install pillow`).

## 4. Commit and hand over
If origin is their own repo:
```bash
git add memory/ references/ CLAUDE.md README.md
git commit -m "onboard: photographer profile, gear and region"
git push
```
(If origin is still the template, don't commit; remind them of step 0.) Then say in two lines what you set up
and ask about their next shoot, or go straight back to the request they opened with.

## Re-running
"I moved", "new gear", "update my profile": edit only the affected sections/files, keep the rest, and commit.
