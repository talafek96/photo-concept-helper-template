---
name: new-shoot
description: Start a new photo shoot for the photographer - read what's already known (chats, Instagram, pasted brief), ask only the gaps (model, team, date/deadline, goal, boldness range, budget, who sees the board), then open shoots/<id>/ with brief.md. Use whenever the photographer mentions a new shoot, model, collab, deadline or "help me plan a shoot with X", drops a brief, a phone number or an Instagram handle - even if they jump straight to "give me concepts" for someone new.
---

# New shoot: intake

Goal: a `shoots/<YYYY-MM>-<model>-<theme>/brief.md` complete enough to design from, with the fewest questions.

## 1. Read before asking
- `memory/MEMORY.md` (injected), `memory/user-photographer.md` (home base, languages, team, limits, budget
  habits: these are the defaults for every answer below), `references/creative-principles.md`.
- If the model exists in `models/`, read her `profile.md`: don't re-ask what we know.
- If the photographer pasted a brief, extract everything from it and only ask for the gaps.

## 2. Ask (one compact message, numbered, skip what's already known)
1. **Model**: name, Instagram handle, is she in the photographer's WhatsApp (contact name)? Any photos she sent?
2. **Team**: producer / stylist / MUA? Their known likes and vetoes (e.g. a producer who wants no more
   beach concepts). The usual team is in `user-photographer.md`.
3. **When**: shoot date or window (drives seasonality and light).
4. **Goal**: portfolio, brand, heritage story, cosplay, editorial? Any angle (culture, character, theme)?
5. **Her references**: images she likes (ask the photographer to drop them in, or point to the chat).
6. **How bold**: soft-poetic ↔ edgy ↔ more skin, within the photographer's own limits. (Never
   nudity/explicit; confirm her own comfort level.)
7. **Where / how far**: where does the model live, does she have a car, what weekday is the shoot (rest days
   such as Shabbat can mean no transit and many places closed)? Centre the radius (~30 min) on the least mobile
   person. Does the photographer drive? Studio OK? Find this in the chats first; ask only if it isn't there.
8. **Budget**: free public spots only, cheap rentals OK, or a paid location? (Default: their budget habits.)
9. **Deliverable**: board language (default from `user-photographer.md`), who will see it (shared with
   model/producer → no internal notes on it), how many concepts.
Offer defaults in brackets so the photographer can answer "defaults" to most.

## Constraints are design inputs
Write each constraint into the brief as what it MEANS for the design, never as a purchase that undoes it:
"no indoor space" → **outdoor only, free public places**, location-led (not "rent an Airbnb/studio"). Paid
venues, studios and rentals only when the photographer asks. Gear = `references/gear.md` only.

## 3. Write the brief
`shoots/<id>/brief.md` with sections: Team · Model (link to `models/<name>/profile.md`) · Window & season
notes · Goal & angle · References (paths) · Boldness · Geography · Budget · Deliverables · Vetoes.
Create `shoots/<id>/{concepts,board}/`. Commit (`shoot <id>: brief`).

## 4. Next
New model → run **`study-model`**. Known model → go straight to **`develop-concepts`**.
Don't make the photographer wait on questions you could have answered with research.
