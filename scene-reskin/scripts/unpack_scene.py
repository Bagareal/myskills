# Unpack a _SCENE export (zip or folder), check it and print a JSON summary.
# Usage: python3 -I unpack_scene.py SCENE.zip|folder outdir [--prefix NAME]
# Writes outdir/photo.<ext>, composite.<ext>, grey.png, mask.png, mask_bw.png, scene.json
# (only the files that exist). Requires: numpy, Pillow

import json
import os
import re
import shutil
import sys
import zipfile

import numpy as np
from PIL import Image, ImageOps

ROLE_RE = re.compile(r"^(?P<prefix>.*?)_?(?:scene_)?(?P<role>photo|composite|grey|mask_bw|mask)\.(?P<ext>png|jpe?g|tiff?|webp)$", re.I)
JSON_RE = re.compile(r"^(?P<prefix>.*?)_?scene\.json$", re.I)


def collect(src):
    """Return {prefix: {role: (name, reader)}} for a zip or a folder."""
    groups = {}
    if os.path.isdir(src):
        entries = [(n, (lambda p=os.path.join(src, n): open(p, "rb"))) for n in sorted(os.listdir(src))
                   if os.path.isfile(os.path.join(src, n))]
    else:
        z = zipfile.ZipFile(src)
        entries = [(os.path.basename(i.filename), (lambda i=i: z.open(i))) for i in z.infolist()
                   if not i.is_dir() and os.path.basename(i.filename)]
    for name, opener in entries:
        m = ROLE_RE.match(name)
        if m:
            role, ext = m.group("role").lower(), m.group("ext").lower()
            groups.setdefault(m.group("prefix"), {})[role] = (name, ext, opener)
            continue
        m = JSON_RE.match(name)
        if m:
            groups.setdefault(m.group("prefix"), {})["json"] = (name, "json", opener)
    return groups


def mask_from(im):
    """Subject = True. Accepts alpha PNG (opaque subject) or black-on-white."""
    if im.mode in ("RGBA", "LA") and np.asarray(im.split()[-1]).min() < 250:
        return np.asarray(im.split()[-1]) > 127
    a = np.asarray(im.convert("L"))
    corners = np.concatenate([a[:20, :20].ravel(), a[:20, -20:].ravel(), a[-20:, :20].ravel(), a[-20:, -20:].ravel()])
    return (a < 128) if corners.mean() > 127 else (a > 127)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    prefix_arg = None
    if "--prefix" in sys.argv:
        prefix_arg = sys.argv[sys.argv.index("--prefix") + 1]
        args = [a for a in args if a != prefix_arg]
    if len(args) != 2:
        sys.exit(__doc__)
    src, outdir = args
    groups = collect(src)
    if not groups:
        sys.exit("No _SCENE files found (expected *_photo.*, *_composite.*, *_grey.png, *_mask*.png, *_SCENE.json).")
    if prefix_arg is not None:
        if prefix_arg not in groups:
            sys.exit("Prefix not found. Available: " + ", ".join(repr(p) for p in groups))
        prefix = prefix_arg
    elif len(groups) == 1:
        prefix = next(iter(groups))
    else:
        sys.exit("Several scenes in the input, pass --prefix with one of: " + ", ".join(repr(p) for p in groups))

    files = groups[prefix]
    os.makedirs(outdir, exist_ok=True)
    out = {}
    for role, (name, ext, opener) in files.items():
        dst = os.path.join(outdir, "scene.json" if role == "json" else f"{role}.{ext}")
        with opener() as r, open(dst, "wb") as w:
            shutil.copyfileobj(r, w)
        out[role] = dst

    warnings = []
    # If the mask/grey/composite are a scaled copy of the photo (same shape, other pixel size), bring them to the
    # photo's size: everything downstream works at the photo's resolution.
    if "photo" in out:
        ref = ImageOps.exif_transpose(Image.open(out["photo"])).size
        for role in ("composite", "grey", "mask", "mask_bw"):
            if role not in out:
                continue
            im = ImageOps.exif_transpose(Image.open(out[role]))
            if im.size != ref and abs(im.size[0] / im.size[1] - ref[0] / ref[1]) < 0.005 * ref[0] / ref[1]:
                im.resize(ref, Image.LANCZOS).save(out[role])
                warnings.append(f"{role} was {im.size[0]}x{im.size[1]}, resized to the photo's {ref[0]}x{ref[1]}")
    for need in ("photo", "grey"):
        if need not in out:
            warnings.append(f"missing {need}")
    sizes = {}
    for role in ("photo", "composite", "grey", "mask", "mask_bw"):
        if role in out:
            sizes[role] = ImageOps.exif_transpose(Image.open(out[role])).size
    if len(set(sizes.values())) > 1:
        warnings.append(f"sizes differ: {sizes}")

    summary = {"prefix": prefix, "files": out, "sizes": sizes, "warnings": warnings}
    if "photo" in sizes:
        w, h = sizes["photo"]
        summary["photo_ratio"] = round(w / h, 4)
        summary["photo_megapixels"] = round(w * h / 1e6, 2)
    mpath = out.get("mask") or out.get("mask_bw") or out.get("grey")
    if mpath:
        m = mask_from(ImageOps.exif_transpose(Image.open(mpath)))
        if m.any():
            ys, xs = np.where(m)
            summary["product_bbox"] = [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]
            summary["product_area_percent"] = round(100 * float(m.mean()), 2)
            h, w = m.shape
            if xs.min() <= 1 or ys.min() <= 1 or xs.max() >= w - 2 or ys.max() >= h - 2:
                warnings.append("the product touches the image border (it may be cut by the frame)")
        else:
            warnings.append("the mask is empty")
    if "json" in out:
        try:
            with open(out["json"]) as f:
                data = json.load(f)
            cam = data.get("camera", {}) if isinstance(data, dict) else {}
            summary["json_keys"] = sorted(data.keys()) if isinstance(data, dict) else []
            summary["camera"] = {k: cam[k] for k in ("focal_mm", "fov_vertical_deg") if k in cam}
        except Exception as e:  # the JSON is informative only
            warnings.append(f"scene.json not readable: {e}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
