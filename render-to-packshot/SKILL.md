---
name: render-to-packshot
description: Turn a grey 3D product render into a photorealistic packshot using only the product's spec documents (marking spec, colour spec, colour conversion chart), no photos, keeping the geometry pixel-exact, with a position check and transparent cutout.
---

# render-to-packshot

Re-skin a grey 3D render of a product using only its specification documents: a marking spec (logos, pictograms, stickers, screen layout), a colour spec (which colour code goes on which part) and a colour conversion chart (the values of each colour code). No photo of the product is used. The geometry always stays the render's: never generate the product from scratch. Output: a transparent PNG (default) or a packshot on pure white.

This skill is written in English, but always talk to the user in their own language. Every choice is asked through forms (AskUserQuestion: up to 4 multiple-choice questions per form; the user can always type another answer). Files cannot travel through a form, so attachments are asked for in chat.

The skill works with any connected generative-AI connector (fal, Magnific, Replicate, a Google Gemini connector or others) that offers an image-editing model accepting several input images. Only the generation call depends on the connector; the scripts do not.

## Scripts

The `scripts/` folder next to this file holds the local tools. They cost no credits. Run them with `python3 -I <skill folder>/scripts/<name>.py ...`. They need numpy, Pillow, scipy and poppler-utils (`pdftoppm`, `pdftotext`, `pdfinfo`); install what is missing (`pip install --break-system-packages numpy pillow scipy openpyxl`). Never rewrite them: use them as they are.

| Script | Purpose |
|---|---|
| `scripts/pdf_crop.py` | Render a page of a spec PDF, whole or cropped to a box |
| `scripts/color_sheet.py` | Build the colour reference sheet from the chart values (Adobe RGB converted to sRGB, sRGB, or a printed swatch) |
| `scripts/recolor_panel.py` | Recolour the dark background of a marking crop (screen drawn black) to the part's spec colour |
| `scripts/pad_to_ratio.py` | Pad the render to the target aspect ratio with its own background colour, never cropping |
| `scripts/compare.py` | Position check: silhouette IoU, bounding boxes, side-by-side and 50% overlay |
| `scripts/cutout.py` | Transparent cutout from the user mask or a mask derived from the render |

## Fixed rules

- No photos. Use only the render, the specs and the chart. If the inputs contain a photo of the product, do not use it as a reference, not even for a single colour: tell the user it was found and ignored.
- Always an image-editing model with several input images. Preferred: Nano Banana 2.1, then Nano Banana 2 as fallback, on whichever connector offers them. A general text-to-image model deforms the product: never use one.
- Never guess endpoint IDs, model slugs or parameter names: read them from the connector's own model search and schema tools.
- Nothing is assumed. Every colour, finish, part and marking comes from the specs, and a part gets a colour only if a numbered callout drawing in the specs proves where it is on this view. If the render shows something the specs do not cover (a zone with no callout, a marking missing from the marking spec of this variant, a code with no row), stop and ask the user before generating. Never fill the gap with a look-alike part, with the marking of another variant, or with a guess.
- Never leave model, aspect ratio or resolution on a connector's `auto` default: set each one explicitly.
- Image 1 is always the render (padded if needed); the colour sheet and the marking crops follow.
- Colours come from the chart values, never from a guess from the colour name. If the chart has no value for a code, use a crop of its printed swatch and say so.
- Never present a result that failed the check as good. Say what is wrong and regenerate.
- Do not add anything personal, or about the user's employer, clients, brands or product codes, to the skill's files or to its documentation.
- Only the steps in this skill. Do not improvise other tools or tricks to rescue a failed check (crop and paste back, replace background, outpaint, upscale). If the position check fails twice in a row, stop, show the overlay and ask, giving the cost of each option.
- State the cost of each paid generation in one line before running it.

## Step 0: inputs (chat)

The user gives a zip or single files. Ask in chat for what is missing:
1. The grey render (plain, uniform background).
2. Optional: a mask of the render (subject black on white, or a PNG with alpha), same framing as the render. It gives the cleanest cutout and handles openings correctly.
3. The marking spec(s): PDF with logos, pictograms, stickers, printed texts and the screen layout (often with the screen ON and OFF).
4. The colour spec(s): PDF or spreadsheet listing each part with its colour name, colour code and finish.
5. The colour conversion chart: PDF listing each colour code with its values (Adobe RGB, sRGB/HEX, CMYK, Pantone, NCS) and a printed swatch.

Extract a zip into its own new, empty folder and list every file. For each PDF read the page count (`pdfinfo`) and the text (`pdftotext -layout`); for spreadsheets read the cells (openpyxl, `data_only=True`). Look at the render and at the pages (render pages at 40-60 dpi with `pdf_crop.py` without a box) before deciding anything.

The text and cells of a colour spec say what each part is, never where it is. Spreadsheets usually carry numbered callout drawings (a number in a box with an arrow to a part, matching the part numbers of the table): they are the only proof of where each part sits. So for every spreadsheet, convert it to PDF (`soffice --headless --convert-to pdf`), render its pages at 100-250 dpi with `pdf_crop.py`, and look at the callout drawings, zoomed on each area. Also list the images embedded in the file (`unzip` it, look in `xl/media`). Do this before the materials list, for every variant.

Sort the specs:
- Variants: several colour versions of the same product (different references or colour names) are variants. Note which marking spec and colour spec belong to each.
- Versions: the same document in several dates or revisions. Use the most recent (latest date in folder or file name, highest revision) and say which one.
- Any photo found: report it as ignored.

Find the available connectors: look at the connected tools (use ToolSearch for deferred ones) for generative-AI connectors that can run an image-editing model with several input images, and use each connector's model search to see whether it offers Nano Banana 2.1 or 2. If none is connected, say so, search the connector registry (SearchMcpRegistry, then SuggestConnectors) and wait for the user to connect it.

## Step 1: settings (forms)

First form, up to these four questions:
1. Variant: one option per variant found (colour name and the main colours in the description). Skip if there is only one.
2. Connector and model: one option per available combination, Nano Banana 2.1 first and marked Recommended, then Nano Banana 2. With a single connector, ask only the model.
3. Background: Transparent PNG (Recommended) / Pure white packshot.
4. Screen: On, as drawn in the marking spec / Off. Only if the product has a screen or display.

Second form:
1. Aspect ratio: Keep the render's ratio (Recommended) / 1:1 / 16:9 / 9:16 (state the render's current ratio).
2. Resolution and variants: 2K, 1 image (Recommended) / 4K, 1 image / 1K, 1 image / 2K, 2 variants. Any other combination can be typed.

Cost check, right after the forms: read the balance and the cost of one round with the chosen settings, with the connector's own tools (see Connector notes). Tell the user the cost per round. If the balance does not cover it, say so before generating.

## Step 2: spec reading and materials (form)

From the colour spec of the chosen variant, list every part with colour name, code and finish. From the chart, take the values of each code:
- Adobe RGB values: keep them as `argb` for `color_sheet.py`, which converts them to sRGB.
- Only sRGB or HEX: use them as `srgb`.
- No values (speckled, textured, crystal, "according to supplier"...): crop the printed swatch of that code from the chart with `pdf_crop.py` and use it as `swatch`. Look at the crop: it must contain only the swatch, no labels or arrows.
- Metallic finishes: add `:metal` so the patch is drawn as a soft gradient.

From the marking spec, list every visible element with its position on the product: logos, wordmarks, stickers, pictograms, warning symbols, screen icons and texts, and the colour or finish of each. If an element the user expects is missing from the marking spec of this variant, or a variant has no marking spec of its own, look in the marking specs of the other variants and versions of the same product, tell the user what you found there and ask whether to use it for this variant. Never apply the marking of another variant without that answer.

Map all this onto the render with a zone table, one row per visible zone of the render (for example: column, lid body, ribbed band, dome top, bowl shell, bowl handle, base plate, base rim, feet): the DS part number and name, the callout drawing and arrow that proves it, the colour code and finish exactly as the DS writes them. Read the callouts zone by zone: the same ribbed look can belong to different parts, and a colour name in the table must not be put on a zone because it looks similar; only the callout decides. A part from the sheets that no callout places on this view (inner parts, rear parts, parts under a cover) is excluded and not painted. A zone with no callout, or a row whose colour the DS leaves empty, is not filled by guessing: list it as open and ask the user about it. Send the list in a message (part, colour name, code, sRGB value, finish; then the marking elements), then a form: "Is this materials list right?" with Correct, go ahead / I'll correct it (the user types the corrections). The list contains only what the DS says, each line with its callout number. Open zones are asked first, each as its own question in a form (up to 4 per form), and nothing is generated while one is open.

## Step 3: references

1. Colour sheet, one patch per colour that appears on the visible parts, labelled with the part:
```
python3 -I scripts/color_sheet.py colors.png "BODY: <NAME>=argb:R,G,B" "TOP: <NAME>=argb:R,G,B:metal" "BOWL: <NAME>=swatch:swatch.png" "BASE: <NAME>=srgb:R,G,B"
```
Keep the printed sRGB values: they go into the prompt and the final report.

2. Marking crops: find each element on the marking spec pages at 40-60 dpi, then crop it at 200-300 dpi (box coordinates scale with the dpi):
```
python3 -I scripts/pdf_crop.py marking.pdf PAGE 200 logo.png X0 Y0 X1 Y1
```
One crop per element (wordmark, sticker, screen...). Look at every crop: whole element, no dimension lines, labels or neighbouring drawings.

3. Background of the crops: the marking spec often draws screens and panels black whatever their real colour. If the colour spec gives that part another colour, recolour the crop's dark background to it, keeping icons and texts light:
```
python3 -I scripts/recolor_panel.py screen.png screen_spec.png R,G,B
```
Use the sRGB value of the part from the colour sheet. Look at the result. If the screen is chosen Off, do not send the screen crop: describe the screen in the prompt as plain, in its spec colour.

## Step 4: canvas

If the render already has the chosen ratio, skip. Otherwise pad it, never crop, with the render's own background colour:
```
python3 -I scripts/pad_to_ratio.py render.png render_pad.png 4:3
```
The user mask does not need padding: `cutout.py` places it the same way.

## Step 5: re-skin

Upload the canvas, the colour sheet and the crops the way the chosen connector requires (see Connector notes). Read the model's schema on that connector and map the settings onto its parameter names:
- input images in this order: canvas, colour sheet, then the marking crops;
- aspect ratio = the chosen ratio;
- resolution and number of images as chosen;
- reasoning or thinking level at its highest if the model has one;
- PNG output if offered.
If a chosen setting does not exist on that connector, say which one and what you used instead.

Background sentence, depending on the choice:
- Transparent: "Keep the plain [colour] background of image 1 unchanged, with no shadow." (Generating on the render's own background keeps edges neutral for the cutout.)
- White: "Replace the plain background of image 1 with a plain pure white seamless studio background, with only a very soft contact shadow directly under the product."

Prompt template (fill the brackets; one sentence per part and per marking element, naming the image that shows it):

```
Re-skin image 1: turn the grey 3D render of the [product, with its main parts], seen from [camera angle], into a photorealistic studio packshot WITHOUT changing its geometry at all. Every contour, edge, corner, curve, seam line, rib, vent, handle and the whole silhouette must stay at exactly the same pixel positions as in image 1. Same camera angle, same framing, same size in the frame. [Background sentence.] No scene, no props, no extra objects. Only paint real materials, using EXACTLY the colours of the swatches in image 2 (no other colours): [part] in the [LABEL] swatch of image 2 ([colour description], sRGB about R G B), [finish]; [...each part...]. [Screen sentence.] [For each marking element: what it is, exactly like image N, its colour or finish, at the place and size of the matching mark in image 1, in the correct perspective.] Keep small embossed marks, vents, printed text and logos exactly where they are in image 1. Soft, even studio lighting from the front-left, gentle reflections, no colour casts.
```

Screen sentence when On and the screen is not black in the colour spec: "The screen on [where] is NOT black and NOT dark: it is the same [LABEL] colour as [part], only glossier, exactly like the panel in image N, switched on, with crisp [colour] backlit icons and text laid out exactly as in image N ([list them]), placed on the screen area of image 1."

Stickers and small logos on a surface seen at a grazing angle: describe the shape explicitly (for example "a red circle outline with a large bold upright capital T centred inside it, filling most of the circle, its stem vertical"), and say whether the inside is transparent or filled.

## Step 6: position check

For each generated image:
```
python3 -I scripts/compare.py render_pad.png reskin.png side.png blend.png
```
How to read it:
- IoU = shared area of the two silhouettes divided by the area covered by either (1.0 = identical). It is a signal, not the verdict: a shadow, or a generated background slightly darker than the render's at the edges, lowers it with a correct product. A generated bbox larger than the reference only towards the image border or only on the shadow side is the background or the shadow.
- The 50% overlay (`blend.png`) is the verdict. Look at it whole and in crops on the top, the edges and the bottom. Contours, seams, logos and proportions must line up with no double edges.
- Also check the re-skin against the spec: each part in its sheet colour (compare visually with image 2), screen in its spec colour, every marking element present, at its place, legible and with the right shape. At 1K, small screen texts are often imprecise: report it.
- Then check zone by zone against the zone table of Step 2: for each row, look at that zone in the re-skin and confirm the colour and finish of that row, and that nothing extra appears (a ring, a trim line or a part that is not in the table). A zone painted from a look-alike part instead of from its own callout is a failed check, even if the overlay is perfect.

## Step 7: review (form)

Send the re-skin(s) and the overlay(s) with SendUserFile, report the IoU and what you saw honestly, including any element that does not match the spec. Then a form: Accept / Regenerate the same prompt / Fix a part (the user types what). With several variants, ask which one to keep. If the user picks Fix a part without typing what, ask in chat. Regenerate only this step; fix references (colour sheet, crops) when the fault comes from them, not only the prompt.

## Step 8: transparent cutout (only if chosen)

```
python3 -I scripts/cutout.py render_pad.png reskin.png reskin_cutout.png [mask.png]
```
With the user mask it uses that (black subject on white, or alpha; any resolution with the same framing as the original render). Without one it derives the mask from the render. Run it only after the overlay passed. Check the red and dark previews in crops along the edges: light or grey fringe, jagged steps, missing thin parts, filled openings. The previews are for your own check only: never send them to the user.

## Delivery

Send only the final image with SendUserFile (the transparent PNG, or the white packshot). Then report in a few lines:
- the colour codes used, part by part, with the chart values and the sRGB values;
- codes that had no values in the chart and were taken from the printed swatch;
- marking elements taken from another variant's or version's spec;
- zones the specs did not cover, and what the user decided for each (none are assumed by the skill);
- any defect still visible (small texts, small logos).

## Connector notes

The steps are the same on every connector; only the parameter names change. Always read the schema; these notes record what was found so far.

fal:
- `google/nano-banana-2.1/edit` or `fal-ai/nano-banana-2/edit`, `image_urls` (canvas first), `aspect_ratio` set explicitly, `resolution` as chosen, `num_images` for variants, `thinking_level` `high`.
- Cost: `estimate_cost`.

Magnific:
- `images_generate` with `mode: imagen-nano-banana-2-1` (Nano Banana 2.1) or, as fallback, `imagen-nano-banana-2-flash` (Nano Banana 2; `imagen-nano-banana-2` is Nano Banana Pro). `aspectRatio` set to the canvas ratio, `resolution` `1k`, `2k` or `4k` as chosen, `count` for variants (one call, never one call per variant). References of type `image`, in order: canvas, colour sheet, crops.
- Local files: `creations_request_upload` (one target per file), HTTP PUT of the raw bytes with the right `Content-Type`, then `creations_finalize_upload` with `visible: false`.
- Do not use `images_replace_background`, `images_remove_background`, `images_expand` or other image tools: the background comes from the prompt and the cutout from `cutout.py`.
- Cost: `account_balance`, then `simulate_cost` with the real arguments.
- Prices seen (Nov 2026, indicative): Nano Banana 2.1 at 1K about 50 credits per image.

## Known failure modes

- A product photo in the inputs used as a reference: its colours fight the chart values. Ignore photos.
- Screen came out black or navy: the marking crop has a black background. Recolour it with `recolor_panel.py` and say in the prompt that the screen is not black.
- Element missing from this variant's marking spec (for example a sticker on the lid): it may be in another variant's or a newer version's spec. Tell the user and ask; never use it silently.
- Colour codes with no values in the chart: use the printed swatch, and say the colour is approximate.
- Small sticker or logo on a surface seen at a grazing angle comes out small or tilted: describe its shape explicitly; it may stay imperfect at 1K.
- Small screen texts imprecise at 1K: use 2K or more when they matter.
- General image model instead of an editing model: the product deforms.
- Model and aspect ratio left on auto (seen on Magnific): re-skin mirrored and enlarged. Set them explicitly.
- Repeated regenerations and rescue edits after a failed check burn credits without fixing the cause: stop after two failures and ask.
- Painting from the colour-spec text alone, without the callout drawings: a ribbed band painted in the colour of a vent window that sits on the back of the product, the visible shell of a part painted in the colour of an inner part, a ring painted chrome that is not visible on this view, the marking of one variant applied to the others. Read the callout drawings first and build the zone table; anything the specs do not cover is asked, never guessed.
