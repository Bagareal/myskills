# render-to-packshot

A Claude skill that turns a **grey 3D product render** into a **photorealistic packshot** using only the product's **specification documents**: a marking spec, a colour spec and a colour conversion chart. No photo of the product is needed or used. The geometry is never regenerated: every contour stays at the same pixel position as in the render, and a local position check proves it before anything is delivered.

Output: a transparent PNG (default) or a packshot on pure white.

## Why

[render-reskin](../render-reskin) paints a render with the materials seen in real photos. Before a product exists, or when the photos show another colour version, there are no usable photos, but the product team already has the specs: which colour code goes on each part, the exact values of each code, and drawings of every logo, sticker and screen. This skill builds the references from those documents, so the colours come from the chart values instead of a photo or a guess from a colour name.

## Inputs

| Input | What it is | Used for |
|---|---|---|
| Grey render | 3D render of the product on a plain background | Geometry (image 1) |
| Mask (optional) | Subject black on white, or PNG with alpha, same framing | Clean transparent cutout |
| Marking spec | PDF with logos, wordmarks, stickers, pictograms, warning symbols, screen layout (on and off) | Crops sent to the model |
| Colour spec | PDF or spreadsheet: each part with colour name, code and finish | Which colour goes where |
| Colour conversion chart | PDF: each colour code with Adobe RGB, sRGB/HEX, CMYK, Pantone or NCS values and a printed swatch | Exact colour values |

They can be given as a zip or as single files. Several colour variants and several dated versions of the same document can be in the same zip: the skill asks which variant to make and uses the most recent version of each document. Any product photo found in the inputs is ignored, and the skill says so.

## How it works

```
specs ──► variant + settings (forms) ──► parts, codes, chart values, marking elements (approved by the user)
                                                    │
                     colour sheet + marking crops ◄─┘
                                    │
grey render ──► pad to ratio ──► re-skin (editing model: render + colour sheet + crops) ──► position check ──► review ──► cutout ──► final image
```

| Step | What happens | Where |
|---|---|---|
| 0. Inputs | Unzip, list files, read PDFs and spreadsheets, sort variants and versions, find a connector | chat + local |
| 1. Settings | Variant, connector and model, background, screen on/off; aspect ratio, resolution and variants; balance and cost per round | forms + connector |
| 2. Spec reading | Parts with colour code, chart values and finish; marking elements and their positions; assumed parts marked; user confirms | form |
| 3. References | Colour sheet from the chart values; marking elements cropped from the PDFs; black screen backgrounds recoloured to the spec colour | local scripts |
| 4. Canvas | Render padded (never cropped) to the target ratio | local script |
| 5. Re-skin | Editing model call with a geometry-locking prompt and the references | connector |
| 6. Position check | Silhouette IoU, bounding boxes, 50% overlay, check against the spec | local script |
| 7. Review | Re-skin and overlay shown; accept, regenerate or fix a part | form |
| 8. Cutout | Transparent PNG from the user mask or a render-derived mask | local script |

At the end Claude reports the colour codes used part by part with their values, the codes taken from a printed swatch, the elements taken from another variant's spec and the assumed parts.

Every choice is asked through multiple-choice forms; Claude talks to the user in their own language.

## Requirements

- **Claude** with skills enabled (claude.ai, Claude desktop app, or Claude Code), with code execution.
- **A generative-AI connector** (MCP) that offers a multi-image editing model. **Tested with Magnific**; other connectors (fal, Replicate, a Google Gemini connector...) need the generation step adapted, see [Connectors and credits](#connectors-and-credits). Recommended model: **Nano Banana 2.1**, with **Nano Banana 2** as fallback.
- **Python 3** with `numpy`, `Pillow`, `scipy` (and `openpyxl` for spreadsheet specs), and **poppler-utils** (`pdftoppm`, `pdftotext`, `pdfinfo`). The scripts cost no credits.

## Installation

### claude.ai / Claude desktop app

1. Download `render-to-packshot.zip` from the [latest release](../../releases/latest), or build it (see the main README).
2. In Claude's settings, open the **Skills** section and upload the zip.
3. Make sure code execution and file creation are enabled.

### Claude Code

```bash
git clone https://github.com/Bagareal/myskills.git
mkdir -p ~/.claude/skills
cp -r myskills/render-to-packshot ~/.claude/skills/
```

## Usage

```
/render-to-packshot
```

```
Make the packshot of this render from the specs in the zip.
```

Then attach the zip, or the render, the mask, the specs and the chart as single files.

## Settings

| Setting | Options | Default |
|---|---|---|
| Variant | One per colour variant found in the specs | - (asked only if there are several) |
| Connector and model | Every available connector/model combination | Nano Banana 2.1 |
| Background | Transparent PNG, pure white packshot | Transparent PNG |
| Screen | On (as drawn in the marking spec), off | - (asked only if there is a screen) |
| Aspect ratio | Keep the render's ratio, 1:1, 16:9, 9:16, or typed | Render's ratio |
| Resolution and variants | 1K/2K/4K, 1-4 images | 2K, 1 image |

## Connectors and credits

**Tested on Magnific only.** This skill has been built and tested with Magnific and Nano Banana 2.1. Everything else in it is connector-independent: the scripts run locally, and the steps and forms are the same anywhere. The only connector-specific part is the generation call in step 5 (how files are uploaded, the model ID, the parameter names). To use another connector, aggregator or model (fal, Replicate, a Google Gemini connector, a different editing model...), adapt that part: the upload of the local files, the model ID, and the mapping of input images, aspect ratio, resolution and number of images onto its parameters, then update the "Connector notes" section of `SKILL.md`. The fal column below comes from [render-reskin](../render-reskin), where fal was used, and has not been tested with this skill.

Same rules as the other imagery skills in this repository:

- **Cost first**: balance and price of one round before the first generation.
- **Nothing on `auto`**: model, aspect ratio and resolution always set explicitly.
- **Only the skill's steps**: no extra tools to rescue a failed check; the background comes from the prompt and the cutout from `cutout.py`.
- **Stop after two failures** of the position check, with the cost of each option.
- **Cost before each call.**

| | fal | Magnific |
|---|---|---|
| Model | `google/nano-banana-2.1/edit`, fallback `fal-ai/nano-banana-2/edit` | `images_generate` with `mode: imagen-nano-banana-2-1`, fallback `imagen-nano-banana-2-flash` (`imagen-nano-banana-2` is Nano Banana Pro) |
| Inputs | `image_urls`: canvas, colour sheet, crops | `references` of type `image`, same order; local files via `creations_request_upload`, PUT, `creations_finalize_upload` |
| Settings | `aspect_ratio` explicit, `resolution` as chosen, `thinking_level` `high` | `aspectRatio` explicit, `resolution` as chosen |
| Variants | `num_images` | `count`, in one call |
| Cost tools | `estimate_cost` | `account_balance`, then `simulate_cost` |

Price seen on Magnific (November 2026, indicative): Nano Banana 2.1 at 1K about 50 credits per image.

## Scripts

All scripts are in [`scripts/`](scripts) and can also be used on their own. `pad_to_ratio.py`, `compare.py` and `cutout.py` are the same as in [render-reskin](../render-reskin), where they are documented in detail.

### `pdf_crop.py`

Renders one page of a PDF, whole or cropped to a box (coordinates in pixels at the chosen dpi).

```bash
python3 -I scripts/pdf_crop.py marking.pdf 1 60 page1.png
python3 -I scripts/pdf_crop.py marking.pdf 1 200 screen.png 300 1850 1850 2230
```

### `color_sheet.py`

Builds the colour sheet sent to the model as image 2: one labelled 300 px patch per colour, and prints the sRGB value of each.

```bash
python3 -I scripts/color_sheet.py colors.png "BODY: GREEN=argb:155,168,165" "TOP: SILVER=argb:179,175,179:metal" "BOWL: SPECKLED=swatch:swatch.png" "BASE: BLACK=srgb:27,25,26"
```

- `argb:R,G,B`: Adobe RGB values from the chart, converted to sRGB (Adobe RGB 1998 primaries, gamma 563/256, D65).
- `srgb:R,G,B`: values used as they are.
- `swatch:file.png`: a crop of the printed swatch, for codes with no values (speckled, textured, crystal...). The median colour is printed.
- `:metal`: draws the patch as a soft metallic gradient.

### `recolor_panel.py`

Marking specs often draw screens black whatever their real colour. This recolours the dark background of a crop to the part's spec colour and keeps light icons and texts light.

```bash
python3 -I scripts/recolor_panel.py screen.png screen_spec.png 151,170,166
```

## Limits and known failure modes

| Problem | Cause | Fix |
|---|---|---|
| Colours drift from the spec | A product photo was used as a reference | Photos are always ignored |
| Screen black or navy instead of the spec colour | Marking crop drawn on black | `recolor_panel.py`, and the prompt says the screen is not black |
| Sticker or logo missing | Not drawn in this variant's marking spec | Look in the other variants' and versions' specs |
| Colour approximate | Code with no values in the chart | Printed swatch used, and reported |
| Small sticker small or tilted | Surface seen at a grazing angle | Describe its shape explicitly in the prompt; higher resolution |
| Small screen texts imprecise | 1K resolution | 2K or more |
| IoU lower with a correct product | Generated background slightly darker at the edges, or a shadow | The overlay decides |
| Product deforms | General text-to-image model | Multi-image editing model only |
| Re-skin mirrored or enlarged | Model and aspect ratio left on `auto` | Set them explicitly |

## License

[MIT](../LICENSE)
