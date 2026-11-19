# Contact sheet of a video: one tile every 1/fps seconds, each labelled with its time.
# Usage: python3 -I contact_sheet.py video.mp4 sheet.png 2
# Requires: Pillow, ffmpeg on PATH

import sys, glob, os, subprocess, tempfile
from PIL import Image, ImageDraw
video, out, fps = sys.argv[1], sys.argv[2], float(sys.argv[3])
d = tempfile.mkdtemp()
subprocess.run(["ffmpeg", "-v", "error", "-i", video, "-vf", f"fps={fps},scale=640:-1", os.path.join(d, "f_%04d.png")], check=True)
fs = sorted(glob.glob(os.path.join(d, "f_*.png")))
tiles = [Image.open(f).convert("RGB") for f in fs]
w, h = tiles[0].size
cols = 4
rows = (len(tiles) + cols - 1) // cols
S = Image.new("RGB", (w * cols, h * rows))
for i, t in enumerate(tiles):
    ImageDraw.Draw(t).text((6, 4), f"{i / fps:.1f}s", fill=(255, 40, 40))
    S.paste(t, ((i % cols) * w, (i // cols) * h))
S.save(out)
print(len(tiles), "frames", S.size)
