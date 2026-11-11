"""Find bookable INTERIORS that match a look (e.g. "old bathroom, pale green tiles, enamel tub") by screening
listing photos at scale. Built during a hunt for an old green-tiled bathroom: 2,300+ Airbnb + 503 LocationZ
listings screened.

Pipeline (work dir defaults to ./scratch/listings, gitignored):
  1. ids     python3 scripts/listings/listings.py airbnb-ids "Lisbon--Portugal" "Porto--Portugal" ... [--amenity 61]
             (Airbnb's "City--Country" URL slug; runs through the photographer's Chrome via opencli;
             amenity 61 = bathtub; 18 results/page, cursor pagination)
  2. photos  python3 scripts/listings/listings.py airbnb-photos          (plain HTTP, no browser, ~20 photos/listing)
             python3 scripts/listings/listings.py locationz-all           (Israel only - LocationZ: every listing, city + photos;
                                                                          for another region's shoot-location site, add a
                                                                          similar collector writing l/<id>.txt)
  3. sheets  python3 scripts/listings/listings.py sheets                 (one numbered contact sheet per listing)
  4. screen  python3 scripts/listings/listings.py screen "<what to look for>"   (Gemini flash scores every sheet)
  5. review  python3 scripts/listings/listings.py top 5                  (best scores) then
             python3 scripts/listings/listings.py show <out.jpg> <id> [<id> ...]  and LOOK at it yourself.

Rules learned the hard way:
  - The photographer wants a place to SHOOT for a few hours, not to live in. Never use long-term rental/sale
    sites. Day-use / a night on Airbnb / shoot-location sites only.
  - Price matters: a few-hour booking at a premium hourly rate was "way too expensive". Lead with cheap options
    and say the price.
  - The AI screen is a filter, not a verdict: open the top hits full size before recommending anything.
  - Short-term rentals near a city are often almost all renovated; widen the radius (other towns) and loosen the
    match (any untouched retro bathroom, colour fixable with a gel/grade) before declaring "nothing exists".
"""
import base64, glob, hashlib, html, io, json, os, re, subprocess, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

WORK = os.environ.get("LISTINGS_DIR", os.path.join(os.getcwd(), "scratch", "listings"))
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"
for d in ("l", "t", "s"):
    os.makedirs(os.path.join(WORK, d), exist_ok=True)


def P(*a):
    return os.path.join(WORK, *a)


def ev(session, js):
    out = subprocess.run(["opencli", "browser", session, "eval", js], capture_output=True, text=True).stdout
    return "\n".join(l for l in out.splitlines() if l.strip() and not re.search(r"pdate available|Download:|Run: npm", l))


def airbnb_ids(queries, amenity=None):
    ids = set(open(P("ids.txt")).read().split()) if os.path.exists(P("ids.txt")) else set()
    for q in queries:
        for off in range(0, 288, 18):
            cur = base64.b64encode(json.dumps({"section_offset": 0, "items_offset": off, "version": 1}).replace(" ", "").encode()).decode()
            url = f"https://www.airbnb.com/s/{q}/homes?adults=1&pagination_search=true&cursor={cur}" + (f"&amenities%5B%5D={amenity}" if amenity else "")
            subprocess.run(["opencli", "browser", "bnb", "open", url], capture_output=True); time.sleep(4)
            got = re.findall(r"^\d+$", ev("bnb", "[...new Set([...document.querySelectorAll('a[href*=\"/rooms/\"]')].map(a=>a.href.split('?')[0].split('/').pop()))].join('\\n')"), re.M)
            if not got:
                break
            ids.update(got)
        print(q, len(ids), flush=True)
    open(P("ids.txt"), "w").write("\n".join(sorted(ids)))


def airbnb_photos():
    ids = open(P("ids.txt")).read().split()

    def g(i):
        fn = P("l", f"{i}.txt")
        if os.path.exists(fn) and os.path.getsize(fn) > 200:
            return
        h = ""
        for _ in range(3):
            try:
                h = urllib.request.urlopen(urllib.request.Request(f"https://www.airbnb.com/rooms/{i}", headers={"User-Agent": UA, "Accept-Language": "en"}), timeout=30).read().decode("utf8", "ignore"); break
            except Exception:
                time.sleep(5)
        t = re.search(r"<title>([^<]*)", h)
        us = []
        for u in re.findall(r'https://a0\.muscache\.com/im/pictures/[^"?\\ ]+\.(?:jpe?g|png|webp)', h):
            if ("Hosting-" in u or re.search(r"pictures/[0-9a-f-]{36}\.jpe?g$", u)) and "Platform" not in u and u not in us:
                us.append(u)
        open(fn, "w").write((html.unescape(t.group(1)) if t else i) + f" | https://www.airbnb.com/rooms/{i}\n" + "\n".join(us))
    with ThreadPoolExecutor(4) as ex:
        list(ex.map(g, ids))
    print(len(ids), "listings")


def locationz_all():
    links = set()
    for p in range(1, 60):
        subprocess.run(["opencli", "browser", "loc", "open", f"https://www.locationz.co.il/search?page={p}"], capture_output=True); time.sleep(4)
        got = [l for l in ev("loc", "[...new Set([...document.querySelectorAll('a[href*=\"/listing/\"]')].map(a=>a.href.split('?')[0]))].join('\\n')").splitlines() if "/listing/" in l]
        if not got:
            break
        links.update(got)

    def g(u):
        try:
            h = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": UA}), timeout=40).read().decode("utf8", "ignore")
        except Exception:
            return
        t = re.search(r'property="og:title" content="([^"]*)', h) or re.search(r"<h1[^>]*>([^<]*)", h)
        city = re.findall(r"([֐-׿'\"\- ]{2,30}), ישראל", h)
        ims = []
        for m in re.findall(r"https://locationz-s3[^\"' ]+?/media/listings/\d+/conversions/[^\"' ]+?-sm\.webp", h):
            if m not in ims:
                ims.append(m)
        i = "lz_" + hashlib.md5(u.encode()).hexdigest()[:10]
        open(P("l", i + ".txt"), "w").write(f"{html.unescape(t.group(1)) if t else u} | {city[0].strip() if city else ''} | {u}\n" + "\n".join(ims))
    with ThreadPoolExecutor(6) as ex:
        list(ex.map(g, sorted(links)))
    print(len(links), "LocationZ listings")


def thumb_url(u):
    if "muscache" in u:
        return u + "?im_w=320"
    return u


def big_url(u):
    if "muscache" in u:
        return u + "?im_w=720"
    if "locationz" in u:
        return u.replace("-sm.webp", "-preview.webp")
    return u


def urls(i):
    return [u for u in open(P("l", i + ".txt")).read().split("\n")[1:] if u.strip()]


def sheets():
    from PIL import Image, ImageDraw

    def dl(u):
        fn = P("t", hashlib.md5(u.encode()).hexdigest() + ".img")
        if not os.path.exists(fn):
            try:
                open(fn, "wb").write(urllib.request.urlopen(urllib.request.Request(thumb_url(u), headers={"User-Agent": "Mozilla/5.0"}), timeout=30).read())
            except Exception:
                return None
        return fn
    for f in sorted(glob.glob(P("l", "*.txt"))):
        i = os.path.basename(f)[:-4]
        if os.path.exists(P("s", i + ".jpg")):
            continue
        with ThreadPoolExecutor(16) as ex:
            fs = [x for x in ex.map(dl, urls(i)) if x]
        if not fs:
            continue
        W, H, C = 240, 170, 8
        sh = Image.new("RGB", (W * C, H * ((len(fs) + C - 1) // C)), "white"); dr = ImageDraw.Draw(sh)
        for k, fn in enumerate(fs):
            try:
                im = Image.open(fn).convert("RGB"); im.thumbnail((W - 4, H - 4))
            except Exception:
                continue
            sh.paste(im, ((k % C) * W, (k // C) * H)); dr.text(((k % C) * W + 3, (k // C) * H + 3), str(k), fill="yellow")
        sh.save(P("s", i + ".jpg"), quality=80)


def screen(criteria):
    key = subprocess.check_output(["security", "find-generic-password", "-s", "photoprep-gemini-key", "-w"]).decode().strip()
    q = ("Contact sheet of numbered photos from one rental listing. " + criteria +
         " Ignore modern renovations styled to look old. Answer JSON only: "
         '{"indices":[...], "score":0-10, "match_note":"short", "has_key_feature":bool}')

    def run(i):
        out = P("s", i + ".json")
        if os.path.exists(out):
            return
        body = {"contents": [{"parts": [{"text": q}, {"inline_data": {"mime_type": "image/jpeg", "data": base64.b64encode(open(P("s", i + ".jpg"), "rb").read()).decode()}}]}],
                "generationConfig": {"responseMimeType": "application/json"}}
        # model ids retire: if this 404s, the error names the replacement - update it here.
        u = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={key}"
        try:
            d = json.load(urllib.request.urlopen(urllib.request.Request(u, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"}), timeout=120))
            json.dump(json.loads(d["candidates"][0]["content"]["parts"][0]["text"]), open(out, "w"))
        except Exception as e:
            print("screen err", i, (e.read().decode()[:200] if hasattr(e, "read") else e), file=sys.stderr)
    ids = [os.path.basename(f)[:-4] for f in glob.glob(P("s", "*.jpg"))]
    with ThreadPoolExecutor(10) as ex:
        list(ex.map(run, ids))


def top(min_score):
    rows = []
    for f in glob.glob(P("s", "*.json")):
        d = json.load(open(f)); i = os.path.basename(f)[:-5]
        if (d.get("score") or 0) >= min_score:
            rows.append((d.get("score"), i, open(P("l", i + ".txt")).readline().strip()[:120], d.get("indices"), d.get("match_note")))
    for r in sorted(rows, reverse=True):
        print(*r, sep=" | ")


def show(out, ids):
    from PIL import Image, ImageDraw
    rows = []
    for i in ids:
        L = urls(i); idx = json.load(open(P("s", i + ".json"))).get("indices", [])[:4]
        ims = []
        for k in idx:
            try:
                im = Image.open(io.BytesIO(urllib.request.urlopen(urllib.request.Request(big_url(L[k]), headers={"User-Agent": "Mozilla/5.0"}), timeout=30).read())).convert("RGB")
                ims.append(im.resize((int(im.width * 380 / im.height), 380)))
            except Exception:
                pass
        if ims:
            rows.append((i, ims))
    W = max(sum(x.width for x in r[1]) for r in rows)
    sh = Image.new("RGB", (W, 400 * len(rows)), "white"); d = ImageDraw.Draw(sh)
    for k, (i, ims) in enumerate(rows):
        x = 0
        for im in ims:
            sh.paste(im, (x, 400 * k + 20)); x += im.width
        d.text((5, 400 * k + 3), i + " " + open(P("l", i + ".txt")).readline()[:90], fill="black")
    sh.save(out, quality=82); print(out)


if __name__ == "__main__":
    cmd, a = sys.argv[1], sys.argv[2:]
    if cmd == "airbnb-ids":
        am = None
        if "--amenity" in a:
            k = a.index("--amenity"); am = a[k + 1]; del a[k:k + 2]
        airbnb_ids(a, am)
    elif cmd == "airbnb-photos":
        airbnb_photos()
    elif cmd == "locationz-all":
        locationz_all()
    elif cmd == "sheets":
        sheets()
    elif cmd == "screen":
        screen(a[0])
    elif cmd == "top":
        top(float(a[0]) if a else 5)
    elif cmd == "show":
        show(a[0], a[1:])
