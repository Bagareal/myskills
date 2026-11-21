# Stage 2 helper: work on a crop of the photo around the product, so the product is bigger in the model's frame
# (small text, icons and digits come out cleaner), then put the generated crop back into the full photo.
# Usage:
#   python3 -I crop_scene.py cut   composite_real.png mask.png RATIO out_crop.png info.json [--margin 0.35]
#   python3 -I crop_scene.py paste generated.png info.json photo.jpg out_full.png
# cut:   crops composite_real.png around the product (mask bounding box plus a margin, as a fraction of its larger
#        side, for shadows and reflections) at the ratio the model takes; the box always stays inside the photo.
# paste: resizes the generated crop to the box and puts it into a copy of the photo (the rest is the photo itself).
#        The result has the photo's size and framing: give it to lock_background.py and compare_scene.py as "result".
# Requires: numpy, Pillow

import json
import sys

import numpy as np
from PIL import Image, ImageOps


def load_mask(path, size):
    im = ImageOps.exif_transpose(Image.open(path))
    if im.mode in ("RGBA", "LA") and np.asarray(im.split()[-1]).min() < 250:
        m = im.split()[-1]
    else:
        m = im.convert("L")
        a = np.asarray(m)
        corners = np.concatenate([a[:20, :20].ravel(), a[:20, -20:].ravel(), a[-20:, :20].ravel(), a[-20:, -20:].ravel()])
        if corners.mean() > 127:
            m = Image.fromarray(255 - a)
    return np.asarray(m.resize(size, Image.LANCZOS)) > 127


def cut(src, mask_p, ratio, dst, info_p, margin):
    rw, rh = (int(x) for x in ratio.split(":"))
    im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    W, H = im.size
    ys, xs = np.where(load_mask(mask_p, (W, H)))
    x0, y0, x1, y1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
    w, h = x1 - x0, y1 - y0
    m = margin * max(w, h)
    bw, bh = w + 2 * m, h + 2 * m
    if bw / bh < rw / rh:
        bw = bh * rw / rh
    else:
        bh = bw * rh / rw
    s = min(1.0, W / bw, H / bh)          # never larger than the photo
    bw, bh = bw * s, bh * s
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    bx = int(round(min(max(cx - bw / 2, 0), W - bw)))
    by = int(round(min(max(cy - bh / 2, 0), H - bh)))
    bw, bh = int(round(bw)), int(round(bh))
    im.crop((bx, by, bx + bw, by + bh)).save(dst)
    with open(info_p, "w") as f:
        json.dump({"photo_w": W, "photo_h": H, "box_x": bx, "box_y": by, "box_w": bw, "box_h": bh}, f)
    print(f"photo {W}x{H} -> crop {bw}x{bh} at ({bx},{by}); product {w}x{h}")


def paste(gen_p, info_p, photo_p, dst):
    with open(info_p) as f:
        info = json.load(f)
    photo = ImageOps.exif_transpose(Image.open(photo_p)).convert("RGB")
    if photo.size != (info["photo_w"], info["photo_h"]):
        sys.exit("The photo does not have the size the crop was made for.")
    g = Image.open(gen_p).convert("RGB")
    gw, gh = g.size
    if abs(gw / gh - info["box_w"] / info["box_h"]) / (info["box_w"] / info["box_h"]) > 0.01:
        print(f"note: generated ratio {gw}x{gh} differs from the crop {info['box_w']}x{info['box_h']}; it is stretched to fit, check the overlay")
    g = g.resize((info["box_w"], info["box_h"]), Image.LANCZOS)
    photo.paste(g, (info["box_x"], info["box_y"]))
    photo.save(dst)
    print("written", dst)


if __name__ == "__main__":
    a = sys.argv[1:]
    margin = 0.35
    if "--margin" in a:
        i = a.index("--margin")
        margin = float(a[i + 1])
        del a[i:i + 2]
    if len(a) == 6 and a[0] == "cut":
        cut(a[1], a[2], a[3], a[4], a[5], margin)
    elif len(a) == 5 and a[0] == "paste":
        paste(a[1], a[2], a[3], a[4])
    else:
        sys.exit(__doc__)
