"""Search Wikimedia Commons for real photos of a place (publishable, with license + author + date).

  python3 scripts/commons/search.py "Old Jaffa alley" [N]

Prints one JSON line per file: title, thumb (800px), page, size, license, artist, date taken.
Generic User-Agent only - never put the photographer's email or name in requests. Run sequentially: parallel calls get 429.
"""
import json, re, sys, time, urllib.parse, urllib.request

UA = {"User-Agent": "LocationBoard/1.0 (photo-reference research)"}


def clean(s):
    return re.sub(r"<[^>]+>", "", s or "").strip()


def search(term, n=25):
    p = {"action": "query", "format": "json", "generator": "search", "gsrsearch": term + " filetype:bitmap", "gsrnamespace": 6,
         "gsrlimit": n, "prop": "imageinfo", "iiprop": "url|extmetadata|size", "iiurlwidth": 800}
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(p)
    d = None
    for attempt in range(6):
        try:
            d = json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60)); break
        except Exception as e:
            if getattr(e, "code", 0) == 429:
                time.sleep(10 * (attempt + 1)); continue
            raise
    if d is None:   # still rate-limited after ~3.5 min of backoff: skip this term instead of crashing the whole grab
        print(f"commons: 429 rate limit persisted, skipped term {term!r}", file=sys.stderr); return
    for pg in sorted(d.get("query", {}).get("pages", {}).values(), key=lambda x: x.get("index", 0)):
        ii = pg["imageinfo"][0]; m = ii.get("extmetadata", {})
        yield {"t": pg["title"], "thumb": ii.get("thumburl"), "page": ii.get("descriptionurl"), "w": ii["width"], "h": ii["height"],
               "lic": m.get("LicenseShortName", {}).get("value"), "artist": clean(m.get("Artist", {}).get("value", "")),
               "date": clean(m.get("DateTimeOriginal", {}).get("value", ""))[:10]}


if __name__ == "__main__":
    for r in search(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 25):
        print(json.dumps(r, ensure_ascii=False))
