---
name: scene-reskin
description: Replace a grey 3D product stand-in placed in a photo of an environment (a _SCENE export from the 3D viewer) with the real product from photos, same position, perspective and size, with AI-made shadows, contact shadow and reflections, plus a position check.
---

# scene-reskin

The 3D viewer's Scene tab exports a `_SCENE.zip`: a photo of an environment with a plain grey 3D product placed on it, in the exact position, perspective and size wanted. This skill turns that grey stand-in into the real product, read from photos of it, integrated in the photo with shadows, contact shadow, reflections and light that match the environment. The rest of the photo stays as it is. Output: the final image at the photo's resolution. The position is proved by the checks, which are for Claude's own use and are not shown to the user.

It works in two stages, so that each AI call has one job and each can be checked:
1. **Re-skin** (the render-reskin method): the grey product alone, on white, cropped around the product, is re-skinned with the real materials from the photos and checked with the silhouette IoU and the 50% overlay. The result is cut out with the exported mask and pasted back at the exact place in the photo.
2. **Scene**: the photo with the real product pasted on it (no shadows, light not matched) goes to the editing model, which adds the shadows, contact shadow, reflections and light integration. The product's own detail (text, icons, logos) must not change. Because the model can garble small text, the final product is always rebuilt by `match_light.py`: detail from the real product, light, shading and white balance from the scene. The result must look photographed in that place, not pasted.

This skill is written in English, but always talk to the user in their own language. Every choice is asked through forms (AskUserQuestion: up to 4 multiple-choice questions per form; the user can always type another answer). Files cannot travel through a form, so attachments are asked for in chat.

The skill works with any connected generative-AI connector (fal, Magnific, Replicate, a Google Gemini connector or others) that offers an image-editing model accepting several input images. The user chooses the service; only the generation calls depend on it, the scripts do not.

## Scripts

The `scripts/` folder next to this file holds the local tools. They cost no credits. Run them with `python3 -I scripts/<name>.py ...` (use the full path of this skill's folder). They need numpy, Pillow and scipy (`pip install --break-system-packages numpy pillow scipy` if missing).

| Script | Purpose |
|---|---|
| `scripts/unpack_scene.py` | Unpack the `_SCENE` zip (or folder), check that all images have the same size, print a JSON summary |
| `scripts/crop_product.py` | Stage 1: cut the grey product out as a "render" (grey on pure white), cropped around the product at the model's ratio and enlarged |
| `scripts/compare.py` | Stage 1 position check on the crop: silhouette IoU, bounding boxes, side-by-side and 50% overlay (same script as render-reskin, do not modify) |
| `scripts/cutout.py` | Stage 1: transparent cutout of the re-skin using the exported mask (same script as render-reskin) |
| `scripts/paste_back.py` | Stage 1: put the cutout back in the photo at the exact place, with clean edges; writes `composite_real.png` |
| `scripts/crop_scene.py` | Stage 2: `cut` crops the photo around the product (so the product is bigger in the model's frame and its small text comes out cleaner); `paste` puts the generated crop back into a copy of the photo |
| `scripts/fit_canvas.py` | Stage 2: `pad` extends the photo to a ratio by mirroring its edges, never cropping; `unpad` removes the padding and resizes back to the photo's size |
| `scripts/match_light.py` | Stage 2, always run: the real product keeps its detail but takes the light, shading, reflections and white balance of the scene from the AI result |
| `scripts/lock_background.py` | Stage 2: put the original photo pixels back everywhere the AI had no reason to change; keep the AI image on the product and its shadows |
| `scripts/compare_scene.py` | Final position check on the photo: `_grey.png` at 50% over the result, mask outline, edge-alignment signal, product change vs the pasted re-skin |

## What the export contains

All images have the photo's resolution.

| File | Content |
|---|---|
| `<name>_SCENE_photo.<ext>` | The original photo of the environment |
| `<name>_SCENE_composite.jpg` | The photo with the grey product placed on it (neutral grey, no shadows, no contact shadow). Only for the user's reference: not sent to the model |
| `<name>_SCENE_grey.png` | Only the grey product, transparent background, exact position |
| `<name>_SCENE_mask.png`, `<name>_SCENE_mask_bw.png` | Product mask (opaque on transparent / black on white), antialiased |
| `<name>_SCENE_mask_alpha.png` | Only when a part was made see-through in the viewer (a clear bowl, a cover): the same mask, where that part covers only as much as it lets through. Not used by the stages below: they use `_mask.png`, where the see-through part counts as solid, and `unpack_scene.py` leaves it out. Use it only if the user wants a transparent cutout of the product alone with that part see-through |
| `<name>_SCENE.json` | Grid corners, focal length, product position/rotation/size, camera (`focal_mm`, `fov_vertical_deg`, `matrix_world`) |

## Fixed rules

- The user sees only two things: the re-skin from stage 1 (to approve) and the final image. Never send overlays, side-by-sides, outlines, previews, region maps, difference maps or numbers from the checks. Run every check yourself. If a check fails, regenerate without asking and without showing the failed attempt (at most 2 silent retries per stage), then tell the user plainly what still does not match.
- Always an image-editing model with several input images. Preferred: Nano Banana 2.1, then Nano Banana 2, on whichever connector offers them. Another multi-image editing model is acceptable if the user picks it, but the checks decide. A general text-to-image model redraws the product and the scene: never use one.
- Never guess endpoint IDs or parameter names: read them from the connector's own model search and schema tools.
- The grey product defines the geometry: silhouette, position, perspective, size. If the real product photos show different proportions from the grey shape, the grey shape wins; tell the user.
- The AI must create the shadows, in stage 2, on the photo. Never fake them by hand.
- The product must reflect the scene's shadows, light and white balance. A product with its studio colours pasted into a scene is a failure even if the position is perfect. Always run `match_light.py` on the stage 2 result, and judge the final image on this: whites of the product have the colour of the scene's whites, its shading follows the light direction, its reflections and the contact shadow are consistent with the surface.
- The reflection of the product on a glossy surface must have the same softness, width and contrast as the reflections already in the photo (for example of another object on the same surface). A dark narrow streak on a surface that reflects softly is wrong.
- The scripts in `scripts/` are fixed: always use them as they are. Do not rewrite them inline; if one needs a change, tell the user.
- Never present a result that failed a check as good. Say what is wrong and regenerate.
- Do not add anything personal, or about the user's employer or clients, to files, prompts or documentation produced with this skill.

## Step 0: inputs (chat)

Ask in chat for:
1. The `_SCENE.zip` (or the single files: at least the photo, `_grey.png` and the mask; the composite is not needed).
2. Real photos of the product. Tell the user plainly: the more reference photos (front, side, back, details), the better the result. With a single photo the model has to guess the parts that photo does not show, and it can get their colours or finishes wrong. Say it again, specifically, if the grey product is seen from an angle the photo does not show (for example a front photo and a three-quarter view in the scene): the visible sides are a guess.

Unpack and check:

```
python3 -I scripts/unpack_scene.py SCENE.zip work/scene
```

Report anything in `warnings` (sizes that differ, the product cut by the frame, an empty mask). Look at the photo yourself. If the grey shape covers something that in reality is in front of the product, tell the user plainly that this skill does not handle foreground objects: the viewer pastes the grey over everything, so the real product would also end up in front. Do not present that as solved.

Find the available connectors: look at the connected tools (use ToolSearch for deferred ones) for generative-AI connectors that can run an image-editing model with several input images, and use each connector's model search to see what is offered. If none is connected, say so, search the connector registry for one (SearchMcpRegistry, then SuggestConnectors) and wait for the user to connect it.

## Step 1: settings (form)

One AskUserQuestion form with three questions:
1. Connector and model: one option per available combination, e.g. "fal - Nano Banana 2.1 (Recommended)", "fal - Nano Banana 2", "[other connector] - Nano Banana 2.1". With a single connector, ask only the model. Used for both stages.
2. The rest of the photo: "Exact photo: everything outside the product and its shadows is restored from the original, pixel for pixel (Recommended)" / "Inspired by the photo: keep the AI image as generated, the rest of the scene may change slightly". The user decides this each time.
3. Resolution and variants: 2K, 1 image (Recommended) / 4K, 1 image / 2K, 2 variants / 1K, 4 variants. Any other combination can be typed. State the photo's size in the question. The re-skin of stage 1 is a crop around the product, enlarged, so it has more detail than the product has in the photo. For stage 2, explain what happens if the photo is larger than the chosen output: with "exact photo" the final image keeps the photo's full resolution (the background is the original, only the product and shadow area is the generated image enlarged); with "inspired" the result is enlarged to the photo's size and is softer than the photo, so tell the user and suggest the largest size the model offers.

If only one product photo was given, repeat the warning about unseen parts right before the form.

## Step 2: materials and light (form)

Read the product photos and list, part by part, the material and colour you see (body, lid, handles, panel, logos, glass, metal, textures). For parts the grey shape shows but no photo shows, write what you will assume and mark it as assumed.

Then look at the environment photo and describe in one or two sentences what the stage 2 prompt will say about the light: where it comes from (window, lamp, ceiling), how hard or soft, what surface the product stands on (and its finish: glossy, matte, textured), how its existing reflections look (for example the reflection of another object: wide and soft, or sharp), and what is next to the product that could cast or receive shadows and reflections. Do not guess the colour temperature by eye: measure the colour of the photo's whites or neutral surfaces (a few crops, average RGB) and say whether they are neutral, cool or warm. Words like "warm light" in a prompt shift the white balance wrongly.

Send both in a message, then a form: "Are the materials and the light description right?" with Correct, go ahead / I'll correct it (the user types the corrections). Use the corrected text in the prompts.

## Step 3: stage 1, re-skin the product alone

Convert RGBA product photos to RGB on white first.

Crop the grey product to a plain render. The crop ratio is the one the model takes: the supported ratio closest to the product's shape (usually 1:1, 4:3 or 3:4), read from the model's schema:

```
python3 -I scripts/crop_product.py work/scene/grey.png work/scene/mask.png work/crop 1:1
```

It writes `render_crop.png` (grey on pure white, enlarged to at least 1024 px on the long side), `mask_crop.png` and `crop.json` (where the crop sits in the photo).

Generate. Upload `render_crop.png` and the product photos the way the chosen connector requires (its own upload tool, a signed URL, or inline data). Read the model's schema and map the settings onto its parameter names:
- input images in this order: `render_crop.png` first, then the product photos;
- aspect ratio = the crop's ratio;
- resolution and number of images as chosen (if the connector has no resolution field, take its largest size up to the chosen one and tell the user);
- reasoning or thinking level at its highest if the model has one;
- PNG output if offered.

If a chosen setting does not exist on that connector, say which one and what you used instead.

Prompt template (fill the brackets):

```
Re-skin image 1: turn the grey 3D render of the [product, with its main parts], seen from [camera angle], into a photorealistic studio packshot WITHOUT changing its geometry at all. Every contour, edge, corner, curve, seam line, rib, vent, handle and the whole silhouette must stay at exactly the same pixel positions as in image 1. Same camera angle, same framing, same size in the frame. Keep the plain white background of image 1 unchanged, with no shadow. No scene, no props, no extra objects. Only paint real materials and colours taken from the other images: [approved materials list, part by part]. Keep small embossed marks, vents, printed text and logos exactly where they are in image 1. Keep the three-quarter viewpoint of image 1: do NOT copy the camera angle of the product photos, they are only a source of materials, colours and printed details. Soft, even studio lighting from the front-left, gentle reflections on metal and glass, no colour casts.
```

Check each candidate exactly as in render-reskin (the crop has a plain background, so the original check works):

```
python3 -I scripts/compare.py work/crop/render_crop.png reskin.png side.png blend.png
```

- IoU = shared area of the two silhouettes divided by the area covered by either (1.0 = identical). It is a signal: here, with no shadow on white, it should be high (about 0.95 or more); clearly lower means the product changed.
- The 50% overlay (`blend.png`) is the verdict: contours, seams, logos and proportions must line up with no double edges, whole and in crops on the top, the edges and the bottom.
- Also look at the re-skin itself: legible text and logos, materials as approved, no invented parts.

Send only the re-skin image with SendUserFile (no overlay, no side-by-side, no IoU) and ask a short form: Accept / Regenerate the same prompt / Fix a part (the user types what). Show it only after it has passed the check above yourself. With several variants, send only those that passed and ask which one to keep. Regenerate only this stage.

When accepted, cut it out with the exported mask and paste it back in the photo:

```
python3 -I scripts/cutout.py work/crop/render_crop.png reskin.png work/reskin_cutout.png work/crop/mask_crop.png
python3 -I scripts/paste_back.py work/reskin_cutout.png work/crop/crop.json work/scene/photo.jpg work/paste
```

`cutout.py` also writes `_preview_red.png` and `_preview_dark.png`: check them in crops along the edges (light or grey fringe, jagged steps, missing thin parts) for your own use, never send them. `paste_back.py` cleans the 1-2 outer pixels of the edge so the white background does not leave a fringe, and writes `product_layer.png` and `composite_real.png` (the photo with the real product pasted: no shadows, light not matched). Look at `composite_real.png` before going on: the product must sit exactly where the grey one was.

## Step 4: stage 2, put it in the scene

Work on a crop around the product, not on the whole photo: the product is then larger in the model's frame and its small text, icons and digits come out clean (on the whole photo they come out garbled when the product is small in the frame).

```
python3 -I scripts/crop_scene.py cut work/paste/composite_real.png work/scene/mask.png 1:1 work/s2_crop.png work/s2_crop.json
```

It crops around the product with a margin (`--margin`, default 0.35 of the product's larger side, enough for shadows and reflections; raise it if the product is near the edge or has long shadows) at the chosen ratio, always inside the photo. Upload `s2_crop.png` plus one or two of the best product photos as detail reference. Same parameter mapping as in step 3, with the ratio of the crop. The model's output ratio can differ slightly from the request: `crop_scene.py paste` handles it and warns if the difference is large.

Prompt template (fill the brackets):

```
Image 1 is a crop of a photo of [short description of the environment] with a real [product] placed on [surface]. The product was added afterwards: it has no shadows and its light does not match the scene yet. Make it look photographed in the scene. Keep the product's exact shape, size, position and perspective, and do NOT redraw, retype, blur or alter ANY text, icon, digit or logo on it ([list the visible texts]); keep its display and panels exactly as they are. Add a contact shadow where it touches [surface], a cast shadow that follows the light of the photo ([approved light description]), and the reflection of the product on [surface]: it must match exactly the reflection already visible in the photo of [existing reflected object]: [softness, width, contrast, tone as described], not a dark sharp streak. Match the photo's exposure and white balance ([measured: neutral / cool / warm], no other cast), noise and sharpness. Do not change anything else. Image 2 is a photo of the real product, only to help keep its details right: ignore its camera angle, background and lighting.
```

Put the generated crop back into the photo and relight the product:

```
python3 -I scripts/crop_scene.py paste generated.png work/s2_crop.json work/scene/photo.jpg work/result.png
python3 -I scripts/match_light.py work/result.png work/paste/composite_real.png work/scene/mask.png work/result_lit.png
```

`match_light.py` rebuilds the product from the real one (all its text and logos intact) with the light, shading, reflections and white balance of the AI result, and prints the colour gap between the AI product and the relit one (it should be close to zero). Then, depending on the choice in Step 1:
- Exact photo:

```
python3 -I scripts/lock_background.py work/scene/photo.jpg work/result_lit.png work/scene/mask.png work/final.png
```

  The script keeps the AI image on the product and on everything connected to it that the AI changed (shadows, contact shadow, reflections), and puts the original photo pixels back everywhere else, with a feathered edge and a small global tone correction. It writes `final_region.png` (white = kept from the AI): it must contain the product and its shadows and nothing else. If shadows are cut, lower `--thr` (default 14); if too much of the photo is taken from the AI, raise it.
- Inspired by the photo (the scene may be rebuilt by the model, the exact photo pixels are not used): do not give the model the photo as the canvas. Give it two images: the pasted product alone on a plain grey background at the photo's size (`product_layer.png` over grey) as the layout that fixes position, size and perspective, and the photo as a style reference only. Ask for a new scene "inspired by image 2" with the product at exactly the position of image 1, with the same light and reflection instructions as above, at the photo's ratio. Resize the result to the photo's size, then run `match_light.py` on it (`composite_real.png` as the real product, as above). No lock step: `result_lit.png` is the final image. If the model moves the product (the checks show it), regenerate.

## Step 5: final check

For each candidate (`final.png`, or `result_lit.png` in inspired mode):

```
python3 -I scripts/compare_scene.py work/scene/photo.jpg work/scene/grey.png work/scene/mask.png work/final.png work/check --ref work/paste/composite_real.png
```

It writes `overlay_grey50.png` (the grey product at 50% over the result), `outline.png` (mask contour in magenta over the result), the same cropped around the product, `side.png` (photo | result) and `product_diff.png` (how much the product changed since the paste, amplified).

How to read it:
- The 50% overlay is the verdict. The grey shape must sit exactly on the real product, with no double edges, on the top, the sides and the base. Check proportions too.
- "Product change vs the pasted re-skin": the product should change only a little (light adapting). A high mean, or many pixels changed by more than 40/255, or a logo that moved in `product_diff.png`, means stage 2 repainted the product: regenerate.
- The edge-alignment signal says whether the strongest edges of the result are on the mask contour or shifted by a few pixels. It is a signal, not the verdict: a product with little contrast against the surface gives a weak signal.
- Look at the result itself, in crops: shadows that follow the light of the photo, a contact shadow where the product touches the surface, a reflection with the same softness as the photo's other reflections, the product's whites and blacks with the scene's colour balance (compare with a neutral object nearby), legible and clean text, icons and display, and the rest of the scene unchanged. Look at the panel or display crop and at the reflection crop every time. If the product still looks studio-lit or pasted, regenerate stage 2.

## Step 6: review (form)

Send only the final image(s) with SendUserFile, after they passed the checks yourself. Then a short form: Accept / Regenerate stage 2 / Redo the re-skin (stage 1) / Fix a part (the user types what, for example "shadow too hard", "logo wrong"). With several variants, ask which one to keep. If the shape or position does not match, regenerate: never accept it.

## Delivery

Send with SendUserFile only the final image (at the photo's resolution; PNG, plus the same format as the photo if it was a JPEG). Report in one or two sentences the resolution of the result, anything the checks still show that you could not fix, and anything assumed (parts no photo showed).

## Known failure modes

- General image model instead of an editing model: the product and the scene are redrawn.
- One product photo only, or photos from another angle than the grey shape: colours and details of unseen sides are a guess. Say so.
- The product looks pasted: studio colours and white balance that differ from the scene. `match_light.py` fixes it by taking the light from the AI result; if the AI result itself has a wrong colour balance, the prompt described the light wrongly (do not guess warm or cool, measure the photo's whites) and stage 2 must be regenerated.
- Garbled text, digits or icons on the product (for example a display with noisy digits, "Start Stop" turned into other words): the model redrew them. `match_light.py` brings back the real detail, so the final image is clean; if the gap is large, regenerate on a tighter crop.
- Stage 1 straightens the product to the angle of the product photo (low IoU, double edges): the prompt must say to keep the viewpoint of the render and ignore the photo's camera angle; regenerate.
- Stage 2 repaints the product (colours shift, logo moves): the "product change" number and `product_diff.png` show it; regenerate, with the product photo as image 2 and the prompt unchanged.
- Stage 2 adds no shadow or a flat one: the prompt asks for them explicitly; regenerate if the contact shadow is missing.
- Shadow in the wrong direction: the light description was wrong or too vague; correct it with the user and regenerate.
- The AI shifts or rescales the product a little in stage 2: the overlay shows double edges; regenerate. A padded canvas with a ratio far from the photo's makes it more likely.
- Light fringe on the pasted product: check `composite_real.png` in crops; it comes from the white background of stage 1, and `paste_back.py` removes the outer pixels' colour. If a fringe remains, regenerate stage 1 on its own background without shadows.
- "Exact photo" cuts a long soft shadow: lower `--thr`.
- Foreground objects in front of the product are not handled: the grey covers everything, so the real product ends up in front.
