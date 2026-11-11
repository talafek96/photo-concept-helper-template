"""Google Places (New): map pins and recent user photos.

  python3 scripts/places.py pin  "Old Town Square, Prague" ["Charles Bridge, Prague" ...]
      -> name | address | Google Maps URL (the format the boards use)
  python3 scripts/places.py photos <out_dir> <name> "Charles Bridge, Prague" [...]
      -> recent Google user photos + contact sheet, to check how a place looks TODAY.

Google user photos are for INTERNAL checking and as AI location references only - never publish them on a
board (licensing). Publishable photos come from Wikimedia Commons (scripts/commons/).
Key: GOOGLE_MAPS_API_KEY in ~/.config/google-maps-mcp.env (Places API (New) enabled on it).
Optional in the same file: PLACES_REGION_CODE=<two-letter CLDR region, e.g. IL, PT, US> to bias results to the
photographer's country, and PLACES_LANGUAGE=<code> (default en). The env vars of the same names override it.
Map URL format: https://www.google.com/maps/search/?api=1&query=<lat>%2C<lng>&query_place_id=<id>
"""
import json, os, sys, urllib.request
from PIL import Image, ImageDraw

ENV_FILE = os.path.expanduser("~/.config/google-maps-mcp.env")
env = {}
if os.path.exists(ENV_FILE):
    env = dict(l.strip().split("=", 1) for l in open(ENV_FILE) if "=" in l and not l.startswith("#"))
KEY = os.environ.get("GOOGLE_MAPS_API_KEY") or env.get("GOOGLE_MAPS_API_KEY")
REGION = os.environ.get("PLACES_REGION_CODE") or env.get("PLACES_REGION_CODE")
LANG = os.environ.get("PLACES_LANGUAGE") or env.get("PLACES_LANGUAGE") or "en"
if not KEY:
    sys.exit(f"no GOOGLE_MAPS_API_KEY in {ENV_FILE} - see README.md (Google Maps / Places setup)")


def text_search(q, fields):
    req_body = {"textQuery": q, "languageCode": LANG}
    if REGION:
        req_body["regionCode"] = REGION
    body = json.dumps(req_body).encode()
    req = urllib.request.Request("https://places.googleapis.com/v1/places:searchText", data=body, headers={
        "Content-Type": "application/json", "X-Goog-Api-Key": KEY, "X-Goog-FieldMask": fields})
    return json.load(urllib.request.urlopen(req, timeout=30)).get("places", [])


def map_url(p):
    loc = p["location"]
    return f"https://www.google.com/maps/search/?api=1&query={loc['latitude']}%2C{loc['longitude']}&query_place_id={p['id']}"


def pin(queries):
    for q in queries:
        ps = text_search(q, "places.id,places.displayName,places.formattedAddress,places.location")
        if not ps:
            print(q, "| NO RESULT"); continue
        p = ps[0]
        print(f"{p['displayName']['text']} | {p.get('formattedAddress')} | {map_url(p)}")


def photos(out_dir, name, queries):
    os.makedirs(out_dir, exist_ok=True)
    ims, meta = [], []
    for q in queries:
        ps = text_search(q, "places.id,places.displayName,places.photos,places.location")
        if not ps:
            continue
        p = ps[0]
        for ph in p.get("photos", [])[:10]:
            fn = os.path.join(out_dir, f"{name}_{len(ims):02d}.jpg")
            try:
                open(fn, "wb").write(urllib.request.urlopen(
                    f"https://places.googleapis.com/v1/{ph['name']}/media?maxWidthPx=1000&key={KEY}", timeout=60).read())
            except Exception:
                continue
            ims.append(fn); meta.append({"file": fn, "place": p["displayName"]["text"], "map": map_url(p),
                                         "authors": [a.get("displayName") for a in ph.get("authorAttributions", [])]})
    json.dump(meta, open(os.path.join(out_dir, name + ".json"), "w"), ensure_ascii=False, indent=1)
    tiles = []
    for i, f in enumerate(ims):
        im = Image.open(f).convert("RGB"); im.thumbnail((400, 300)); c = Image.new("RGB", (400, 300), "white")
        c.paste(im, ((400 - im.width) // 2, (300 - im.height) // 2))
        d = ImageDraw.Draw(c); d.rectangle([0, 0, 34, 22], fill="black"); d.text((4, 4), str(i), fill="yellow"); tiles.append(c)
    s = Image.new("RGB", (5 * 400, max(1, (len(tiles) + 4) // 5) * 300), "white")
    for i, c in enumerate(tiles):
        s.paste(c, ((i % 5) * 400, (i // 5) * 300))
    s.save(os.path.join(out_dir, name + "_sheet.jpg"), quality=80)
    print(name, len(ims), "->", os.path.join(out_dir, name + "_sheet.jpg"))


if __name__ == "__main__":
    if sys.argv[1] == "pin":
        pin(sys.argv[2:])
    elif sys.argv[1] == "photos":
        photos(sys.argv[2], sys.argv[3], sys.argv[4:])
