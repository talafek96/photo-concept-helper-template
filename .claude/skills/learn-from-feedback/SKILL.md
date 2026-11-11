---
name: learn-from-feedback
description: Turn the photographer's corrections, rejections and preferences into durable, committed rules in memory/ so mistakes never repeat - and rewrite the template's default rules when the photographer disagrees with them. Use whenever the photographer corrects you, rejects a concept/frame/location, swears or sounds annoyed ("wtf", "no", "too expensive", "that's not what I meant"), says "remember", states a preference - and at the end of every shoot session.
---

# Learn from feedback

This repo improves only through `memory/`. A lesson that isn't written and committed is lost.

## When the photographer pushes back
1. **Stop and understand.** A bare "no" is not a brief. Find what is actually wrong (look at the thing again,
   read their exact words). If not obvious, ask ONE short question. Never answer a rejection with its opposite.
2. **Two misses on the same thing: stop guessing** and ask them to show/describe what they want.
3. **Fix the work first**, then state in one line what you changed. Never call taste work "fixed"/"good".
4. **Name the general rule** in one line ("so the rule is: places for a shoot = hours of use, never a lease?")
   and confirm when it's not obvious. Save the general rule, with the incident as one line of evidence.

## Writing the memory
- Check `memory/MEMORY.md`: if a file covers it, **update that file** (rewrite; don't append a contradiction).
- **Template defaults.** Files with `origin: template-default` were learned on another photographer's shoots.
  When this photographer contradicts one ("I like beach concepts", "I only own one flash", "spicy is off the
  table for me"), their word wins: rewrite the file to their rule with their words as the **Why:**, set
  `origin: photographer`, or delete the file (and its index line and any `[[link]]` to it) if the rule no
  longer applies at all. Also fix any skill, `references/` file or `CLAUDE.md` hard rule that states the old
  default, so nothing contradicts the new rule. When they confirm a default, just flip `origin`.
- Facts about who they are, their team, limits or budget go in `memory/user-photographer.md`, not a new file.
- Otherwise a new file `memory/feedback-<kebab-name>.md`:
  ```markdown
  ---
  name: feedback-<kebab-name>
  description: "<one line: the rule>"
  metadata:
    type: feedback
    origin: photographer
    modified: <YYYY-MM-DD>
  ---
  <The rule, 2-6 lines. **Why:** the incident in one line. **How to apply:** where it bites.>
  ```
  Other types: `user-*` (who the photographer/team are), `reference-*` (facts, places, tools), `project-*` (state of a shoot).
- Add/adjust the one-line entry in `memory/MEMORY.md`.
- If the lesson changes how a skill works, edit the skill too (the memory says the rule; the skill does it).
- Durable facts about places/seasons/gear → the `references/` file instead of memory.
- Commit + push in the same change as the work: `git add memory/ ... && git commit -m "memory: <rule>" && git push`.

## Pitfalls (failures that weren't the photographer's taste)
Tool errors, workarounds, wrong assumptions and steps the photographer had to ask for go into `PITFALLS.md`
(`symptom → cause → fix → where fixed`) and the fix goes into the skill or script itself. The file
explains how to maintain it. Same commit.

## Budget
`feedback-*` files and the index are injected into every session. Keep each compact, merge duplicates, prune
superseded rules. Long specs belong in `references/` with a pointer.

## End of session
Before wrapping a shoot session: list what the photographer corrected today, check each is in memory, update
`shoots/<id>/notes.md` (boards, concept status, what worked/failed), commit and push.
