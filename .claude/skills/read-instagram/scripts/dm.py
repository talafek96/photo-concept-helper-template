"""Read an Instagram DM thread (text + photos she sent) through the photographer's logged-in Chrome. READ-ONLY.

  python3 .claude/skills/read-instagram/scripts/dm.py <handle | thread_url> <out_dir> [scrolls_up=6] [--session igdm]

Finds the thread the way a person does: opens her profile, presses its "Message" button (opens a small
chat popup), takes the /direct/t/<id> link from that popup and opens it full page. (ig.me/m/<handle> links
are unreliable - don't use them.) Pass a /direct/t/ URL instead of a handle to skip this.
Then scrolls up to load history, then saves <out_dir>/dm.txt (the visible conversation text, oldest first as rendered) and every
photo in the thread >=250px as <out_dir>/dm_NN.jpg.

Side effects to know: opening a thread marks it SEEN for her (Instagram read receipt). Never type, click
"Message...", send, react, or open the note composer ("Your note" / "What's on your mind?" at the top of the
inbox is a public note - don't click it). Only navigate by URL; never click inbox rows by position.
Don't commit dm.txt or the photos (models/<name>/ig/ is gitignored); summarise what matters into profile.md.
"""
import json, os, re, subprocess, sys, time, urllib.request

args = [a for a in sys.argv[1:] if not a.startswith("--")]
S = sys.argv[sys.argv.index("--session") + 1] if "--session" in sys.argv else "igdm"
if "--session" in sys.argv:
    args.remove(S)
who, out = args[0], args[1]
scrolls = int(args[2]) if len(args) > 2 else 6
os.makedirs(out, exist_ok=True)

PANE = ('(()=>{const ds=[...document.querySelectorAll("main div")].filter(d=>d.scrollHeight>d.clientHeight+100'
        '&&/auto|scroll/.test(getComputedStyle(d).overflowY)&&!d.closest("[aria-label=\\"Thread list\\"]"));'
        'ds.sort((a,b)=>b.getBoundingClientRect().left-a.getBoundingClientRect().left||b.innerText.length-a.innerText.length);'
        'return ds[0]||null})()')


def ev(js):
    o = subprocess.run(["opencli", "browser", S, "eval", js], capture_output=True, text=True).stdout
    return "\n".join(l for l in o.splitlines() if l.strip() and not re.search(r"pdate available|Download:|Run: npm", l)).strip()


def thread_url(handle):
    subprocess.run(["opencli", "browser", S, "open", f"https://www.instagram.com/{handle}/"], capture_output=True)
    time.sleep(7)
    # The button label follows the Instagram UI language: add yours to the regex if it isn't English or Hebrew.
    found = ev('(()=>{const b=[...document.querySelectorAll("main div[role=\\"button\\"]")].find(e=>/^(Message|שליחת הודעה|הודעה)$/.test(e.innerText.trim()));'
               'if(!b)return "none";b.setAttribute("data-pch-msg","1");return "ok"})()')
    if "ok" not in found:
        sys.exit("no Message button on the profile (not logged in, or the account doesn't accept messages)")
    subprocess.run(["opencli", "browser", S, "click", "[data-pch-msg]"], capture_output=True)
    for _ in range(10):
        time.sleep(2)
        h = ev('(()=>{const a=document.querySelector("a[href*=\\"/direct/t/\\"]");return a?a.getAttribute("href"):""})()')
        if "/direct/t/" in h:
            return "https://www.instagram.com" + h.strip()
    sys.exit("Message popup opened but no thread link appeared")


url = who if who.startswith("http") else thread_url(who.lstrip("@"))
subprocess.run(["opencli", "browser", S, "open", url], capture_output=True); time.sleep(9)
for _ in range(scrolls):
    ev(f'(()=>{{const p={PANE};if(p)p.scrollTop=0;return 1}})()'); time.sleep(3)
d = json.loads(ev(f'(()=>{{const p={PANE};if(!p)return JSON.stringify({{err:"no thread pane"}});'
                  'const imgs=[...new Set([...p.querySelectorAll("img")].filter(i=>i.naturalWidth>=250).map(i=>i.currentSrc||i.src))];'
                  'const h=document.querySelector("main header, main [role=banner]");'
                  'return JSON.stringify({url:location.href,text:p.innerText,imgs})})()') or '{"err":"eval failed"}')
if d.get("err"):
    # An empty thread (never messaged) has no scrollable message pane.
    open(os.path.join(out, "dm.txt"), "w").write(url + "\n\n(no messages in this thread)\n")
    sys.exit(print(f"{url}: no messages found (empty thread, or the page didn't load - check with a screenshot)"))
open(os.path.join(out, "dm.txt"), "w").write(d["url"] + "\n\n" + d["text"])
n = 0
for src in d["imgs"]:
    try:
        data = urllib.request.urlopen(urllib.request.Request(src, headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read()
        n += 1
        open(os.path.join(out, f"dm_{n:02d}.jpg"), "wb").write(data)
    except Exception as e:
        print("dl fail", e, file=sys.stderr)
print(f"{d['url']}: {len(d['text'])} chars, {n} photos -> {out}")
