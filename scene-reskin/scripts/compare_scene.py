# Position check for scene-reskin.
# Usage: python3 -I compare_scene.py photo.png grey.png mask.png result.png outdir [--ref composite_real.png]
#   photo   = original environment photo (also gives the output size)
#   grey    = grey product on transparent background, exact position (the _grey.png of the export)
#   mask    = product mask (alpha PNG, or black on white / white on black)
#   result  = the generated image (any size, same framing as the photo)
#   --ref   = optional: the photo with the re-skinned product pasted on it (composite_real.png). The script then also
#             reports how much the product itself changed between the pasted version and the result (inside the mask)
#             and writes product_diff.png (differences amplified x4).
# Writes in outdir:
#   overlay_grey50.png   result with the grey product laid over it at 50%  (the verdict)
#   outline.png          result with the contour of the mask drawn in magenta
#   overlay_crop.png / outline_crop.png   the same, cropped around the product
#   side.png             original photo | result, for the overall look
# Prints an edge-alignment signal: is the strongest edge of the result on the mask contour, or shifted?
# That number is a signal, not the verdict: the verdict is the 50% overlay, looked at whole and in crops.
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


def edge_alignment(result_rgb, mask, long_side=1200):
    """Mean edge strength of the result on the mask contour, for shifts of a few pixels."""
    h, w = mask.shape
    s = min(1.0, long_side / max(w, h))
    ws, hs = max(1, round(w * s)), max(1, round(h * s))
    g = np.asarray(Image.fromarray(result_rgb).convert("L").resize((ws, hs), Image.LANCZOS)).astype(float)
    m = np.asarray(Image.fromarray((mask * 255).astype(np.uint8)).resize((ws, hs), Image.LANCZOS)) > 127
    grad = ndimage.gaussian_gradient_magnitude(g, sigma=1.2)
    border = m & ~ndimage.binary_erosion(m, iterations=1)
    margin = 4
    border[:margin] = border[-margin:] = False
    border[:, :margin] = border[:, -margin:] = False
    ys, xs = np.where(border)
    if len(ys) < 20:
        return None
    r = max(3, round(0.012 * max(ws, hs)))
    best = (-1.0, 0, 0)
    base = None
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            yy = np.clip(ys + dy, 0, hs - 1)
            xx = np.clip(xs + dx, 0, ws - 1)
            v = float(grad[yy, xx].mean())
            if dx == 0 and dy == 0:
                base = v
            if v > best[0]:
                best = (v, dx, dy)
    return {"score_at_zero": round(base, 2), "best_score": round(best[0], 2),
            "best_shift_px": [round(best[1] / s), round(best[2] / s)], "search_radius_px": round(r / s)}


def main():
    argv = sys.argv[1:]
    ref_p = None
    if "--ref" in argv:
        i = argv.index("--ref")
        ref_p = argv[i + 1]
        del argv[i:i + 2]
    if len(argv) != 5:
        sys.exit(__doc__)
    photo_p, grey_p, mask_p, result_p, outdir = argv
    os.makedirs(outdir, exist_ok=True)
    photo = ImageOps.exif_transpose(Image.open(photo_p)).convert("RGB")
    size = photo.size
    result = Image.open(result_p).convert("RGB")
    if result.size != size:
        print(f"note: result is {result.size[0]}x{result.size[1]}, resized to the photo size {size[0]}x{size[1]}")
        result = result.resize(size, Image.LANCZOS)
    grey = ImageOps.exif_transpose(Image.open(grey_p)).convert("RGBA").resize(size, Image.LANCZOS)
    mask = load_mask(mask_p, size)
    if not mask.any():
        sys.exit("The mask is empty.")

    res = np.asarray(result).astype(float)
    ga = np.asarray(grey).astype(float)
    a = (ga[..., 3:4] / 255.0) * 0.5
    overlay = (res * (1 - a) + ga[..., :3] * a).clip(0, 255).astype(np.uint8)

    border = mask & ~ndimage.binary_erosion(mask, iterations=1)
    t = max(1, round(max(size) / 1500))
    border = ndimage.binary_dilation(border, iterations=t - 1) if t > 1 else border
    outline = np.asarray(result).copy()
    outline[border] = (255, 0, 255)

    ys, xs = np.where(mask)
    pad = round(0.04 * max(size))
    box = (max(0, xs.min() - pad), max(0, ys.min() - pad), min(size[0], xs.max() + pad), min(size[1], ys.max() + pad))

    ov_img, ol_img = Image.fromarray(overlay), Image.fromarray(outline)
    ov_img.save(os.path.join(outdir, "overlay_grey50.png"))
    ol_img.save(os.path.join(outdir, "outline.png"))
    ov_img.crop(box).save(os.path.join(outdir, "overlay_crop.png"))
    ol_img.crop(box).save(os.path.join(outdir, "outline_crop.png"))
    side = Image.new("RGB", (size[0] * 2, size[1]))
    side.paste(photo, (0, 0))
    side.paste(result, (size[0], 0))
    side.thumbnail((3000, 3000))
    side.save(os.path.join(outdir, "side.png"))

    ea = edge_alignment(np.asarray(result), mask)
    print("product bbox", [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())])
    if ea:
        print("edge alignment:", ea)
        sx, sy = ea["best_shift_px"]
        if max(abs(sx), abs(sy)) > max(2, round(0.002 * max(size))) and ea["best_score"] > ea["score_at_zero"] * 1.25:
            print(f"SIGNAL: the strongest edges sit about {sx},{sy} px away from the mask contour: the product may have moved. Check the overlay.")
        else:
            print("signal: no clear shift of the contour (not a verdict, look at the overlay)")
    if ref_p:
        ref = np.asarray(ImageOps.exif_transpose(Image.open(ref_p)).convert("RGB").resize(size, Image.LANCZOS)).astype(float)
        inner = ndimage.binary_erosion(mask, iterations=max(2, round(0.004 * max(size))))
        sig = max(1.0, 0.0015 * max(size))
        d = np.abs(ndimage.gaussian_filter(ref, (sig, sig, 0)) - ndimage.gaussian_filter(res, (sig, sig, 0))).max(axis=2)
        print(f"product change vs the pasted re-skin (inside the mask): mean {d[inner].mean():.1f}/255, "
              f"{100 * float((d[inner] > 40).mean()):.1f}% of the product changed by more than 40/255")
        Image.fromarray((d * 4).clip(0, 255).astype(np.uint8)).save(os.path.join(outdir, "product_diff.png"))
    print("written:", ", ".join(sorted(os.listdir(outdir))))


if __name__ == "__main__":
    main()
