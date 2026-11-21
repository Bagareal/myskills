# scene-reskin

A Claude skill that places a **real product** into a **photo of an environment**, in the exact position, perspective and size set in the 3D viewer's Scene tab. The viewer exports a `_SCENE.zip` with the photo and a plain grey 3D stand-in of the product; this skill replaces the grey stand-in with the real product (materials, colours, logos from real product photos), with shadows, contact shadow, reflections and light that match the environment. Local checks prove the product did not move.

Output: the final image at the photo's resolution. The user only sees the re-skin (to approve) and the final image; the position checks run behind the scenes.

It is the sibling of [render-reskin](../render-reskin): same approach, but on a real photo instead of a plain background.

## How it works

Two stages, so that each AI call has one job and each can be checked:

```
STAGE 1  grey product ──► crop on white ──► re-skin (editing model + product photos) ──► check (IoU + 50% overlay)
                                                                                              │
                                              cutout with the exported mask ──► paste back in the photo
                                                                                              │
STAGE 2  crop of photo + real product pasted ──► editing model adds shadows, contact shadow, reflections, light
                                                                                              │
         final image ◄── final check (grey at 50%) ◄── lock background (optional) ◄── match light ◄── paste crop back
```

| Step | What happens | Where |
|---|---|---|
| 0. Inputs | Unpack the zip, check sizes, product photos, find a connector | chat, local script |
| 1. Settings | Connector and model, "exact photo" or "inspired", resolution and variants | form |
| 2. Materials and light | Part-by-part materials list and a description of the photo's light, approved by the user | form |
| 3. Stage 1: re-skin | Grey product cropped on white and re-skinned like in render-reskin; checked with `compare.py`; cut out with the mask and pasted back | connector, local scripts, form |
| 4. Stage 2: scene | A crop of the photo with the real product pasted goes to the editing model, which adds shadows and reflections; `match_light.py` then gives the real product the scene's light and white balance; background lock restores the rest of the photo | connector, local scripts |
| 5. Final check | Grey product at 50% over the result, mask outline, product change vs the pasted re-skin | local script |
| 6. Review | Accept, regenerate stage 2, redo the re-skin, or fix a part | form |

Every choice is asked through multiple-choice forms; Claude talks to the user in their own language. The generation service is the user's choice (Magnific, fal or another connector with a multi-image editing model).

## What the `_SCENE.zip` contains

All images have the photo's resolution.

| File | Content |
|---|---|
| `<name>_SCENE_photo.<ext>` | The original photo of the environment |
| `<name>_SCENE_composite.jpg` | The photo with the grey product on it (no shadows, no contact shadow) |
| `<name>_SCENE_grey.png` | Only the grey product on a transparent background, exact position |
| `<name>_SCENE_mask.png` | Product opaque on transparent, antialiased edges |
| `<name>_SCENE_mask_bw.png` | Product black on white |
| `<name>_SCENE.json` | Grid corners, focal length, product position/rotation/size, camera |

## Requirements

- **Claude** with skills enabled (claude.ai, Claude desktop app, or Claude Code), with code execution.
- **A generative-AI connector** (MCP) offering a multi-image editing model, for example Magnific, fal, Replicate or a Google Gemini connector. Recommended model: **Nano Banana 2.1**, then **Nano Banana 2**.
- **Python 3** with `numpy`, `Pillow` and `scipy`. The scripts cost no credits.

## Installation

### claude.ai / Claude desktop app

1. Download `scene-reskin.zip` from the [latest release](../../releases/latest).
2. In Claude's settings, open the **Skills** section and upload the zip.
3. Make sure code execution and file creation are enabled.

### Claude Code

```bash
git clone https://github.com/Bagareal/myskills.git
mkdir -p ~/.claude/skills
cp -r myskills/scene-reskin ~/.claude/skills/
```

## Usage

Invoke it by name or describe the task:

```
/scene-reskin
```

```
Replace the grey product in this scene export with the real product from these photos.
```

Then attach:

1. **The `_SCENE.zip`** from the viewer (or the single files: at least the photo, `_grey.png` and the mask).
2. **Real photos of the product.** More angles (front, side, back, details) give better results. With a single photo, the colours and finishes of unseen sides are a guess, and the skill says so.

## Settings

| Setting | Options | Default |
|---|---|---|
| Connector and model | Every available connector/model combination | Nano Banana 2.1 |
| Rest of the photo | Exact photo (original pixels restored outside product and shadows), or inspired (AI image as generated) | Exact photo |
| Resolution and variants | 1K/2K/4K, 1-4 images | 2K, 1 image |

The aspect ratio is not a setting: the photo's own ratio is used, with padding only if the model cannot take it.

If the photo is larger than the model's output, "exact photo" keeps the photo's full resolution everywhere except the product and shadow area, which is the generated image enlarged. "Inspired" enlarges the whole result and is softer than the photo.

## Scripts

All scripts are in [`scripts/`](scripts) and can also be used on their own.

### `unpack_scene.py`

```bash
python3 -I scripts/unpack_scene.py SCENE.zip work/scene [--prefix NAME]
```

Extracts the files with fixed names (`photo.*`, `composite.*`, `grey.png`, `mask.png`, `mask_bw.png`, `scene.json`) and prints a JSON summary: sizes, ratio, product bounding box and area, camera values, warnings (sizes that differ, product cut by the frame, empty mask). Accepts a folder instead of a zip.

### `crop_product.py`

```bash
python3 -I scripts/crop_product.py work/scene/grey.png work/scene/mask.png work/crop 1:1 [--margin 0.12] [--min-side 1024] [--max-side 2048]
```

Makes the "render" for stage 1: the grey product on pure white, cropped around the product at the given ratio with a margin, enlarged to at least `--min-side`. Also writes the matching mask and `crop.json` (position of the crop in the photo). The crop can extend beyond the photo; that part is white.

### `compare.py` and `cutout.py`

The same scripts as in [render-reskin](../render-reskin), used in stage 1.

```bash
python3 -I scripts/compare.py work/crop/render_crop.png reskin.png side.png blend.png
python3 -I scripts/cutout.py work/crop/render_crop.png reskin.png work/reskin_cutout.png work/crop/mask_crop.png
```

`compare.py` prints the silhouette IoU and bounding boxes and writes a side-by-side and a 50% overlay (the overlay is the verdict). `cutout.py` builds the transparent PNG from the exported mask.

### `paste_back.py`

```bash
python3 -I scripts/paste_back.py work/reskin_cutout.png work/crop/crop.json work/scene/photo.jpg work/paste
```

Puts the re-skinned product back in the photo at the exact place of the grey one. The 1-2 outer pixels of the edge take the colour just inside, so the white background of stage 1 leaves no fringe. Writes `product_layer.png` (transparent, photo size) and `composite_real.png` (photo plus product, no shadows).

### `crop_scene.py`

```bash
python3 -I scripts/crop_scene.py cut work/paste/composite_real.png work/scene/mask.png 1:1 work/s2_crop.png work/s2_crop.json [--margin 0.35]
python3 -I scripts/crop_scene.py paste generated.png work/s2_crop.json work/scene/photo.jpg work/result.png
```

Stage 2 works on a crop around the product, so the product is larger in the model's frame and its small text, icons and digits come out clean. `cut` crops with a margin for shadows and reflections, always inside the photo. `paste` resizes the generated crop to the box and puts it into a copy of the photo, so the result has the photo's size and framing.

### `match_light.py`

```bash
python3 -I scripts/match_light.py work/result.png work/paste/composite_real.png work/scene/mask.png work/result_lit.png [--sigma-frac 0.018] [--erode 2]
```

The real product pasted from stage 1 has perfect detail but studio light; the AI result has the scene's light on the product but can garble small text. This script keeps the detail of the real product and takes the low-frequency light, shading, reflections and white balance from the AI result, only inside the mask. Always run it: a product that does not share the scene's light looks pasted. It prints the colour gap between the AI product and the relit one.

### `fit_canvas.py`

```bash
python3 -I scripts/fit_canvas.py pad   work/paste/composite_real.png work/composite_pad.png 3:2 work/pad.json
python3 -I scripts/fit_canvas.py unpad generated.png work/pad.json work/result.png
```

`pad` extends an image to a ratio by mirroring its own edges (never cropping) and records the padding. `unpad` removes it from the generated image and resizes back to the photo's size. Only needed when stage 2 is run on the whole photo and the model cannot take its ratio.

### `lock_background.py`

```bash
python3 -I scripts/lock_background.py work/scene/photo.jpg work/result.png work/scene/mask.png work/final.png [--thr 14] [--no-color-match]
```

Keeps the AI image on the product and on everything connected to it that the AI changed (shadows, contact shadow, reflections), and restores the original photo pixels elsewhere, with a feathered edge and a small global tone correction. The product is not cut out and pasted, so the AI's shadows survive. Writes `final_region.png` to show what was kept. `--thr` is the difference (0-255) above which a pixel counts as changed: lower keeps fainter shadows.

### `compare_scene.py`

```bash
python3 -I scripts/compare_scene.py work/scene/photo.jpg work/scene/grey.png work/scene/mask.png work/final.png work/check [--ref work/paste/composite_real.png]
```

Writes the grey product at 50% over the result (`overlay_grey50.png`, the verdict), the mask outline over the result, the same cropped around the product, and a side-by-side with the original photo. It prints an edge-alignment signal (whether the strongest edges of the result sit on the mask contour or shifted by some pixels). With `--ref` it also reports how much the product changed since the paste (inside the mask) and writes `product_diff.png`. The numbers are signals: the overlay is the verdict.

## Limits and known failure modes

| Problem | Cause | Fix |
|---|---|---|
| Objects in front of the product are covered | The viewer pastes the grey over everything; the composite has no occlusion information | Not handled. The skill warns about it |
| Product moved or rescaled | The model did not keep the geometry | The overlay shows double edges: regenerate (stage 1 or 2, whichever shows it) |
| Product repainted in stage 2 | The model re-interpreted it while adding shadows | "Product change" number and `product_diff.png`; regenerate stage 2 |
| No shadow or a flat look | The model left the pasted product as it was | The prompt asks for the shadows explicitly; regenerate stage 2 |
| Shadow in the wrong direction | Light description too vague or wrong | Correct it in the approval form and regenerate |
| Long soft shadow cut in "exact photo" | Threshold too high | Lower `--thr` |
| Wrong colour on a side | That side is in no product photo | Add more photos; the skill marks assumed parts |
| Product looks pasted (studio colours, wrong white balance) | Stage 1 light is not the scene's | `match_light.py` takes the light from the AI result; measure the photo's whites for the prompt instead of guessing "warm" or "cool" |
| Garbled text, digits or icons on the product | The model redrew small details | Stage 2 on a crop; `match_light.py` restores the real detail |
| Product reflection harder than the photo's other reflections | The prompt did not describe the existing reflections | Describe their softness, width and contrast in the prompt and regenerate |
| Stage 1 re-skin straightened to the product photo's angle | The model copies the photo's camera angle | The prompt says to keep the render's viewpoint |
| Rest of the scene changed | The editing model redraws the whole image | Use "exact photo" |

## License

[MIT](../LICENSE)
