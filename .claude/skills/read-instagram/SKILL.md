---
name: read-instagram
description: Pull a model's (or the photographer's own) Instagram into the repo through the photographer's logged-in Chrome (OpenCLI bridge) - every post with all carousel slides at full size plus captions/credits, her story highlights, and the Instagram DM thread between the photographer and her (text + photos she sent). Use whenever a task needs anything from Instagram - "look at her Instagram", "check her highlights", "what did she send me on Insta", a new model's handle, refreshing refs, learning the photographer's own style at onboarding - even if they only paste an instagram.com link.
---

# Read Instagram

Everything goes through the photographer's own Chrome session via OpenCLI, so it sees what they see
(private accounts they follow, their DMs). Instagram's official API isn't used: `opencli instagram ...` adapters
rate-limit (429) and miss carousels.

**Before anything:** `opencli doctor` must show `Extension: connected`. If not, ask the photographer to open Chrome
(the profile with the OpenCLI extension); don't try to work around it.

## Posts (her portfolio)
```bash
python3 .claude/skills/read-instagram/scripts/grab.py <handle> models/<name>/ig 36   # >15 posts: background job
python3 scripts/sheet.py models/<name>/ig                                            # one-look overview
```
Each post page embeds its own JSON; `scripts/post.js` reads that, so you get every slide of a carousel at
the largest size plus caption, likes, tagged users. `posts.json` keeps the metadata; reruns skip posts
already downloaded. Reels/videos come in as their cover frame (`video: true`).

Why not scrape `<img>` tags: the post page also renders the profile grid and "more posts" thumbnails,
so tag-scraping saves the same grid (and other people's photos) for every post. That bug shipped once.

Read captions for credits: a model's feed includes work by other photographers and posts with other
models. Before picking identity refs, confirm the photo is clearly her.

Going further back than the newest N (e.g. "before all the yoga pictures"): raise N (each post ~7s, so
100 posts ≈ 12 min, run in background), then sort `posts.json` by `taken_at` and look at the older ones.
**The grid only loads while the Chrome tab is visible.** With the Mac locked (photographer asleep or away) it
stops at 12-24 posts and grab.py prints a WARNING. Then use highlights for the older period, say in the
profile that the feed was cut, and rerun when the photographer is at the Mac.

## Highlights (stories she chose to keep)
```bash
python3 .claude/skills/read-instagram/scripts/highlights.py <handle> models/<name>/ig/highlights
python3 scripts/sheet.py models/<name>/ig/highlights
```
Reads the highlight ids from the profile header, opens each `/stories/highlights/<id>/` URL and takes
the whole reel from the JSON the page embeds. Nothing is clicked: the "View story" gate stays closed, so
nothing is played or marked seen. Writes `highlights.json` (title, date, video flag, mentions, link
stickers) + `NN_KK.jpg`. Highlights often reach further back than the feed (one test: 6 highlights,
60 items reaching ~6 months back). They're the best view of her life outside her latest phase, and link stickers
show her paid-content channels.

## DM thread with the model
```bash
python3 .claude/skills/read-instagram/scripts/dm.py <handle> models/<name>/ig/dm 6   # 6 scroll-ups of history
```
Opens her profile, presses its **Message** button (a small chat popup), takes the `/direct/t/<id>` link
from the popup and opens that full page, so no inbox rows are clicked. `ig.me/m/<handle>` links don't
open the thread reliably; don't use them. Save the thread URL in `profile.md` and pass it next time. Saves `dm.txt` + `dm_NN.jpg` (photos in the thread).

Things that are visible to other people, which is why the script only clicks the profile Message button and otherwise navigates by URL:
- Opening a thread marks it **seen** for her. Fine for the model's thread the photographer asked about;
  never open other people's threads (not even "to test" - ask the photographer for a thread to test on).
- The top of the inbox has "Your note" / "What's on your mind?": that is a public note composer. Never
  click it. Never type in "Message...", send, react or like.

## The photographer's own feed (onboarding, or "learn my style")
Same `grab.py` (and optionally `highlights.py`) on their own handle, into `scratch/own-ig/` (gitignored), then
`scripts/sheet.py scratch/own-ig` and look at the strongest posts full size. Write only a summary into
`memory/user-photographer.md` → What they shoot: genres, light (direct flash, gels, natural), palette, lenses
and framing they favour, the models/looks they cast, what gets the most engagement. No DMs here.

## Output and privacy
All downloads land in `models/<name>/ig/` (gitignored: her photos and messages stay on this Mac). What
matters for the shoot goes into `models/<name>/profile.md` as a summary, not quotes of private messages.
