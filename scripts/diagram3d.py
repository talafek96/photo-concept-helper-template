"""3D illustrated lighting diagram (default style: cream paper, ink line-art, 3/4 perspective, realistic grey
gear, translucent coloured beams, bold uppercase labels + dashed arrows; the style one photographer picked).
Style refs: every image in references/diagram-style/ (drop 2-3 diagrams in the style YOU want there; with none,
the STYLE text below is used alone). Gear product photos for --gear: references/gear-photos/.
Full workflow: .claude/skills/lighting-diagram/SKILL.md.

Fresh render (geometry comes from the layout blockout, not from text alone):
  python3 scripts/diagram3d.py <out.png> <prompt.txt> --layout <blockout.png> [--photo <frame.png>]
          [--loc <real_photo.jpg> ...] [--gear <product_photo.jpg> ...]
Small fix on a render that is already right in geometry (keeps everything else):
  python3 scripts/diagram3d.py <out.png> <edit.txt> --edit <draft.png> [--photo <crop.png>] [--gear ...]

<prompt.txt> holds ONLY the view, scene geometry, each object and the exact label texts (template:
.claude/skills/lighting-diagram/references/prompt-template.md). The style text, the style refs and a sentence
naming every attached image in order are added here, so the prompt never has to count images ("the FOURTH image").
Lessons (Nov 2026): editing a flawed draft keeps its geometry errors - regenerate fresh;
never feed a diagram into the photo generation (it mirrored the pose and invented architecture).
"""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SD = os.path.join(REPO, "references/diagram-style")
STYLE_REFS = sorted(os.path.join(_SD, f) for f in (os.listdir(_SD) if os.path.isdir(_SD) else [])
                    if f.lower().endswith((".jpg", ".jpeg", ".png")))[:3]
STYLE = ("Draw a photographer's LIGHTING DIAGRAM (if style-reference images are attached, in EXACTLY their style): warm cream "
         "paper with subtle texture; the scene as black ink line-art with soft pencil shading in perspective "
         "(not top-down); people as line-art with only light colour washes; lighting gear and camera as "
         "realistic dark-grey shaded objects on their stands; each light as a translucent soft-edged coloured beam "
         "from the modifier to exactly what it hits; labels: BOLD UPPERCASE heading, regular-weight details below, "
         "thin dashed curved arrow to the object. Lots of cream space, no frame, no watermark, no text other than "
         "the labels given.\n\n")
ROLES = {
    "style": "a STYLE reference only (copy the drawing style, not its scene, gear or text)",
    "layout": "a crude LAYOUT BLOCKOUT rendered from the exact viewpoint of this diagram: copy every position, "
              "height, the walls and the perspective from it; the dashed rectangle, if any, is the real lens frame",
    "photo": "the photo this diagram explains: copy the people's pose, costumes and look from it (not its camera angle)",
    "loc": "a real photo of the location: copy the real architecture, materials and details",
    "gear": "a product photo of a piece of gear in the scene: draw that object with this shape",
    "edit": "the DRAFT diagram to edit",
}


def attachments(refs):
    lines = [f"Image {i}: {ROLES[role]}." for i, (role, _) in enumerate(refs, 1)]
    return "ATTACHED IMAGES, in order:\n" + "\n".join(lines) + "\n\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out"); ap.add_argument("prompt")
    ap.add_argument("--layout"); ap.add_argument("--photo"); ap.add_argument("--edit")
    ap.add_argument("--loc", nargs="*", default=[]); ap.add_argument("--gear", nargs="*", default=[])
    ap.add_argument("--aspect", default="4:5"); ap.add_argument("--provider", default="google")  # openrouter = same model
    a = ap.parse_args()
    body = open(a.prompt).read()
    if a.edit:
        refs = [("edit", a.edit)]
        head = ("EDIT image 1 (a finished lighting diagram). Keep EVERYTHING exactly the same - style, viewpoint, "
                "walls, every light, stand, beam, the camera and ALL text - except the changes listed below.\n\n")
        style = ""
    else:
        if not a.layout:
            print("warning: no --layout blockout; positions will drift (make one with "
                  ".claude/skills/lighting-diagram/scripts/blockout.py)", file=sys.stderr)
        refs = [("style", p) for p in STYLE_REFS] + ([("layout", a.layout)] if a.layout else [])
        head, style = "", STYLE
    refs += ([("photo", a.photo)] if a.photo else []) + [("loc", p) for p in a.loc] + [("gear", p) for p in a.gear]
    prompt = head + style + attachments(refs) + body
    ok = gen.generate(a.out, prompt, [p for _, p in refs], a.provider, a.aspect, force=True)
    print(a.out if ok else "FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
