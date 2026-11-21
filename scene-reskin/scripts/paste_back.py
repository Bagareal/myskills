# Stage 1 output: put the re-skinned product back in the photo, at the exact place of the grey one.
# Usage: python3 -I paste_back.py cutout.png crop.json photo.jpg outdir
#   cutout  = the transparent PNG made by cutout.py from the re-skin of render_crop.png (any size, same framing)
#   crop.json = from crop_product.py
#   photo   = the original environment photo
# Writes in outdir: product_layer.png (re-skinned product on transparent, photo size, exact position) and
# composite_real.png (the photo with the product pasted on it: no shadows, light not matched yet; this is the
# image the AI gets in stage 2).
# The edges are cleaned: the colour of the 1-2 outer pixels is replaced by the colour just inside, so the white
# background the product was generated on does not leave a light fringe on the kitchen.
# Requires: numpy, Pillow, scipy

import json
import os
import sys

import numpy as np
from PIL import Image, ImageOps
from scipy import ndimage


def main():
    if len(sys.argv) != 5:
        sys.exit(__doc__)
    cut_p, info_p, photo_p, outdir = sys.argv[1:5]
    os.makedirs(outdir, exist_ok=True)
    with open(info_p) as f:
        info = json.load(f)
    photo = ImageOps.exif_transpose(Image.open(photo_p)).convert("RGB")
    W, H = photo.size
    if (W, H) != (info["photo_w"], info["photo_h"]):
        sys.exit(f"The photo is {W}x{H} but the crop was made for {info['photo_w']}x{info['photo_h']}.")
    cut = Image.open(cut_p).convert("RGBA").resize((info["box_w"], info["box_h"]), Image.LANCZOS)

    a = np.asarray(cut).astype(float)
    alpha = a[..., 3] / 255.0
    rgb = a[..., :3]
    core = ndimage.binary_erosion(alpha > 0.98, iterations=max(1, round(max(cut.size) / 600)))
    if core.any():
        idx = ndimage.distance_transform_edt(~core, return_distances=False, return_indices=True)
        nearest = rgb[idx[0], idx[1]]
        fix = ndimage.binary_dilation(alpha > 0.02, iterations=1) & ~core
        rgb = np.where(fix[..., None], nearest, rgb)
    clean = np.dstack([rgb, alpha * 255]).clip(0, 255).astype(np.uint8)
    clean_img = Image.fromarray(clean, "RGBA")

    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    layer.paste(clean_img, (info["box_x"], info["box_y"]))
    comp = photo.convert("RGBA")
    comp.alpha_composite(layer)
    layer.save(os.path.join(outdir, "product_layer.png"))
    comp.convert("RGB").save(os.path.join(outdir, "composite_real.png"))
    print("written:", os.path.join(outdir, "product_layer.png"), os.path.join(outdir, "composite_real.png"))


if __name__ == "__main__":
    main()
