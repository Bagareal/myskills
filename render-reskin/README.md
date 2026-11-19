# render-reskin

A Claude skill that turns a **grey 3D product render** into a **photorealistic packshot**, using real photos of the product for materials and colours. The product geometry is never regenerated: every contour stays at the same pixel position as in the render, and a local position check proves it before anything is delivered.

Output: a packshot on pure white, or a transparent PNG.

## Why

Text-to-image models redraw products: proportions drift, details move, logos warp. A 3D render already has the exact geometry, but it looks like clay. This skill keeps the render's geometry and only "paints" it with the real materials, using a multi-image editing model (render as image 1, product photos as the following images), then checks the result against the render pixel by pixel.

## How it works

```
grey render ──► pad to ratio ──► re-skin (editing model, render + photos) ──► position check ──► review ──► [cutout] ──► final image
                                        ▲
          product photos ──► materials list (approved by the user)
```

| Step | What happens | Where |
|---|---|---|
| 0. Inputs | Render, product photos, optional mask; finds a usable connector | chat |
| 1. Settings | Connector and model, background, aspect ratio, resolution and variants | form |
| 2. Materials | Claude lists material and colour of each part; the user confirms or corrects | form |
| 3. Canvas | Render padded (never cropped) to the target ratio | local script |
| 4. Re-skin | Editing model call with a geometry-locking prompt | connector |
| 5. Position check | Silhouette IoU, bounding boxes and a 50% overlay | local script |
| 6. Review | Re-skin and overlay shown; accept, regenerate or fix a part | form |
| 7. Cutout | Optional transparent PNG from a user mask or a render-derived mask | local script |

Every choice is asked through multiple-choice forms; Claude talks to the user in their own language.

## Requirements

- **Claude** with skills enabled (claude.ai, Claude desktop app, or Claude Code).
- **A generative-AI connector** (MCP) that offers a multi-image editing model, for example fal, Replicate or a Google Gemini connector. Recommended model: **Nano Banana 2.1**, then **Nano Banana 2**. If no connector is available, the skill suggests one.
- **Python 3** with `numpy`, `Pillow` and `scipy` in the environment where Claude runs code. The scripts cost no credits.

## Installation

### claude.ai / Claude desktop app

1. Download `render-reskin.zip` from the [latest release](../../releases/latest).
2. In Claude's settings, open the **Skills** section and upload the zip.
3. Make sure code execution and file creation are enabled.

### Claude Code

Copy the folder into your skills directory:

```bash
git clone https://github.com/Bagareal/myskills.git
mkdir -p ~/.claude/skills
cp -r myskills/render-reskin ~/.claude/skills/
```

For a single project, copy it into `.claude/skills/` inside that project instead.

## Usage

Invoke it by name or describe the task:

```
/render-reskin
```

```
Turn this grey render into a realistic packshot on white, using these product photos.
```

Then attach:

1. **The grey render** on a plain, uniform background.
2. **Real photos of the product.** More angles (front, side, back, details) give better results. With a single photo, the colours and finishes of unseen sides are a guess, and the skill says so.
3. **Optional mask** (only for a transparent PNG): subject black on white, or a PNG with alpha, with the same framing as the render. It gives the cleanest edges and keeps openings in the product (handles, gaps) transparent.

## Settings

| Setting | Options | Default |
|---|---|---|
| Connector and model | Every available connector/model combination | Nano Banana 2.1 |
| Background | Pure white packshot, transparent PNG | - |
| Aspect ratio | Keep the render's ratio, 1:1, 16:9, 9:16, or typed | Render's ratio |
| Resolution and variants | 1K/2K/4K, 1-4 images | 2K, 1 image |

If a setting does not exist on the chosen connector, Claude says which one and what it used instead.

## Scripts

All scripts are in [`scripts/`](scripts) and can also be used on their own.

### `pad_to_ratio.py`

Pads an image to a target aspect ratio, centring it on a canvas filled with its own background colour (sampled from the top-left corner). It never crops.

```bash
python3 -I scripts/pad_to_ratio.py render.png render_pad.png 16:9
```

### `compare.py`

Compares the generated image with the reference render.

```bash
python3 -I scripts/compare.py render_pad.png reskin.png side.png blend.png
```

Prints the silhouette IoU and both bounding boxes, and writes a side-by-side image and a 50% overlay.

- **IoU** (intersection over union of the two silhouettes, 1.0 = identical) is a signal, not the verdict. A soft contact shadow on a white background widens the generated silhouette and lowers the IoU even when the product is correct (values from 0.65 to 0.87 have been seen with correct products). A bounding box larger only on the shadow side is the shadow.
- **The overlay is the verdict.** Contours, seams, logos and proportions must line up with no double edges.

### `cutout.py`

Builds the transparent PNG.

```bash
python3 -I scripts/cutout.py render_pad.png reskin.png reskin_cutout.png [mask.png]
```

- With a mask: uses it (black on white or alpha, any resolution, same framing as the original render), fitted to the canvas the same way `pad_to_ratio.py` placed the render.
- Without a mask: derives one from the render (background threshold, closing, hole filling, largest object, slight erosion, soft edge).
- Also writes red and dark preview images to inspect edges.

Run it only after the position check passed: if the product moved, the mask no longer fits.

## Limits and known failure modes

| Problem | Cause | Fix |
|---|---|---|
| Product deforms | General text-to-image model | Use a multi-image editing model on the render |
| Wrong colour on a side | That side is in no photo | Add more photos; the skill marks assumed parts |
| Perspective shifts | Scene or props asked in the same edit | This skill is plain background only; see [render-to-product-video](../render-to-product-video) for scenes |
| Openings filled in the cutout | Derived mask fills holes | Provide a mask |
| Parts cut in the cutout | Surface almost the same colour as the render background | Provide a mask |
| Light fringe on edges | Generated on a different background | Transparent mode generates on the render's own background; a mask helps further |
| White parts lost | AI background remover on white | Never used here: the mask comes from the render or the user |

## License

[MIT](../LICENSE)
