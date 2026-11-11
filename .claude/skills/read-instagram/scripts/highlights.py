"""Download a model's story highlights (every item, full size) through the photographer's logged-in Chrome. READ-ONLY.

  python3 .claude/skills/read-instagram/scripts/highlights.py <username> <out_dir> [--session ig]

How: opens the profile, reads the highlight links from the header (a[href*="/stories/highlights/"]),
then opens each https://www.instagram.com/stories/highlights/<id>/ URL. Instagram embeds the WHOLE reel
in that page's JSON (xdt_api__v1__feed__reels_media__connection -> node.items), so nothing is clicked:
the "View story" gate stays closed and no item is played or marked seen. Videos come in as their cover
frame (video=true) plus the video URL in the JSON.

Output: <out_dir>/<NN>_<k>.jpg and <out_dir>/highlights.json
  [{id, title, items:[{file, taken_at, video, video_url, alt, mentions, links}]}]
Then: python3 scripts/sheet.py <out_dir> and LOOK. Highlights are often older than the feed and show
her life outside the latest phase (hobbies, stage work, paid-content links).
Research material only: gitignored, never published.
"""
import json, os, re, subprocess, sys, time, urllib.request

args = [a for a in sys.argv[1:] if not a.startswith("--")]
S = sys.argv[sys.argv.index("--session") + 1] if "--session" in sys.argv else "ig"
if "--session" in sys.argv:
    args.remove(S)
user, out = args[0].lstrip("@"), args[1]
os.makedirs(out, exist_ok=True)

REEL_JS = r'''(()=>{const ID="highlight:__ID__";let hit=null;
const walk=o=>{if(hit||!o||typeof o!=="object")return;if(o.id===ID&&Array.isArray(o.items)){hit=o;return}for(const k in o)walk(o[k])};
for(const s of document.querySelectorAll('script[type="application/json"]')){if(!s.textContent.includes(ID))continue;try{walk(JSON.parse(s.textContent))}catch(e){}if(hit)break}
if(!hit)return JSON.stringify({err:"notfound"});
const best=m=>{const c=(m.image_versions2||{}).candidates||[];c.sort((a,b)=>b.width*b.height-a.width*a.height);return c[0]?c[0].url:null};
const vid=m=>{const v=m.video_versions||[];v.sort((a,b)=>(b.width||0)-(a.width||0));return v[0]?v[0].url:null};
return JSON.stringify({id:hit.id,title:hit.title||"",items:hit.items.map(m=>({url:best(m),video:!!m.video_versions,video_url:vid(m),
taken_at:m.taken_at,alt:m.accessibility_caption||"",
mentions:(m.reel_mentions||[]).map(r=>(r.user||{}).username).filter(Boolean),
links:(m.story_link_stickers||[]).map(l=>((l.story_link||{}).url)||"").filter(Boolean)}))})})()'''


def ev(js):
    o = subprocess.run(["opencli", "browser", S, "eval", js], capture_output=True, text=True).stdout
    return "\n".join(l for l in o.splitlines() if l.strip() and not re.search(r"pdate available|Download:|Run: npm", l)).strip()


def opn(url, wait):
    subprocess.run(["opencli", "browser", S, "open", url], capture_output=True)
    time.sleep(wait)


opn(f"https://www.instagram.com/{user}/", 7)
hl = json.loads(ev('JSON.stringify([...new Map([...document.querySelectorAll("a[href*=\\"/stories/highlights/\\"]")]'
                   '.map(a=>[a.getAttribute("href").split("/").filter(Boolean).pop(),a.innerText.trim()])).entries()])') or "[]")
print(len(hl), "highlights", flush=True)

res = []
for n, (hid, label) in enumerate(hl, 1):
    opn(f"https://www.instagram.com/stories/highlights/{hid}/", 8)
    try:
        d = json.loads(ev(REEL_JS.replace("__ID__", hid)))
    except Exception:
        d = {"err": "eval"}
    if d.get("err"):
        print(hid, label, "skip:", d["err"], flush=True)
        continue
    d["title"] = d["title"] or label
    for k, it in enumerate(d["items"], 1):
        if not it["url"]:
            continue
        try:
            data = urllib.request.urlopen(urllib.request.Request(it["url"], headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read()
            it["file"] = f"{n:02d}_{k:02d}.jpg"
            open(os.path.join(out, it["file"]), "wb").write(data)
        except Exception as e:
            print("dl fail", hid, k, e, file=sys.stderr)
        del it["url"]
    res.append(d)
    json.dump(res, open(os.path.join(out, "highlights.json"), "w"), ensure_ascii=False, indent=1)
    print(f"{n:02d} {d['title']}: {len(d['items'])} items", flush=True)
print("done ->", out)
