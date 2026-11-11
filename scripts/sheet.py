"""Contact sheet of a storyboard (or any folder of images) for review in one look.

  python3 scripts/sheet.py shoots/<shoot>/boards/<slug>        -> shoots/<shoot>/boards/<slug>_sheet.jpg
  python3 scripts/sheet.py <folder> --web <out_dir> <slug>     -> also writes 1600px q82 web copies <slug>-NN.jpg

Always look at the sheet AND at each frame full size before showing the photographer: face drift, wardrobe changes,
extra limbs, fake signage and wrong architecture hide at thumbnail size.
"""
import glob, os, sys
from PIL import Image, ImageDraw

d = sys.argv[1].rstrip("/")
files = sorted(glob.glob(os.path.join(d, "*.png")) + glob.glob(os.path.join(d, "*.jpg")))
W, H, C = 600, 400, 3
rows = (len(files) + C - 1) // C
sheet = Image.new("RGB", (W * C, H * rows), "white")
for i, f in enumerate(files):
    im = Image.open(f).convert("RGB"); im.thumbnail((W - 6, H - 6))
    sheet.paste(im, ((i % C) * W + 3, (i // C) * H + 3))
    dr = ImageDraw.Draw(sheet); dr.rectangle([(i % C) * W, (i // C) * H, (i % C) * W + 40, (i // C) * H + 26], fill="black")
    dr.text(((i % C) * W + 8, (i // C) * H + 6), os.path.splitext(os.path.basename(f))[0], fill="yellow")
out = d + "_sheet.jpg"
sheet.save(out, quality=82)
print(out, len(files))

if "--web" in sys.argv:
    k = sys.argv.index("--web"); od, slug = sys.argv[k + 1], sys.argv[k + 2]
    os.makedirs(od, exist_ok=True)
    for f in files:
        n = os.path.splitext(os.path.basename(f))[0]
        im = Image.open(f).convert("RGB"); im.thumbnail((1600, 1600))
        im.save(os.path.join(od, f"{slug}-{n}.jpg"), quality=82)
    print("web copies ->", od)
