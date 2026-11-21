# Position check: silhouette IoU, bounding boxes, side-by-side image and 50% overlay.
# Usage: python3 -I compare.py reference.png generated.png side.png blend.png
# Requires: numpy, Pillow

import sys
from PIL import Image
import numpy as np
ref = Image.open(sys.argv[1]).convert("RGB")
out = Image.open(sys.argv[2]).convert("RGB").resize(ref.size, Image.LANCZOS)
def mask(im):
    a = np.asarray(im).astype(int)
    bg = a[5:30, 5:30].reshape(-1, 3).mean(axis=0)
    return np.abs(a - bg).sum(axis=2) > 30
m1, m2 = mask(ref), mask(out)
iou = (m1 & m2).sum() / (m1 | m2).sum()
print("IoU silhouette:", round(float(iou), 3))
for n, m in (("reference", m1), ("generated", m2)):
    ys, xs = np.where(m)
    print(n, "bbox", xs.min(), ys.min(), xs.max(), ys.max())
blend = Image.blend(ref, out, 0.5)
side = Image.new("RGB", (ref.width * 2, ref.height))
side.paste(ref, (0, 0)); side.paste(out, (ref.width, 0))
side.resize((side.width // 2, side.height // 2)).save(sys.argv[3])
blend.save(sys.argv[4])
