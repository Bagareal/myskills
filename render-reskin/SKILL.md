---
name: render-reskin
description: Turn a grey 3D product render into a photorealistic packshot from real product photos, keeping the geometry pixel-exact, with a position check and optional transparent cutout.
---

# render-reskin

Re-skin a grey 3D render of a product with the real materials and colours read from photos of the product. The geometry always stays the render's: never generate the product from scratch. Output: a packshot on pure white, or a transparent PNG.

This skill is written in English, but always talk to the user in their own language. Every choice is asked through forms (AskUserQuestion: up to 4 multiple-choice questions per form; the user can always type another answer). Files cannot travel through a form, so attachments are asked for in chat.

The skill works with any connected generative-AI connector (fal, Replicate, a Google Gemini connector or others) that offers an image-editing model accepting several input images. Only the generation call depends on the connector; the scripts do not.

## Scripts

The `scripts/` folder next to this file holds the local tools. They cost no credits. Run them with `python3 -I scripts/<name>.py ...` (use the full path of this skill's folder). They need numpy, Pillow and scipy (`pip install --break-system-packages numpy pillow scipy` if missing).

| Script | Purpose |
|---|---|
| `scripts/pad_to_ratio.py` | Pad the render to the target aspect ratio with its own background colour, never cropping |
| `scripts/compare.py` | Position check: silhouette IoU, bounding boxes, side-by-side and 50% overlay |
| `scripts/cutout.py` | Transparent cutout from a user mask or from a mask derived from the render |

Do not modify `compare.py`: it is the reference check.

## Fixed rules

- Always an image-editing model with several input images. Preferred: Nano Banana 2.1, then Nano Banana 2, on whichever connector offers them (for example on fal: `google/nano-banana-2.1/edit`, `fal-ai/nano-banana-2/edit`). Another multi-image editing model is acceptable if the user picks it, but the position check decides. A general text-to-image model deforms the product: never use one.
- Never guess endpoint IDs or parameter names: read them from the connector's own model search and schema tools.
- Never leave model, aspect ratio or resolution on a connector's `auto` default: set each one explicitly (see Connector notes).
- Image 1 is always the render (padded if needed); the real photos follow.
- Never present a result that failed the check as good. Say what is wrong and regenerate.
- Do not add anything personal, or about the user's employer or clients, to files, prompts or documentation produced with this skill.
- Only the steps in this skill. Do not improvise other tools or tricks to rescue a failed check (crop and paste back, replace background, outpaint, upscale). If the position check fails twice in a row, stop, show the overlay and ask, giving the cost of each option.
- State the cost of each paid generation in one line before running it.

## Step 0: inputs (chat)

Ask in chat for:
1. The grey render (plain, uniform background).
2. Real photos of the product. Tell the user plainly: the more reference photos (front, side, back, details), the better the result. With a single photo the model has to guess the parts that photo does not show, and it can get their colours or finishes wrong.
3. Optional, only if they want a transparent PNG: a mask of the render (subject black on white background, or a PNG with alpha), same framing as the render. Explain that it gives the cleanest edges and handles openings in the product correctly; without it the mask is derived from the render. The 3D viewer's Save the image gives one ZIP (`<name>_POV.zip`): unzip it first. It holds the render, `_mask.png`, `_mask_bw.png` and, only when a part was made see-through in the viewer (a clear bowl, a cover), `_mask_alpha.png`.

Check sizes and aspect ratios of what arrived.

Find the available connectors: look at the connected tools (use ToolSearch for deferred ones) for generative-AI connectors that can run an image-editing model with several input images, and use each connector's model search to see whether it offers Nano Banana 2.1 or 2. If none is connected, say so, search the connector registry for one (SearchMcpRegistry, then SuggestConnectors) and wait for the user to connect it.

## Step 1: settings (form)

One AskUserQuestion form with these four questions:
1. Connector and model: one option per available combination, e.g. "fal - Nano Banana 2.1 (Recommended)", "fal - Nano Banana 2", "[other connector] - Nano Banana 2.1". Put Nano Banana 2.1 first. With a single connector, ask only the model.
2. Background: Pure white packshot / Transparent PNG.
3. Aspect ratio: Keep the render's ratio (Recommended) / 1:1 / 16:9 / 9:16 (state the render's current ratio in the question).
4. Resolution and variants: 2K, 1 image (Recommended) / 4K, 1 image / 2K, 2 variants / 1K, 4 variants. Any other combination can be typed (1K/2K/4K, 1-4 images).

If only one product photo was given, repeat the warning about unseen parts in the question text or right before the form.

Cost check, right after this form: read the balance and the cost of one round with the chosen resolution and number of images, with the connector's own tools (see Connector notes). Tell the user the cost per round. If the balance does not cover it, say so before generating.

## Step 2: materials (form)

Read the photos and list, part by part, the material and colour you see (body, lid, handles, panel, logos, glass, metal, textures). For parts the render shows but no photo shows, write what you will assume and mark it as assumed. Send the list in a message, then a form: "Is this materials list right?" with Correct, go ahead / I'll correct it (the user types the corrections). Use the corrected list in the prompt.

## Step 3: canvas

If the render already has the chosen ratio, skip. Otherwise pad it, never crop, with the render's own background colour:

```
python3 -I scripts/pad_to_ratio.py render.png render_pad.png 16:9
```

The user mask does not need padding: `cutout.py` places it the same way.

## Step 4: re-skin

Convert RGBA photos to RGB on white first. Upload the canvas and the photos the way the chosen connector requires (its own upload tool, a signed URL, or inline data). Read the model's schema on that connector and map the settings onto its parameter names:
- input images in this order: canvas first, then the photos (on fal: `image_urls`);
- aspect ratio = the chosen ratio;
- resolution and number of images as chosen (if the connector has no resolution field, take its largest size up to the chosen one and tell the user);
- reasoning or thinking level at its highest if the model has one (on fal: `thinking_level` `high`);
- PNG output if offered.

If a chosen setting does not exist on that connector, say which one and what you used instead.

Background sentence, depending on the choice:
- White: "Replace the plain background of image 1 with a plain pure white seamless studio background, with only a very soft contact shadow directly under the product."
- Transparent: "Keep the plain [colour] background of image 1 unchanged, with no shadow." (Generating on the render's own background keeps edges neutral for the cutout.)

Prompt template (fill the brackets):

```
Re-skin image 1: turn the grey 3D render of the [product, with its main parts], seen from [camera angle], into a photorealistic studio packshot WITHOUT changing its geometry at all. Every contour, edge, corner, curve, seam line, rib, vent, handle and the whole silhouette must stay at exactly the same pixel positions as in image 1. Same camera angle, same framing, same size in the frame. [Background sentence.] No scene, no props, no extra objects. Only paint real materials and colours taken from the other images: [approved materials list, part by part]. Keep small embossed marks, vents, printed text and logos exactly where they are in image 1. Soft, even studio lighting from the front-left, gentle reflections on metal and glass, no colour casts.
```

## Step 5: position check

For each generated image:

```
python3 -I scripts/compare.py render_pad.png reskin.png side.png blend.png
```

How to read it:
- IoU = shared area of the two silhouettes divided by the area covered by either (1.0 = identical). It is a signal, not the verdict: a soft shadow on the white background widens the generated silhouette and lowers it (0.87 with a correct product; 0.646 has been seen with a correct product too). A generated bbox larger than the reference only on the shadow side is the shadow.
- The 50% overlay (`blend.png`) is the verdict. Look at it whole and in crops on the top, the edges and the bottom. Contours, seams, logos and proportions must line up with no double edges.
- Also look at the re-skin itself: legible text and logos, materials as approved, no invented parts.

## Step 6: review (form)

Send the re-skin(s) and the overlay(s) with SendUserFile, report the IoU and what you saw in the overlay honestly. Then a form: Accept / Regenerate the same prompt / Fix a part (the user types what). With several variants, ask which one to keep. Regenerate only this step.

## Step 7: transparent cutout (only if chosen)

```
python3 -I scripts/cutout.py render_pad.png reskin.png reskin_cutout.png [mask.png]
```

With the user mask it uses that (black subject on white, or alpha; any resolution with the same framing as the original render). When the viewer gave a `_mask_alpha.png`, pass that one here instead of `_mask.png`: the see-through part then stays see-through in the transparent PNG (cutout.py keeps the in-between alpha values). Every position check (IoU, overlay) keeps using `_mask.png`. Without one it derives the mask from the render: background threshold, small closing, holes filled, largest object kept, a few pixels eroded, soft edge. Run it only after the overlay passed: if the product moved, the mask no longer fits.

The script also writes `<name>_preview_red.png` and `<name>_preview_dark.png`. Check them in crops along the edges: light or grey fringe, jagged steps, missing thin parts (cables, feet), filled openings. The previews are for your own check only: never send them to the user. Limits of the derived mask, to tell the user when they apply: openings where the background shows through get filled (a user mask fixes it); surfaces almost the same colour as the render background can be cut; JPEG renders give slightly stepped edges.

## Delivery

Send only the final image with SendUserFile: the transparent PNG (or the white packshot if white was chosen). No previews, no overlay, no intermediate re-skin at this stage: the overlay was already shown in step 6. With several accepted variants, send only the final image of each. Report in one or two sentences what passed, any edge defect found in the previews, and anything assumed (parts no photo showed).

## Connector notes

The steps are the same on every connector; only the parameter names change. Always read the schema; these notes record what was found so far.

fal:
- `google/nano-banana-2.1/edit` or `fal-ai/nano-banana-2/edit`, `image_urls` (canvas first), `aspect_ratio` set explicitly, `resolution` as chosen, `num_images` for variants, `thinking_level` `high`.
- Cost: `estimate_cost`.

Magnific:
- `images_generate` with `mode: imagen-nano-banana-2-flash` (this is Nano Banana 2; `imagen-nano-banana-2` is Nano Banana Pro), `aspectRatio` set to the canvas ratio, `resolution` `2k` or `4k` as chosen, `count` for variants (one call, never one call per variant). Image 1 = first `references` entry of type `image`, then the real photos. Do not use `images_replace_background`, `images_remove_background`, `images_expand` or other image tools in this skill: the white background comes from the prompt and the cutout from `cutout.py`.
- Cost: `account_balance`, then `simulate_cost` with the real arguments.
- Prices seen (Nov 2026, indicative): about 65-75 credits per image at 2K, 150 at 4K.

## Known failure modes

- General image model instead of an editing model: the product deforms.
- One photo only: colours of unseen sides are a guess. Say so.
- White parts on a white background: fine for the packshot, but never use an AI background remover for the cutout; use the render-derived or user mask.
- Asking for a scene or props in the same edit shifts the perspective: this skill is plain background only.
- Fringe on cutout edges: generate on the render's own background (already the rule for transparent) and use a user mask when edges matter.
- Magnific with model and aspect ratio left on auto: re-skin on the full canvas came back mirrored and enlarged. Set Nano Banana 2 and the ratio explicitly.
- Repeated regenerations and rescue edits after a failed check burn credits without fixing the cause: stop after two failures and ask.
