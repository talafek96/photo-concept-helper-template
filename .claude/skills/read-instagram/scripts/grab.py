"""Download a model's Instagram posts (every carousel slide, full resolution) through the photographer's logged-in Chrome.

  python3 .claude/skills/read-instagram/scripts/grab.py <username> <out_dir> [max_posts=36] [--session ig]

How: opens the profile in the OpenCLI browser bridge, scrolls to collect the profile's own post links,
then opens each post and reads the post JSON that Instagram embeds in the page (post.js (next to this script)):
all slides at the largest size, caption, likes, comment count, tagged users. Videos/reels: the cover
frame is saved and marked video=true. Scraping <img> tags does NOT work (it catches the profile grid and
"more posts" thumbnails, i.e. other people's photos) - don't go back to that.

Output: <out_dir>/<code>_<k>.jpg and <out_dir>/posts.json (merged across runs; existing posts skipped).
Then: python3 scripts/sheet.py <out_dir> and LOOK. Posts may include other models or the photographer's
work (check `owner`, `caption` credits): pick identity refs only from photos that are clearly her.
Needs: `opencli doctor` -> Extension connected. ~7s per post; >15 posts -> run as a background job.
Research material only: gitignored, never published.
"""
import json, os, re, subprocess, sys, time, urllib.request

args = [a for a in sys.argv[1:] if not a.startswith("--")]
S = sys.argv[sys.argv.index("--session") + 1] if "--session" in sys.argv else "ig"
if "--session" in sys.argv:
    args.remove(S)
user, out = args[0].lstrip("@"), args[1]
limit = int(args[2]) if len(args) > 2 else 36
POST_JS = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "post.js")).read()
os.makedirs(out, exist_ok=True)


def ev(js):
    o = subprocess.run(["opencli", "browser", S, "eval", js], capture_output=True, text=True).stdout
    return "\n".join(l for l in o.splitlines() if l.strip() and not re.search(r"pdate available|Download:|Run: npm", l)).strip()


def opn(url, wait):
    subprocess.run(["opencli", "browser", S, "open", url], capture_output=True)
    time.sleep(wait)


opn(f"https://www.instagram.com/{user}/", 7)
links = []
stall = 0
for _ in range(max(2, limit // 6)):
    before = len(links)
    got = ev('JSON.stringify([...new Set([...document.querySelectorAll("main a[href*=\\"/p/\\"],main a[href*=\\"/reel/\\"]")].map(a=>a.getAttribute("href")))])')
    try:
        for h in json.loads(got):
            code = h.strip("/").split("/")[-1]
            if code not in links:
                links.append(code)
    except Exception:
        pass
    if len(links) >= limit:
        break
    stall = stall + 1 if len(links) == before else 0
    if stall >= 3:
        break
    ev('window.scrollTo(0,document.scrollingElement.scrollHeight);1'); time.sleep(4)
if len(links) < limit:
    vis = ev("document.visibilityState")
    print(f"WARNING: profile grid stopped loading at {len(links)} posts (page visibility: {vis}). "
          "Instagram only loads more while the tab is visible - if the Mac is locked/asleep this is the "
          "ceiling. Use highlights.py for her older material and rerun grab.py when the photographer is at the Mac.",
          file=sys.stderr, flush=True)
links = links[:limit]
print(len(links), "posts", flush=True)

pj = os.path.join(out, "posts.json")
posts = json.load(open(pj)) if os.path.exists(pj) else []
have = {p["code"] for p in posts}
for code in links:
    if code in have:
        continue
    opn(f"https://www.instagram.com/p/{code}/", 7)
    try:
        d = json.loads(ev(POST_JS.replace("__CODE__", code)))
    except Exception:
        d = {"err": "eval"}
    if d.get("err"):
        print(code, "skip:", d["err"], flush=True)
        continue
    for k, it in enumerate(d["items"], 1):
        if not it["url"]:
            continue
        try:
            data = urllib.request.urlopen(urllib.request.Request(it["url"], headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read()
            open(os.path.join(out, f"{code}_{k}.jpg"), "wb").write(data)
            it["file"] = f"{code}_{k}.jpg"
        except Exception as e:
            print("dl fail", code, k, e, file=sys.stderr)
    d["url"] = f"https://www.instagram.com/p/{code}/"
    posts.append(d)
    json.dump(posts, open(pj, "w"), ensure_ascii=False, indent=1)
    print(code, len(d["items"]), "slides", "(video)" if any(i["video"] for i in d["items"]) else "", flush=True)
print("done ->", out)
