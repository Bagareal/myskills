# Build the colour reference sheet sent to the model, from the values of the colour conversion chart.
# Usage: python3 -I color_sheet.py out.png "LABEL=argb:R,G,B" "LABEL=srgb:R,G,B[:metal]" "LABEL=swatch:swatch.png" ...
#   argb   = Adobe RGB values from the chart, converted to sRGB
#   srgb   = sRGB or HEX-derived values, used as they are
#   swatch = a crop of the printed swatch from the chart, for colours with no values (speckled, textured...)
#   :metal = draw the patch as a soft metallic gradient instead of a flat fill
# Prints the sRGB value of each patch. Requires: numpy, Pillow
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

M_ADOBE = np.array([[0.5767309, 0.1855540, 0.1881852],
                    [0.2973769, 0.6273491, 0.0752741],
                    [0.0270343, 0.0706872, 0.9911085]])
M_SRGB = np.linalg.inv(np.array([[0.4124564, 0.3575761, 0.1804375],
                                 [0.2126729, 0.7151522, 0.0721750],
                                 [0.0193339, 0.1191920, 0.9503041]]))


def adobe_to_srgb(rgb):
    lin = (np.array(rgb) / 255) ** (563 / 256)
    x = np.clip(M_SRGB @ (M_ADOBE @ lin), 0, 1)
    s = np.where(x <= 0.0031308, 12.92 * x, 1.055 * x ** (1 / 2.4) - 0.055)
    return tuple(int(round(v * 255)) for v in s)


out = sys.argv[1]
entries = sys.argv[2:]
W = 300 * len(entries)
im = Image.new("RGB", (W, 400), (255, 255, 255))
d = ImageDraw.Draw(im)
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
except OSError:
    font = ImageFont.load_default()

for i, entry in enumerate(entries):
    label, spec = entry.split("=", 1)
    kind, _, rest = spec.partition(":")
    x0 = i * 300
    if kind == "swatch":
        sw = Image.open(rest).convert("RGB").resize((300, 300))
        im.paste(sw, (x0, 0))
        med = np.median(np.asarray(sw).reshape(-1, 3), axis=0)
        print(label, "swatch median sRGB", tuple(int(v) for v in med))
    else:
        metal = rest.endswith(":metal")
        vals = tuple(int(v) for v in rest.replace(":metal", "").split(","))
        c = adobe_to_srgb(vals) if kind == "argb" else vals
        print(label, kind, vals, "-> sRGB", c, "(metal)" if metal else "")
        if metal:
            for y in range(300):
                t = y / 299
                col = tuple(int(c[k] * (1 - t) + min(255, c[k] + 50) * t * (1 - abs(0.5 - t)) + c[k] * t * abs(0.5 - t)) for k in range(3))
                d.line((x0, y, x0 + 299, y), fill=col)
        else:
            d.rectangle((x0, 0, x0 + 299, 299), fill=c)
    d.text((x0 + 10, 330), label, fill=(0, 0, 0), font=font)

im.save(out)
print("saved", out, im.size)
