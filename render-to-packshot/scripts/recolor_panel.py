# Recolour the dark background of a crop taken from the marking spec (e.g. a screen drawn black)
# to the colour the colour spec gives for that part, keeping light icons and text light.
# Usage: python3 -I recolor_panel.py crop.png out.png R,G,B   (sRGB of the part)
# Requires: numpy, Pillow, scipy
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

src, dst = sys.argv[1], sys.argv[2]
col = np.array([float(v) for v in sys.argv[3].split(",")])

a = np.asarray(Image.open(src).convert("RGB")).astype(float)
lum = a.mean(axis=2) / 255.0
dark = lum < 0.5
panel = ndimage.binary_fill_holes(ndimage.binary_closing(dark, iterations=6))
out = a.copy()
out[panel] = col * (1 - lum[panel, None]) + 255 * lum[panel, None]
Image.fromarray(out.astype(np.uint8)).save(dst)
print("recoloured", int(panel.sum()), "px ->", dst)
