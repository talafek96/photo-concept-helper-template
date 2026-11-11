"""Download Commons candidates for one place and build a numbered contact sheet to pick from.

  python3 scripts/commons/grab.py <out_dir> <name> "search term 1" ["term 2" ...]

Writes <out_dir>/<name>/NN.jpg, <out_dir>/<name>.json (credits: artist, license, page, date) and
<out_dir>/<name>_sheet.jpg. LOOK at the sheet: delete files that don't show what the title claims
(an "orchard" once turned out to be a highway interchange), and prefer the newest dates -
places change (a renovated street was once shown from a 2010 photo and the photographer noticed).
"""
import json, os, sys, time, urllib.request
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from search import search, UA

out_dir, name, terms = sys.argv[1], sys.argv[2], sys.argv[3:]
os.makedirs(os.path.join(out_dir, name), exist_ok=True)
rows = []
for t in terms:
    for r in search(t, 16):
        if r["thumb"] and r["w"] >= 1000 and r["lic"] and not any(x["t"] == r["t"] for x in rows):
            rows.append(r)
    time.sleep(1)
rows.sort(key=lambda r: r.get("date") or "0000", reverse=True)   # newest first
rows = rows[:30]
tiles = []
for i, r in enumerate(rows):
    p = os.path.join(out_dir, name, f"{i:02d}.jpg")
    r["file"] = p
    if not os.path.exists(p):
        for a in range(3):
            try:
                open(p, "wb").write(urllib.request.urlopen(urllib.request.Request(r["thumb"], headers=UA), timeout=60).read()); break
            except Exception:
                time.sleep(3)
    try:
        im = Image.open(p).convert("RGB")
    except Exception:
        continue
    im.thumbnail((400, 300)); c = Image.new("RGB", (400, 300), "white"); c.paste(im, ((400 - im.width) // 2, (300 - im.height) // 2))
    d = ImageDraw.Draw(c); d.rectangle([0, 0, 110, 22], fill="black"); d.text((4, 4), f"{i} {r.get('date') or '?'}", fill="yellow")
    tiles.append(c)
json.dump(rows, open(os.path.join(out_dir, name + ".json"), "w"), ensure_ascii=False, indent=1)
cols = 5
sheet = Image.new("RGB", (cols * 400, max(1, (len(tiles) + cols - 1) // cols) * 300), "white")
for i, c in enumerate(tiles):
    sheet.paste(c, ((i % cols) * 400, (i // cols) * 300))
sheet.save(os.path.join(out_dir, name + "_sheet.jpg"), quality=80)
print(name, len(tiles), "->", os.path.join(out_dir, name + "_sheet.jpg"))
