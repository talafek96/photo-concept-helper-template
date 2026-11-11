"""Generate a storyboard (one image per frame) for a concept JSON.

Usage:
  python3 scripts/gen.py shoots/<shoot>/concepts/<slug>.json            # all missing frames
  python3 scripts/gen.py <concept.json> 3,5                               # only frames 3 and 5 (delete them first to redo)
  python3 scripts/gen.py <concept.json> --provider fal                    # skip Google (bold / refused content)
  python3 scripts/gen.py <concept.json> 4 --force                         # overwrite frame 4

Concept JSON (worked example: templates/concepts/example.json):
  slug, title, model (folder under models/), premise, setting, wardrobe, look, frames[],
  optional loc_refs[] (paths relative to repo root: real photos of the actual location),
  optional provider ("google" | "fal" | "openrouter"), optional aspect ("3:2" default, "2:3", "1:1"),
  optional tag (soft | editorial | bold | spicy; for the board, ignored here).

Output: shoots/<shoot>/boards/<slug>/NN.png  (the concept file's shoot folder).
Frame 1 is the anchor; frames 2+ get it as the last reference so set, wardrobe and face stay put.
Keys come from the macOS Keychain (photoprep-gemini-key, fal-key, openrouter-key) and are never printed.
A missing key just skips that provider; with no key at all, every frame fails with a clear message.
"""
import base64, glob, json, os, subprocess, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def keychain(name):
    return subprocess.run(["security", "find-generic-password", "-s", name, "-w"], capture_output=True, text=True).stdout.strip()


GOOGLE_KEY = keychain("photoprep-gemini-key")
FAL_KEY = keychain("fal-key")
OR_KEY = keychain("openrouter-key")
GOOGLE_MODEL = "gemini-3-pro-image"                  # Nano Banana Pro
FAL_MODEL = "fal-ai/bytedance/seedream/v4.5/edit"    # forgiving; safety checker off
OR_MODELS = ["google/gemini-3-pro-image-preview",   # Nano Banana Pro billed via OpenRouter: no Google daily limit
             "openai/gpt-5.4-image-2"]              # 502 "Complexity none not supported" as of Nov 2026


def model_refs(model):
    d = os.path.join(REPO, "models", model, "refs")
    refs = sorted(glob.glob(os.path.join(d, "*.jpg")) + glob.glob(os.path.join(d, "*.png")))
    if not refs:
        sys.exit(f"no identity refs in {d} - run the study-model skill first")
    return refs[:6]


def identity(model):
    p = os.path.join(REPO, "models", model, "identity.txt")
    if os.path.exists(p):
        return open(p).read().strip()
    return (f"IDENTITY: The person in this image MUST be the exact same real person shown in the attached reference photos "
            f"('{model}'): same face, eyes, brows, lips, skin, hair, build and tattoos. Do not make a generic model.")


def part_img(path):
    with open(path, "rb") as f:
        return {"inline_data": {"mime_type": "image/png" if path.endswith(".png") else "image/jpeg",
                                "data": base64.b64encode(f.read()).decode()}}


def data_uri(path):
    """fal/OpenRouter get refs inline; full-size anchor PNGs (6-8 MB each) broke the upload (Broken pipe),
    so every ref is sent as a <=1152px JPEG copy (1536 still broke on 9-ref frames)."""
    import tempfile
    small = os.path.join(tempfile.gettempdir(), "gen_ref_" + str(abs(hash(os.path.abspath(path)))) + ".jpg")
    if not os.path.exists(small) or os.path.getmtime(small) < os.path.getmtime(path):
        subprocess.run(["sips", "-Z", "1152", "-s", "format", "jpeg", "-s", "formatOptions", "80", path, "--out", small], capture_output=True)
    with open(small if os.path.exists(small) else path, "rb") as f:
        return "data:image/jpeg;base64," + base64.b64encode(f.read()).decode()


def gen_google(out, prompt, refs, aspect):
    if not GOOGLE_KEY:
        return None
    body = {"contents": [{"parts": [{"text": prompt}] + [part_img(p) for p in refs]}],
            "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": aspect, "imageSize": "2K"}}}
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GOOGLE_MODEL}:generateContent?key={GOOGLE_KEY}"
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
            d = json.load(urllib.request.urlopen(req, timeout=300))
            for c in d.get("candidates", []):
                for p in c.get("content", {}).get("parts", []):
                    if "inlineData" in p:
                        open(out, "wb").write(base64.b64decode(p["inlineData"]["data"]))
                        return out
            txt = json.dumps(d)
            print("google: no image", os.path.basename(out), txt[:300], file=sys.stderr)
            if ("SAFETY" in txt or "PROHIBITED" in txt) and attempt >= 1:
                return None   # a second refusal will not change; hand over to fal
        except Exception as e:
            msg = e.read().decode()[:2000] if hasattr(e, "read") else str(e)  # the quota metric name (per_day vs spend) comes late
            print("google err", os.path.basename(out), attempt, msg[:400], file=sys.stderr)
            if "per_day" in msg or "PerDay" in msg:
                print("!! Google daily request limit (Tier 1: 250/day per model, failed calls count) - resets in ~24h; "
                      "use --provider openrouter (same Nano Banana Pro)", file=sys.stderr)
                return None
            if "spend" in msg.lower() or "prepay" in msg.lower() or "billing" in msg.lower():
                print("!! Google monthly spend cap - ask the photographer to raise it at https://ai.studio/spend (pick the key's project)", file=sys.stderr)
                return None
        time.sleep(10 * (attempt + 1))
    return None


def gen_fal(out, prompt, refs, aspect):
    if not FAL_KEY:
        return None
    w, h = (2048, 1365) if aspect == "3:2" else (1365, 2048) if aspect == "2:3" else (2048, 2048)
    body = {"prompt": prompt, "image_urls": [data_uri(p) for p in refs], "num_images": 1,
            "enable_safety_checker": False, "image_size": {"width": w, "height": h}}
    for attempt in range(3):
        try:
            req = urllib.request.Request("https://fal.run/" + FAL_MODEL, data=json.dumps(body).encode(),
                                         headers={"Authorization": "Key " + FAL_KEY, "Content-Type": "application/json"})
            d = json.load(urllib.request.urlopen(req, timeout=600))
            if d.get("images"):
                urllib.request.urlretrieve(d["images"][0]["url"], out)
                print("fal ok", os.path.basename(out), file=sys.stderr)
                return out
            print("fal: no image", json.dumps(d)[:300], file=sys.stderr)
        except Exception as e:
            print("fal err", attempt, e.read().decode()[:300] if hasattr(e, "read") else e, file=sys.stderr)
        time.sleep(10)
    return None


def gen_openrouter(out, prompt, refs, aspect):
    if not OR_KEY:
        return None
    content = [{"type": "text", "text": prompt + f"\nOutput a single {aspect} photograph."}]
    content += [{"type": "image_url", "image_url": {"url": data_uri(p)}} for p in refs]
    for model, attempt in [(m, a) for m in OR_MODELS for a in range(2)]:
        body = {"model": model, "modalities": ["image", "text"], "messages": [{"role": "user", "content": content}],
                "image_config": {"aspect_ratio": aspect}}
        try:
            req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=json.dumps(body).encode(),
                                         headers={"Content-Type": "application/json", "Authorization": f"Bearer {OR_KEY}"})
            d = json.load(urllib.request.urlopen(req, timeout=600))
            for im in (d.get("choices") or [{}])[0].get("message", {}).get("images", []):
                open(out, "wb").write(base64.b64decode(im["image_url"]["url"].split(",", 1)[1]))
                print("openrouter ok", os.path.basename(out), file=sys.stderr)
                return out
            print("openrouter: no image", model, json.dumps(d)[:300], file=sys.stderr)
        except Exception as e:
            print("openrouter err", model, attempt, e.read().decode()[:300] if hasattr(e, "read") else e, file=sys.stderr)
        time.sleep(10)
    return None


CHAIN = {"google": [gen_google, gen_openrouter, gen_fal], "fal": [gen_fal, gen_google, gen_openrouter],
         "openrouter": [gen_openrouter, gen_fal]}


STRICT = False


def generate(out, prompt, refs, provider, aspect, force=False):
    if os.path.exists(out) and not force:
        return out
    chain = CHAIN[provider][:1] if STRICT else CHAIN[provider]
    for fn in chain:
        if fn(out, prompt, refs, aspect):
            open(out + ".src", "w").write(fn.__name__)  # which provider made it (fallbacks are weaker; review, tell the photographer)
            if fn is not chain[0]:
                print(f"!! {os.path.basename(out)}: fell back to {fn.__name__}", file=sys.stderr)
            return out
    print("FAILED", out, file=sys.stderr)
    return None


def frame_prompt(c, i, frame, anchor):
    total = len(c["frames"])
    p = (f"Create frame {i} of {total} of a continuous cinematic storyboard for a fine-art fashion photo series titled '{c['title']}'. "
         "This must look like a real photograph shot on a full-frame camera, not an illustration. No text, no captions, no borders, no watermarks.\n\n"
         f"{identity(c['model'])}\n\nSTORY SO FAR: {c['premise']}\n\nSETTING (identical in every frame): {c['setting']}\n\n"
         f"WARDROBE & HAIR (identical in every frame unless the shot says otherwise): {c['wardrobe']}\n\n"
         f"LOOK: {c['look']}\n\nTHIS FRAME ({i}/{total}): {frame}")
    if c.get("loc_refs"):
        p += (f"\n\nREAL LOCATION: after the photos of the model, the next {len(c['loc_refs'])} attached images are real photos of the actual location. "
              "Reproduce its real architecture, stone, colours, plants and details faithfully, as if shot on that exact spot; "
              "leave out cars, tourists and sign clutter. Do not copy any person from those location photos.")
    if anchor:
        p += ("\n\nThe last attached image is frame 1 of this same series: keep the same location, architecture, props, wardrobe, "
              "color grade and the same person, as if shot minutes later on the same set.")
    return p


def run(concept_file, only=None, provider=None, force=False):
    if not (GOOGLE_KEY or FAL_KEY or OR_KEY):
        sys.exit("no image API key in the Keychain (photoprep-gemini-key / fal-key / openrouter-key) - see README.md")
    c = json.load(open(concept_file))
    shoot_dir = os.path.dirname(os.path.dirname(os.path.abspath(concept_file)))
    od = os.path.join(shoot_dir, "boards", c["slug"])
    os.makedirs(od, exist_ok=True)
    provider = provider or c.get("provider", "google")
    aspect = c.get("aspect", "3:2")
    refs = model_refs(c["model"])
    loc = [os.path.join(REPO, p) for p in c.get("loc_refs", [])]
    first = os.path.join(od, "01.png")
    if not only or 1 in only:
        generate(first, frame_prompt(c, 1, c["frames"][0], False), refs + loc, provider, aspect, force and (not only or 1 in only))
    if not os.path.exists(first):
        sys.exit("frame 1 (the anchor) failed - fix it before the rest")
    jobs = []
    with ThreadPoolExecutor(4) as ex:
        for i, fr in enumerate(c["frames"][1:], start=2):
            if only and i not in only:
                continue
            out = os.path.join(od, f"{i:02d}.png")
            jobs.append(ex.submit(generate, out, frame_prompt(c, i, fr, True), refs + loc + [first], provider, aspect, force))
    print(c["slug"], [os.path.basename(j.result() or "FAILED") for j in jobs])


if __name__ == "__main__":
    args = sys.argv[1:]
    provider = None
    if "--provider" in args:
        k = args.index("--provider"); provider = args[k + 1]; del args[k:k + 2]
    force = "--force" in args
    STRICT = "--strict" in args  # no fallback: fail instead of silently using a weaker model
    args = [a for a in args if a not in ("--force", "--strict")]
    only = set(int(x) for x in args[1].split(",")) if len(args) > 1 else None
    run(args[0], only, provider, force)
