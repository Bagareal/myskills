# Stage 1 input: cut the grey product out of the scene as a plain "render" (grey on white), cropped around the
# product at the ratio the editing model will use, so it can be re-skinned like in render-reskin.
# Usage: python3 -I crop_product.py grey.png mask.png outdir RATIO [--margin 0.12] [--min-side 1024] [--max-side 2048]
#   grey    = the _grey.png of the export (grey product on transparent background)
#   mask    = the product mask (alpha PNG, or black on white / white on black); falls back to grey's alpha
#   RATIO   = width:height of the crop, e.g. 1:1 or 4:3 (a ratio the model supports)
#   margin  = free space around the product, as a fraction of its larger side (default 0.12)
#   min-side/max-side = the crop is enlarged (Lanczos) up to min-side on its long side if smaller, never above max-side
# Writes in outdir: render_crop.png (grey on pure white), mask_crop.png (white product on black, same canvas),
# crop.json (where the crop sits in the photo, and the scale). The crop may extend beyond the photo: that part is white.
# Requires: numpy, Pillow

import json
import os
import sys

import numpy as np
from PIL import Image, ImageOps


def load_mask(im):
    if im.mode in ("RGBA", "LA") and np.asarray(im.split()[-1]).min() < 250:
        m = im.split()[-1]
    else:
        m = im.convert("L")
        a = np.asarray(m)
        corners = np.concatenate([a[:20, :20].ravel(), a[:20, -20:].ravel(), a[-20:, :20].ravel(), a[-20:, -20:].ravel()])
        if corners.mean() > 127:
            m = Image.fromarray(255 - a)
    return m


def opt(args, name, default):
    if name in args:
        i = args.index(name)
        v = float(args[i + 1])
        del args[i:i + 2]
        return v
    return default


def main():
    args = sys.argv[1:]
    margin = opt(args, "--margin", 0.12)
    min_side = opt(args, "--min-side", 1024)
    max_side = opt(args, "--max-side", 2048)
    if len(args) != 4:
        sys.exit(__doc__)
    grey_p, mask_p, outdir, ratio = args
    rw, rh = (int(x) for x in ratio.split(":"))
    os.makedirs(outdir, exist_ok=True)

    grey = ImageOps.exif_transpose(Image.open(grey_p)).convert("RGBA")
    W, H = grey.size
    mask = load_mask(ImageOps.exif_transpose(Image.open(mask_p))).resize((W, H), Image.LANCZOS)
    ys, xs = np.where(np.asarray(mask) > 127)
    if len(xs) == 0:
        sys.exit("The mask is empty.")
    x0, y0, x1, y1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
    w, h = x1 - x0, y1 - y0
    m = margin * max(w, h)
    bw, bh = w + 2 * m, h + 2 * m
    if bw / bh < rw / rh:
        bw = bh * rw / rh
    else:
        bh = bw * rh / rw
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    bx, by = int(round(cx - bw / 2)), int(round(cy - bh / 2))
    bw, bh = int(round(bw)), int(round(bh))

    flat = Image.new("RGB", (W, H), (255, 255, 255))
    flat.paste(grey, (0, 0), grey)
    render = Image.new("RGB", (bw, bh), (255, 255, 255))
    render.paste(flat, (-bx, -by))
    mcrop = Image.new("L", (bw, bh), 0)
    mcrop.paste(mask, (-bx, -by))

    scale = 1.0
    long_side = max(bw, bh)
    if long_side < min_side:
        scale = min_side / long_side
    scale = min(scale, max_side / long_side) if long_side * scale > max_side else scale
    cw, ch = max(1, round(bw * scale)), max(1, round(bh * scale))
    if (cw, ch) != (bw, bh):
        render = render.resize((cw, ch), Image.LANCZOS)
        mcrop = mcrop.resize((cw, ch), Image.LANCZOS)
    render.save(os.path.join(outdir, "render_crop.png"))
    mcrop.save(os.path.join(outdir, "mask_crop.png"))
    info = {"photo_w": W, "photo_h": H, "box_x": bx, "box_y": by, "box_w": bw, "box_h": bh,
            "crop_w": cw, "crop_h": ch, "scale": scale, "ratio": ratio,
            "product_bbox": [int(x0), int(y0), int(x1), int(y1)]}
    with open(os.path.join(outdir, "crop.json"), "w") as f:
        json.dump(info, f, indent=1)
    print(f"product {w}x{h}px in a {W}x{H} photo -> crop {bw}x{bh} at ({bx},{by}), scaled x{scale:.2f} to {cw}x{ch}")


if __name__ == "__main__":
    main()
