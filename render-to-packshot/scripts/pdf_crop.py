# Render one page of a PDF spec sheet to PNG, optionally cropping a box.
# Usage: python3 -I pdf_crop.py spec.pdf PAGE DPI out.png [X0 Y0 X1 Y1]
#   Without a box: writes the whole page (use a low DPI, e.g. 60, to look at it and find coordinates).
#   With a box: coordinates are in pixels of the page rendered at DPI.
# Requires: Pillow, poppler-utils (pdftoppm)
import os
import subprocess
import sys
import tempfile
from PIL import Image

pdf, page, dpi, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
box = tuple(int(v) for v in sys.argv[5:9]) if len(sys.argv) >= 9 else None

with tempfile.TemporaryDirectory() as tmp:
    prefix = os.path.join(tmp, "page")
    subprocess.run(["pdftoppm", "-r", str(dpi), "-png", "-f", str(page), "-l", str(page), pdf, prefix], check=True)
    rendered = [f for f in os.listdir(tmp) if f.endswith(".png")][0]
    im = Image.open(os.path.join(tmp, rendered)).convert("RGB")
    print("page", page, "at", dpi, "dpi:", im.size)
    if box:
        im = im.crop(box)
    im.save(out)
    print("saved", out, im.size)
