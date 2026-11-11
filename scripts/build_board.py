"""Render a shoot's board from shoots/<shoot>/board/board.json -> board/index.html (any language, RTL or LTR).

  python3 scripts/build_board.py shoots/<shoot>

Images the page references live in shoots/<shoot>/board/img/:
  <slug>-NN.jpg   AI frames  (python3 scripts/sheet.py shoots/<shoot>/boards/<slug> --web shoots/<shoot>/board/img <slug>)
  ref-*.jpg       real location photos (Commons, with credit fields filled in board.json)
Publish with the Artifact tool: file_path = board/index.html, root = board/, files = the img/ list printed below.
The design (tokens, dark mode, treatment-book layout, lightbox) was approved on earlier boards - keep it;
per-chapter accent colours come from board.json. Worked example: templates/board/example-board.json.

Language: "lang" + "dir" set the page. UI labels ("Storyboard", "Camera", "Signature frame"...) come from
STRINGS below for "he" and "en" (any other lang falls back to English); override any of them, or supply a
whole new language, with a "strings" object in board.json using the same keys.

board.json schema (all text is HTML-safe already; write it in the board language):
{
  "title": "Maya: Night Swim",               # <title>, 2-4 words
  "lang": "en", "dir": "ltr",                # e.g. "he"/"rtl"
  "strings": {"storyboard": "..."},          # optional UI label overrides (keys: see STRINGS)
  "real_tag": "Real photo", "ai_tag": "AI sketch",   # optional; default from STRINGS
  "label": "Concept board · photographer × producer × Maya · shoot window: <month year>",
  "h1": "Maya", "h1_sub": "/ Night Swim",
  "strip": ["nightswim-05.jpg", ...],        # 3 hero frames for the masthead
  "intro": ["<p text>", ...],
  "overview": {"head": ["Concept","Where","When","Look"], "rows": [["<a href='#slug'>..</a>", ...], ...]},   # optional
  "chapters": [{
     "slug": "nightswim", "accent": "#2F5E8C", "accent_dark": "#7FA9D6",
     "num": "01", "title": "Night Swim", "title_lang": "en", "trans": "translation", "logline": "...",
     "hero": 5,                               # frame number used as the chapter hero; title_lang defaults to the board lang
     "real_title": "How it really looks", "real": ["paragraph", ...],
     "photos": [{"file": "ref-colony-01.jpg", "cap": "...", "year": "2024", "artist": "...", "license": "CC BY-SA 4.0", "page": "https://commons..."}],
     "places": [{"name": "...", "meta": "...", "url": "<maps url>", "body": "...", "pick": true}],
     "logistics": "...",
     "root": {"label": "The root", "quote": "...", "quote_lang": "en", "text": "..."},   # optional
     "frames": [{"title": "...", "action": "...", "camera": "...", "sig": false, "label": "",
                 "light": "<svg or <img> of THIS frame's light plan>", "light_text": [["Key", "..."], ...]}],  # light optional
     "diagram": "<svg ...>",                  # optional, from scripts/diagram.py
     "prod": [["Styling", "..."], ["Light with your kit", "..."], ["Logistics", "..."]]
  }],
  "sections": [{"id": "plan", "h2": "Shoot-day plan", "html": "<div class='cols'>...</div>"}],
  "tabs": [{"id": "city", "label": "City", "chapters": ["slug", ...], "overview": true, "intro": "..."},   # optional:
           {"id": "plan", "label": "Shoot day", "section": "plan"}]   # sticky tab bar, one panel per tab, #hash routing
}
"""
import html, json, os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
E = html.escape

STRINGS = {
    "he": {"real_tag": "צילום אמיתי", "ai_tag": "סקיצת AI", "photo_by": "צילום:", "pick": "נקודת הצילום",
           "sig": "פריים חתימה", "camera": "מצלמה", "action": "פעולה", "frame": "פריים",
           "real_title": "איך זה נראה במציאות", "diagram": "דיאגרמת תאורה", "storyboard": "סטוריבורד",
           "frames_hint": "פריימים · לחצו להגדלה", "overview": "במבט אחד", "toc": "תוכן",
           "lightbox": "תצוגה מוגדלת", "open_frame": "פתיחת פריים",
           "light_for": "תאורה לפריים", "chapters": "פרקים", "tabs": "לשוניות"},
    "en": {"real_tag": "Real photo", "ai_tag": "AI sketch", "photo_by": "Photo:", "pick": "Shooting spot",
           "sig": "Signature frame", "camera": "Camera", "action": "Action", "frame": "Frame",
           "real_title": "How it really looks", "diagram": "Lighting diagram", "storyboard": "Storyboard",
           "frames_hint": "frames · click to enlarge", "overview": "At a glance", "toc": "Contents",
           "lightbox": "Enlarged view", "open_frame": "Open frame",
           "light_for": "Light for frame", "chapters": "Chapters", "tabs": "Tabs"},
}
T = dict(STRINGS["en"])   # set per board in build()


def fig(p, real_tag):
    year = f" ({p['year']})" if p.get("year") else ""
    credit = ""
    if p.get("artist"):
        lic = f'<a href="{E(p.get("page", ""))}">{E(p.get("license", ""))}</a>' if p.get("page") else E(p.get("license", ""))
        credit = f' · {T["photo_by"]} <span dir="auto">{E(p["artist"])}</span>, {lic}'
    return (f'<figure><img src="img/{p["file"]}" alt="{E(p["cap"])}" loading="lazy">'
            f'<figcaption><span class="tag real">{real_tag}</span> {p["cap"]}{year}{credit}</figcaption></figure>')


def place(i, p):
    pick = f' <span class="pick">{T["pick"]}</span>' if p.get("pick") else ""
    m = f'<a class="map" href="{E(p["url"])}">Google Maps ↗</a>' if p.get("url") else ""
    return (f'<div class="place"><div class="meta"><h4><span class="rank">{i:02d}</span> {p["name"]}{pick}</h4><span>{p.get("meta", "")}</span>'
            f'{m}</div><div class="body"><p>{p.get("body", "")}</p></div></div>')


def shot(slug, n, f, ai_tag):
    nn = f"{n:02d}"
    s = f'<span class="sig">{T["sig"]}</span>' if f.get("sig") else ""
    cam = f'<dt>{T["camera"]}</dt><dd>{f["camera"]}</dd>' if f.get("camera") else ""
    lab = f' · {f["label"]}' if f.get("label") else ""
    lt = ""
    if f.get("light"):  # the light plan belongs to THIS frame and sits right under it
        rows = "".join(f"<dt>{h}</dt><dd>{t}</dd>" for h, t in f.get("light_text", []))
        lt = (f'<div class="shot-light"><h5>{T["light_for"]} {nn}</h5><div class="sl-grid"><div class="sl-svg">{f["light"]}</div>'
              f'<dl class="sl-text">{rows}</dl></div></div>')
    return (f'<div class="shot"><img src="img/{slug}-{nn}.jpg" alt="{T["frame"]} {n}: {E(re.sub("<[^>]+>", "", f["title"]))}" loading="lazy">'
            f'<div class="shot-text">{s}<span class="shot-no">{nn}{lab}</span><h4>{f["title"]}</h4><dl><dt>{T["action"]}</dt><dd>{f["action"]}</dd>{cam}</dl></div>{lt}</div>')


def chapter(c, real_tag, ai_tag):
    slug, n = c["slug"], len(c["frames"])
    real = ""
    if c.get("real") or c.get("photos") or c.get("places"):
        real = (f'<div class="loc"><h3 style="font-size:24px">{c.get("real_title", T["real_title"])}</h3>'
                f'<div class="realtext">{"".join(f"<p>{p}</p>" for p in c.get("real", []))}</div>'
                f'<div class="loc-photos">{"".join(fig(p, real_tag) for p in c.get("photos", []))}</div>'
                f'<div class="places">{"".join(place(i + 1, p) for i, p in enumerate(c.get("places", [])))}</div>'
                f'<p class="muted">{c.get("logistics", "")}</p></div>')
    root = ""
    if c.get("root"):
        r = c["root"]
        root = (f'<div class="heritage"><span class="label">{r.get("label", "")}</span>'
                f'<p class="quote" lang="{r["quote_lang"]}">{r.get("quote", "")}</p><p>{r.get("text", "")}</p></div>')
    diagram = f'<div class="diagram-wrap"><h3>{T["diagram"]}</h3>{c["diagram"]}</div>' if c.get("diagram") else ""
    prod = "".join(f"<div><h3>{h}</h3><p>{t}</p></div>" for h, t in c.get("prod", []))
    return f'''
<article class="chapter" data-c="{slug}" id="{slug}">
  <div class="ch-head">
    <div class="ch-num">{c.get("num", "")}</div>
    <h2 class="ch-title" lang="{c["title_lang"]}">{c["title"]}</h2>
    <p class="ch-trans">{c.get("trans", "")}</p>
    <p class="logline">{c.get("logline", "")}</p>
  </div>
  <img class="hero" src="img/{slug}-{c.get("hero", 1):02d}.jpg" alt="{E(c["title"])}">
  {real}
  {root}
  <div class="board">
    <div class="board-head"><h3>{T["storyboard"]}</h3><span class="tag ai">{ai_tag} · {n} {T["frames_hint"]}</span></div>
    <div class="contact" data-set="{slug}" data-count="{n}"></div>
    <div class="shots">{"".join(shot(slug, i + 1, f, ai_tag) for i, f in enumerate(c["frames"]))}</div>
  </div>
  {diagram}
  <div class="prod">{prod}</div>
</article>'''


def accents(chs):
    out = []
    for c in chs:
        if c.get("accent"):
            out.append(f'.chapter[data-c="{c["slug"]}"]{{--accent:{c["accent"]}}}')
        if c.get("accent_dark"):
            out.append(f'@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]) .chapter[data-c="{c["slug"]}"]{{--accent:{c["accent_dark"]}}}}}')
            out.append(f':root[data-theme="dark"] .chapter[data-c="{c["slug"]}"]{{--accent:{c["accent_dark"]}}}')
    return "\n".join(out)


def build(shoot):
    bd = os.path.join(shoot, "board")
    b = json.load(open(os.path.join(bd, "board.json")))
    T.clear(); T.update(STRINGS.get(b.get("lang", "en"), STRINGS["en"])); T.update(b.get("strings", {}))
    css = open(os.path.join(REPO, "templates", "board", "board.css")).read()
    extra = (".realtext{display:grid;gap:10px;max-width:76ch}.loc-photos figure img{cursor:zoom-in}figcaption a{color:inherit}"
             ".diagram-wrap{margin:28px 0}.diagram-wrap svg{width:100%;max-width:640px;height:auto;display:block}"
             ".shot-light{grid-column:1/-1;border-top:2px solid var(--accent);padding-top:14px}.shot-light h5{font-size:17px;font-weight:800;margin:0 0 10px}"
             ".sl-grid{display:grid;grid-template-columns:1fr;gap:16px;align-items:start}"
             ".sl-svg svg{width:100%;height:auto;display:block}.sl-text{margin:0;display:grid;grid-template-columns:auto 1fr;gap:8px 14px;font-size:15px}"
             ".sl-text dt{font-size:13px;font-weight:700;color:var(--muted);padding-top:2px}.sl-text dd{margin:0}"
             "@media (max-width:760px){.sl-grid{grid-template-columns:1fr}}"
             # tabs (optional board["tabs"]): sticky bar, one panel per tab, chapter chips per panel
             "body::before{content:'';position:fixed;inset:0 0 auto;height:env(safe-area-inset-top,0px);z-index:10;background:var(--bg)}"
             ".tabbar{position:sticky;top:env(safe-area-inset-top,0px);z-index:9;background:var(--bg);border-bottom:1px solid var(--line);"
             "display:flex;gap:6px;overflow-x:auto;padding-block:10px;margin-bottom:8px;scrollbar-width:none}"
             ".tabbar a{flex:0 0 auto;text-decoration:none;color:var(--ink);font-weight:700;font-size:15px;padding:8px 14px;border-radius:999px;border:1px solid var(--line)}"
             ".tabbar a[aria-current=page]{background:var(--ink);color:var(--bg);border-color:var(--ink)}"
             ".chips{display:flex;flex-wrap:wrap;gap:8px;margin:6px 0 22px}.chips a{font-size:14px;text-decoration:none;color:var(--ink);"
             "padding:5px 12px;border-radius:999px;background:var(--surface);border:1px solid var(--line)}.chips a:hover{border-color:var(--ink)}"
             ".tabpanel>.tab-intro{max-width:76ch;margin-bottom:10px}.tabpanel>h2.tab-h{font-size:30px;font-weight:800;margin:18px 0 6px}.tabpanel .chapter{scroll-margin-top:70px}.tabpanel{scroll-margin-top:70px}")
    real_tag, ai_tag = b.get("real_tag", T["real_tag"]), b.get("ai_tag", T["ai_tag"])
    chs = b["chapters"]
    for c in chs:  # titles/quotes default to the board language (a hardcoded default once mis-tagged every title)
        c.setdefault("title_lang", b.get("lang", "en"))
        if c.get("root"):
            c["root"].setdefault("quote_lang", c["title_lang"])
    ov = ""
    if b.get("overview"):
        o = b["overview"]
        ov = (f'<section class="block" id="overview"><h2>{o.get("h2", T["overview"])}</h2><div class="tablewrap"><table><thead><tr>'
              + "".join(f"<th>{h}</th>" for h in o["head"]) + "</tr></thead><tbody>"
              + "".join("<tr>" + "".join(f"<td>{x}</td>" for x in r) + "</tr>" for r in o["rows"]) + "</tbody></table></div></section>")
    secs = "".join(f'<section class="block" id="{s["id"]}"><h2>{s["h2"]}</h2>{s["html"]}</section>' for s in b.get("sections", []))
    toc = "".join(f'<a href="#{c["slug"]}" lang="{c["title_lang"]}">{c["title"]}</a>' for c in chs) + \
        "".join(f'<a href="#{s["id"]}">{s["h2"]}</a>' for s in b.get("sections", []))
    strip = "".join(f'<img src="img/{s}" alt="">' for s in b.get("strip", []))
    body = f"{ov}\n" + "".join(chapter(c, real_tag, ai_tag) for c in chs) + f"\n{secs}"
    tabbar = ""
    if b.get("tabs"):  # true tabs: each tab is a panel; hash routing (#tabid or #chapter-slug) shows the right panel
        by = {c["slug"]: c for c in chs}
        secd = {x["id"]: x for x in b.get("sections", [])}
        panels = []
        for t in b["tabs"]:
            inner = f'<h2 class="tab-h">{t["label"]}</h2>'
            if t.get("intro"):
                inner += f'<div class="tab-intro prose">{t["intro"]}</div>'
            if t.get("chapters"):
                inner += f'<nav class="chips" aria-label="{T["chapters"]}">' + "".join(
                    f'<a href="#{sl}">{by[sl]["num"].split("·")[0].strip()} {by[sl]["title"]}</a>' for sl in t["chapters"]) + "</nav>"
                if t.get("overview") and b.get("overview"):
                    o = b["overview"]; rows = [r for r in o["rows"] if any(f"#{sl}'" in r[0] for sl in t["chapters"])]
                    inner += ('<div class="tablewrap"><table><thead><tr>' + "".join(f"<th>{h}</th>" for h in o["head"]) + "</tr></thead><tbody>"
                              + "".join("<tr>" + "".join(f"<td>{x}</td>" for x in r) + "</tr>" for r in rows) + "</tbody></table></div>")
                inner += "".join(chapter(by[sl], real_tag, ai_tag) for sl in t["chapters"])
            if t.get("section"):
                inner += secd[t["section"]]["html"]
            panels.append(f'<section class="tabpanel" id="{t["id"]}" data-tab>{inner}</section>')
        body = "".join(panels)
        tabbar = f'<nav class="tabbar" aria-label="{T["tabs"]}">' + "".join(f'<a href="#{t["id"]}" data-tablink="{t["id"]}">{t["label"]}</a>' for t in b["tabs"]) + "</nav>"
    page = f'''<title>{E(b["title"])}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;600;700;800&family=Be+Vietnam+Pro:ital,wght@0,300;0,400;0,700;0,800;1,300&display=swap">
<style>{css}
{extra}
{accents(chs)}</style>
<div class="wrap" dir="{b.get("dir", "ltr")}" lang="{b.get("lang", "en")}">
<header class="mast">
  <div class="label">{b.get("label", "")}</div>
  <h1>{b.get("h1", "")} <span>{b.get("h1_sub", "")}</span></h1>
  <div class="mast-strip">{strip}</div>
  <div class="prose">{"".join(f"<p>{p}</p>" for p in b.get("intro", []))}</div>
  {"" if b.get("tabs") else f'<nav class="toc" aria-label="{T["toc"]}">{toc}</nav>'}
</header>
{tabbar}
{body}
</div>
<dialog id="lb" aria-label="{T["lightbox"]}"><img alt=""><p></p></dialog>
<script>
(() => {{
  const lb = document.getElementById('lb'), lbImg = lb.querySelector('img'), lbCap = lb.querySelector('p');
  function open(src, cap){{ lbImg.src = src; lbCap.textContent = cap; lb.showModal(); }}
  document.querySelectorAll('.contact').forEach(c => {{
    const set = c.dataset.set, count = +(c.dataset.count || 6);
    for (let i = 1; i <= count; i++) {{
      const n = String(i).padStart(2, '0'), b = document.createElement('button');
      b.setAttribute('aria-label', '{T["open_frame"]} ' + n);
      b.innerHTML = `<img src="img/${{set}}-${{n}}.jpg" alt="" loading="lazy"><span>${{n}}</span>`;
      b.addEventListener('click', () => open(`img/${{set}}-${{n}}.jpg`, '{T["frame"]} ' + n + ' · {ai_tag}'));
      c.appendChild(b);
    }}
  }});
  document.querySelectorAll('.shot img, .hero, .mast-strip img').forEach(img =>
    img.addEventListener('click', () => open(img.getAttribute('src'), (img.alt || '') + ' · {ai_tag}')));
  document.querySelectorAll('.loc-photos img').forEach(img =>
    img.addEventListener('click', () => open(img.getAttribute('src'), img.closest('figure').querySelector('figcaption').textContent)));
  lb.addEventListener('click', () => lb.close());
  const panels = [...document.querySelectorAll('[data-tab]')];
  if (panels.length) {{
    const links = [...document.querySelectorAll('[data-tablink]')];
    function route() {{
      const id = decodeURIComponent(location.hash.slice(1));
      let el = id && document.getElementById(id);
      let panel = el && (el.matches('[data-tab]') ? el : el.closest('[data-tab]'));
      if (!panel) panel = panels[0];
      panels.forEach(p => p.hidden = p !== panel);
      links.forEach(a => a.dataset.tablink === panel.id ? a.setAttribute('aria-current', 'page') : a.removeAttribute('aria-current'));
      const target = (el && el !== panel) ? el : panel;
      if (id) requestAnimationFrame(() => target.scrollIntoView({{block: 'start'}}));
    }}
    window.addEventListener('hashchange', route); route();
  }}
}})();
</script>
'''
    open(os.path.join(bd, "index.html"), "w").write(page)
    used = sorted(set(re.findall(r'img/([\w.-]+\.jpg)', page)) | {f"{c['slug']}-{i:02d}.jpg" for c in chs for i in range(1, len(c["frames"]) + 1)})
    missing = [u for u in used if not os.path.exists(os.path.join(bd, "img", u))]
    json.dump(["img/" + u for u in used], open(os.path.join(bd, "used.json"), "w"), indent=0)
    print(os.path.join(bd, "index.html"), len(page), "bytes,", len(used), "images")
    if missing:
        print("MISSING images:", missing)



if __name__ == "__main__":
    build(sys.argv[1].rstrip("/"))
