# Fit an image to an aspect ratio without cropping, and undo it later.
# Usage:
#   python3 -I fit_canvas.py pad   in.png out.png 3:2 info.json
#   python3 -I fit_canvas.py unpad generated.png info.json out.png
# pad: extends the image by mirroring its own edges (no flat colour band, so the editing model does not
#      read the padding as part of the scene) and records the padding in info.json.
# unpad: crops the padding away from the generated image and resizes it back to the original size.
# Requires: numpy, Pillow

import json
import sys

import numpy as np
from PIL import Image, ImageOps


def pad(src, dst, ratio, info_path):
    rw, rh = (int(x) for x in ratio.split(":"))
    im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    w, h = im.size
    left = right = top = bottom = 0
    target_w = round(h * rw / rh)
    if target_w > w:
        left = (target_w - w) // 2
        right = target_w - w - left
    elif target_w < w:
        target_h = round(w * rh / rw)
        top = (target_h - h) // 2
        bottom = target_h - h - top
    a = np.asarray(im)
    for mode in ("reflect", "symmetric", "edge"):
        try:
            padded = np.pad(a, ((top, bottom), (left, right), (0, 0)), mode=mode)
            break
        except ValueError:  # padding larger than the image for this mode
            continue
    Image.fromarray(padded).save(dst)
    info = {"orig_w": w, "orig_h": h, "left": left, "right": right, "top": top, "bottom": bottom,
            "canvas_w": w + left + right, "canvas_h": h + top + bottom}
    with open(info_path, "w") as f:
        json.dump(info, f)
    print(f"{w}x{h} -> {info['canvas_w']}x{info['canvas_h']} (padding L{left} R{right} T{top} B{bottom})")


def unpad(src, info_path, dst):
    with open(info_path) as f:
        info = json.load(f)
    g = Image.open(src).convert("RGB")
    gw, gh = g.size
    sx, sy = gw / info["canvas_w"], gh / info["canvas_h"]
    if abs(sx - sy) / max(sx, sy) > 0.01:
        print(f"WARNING: generated ratio {gw}x{gh} differs from the padded canvas "
              f"{info['canvas_w']}x{info['canvas_h']}; the crop is approximate, check the overlay carefully")
    box = (round(info["left"] * sx), round(info["top"] * sy),
           round((info["left"] + info["orig_w"]) * sx), round((info["top"] + info["orig_h"]) * sy))
    g = g.crop(box).resize((info["orig_w"], info["orig_h"]), Image.LANCZOS)
    g.save(dst)
    print(f"{gw}x{gh} -> crop {box} -> {info['orig_w']}x{info['orig_h']}")


if __name__ == "__main__":
    if len(sys.argv) == 6 and sys.argv[1] == "pad":
        pad(*sys.argv[2:6])
    elif len(sys.argv) == 5 and sys.argv[1] == "unpad":
        unpad(*sys.argv[2:5])
    else:
        sys.exit(__doc__)
