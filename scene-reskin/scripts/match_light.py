# Stage 2 finish: make the real product take the light, tone and white balance of the scene.
# The AI result has the right light on the product but can garble its small text, icons and logos; the pasted
# real product has perfect detail but the studio light of stage 1. This script keeps the DETAIL of the pasted
# product and takes the LOW-FREQUENCY light and colour (shading, reflections, white balance, contrast) from the AI result,
# only inside the product mask. Everything outside the mask stays the AI result.
# Usage: python3 -I match_light.py result.png composite_real.png mask.png out.png [--sigma-frac 0.018] [--erode 2]
#   result.png          stage 2 output (any size; resized to the photo's size)
#   composite_real.png  photo with the real product pasted (from paste_back.py)
#   mask.png            exported product mask (alpha PNG or black/white)
#   --sigma-frac        blur radius as a fraction of the product's larger side (default 0.018). Larger = the AI shapes
#                       count less, more risk of a light mismatch; smaller = more of the AI's garbled detail leaks in.
# Requires: numpy, Pillow, scipy

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


def main(result_p, real_p, mask_p, out_p, sigma_frac, erode):
    real_im = ImageOps.exif_transpose(Image.open(real_p)).convert("RGB")
    W, H = real_im.size
    ai = np.asarray(Image.open(result_p).convert("RGB").resize((W, H), Image.LANCZOS)).astype(float)
    real = np.asarray(real_im).astype(float)
    m = load_mask(mask_p, (W, H))
    ys, xs = np.where(m)
    side = max(xs.max() - xs.min(), ys.max() - ys.min())
    sigma = max(2.0, sigma_frac * side)

    w = ndimage.binary_erosion(m, iterations=erode + 1).astype(float)

    def masked_blur(x):
        num = np.stack([ndimage.gaussian_filter(x[..., c] * w, sigma) for c in range(3)], -1)
        den = ndimage.gaussian_filter(w, sigma)[..., None] + 1e-6
        return num / den

    la, lr = masked_blur(ai), masked_blur(real)
    ratio = np.clip((la + 8) / (lr + 8), 0.5, 1.6)      # light and colour of the scene, as a gain on the real product
    lit = np.clip(real * ratio, 0, 255)
    a = ndimage.gaussian_filter(ndimage.binary_erosion(m, iterations=erode).astype(float), 1.5)[..., None]
    out = ai * (1 - a) + lit * a
    Image.fromarray(out.astype(np.uint8)).save(out_p)

    core = ndimage.binary_erosion(m, iterations=int(sigma))
    if core.sum() > 0:
        d = np.abs(ai[core].mean(0) - lit[core].mean(0))
        print(f"sigma {sigma:.1f}px; mean colour gap between AI product and relit product: {d.round(1).tolist()} (should be small)")
    print("written", out_p)


if __name__ == "__main__":
    a = sys.argv[1:]
    sf, er = 0.018, 2
    if "--sigma-frac" in a:
        i = a.index("--sigma-frac"); sf = float(a[i + 1]); del a[i:i + 2]
    if "--erode" in a:
        i = a.index("--erode"); er = int(a[i + 1]); del a[i:i + 2]
    if len(a) != 4:
        sys.exit(__doc__)
    main(a[0], a[1], a[2], a[3], sf, er)
