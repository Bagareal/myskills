# Keep the rest of the photo identical: restore the original pixels everywhere the AI had no reason to change.
# Usage: python3 -I lock_background.py photo.png result.png mask.png out.png [--thr 14] [--no-color-match]
#   photo   = original environment photo (sets the output size)
#   result  = generated image (any size, same framing as the photo, padding already removed)
#   mask    = product mask (alpha PNG, or black on white / white on black)
#   out     = final image (format from the extension; JPEG at quality 95; the photo's ICC profile is kept)
# How it works: the region to keep from the AI = the product mask, plus every area connected to it where the
# AI result differs from the photo (shadows, contact shadow, reflections, colour bounce), grown a little and
# feathered. Outside that region the original photo pixels are put back, at full resolution.
# The product is NOT cut out and pasted: the AI image is kept inside the region, shadows included.
# --thr          difference (0-255) above which a pixel counts as changed by the AI (default 14; lower keeps
#                fainter shadows, higher restores more of the photo)
# --no-color-match  skip the small global tone correction applied to the AI image before blending
# Also writes <out>_region.png (white = taken from the AI image) to check what was kept.
# Requires: numpy, Pillow, scipy

import os
import sys

import numpy as np
from PIL import Image, ImageOps
from scipy import ndimage


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


def main():
    args = [a for a in sys.argv[1:]]
    color_match = "--no-color-match" not in args
    args = [a for a in args if a != "--no-color-match"]
    thr = 14.0
    if "--thr" in args:
        i = args.index("--thr")
        thr = float(args[i + 1])
        del args[i:i + 2]
    if len(args) != 4:
        sys.exit(__doc__)
    photo_p, result_p, mask_p, out_p = args

    src = ImageOps.exif_transpose(Image.open(photo_p))
    icc = src.info.get("icc_profile")
    photo = src.convert("RGB")
    size = photo.size
    result = Image.open(result_p).convert("RGB")
    if result.size != size:
        print(f"note: result is {result.size[0]}x{result.size[1]}, resized to the photo size {size[0]}x{size[1]}")
        result = result.resize(size, Image.LANCZOS)
    mask_full = load_mask(mask_p, size)
    if not mask_full.any():
        sys.exit("The mask is empty.")

    long_side = max(size)
    s = min(1.0, 1500 / long_side)
    ws, hs = max(1, round(size[0] * s)), max(1, round(size[1] * s))
    L = max(ws, hs)
    P = np.asarray(photo.resize((ws, hs), Image.BOX)).astype(float)
    R = np.asarray(result.resize((ws, hs), Image.BOX)).astype(float)
    M = np.asarray(Image.fromarray((mask_full * 255).astype(np.uint8)).resize((ws, hs), Image.BOX)) > 127

    def dist_mask(px):
        return ndimage.binary_dilation(M, iterations=max(1, round(px)))

    # small global tone correction, measured far from the product only
    offset = np.zeros(3)
    if color_match:
        far = ~dist_mask(0.10 * L)
        if far.sum() > 0.05 * far.size:
            offset = np.median((P - R)[far], axis=0)
            if np.abs(offset).max() > 12:
                print(f"warning: the AI image differs from the photo by {offset.round(1)} even far from the product; "
                      "colour match skipped for that part")
                offset = np.clip(offset, -12, 12)
    Rc = (R + offset).clip(0, 255)

    sig = max(1.0, 0.003 * L)
    diff = np.abs(ndimage.gaussian_filter(P, (sig, sig, 0)) - ndimage.gaussian_filter(Rc, (sig, sig, 0))).max(axis=2)

    core = dist_mask(0.004 * L)
    low = (diff > thr) | core
    lab, n = ndimage.label(low)
    keep = np.unique(lab[core])
    keep = keep[keep > 0]
    region = np.isin(lab, keep)
    region = ndimage.binary_closing(region, iterations=max(1, round(0.004 * L)))
    region = ndimage.binary_fill_holes(region)
    region = ndimage.binary_dilation(region, iterations=max(1, round(0.012 * L)))
    alpha_s = ndimage.gaussian_filter(region.astype(float), max(1.0, 0.010 * L))
    alpha_s = np.maximum(alpha_s, ndimage.gaussian_filter(core.astype(float), 1.0))
    alpha_s = alpha_s.clip(0, 1)

    cover = 100 * float(region.mean())
    prod = 100 * float(M.mean())
    print(f"kept from the AI image: {cover:.1f}% of the frame (product alone: {prod:.1f}%), "
          f"tone offset applied: {offset.round(1).tolist()}")
    if cover > 60:
        print("WARNING: the AI changed most of the photo, so most of it is kept from the AI image. "
              "Try a higher --thr, or regenerate with the instruction to leave the rest untouched.")

    alpha = np.asarray(Image.fromarray((alpha_s * 255).astype(np.uint8)).resize(size, Image.BILINEAR)).astype(float) / 255.0
    off_full = offset.reshape(1, 1, 3)
    res_f = np.asarray(result).astype(float)
    pho_f = np.asarray(photo).astype(float)
    final = pho_f * (1 - alpha[..., None]) + (res_f + off_full).clip(0, 255) * alpha[..., None]
    final_img = Image.fromarray(final.round().astype(np.uint8))

    ext = os.path.splitext(out_p)[1].lower()
    save_kw = {}
    if ext in (".jpg", ".jpeg"):
        save_kw = {"quality": 95, "subsampling": 0}
    if icc:
        save_kw["icc_profile"] = icc
    final_img.save(out_p, **save_kw)
    region_p = os.path.splitext(out_p)[0] + "_region.png"
    Image.fromarray((alpha * 255).astype(np.uint8)).save(region_p)
    print("written:", out_p, region_p)


if __name__ == "__main__":
    main()
