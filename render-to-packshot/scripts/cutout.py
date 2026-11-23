# Transparent cutout of the re-skin, from a user mask or a mask derived from the render.
# Usage: python3 -I cutout.py canvas.png reskin.png out.png [mask.png]
# Requires: numpy, Pillow, scipy

import sys
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

# canvas = the (padded) render sent to the model; mask = optional user mask
canvas_path, reskin_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
mask_path = sys.argv[4] if len(sys.argv) > 4 else None

canvas = Image.open(canvas_path).convert("RGB")
reskin = Image.open(reskin_path).convert("RGB")
W, H = canvas.size

if mask_path:
    m = Image.open(mask_path)
    if m.mode in ("RGBA", "LA") and np.asarray(m.split()[-1]).min() < 250:
        m = m.split()[-1]                      # alpha PNG: subject = opaque
    else:
        m = m.convert("L")
        a = np.asarray(m)
        corners = np.concatenate([a[:20, :20].ravel(), a[:20, -20:].ravel(), a[-20:, :20].ravel(), a[-20:, -20:].ravel()])
        if corners.mean() > 127:               # white background, black subject
            m = Image.fromarray(255 - a)
    # fit the mask into the canvas exactly like pad_to_ratio.py (centred, no crop)
    s = min(W / m.width, H / m.height)
    m = m.resize((round(m.width * s), round(m.height * s)), Image.LANCZOS)
    full = Image.new("L", (W, H), 0)
    full.paste(m, ((W - m.width) // 2, (H - m.height) // 2))
    alpha = full
    source = "user mask"
else:
    a = np.asarray(canvas).astype(int)
    bg = a[5:30, 5:30].reshape(-1, 3).mean(axis=0)
    m = np.abs(a - bg).sum(axis=2) > 12
    m = ndimage.binary_closing(m, iterations=3)
    m = ndimage.binary_fill_holes(m)
    lab, n = ndimage.label(m)
    m = lab == (np.argmax(ndimage.sum(m, lab, range(1, n + 1))) + 1)
    m = ndimage.binary_erosion(m, iterations=max(1, round(min(W, H) / 1000)))
    alpha = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(min(W, H) / 2000))
    source = "derived from render"

alpha = alpha.resize(reskin.size, Image.LANCZOS)
out = reskin.copy()
out.putalpha(alpha)
out.save(out_path)

base = out_path.rsplit(".", 1)[0]
for name, col in (("red", (200, 30, 30)), ("dark", (30, 30, 30))):
    p = Image.new("RGB", out.size, col)
    p.paste(out, (0, 0), out)
    p.save(f"{base}_preview_{name}.png")
print("mask:", source, "| output", out.size, "| previews:", base + "_preview_red.png", base + "_preview_dark.png")
