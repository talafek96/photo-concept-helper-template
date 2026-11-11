---
name: scout-locations
description: Find and verify REAL shoot locations in the photographer's region - current look from recent dated photos, publishable reference photos with credits (Wikimedia Commons), Google Maps pins, permits, price, and bookable interiors (Airbnb day-use, shoot-location sites, boutique hotels) screened by photo at scale. Use whenever a concept needs a place, the photographer asks "find me a real location / a place that looks like this / somewhere cheap to shoot", or a location on a board may be out of date.
---

# Scout locations

The rule that matters most: **never describe or render a place you haven't seen in recent photos.**
A historic street once went on a board from a 2010 pastel-postcard photo; today it's renovated cream with
towers behind, and the photographer noticed. Every location claim needs a dated photo.

## Public places (streets, parks, stairs, viewpoints)
**Radius first:** centre on the least mobile person (from `brief.md`: where the model lives, car or not,
weekday), not on the photographer's home base. Places on the photographer's route are stretch options. For every
place record its **status on the shoot weekday** (rest days such as Shabbat or Sunday: open/closed, crowds,
public transport) and **parking**.
For an outdoor / location-led shoot, start with a **long list of ~20** places with texture and character, not
just parks and promenades: industrial edges, legal ruins, quarries, dunes, rock coast, wadis, rail/port edges,
old quarters, markets after closing, public rooftops/car parks. Then pick ~10 for variety of texture and light.
Bookable interiors (below) only when the brief allows paid indoor space.
1. Candidates from knowledge + `references/<region>-locations.md` + web search.
2. **Current look (internal):** `python3 scripts/places.py photos shoots/<id>/locations/gp <name> "<place, city>"`
   → recent Google user photos. Look at them. These may be used as `loc_refs` for AI but are **never
   published** (licensing).
3. **Publishable photos:** `python3 scripts/commons/grab.py shoots/<id>/locations <name> "<term>" ["<term 2>"]`
   → contact sheet sorted newest first, with credits JSON. Look at the sheet; delete anything that doesn't
   show what it claims; prefer ≤3 years old and always show the year in the caption. Commons is rate-limited:
   run sequentially; generic User-Agent only (never the photographer's email/name).
4. **Pin:** `python3 scripts/places.py pin "<place, city>"` → name | address | Maps URL
   (`https://www.google.com/maps/search/?api=1&query=<lat>%2C<lng>&query_place_id=<id>`).
5. **Sun direction (mandatory for every outdoor concept).** Note which way the camera and model face and
   where the sun is at the planned time (compute it for the date and coordinates, e.g. with a sun-position calculator or
   a few lines of Python; never guess. For scale: coastal Israel in late November has sunrise ~06:20 at az ~115°,
   sunset ~16:40 at az ~245°). Hills delay the first/last direct sun (a ridge to the east shades a bay-side
   city at sunrise). Write it into the concept: "sun from X, behind camera / side /
   backlight". A frame "against the sunrise" only works if the view actually faces east.
6. Check what's sensitive or changed (memorial sites, construction, closures). A square that became a
   memorial site and a memorial garden with a crypt were dropped for this reason.
7. Write down: what's really there today, best time (light + crowds), parking, permit body, risks (traffic,
   crowds, towers in the background and how to frame them out).
If the Google Maps MCP is down, these scripts still work (direct API). If they fail too, say so; don't estimate.

## Bookable interiors (a bathroom, a balcony, a black studio...)
The photographer needs a place to **shoot for a few hours**, cheap. Not a lease: never long-term rental or
sale sites. Order: Airbnb (day use / one night, message host about photography, water, props) → boutique
hotels on Booking (old buildings) → the region's shoot-location sites (pricey per hour; some have a free scout
service; Israel: LocationZ, see `israel-locations.md`) → a friend's/Facebook-group apartment.
Screen at scale with `scripts/listings/listings.py` (see its docstring): collect ids → photos → sheets →
Gemini screen with a precise description → `top` → `show` and LOOK yourself before recommending.
If nothing matches nearby: widen the radius, loosen to "fixable with a gel/grade/props", and say clearly
what you searched (counts) and what you didn't find.
Report each with: link, what matches, what doesn't (and how to hide it), price/min-stay, and the host
question to ask. Lead with the cheapest that works.

## Output
- In `shoots/<id>/locations/`: photos + credits JSON (gitignored images; commit the JSON).
- Into the concept: `setting` rewritten to the real current look; `loc_refs` 3-6 photos.
- Into the board chapter: "How it really looks" text, 2-6 credited real photos with years, places with map
  links (mark the actual shooting spot), logistics/permit line.
- New verified facts → `references/<region>-locations.md` (with the month you checked; create it if missing). Commit.
Parallel research across several concepts: spawn `location-scout` subagents (`.claude/agents/`), one per
concept, each with its own opencli session name.
