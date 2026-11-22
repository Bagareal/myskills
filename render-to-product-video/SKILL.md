---
name: render-to-product-video
description: From a grey 3D render plus real product photos, create a re-skin, a start frame in a described scene and a video that follows a reference camera move. Use for product videos made from renders.
---

# render-to-product-video

Three generations, in order: re-skin of the render, start frame in a scene, video. The product geometry stays the one of the render in every step. Never generate the product from scratch.

This skill is written in English, but always talk to the user in their own language. Every choice is asked through forms (AskUserQuestion: up to 4 multiple-choice questions per form; the user can always type another answer). Files cannot travel through a form, so attachments are asked for in chat.

The skill works with any connected generative-AI connector (fal, Replicate, a Google Gemini connector or others) that offers the two kinds of model it needs: an image-editing model accepting several input images, and a video model accepting a start image plus a motion-reference video. Only the generation calls depend on the connector; the scripts do not.

## Scripts

The `scripts/` folder next to this file holds the local tools. They cost no credits. Run them with `python3 -I scripts/<name>.py ...` (use the full path of this skill's folder). They need numpy and Pillow (`pip install --break-system-packages numpy pillow` if missing); `contact_sheet.py` also needs ffmpeg.

| Script | Purpose |
|---|---|
| `scripts/pad_to_ratio.py` | Pad the render to the target aspect ratio with its own background colour, never cropping |
| `scripts/compare.py` | Position check: silhouette IoU, bounding boxes, side-by-side and 50% overlay |
| `scripts/contact_sheet.py` | One labelled tile every 0.5 s of a video, to read a camera move or inspect a result |

Do not modify `compare.py`: it is the reference check.

## Fixed rules

- Images: always an image-editing model with several input images. Preferred: Nano Banana 2.1, then Nano Banana 2, on whichever connector offers them (for example on fal: `google/nano-banana-2.1/edit`, `fal-ai/nano-banana-2/edit`). A general text-to-image model deforms the product: never use one.
- Video: a model with a start image plus a motion-reference video. Preferred: Seedance 2.5 reference-to-video; another model with the same inputs is acceptable if the user picks it. Audio off unless asked.
- Never guess endpoint IDs or parameter names: read them from the connector's own model search and schema tools.
- Never leave model, aspect ratio or resolution on a connector's `auto` default: set each one explicitly (see Connector notes).
- Always show the start frame and wait for the user's approval before generating the video.
- If a check fails, say so and regenerate only that step. Never present a flawed result as good.
- Never describe the camera move from memory: inspect the reference every 0.5 s first.
- From the reference video copy only the camera path and timing.
- Do not add anything personal, or about the user's employer or clients, to files, prompts or documentation produced with this skill.
- Budget first: before the first paid generation, check the balance and estimate the cost of the whole pipeline (re-skin + start frame + video). The video is by far the most expensive step. If the balance does not cover the video plus one retry of each image step, stop and tell the user before spending anything.
- Only the steps in this skill. Do not improvise other tools or tricks to rescue a failed step (crop and paste back, replace background, outpaint, upscale, 4K). If a step fails twice, stop, show what went wrong and ask, giving the cost of each option.
- State the cost of each paid call in one line before running it.

## Step 0: inputs (chat)

Ask in chat for:
1. The grey render (plain, uniform background).
2. Real photos of the product. They give the true colours. Tell the user plainly: the more reference photos (front, side, back, details), the better the result, especially for the sides the camera reveals. With a single photo the model has to guess the parts that photo does not show.
3. The camera reference video (the move to copy).
4. Optional: photos of the desired environment.

Check sizes, aspect ratios and, for the reference video, duration, resolution and frame rate (ffprobe).

Find the available connectors: look at the connected tools (use ToolSearch for deferred ones) for generative-AI connectors, and use each connector's model search to see whether it offers Nano Banana 2.1 or 2 and Seedance 2.5 reference-to-video (or another video model with a start image and a motion-reference video). If none is connected, or one of the two kinds of model is missing, say so, search the connector registry for one (SearchMcpRegistry, then SuggestConnectors) and wait for the user to connect it.

## Step 1: settings (form)

One AskUserQuestion form with these four questions:
1. Image connector and model: one option per available combination, e.g. "fal - Nano Banana 2.1 (Recommended)", "fal - Nano Banana 2". Put Nano Banana 2.1 first.
2. Video connector and model: e.g. "fal - Seedance 2.5 reference-to-video (Recommended)", plus any other model with the same inputs.
3. Aspect ratio: 16:9 (Recommended) / 9:16 vertical (state the reference video's ratio in the question).
4. Duration and resolution: Match the reference, 1080p (Recommended) / Match the reference, 720p / other (typed). Small panel text is often unreadable at 720p.

9:16: if the user provides a vertical reference video, use it. If the reference is 16:9, proceed but warn that the camera path is copied and the framing may change (the product can look narrower or get cropped); repeat the warning when showing the start frame.

If only one product photo was given, repeat the warning about unseen parts in the question text or right before the form.

Budget check, right after this form: read the balance, then the cost of the video with the chosen model, duration and resolution, then of the image steps, with the connector's own tools (see Connector notes). Show the total to the user. If it does not fit, say so and offer what does (lower resolution, shorter duration, another model or connector). Do not start until it fits.

## Step 2: scene (form)

One AskUserQuestion form:
1. Environment: I'll describe it (typed) / I attached environment photos. No presets: the environment comes from the user.
2. Light: offer two or three concrete setups that fit the environment (direction, hardness, fall-off, what stays in shadow), plus the typed option.
3. Scene content: Product only, nothing else / something typed (a cup, steam, props).
4. Audio: Off (Recommended) / On.

Turn vague wishes into concrete light: direction, hardness, fall-off, what stays in shadow. A bare "edge light" produced random reflections.

## Step 3: materials (form)

Read the photos and list, part by part, the material and colour you see (body, lid, handles, panel, logos, glass, metal, textures). For parts the render shows but no photo shows, write what you will assume and mark it as assumed. Send the list in a message, then a form: "Is this materials list right?" with Correct, go ahead / I'll correct it (the user types the corrections). Use the corrected list in the prompts.

## Step 4: canvas

If the render already has the target ratio, skip. Otherwise pad it, never crop, with the render's own background colour:

```
python3 -I scripts/pad_to_ratio.py render.png render_pad.png 16:9
```

Use `9:16` for vertical.

## Step 5: re-skin (plain background, no scene)

Convert RGBA photos to RGB on white first. Upload the canvas and the photos the way the chosen connector requires (its own upload tool, a signed URL, or inline data). Read the model's schema and map the settings onto its parameter names: input images with the canvas first, then the photos (on fal: `image_urls`); same aspect ratio as the canvas; 2K; reasoning or thinking level at its highest if the model has one (on fal: `thinking_level` `high`); PNG output if offered. If a setting does not exist on that connector, say which one and what you used instead.

Prompt template (fill the brackets):

```
Re-skin image 1: turn the grey 3D render of the [product], seen from [camera angle], into a photorealistic product photo WITHOUT changing its geometry at all. Every contour, edge, corner, curve, seam line and the whole silhouette must stay at exactly the same pixel positions as in image 1. Keep the plain [colour] background of image 1 unchanged: no scene, no props, no extra objects. Only paint real materials and colours taken from the other images: [approved materials list, part by part]. Keep small embossed marks and printed logos where they are.
```

Verify:

```
python3 -I scripts/compare.py render_pad.png reskin.png side.png blend.png
```

How to read it:
- IoU = shared area of the two silhouettes divided by the area covered by either (1.0 = identical). It is a signal, not the verdict: a soft shadow added by the generator widens the silhouette and lowers it even when the product is right (0.646 was seen with a correct product).
- The 50% overlay (`blend.png`) is the verdict, ideally cropped on the product. If contours, seams and proportions line up with no double edges, continue. Otherwise regenerate this step.

## Step 6: start frame (form)

Image 1 = the re-skin, plus any photos of the desired environment. Same image model, aspect ratio and settings as step 5. The product stays completely unchanged, only the environment and the light change. Prompt template:

```
Keep the [product] in image 1 COMPLETELY UNCHANGED: same camera angle, same geometry, same silhouette, same position and size in the frame, same materials and colours. Do not redraw, rotate, scale or reshape the product. Only change the environment: [scene described by the user], with [concrete light: direction, hardness, where it falls, what stays in shadow]. [Scene content, e.g. a cup with a little coffee, steam]. No text, no extra objects.
```

Verify with the overlay against the re-skin. On a scene or a dark background the IoU is meaningless (the background mask no longer isolates the product): judge by eye.

Send the start frame with SendUserFile and wait for approval with a form: Approve, make the video / Regenerate the same prompt / Change something (the user types what). Regenerate only this step if they want changes.

## Step 7: camera reference

Extract a frame every 0.5 s and look at all of them:

```
python3 -I scripts/contact_sheet.py reference.mp4 reference_sheet.png 2
```

Write the camera path interval by interval. A continuous orbit passes the front view and keeps going. Do not speed up the reference to shorten the video: the first frame drifts; use the original and a matching duration. Check the reference against the video model's limits in its schema (for Seedance 2.5 on fal: 1.8-30.2 s, 300-6000 px per side, aspect ratio 0.4-2.5, 24-60 fps, up to 200 MB).

## Step 8: video

Upload the approved start frame, the photos and the reference video the way the connector requires. Inputs: image 1 = the approved start frame (exact first frame), images 2 and 3 = the real photos (only for the sides the camera reveals), video 1 = the reference (camera path only). Read the model's schema and map: aspect ratio and resolution as chosen, duration matching the reference, audio as chosen (on fal Seedance 2.5: task `reference`, duration as a string, `generate_audio` false). Prompt template (adapt the camera path to what you saw in step 7):

```
@Image1 is the exact first frame: [description of the start frame]. @Image2 and @Image3 are real photos of the product: use them only to keep it identical when the camera reveals its sides and front. @Video1 is a camera-motion reference ONLY: copy its camera path and timing ([camera path observed, interval by interval]), but do NOT copy its grey look, its plain background or its framing. The product stays completely static and rigid; only the camera moves, and the product changes perspective accordingly. [What stays constant in the scene.] [Light: slow, continuous, attached to the product, no flashes or random reflections.] No cuts, no text, no overlays, no extra objects.
```

If the chosen video model refers to inputs differently than `@Image1` / `@Video1`, use its own syntax from the schema or docs.

## Step 9: inspect the video (form)

```
python3 -I scripts/contact_sheet.py video.mp4 sheet.png 2
```

Look at every tile and report honestly: camera path against the reference, product rigidity, background constancy, legibility of text and logos, light behaviour, stray objects. Send the video with SendUserFile, then a form: Accept / Regenerate the same prompt / Fix something (the user types what). Re-running never gives an identical result, so keep an accepted video.

## Delivery

Deliver in order with SendUserFile: re-skin, start frame, video. No contact sheets or overlays at this stage. Report in one or two sentences what passed and anything assumed (parts no photo showed).

## Connector notes

The steps are the same on every connector; only the parameter names change. Always read the schema; these notes record what was found so far.

fal:
- Images: `google/nano-banana-2.1/edit` or `fal-ai/nano-banana-2/edit`, `image_urls` (canvas first), `aspect_ratio` set explicitly, `resolution` `2K`, `thinking_level` `high`.
- Video: Seedance 2.5 reference-to-video, `image_urls` (start frame first), `video_urls`, task `reference`, duration as a string, `generate_audio` false.
- Cost: `estimate_cost`.

Magnific:
- Images: `images_generate` with `mode: imagen-nano-banana-2-flash` (this is Nano Banana 2; `imagen-nano-banana-2` is Nano Banana Pro), `aspectRatio` set to the canvas ratio, `resolution: 2k`. Image 1 = first `references` entry of type `image`, then the real photos. Do not use `images_replace_background`, `images_expand` or other image tools in this pipeline.
- Video: `video_generate` with `slug: bytedance-seedance-pro-2.5`, `withSoundEffects: false`. On Magnific `keyframes.start` cannot be combined with references: pass the approved start frame as the first `image` reference (@Image1), the real photos as further `image` references, the camera reference as a `video` reference.
- Cost: `account_balance`, then `simulate_cost` with the real arguments. The video quote leaves out the seconds of the reference video, so the real price is higher.
- Prices seen (Nov 2026, indicative): image edit about 65-75 credits at 2K, 150 at 4K; Seedance 2.5 10 s 1080p 5400+ credits, 5 s 720p 1300+; Seedance 2.5 Flash 10 s 720p 1700+.

## Known failure modes

- A general image model deforms the product: use an editing model on the render.
- Material and scene changed in one edit shifts the perspective: re-skin first on the plain background, then the scene.
- Orbit described from the first and last frame stops early: inspect every 0.5 s.
- Reference sped up 2x: the first frame drifts. Use the original.
- Grey look or plain background of the reference leaks: say explicitly that the reference is camera motion only.
- Random reflection or light streak: describe the light as attached to the product, slow, with direction and fall-off.
- Stray transparent object near the base, tiny coloured lights, a lighter front in the final frames: check on the contact sheet.
- Small panel text unreadable at 720p: use 1080p.
- Magnific with model and aspect ratio left on auto: re-skin on the full canvas came back mirrored and enlarged. Set Nano Banana 2 and the ratio explicitly.
- Credits spent on images and repair attempts, none left for the video: check the video cost before the first generation.
