# Models

The pipeline needs two capabilities. Any model that provides them can be used.

## Image editing (re-skin and start frame)

Required behaviour:

- Edits an input image and leaves what you did not ask to change stable.
- Accepts several input images (render plus real photos).
- Supports the target aspect ratio and a resolution of at least 2K.

Used in the example: **Nano Banana 2.1 edit** (`google/nano-banana-2.1/edit` on fal).

| Parameter | Value used |
|---|---|
| `prompt` | see [prompts.md](prompts.md) |
| `image_urls` | render first, then photos (up to 14 accepted) |
| `aspect_ratio` | `16:9` or `9:16` |
| `resolution` | `2K` |
| `thinking_level` | `high` |

Lesson: a general image generation model that is asked to produce the product shot (GPT Image 2.6 in an early test) deformed the product. Use an editing model and give it the render as the anchor.

## Video with reference inputs

Required behaviour:

- Takes a start image as the exact first frame.
- Takes a video used only as camera-motion reference, with the prompt able to assign a role to each input.
- Takes extra reference images (the real photos).

Used in the example: **Seedance 2.5 reference-to-video** (`bytedance/seedance-2.5/us/reference-to-video` on fal).

| Parameter | Value used |
|---|---|
| `prompt` | uses `@Image1`, `@Image2`, `@Video1` tags, see [prompts.md](prompts.md) |
| `image_urls` | start frame, then real photos |
| `video_urls` | the camera reference |
| `task` | `reference` |
| `aspect_ratio` | `16:9` (or `9:16`) |
| `resolution` | `480p`, `720p`, `1080p` or `4k` |
| `duration` | string, `"4"` to `"30"` (seconds) |
| `generate_audio` | `false` |

Reference video limits: 1.8 to 30.2 s, 300 to 6000 px per side, aspect ratio 0.4 to 2.5, 24 to 60 fps, up to 200 MB.

## Swapping models

Keep the roles, not the names: "image editor that preserves geometry" for stages 2 and 3, "start image plus motion-reference video" for stage 5. Keep the local checks as they are, since they only look at the outputs. If a video model has no way to assign roles to its inputs, expect the reference's look (grey render, plain background) to leak into the result, and test for it.

## Connector notes

Never leave model, aspect ratio or resolution on a connector's `auto` default. Check the cost before generating.

fal:
- Parameters as in the tables above.
- Cost: `estimate_cost`.

Magnific:
- Images: `images_generate` with `mode: imagen-nano-banana-2-flash` (this is Nano Banana 2; `imagen-nano-banana-2` is Nano Banana Pro), `aspectRatio` set to the canvas ratio, `resolution: 2k`. Image 1 = first `references` entry of type `image`, then the real photos. Do not use `images_replace_background`, `images_expand` or other image tools in this pipeline.
- Video: `video_generate` with `slug: bytedance-seedance-pro-2.5`, `withSoundEffects: false`. On Magnific `keyframes.start` cannot be combined with references: pass the approved start frame as the first `image` reference (@Image1), the real photos as further `image` references, the camera reference as a `video` reference.
- Cost: `account_balance`, then `simulate_cost` with the real arguments. The video quote leaves out the seconds of the reference video, so the real price is higher.
- Prices seen (Nov 2026, indicative): image edit about 65-75 credits at 2K, 150 at 4K; Seedance 2.5 10 s 1080p 5400+ credits, 5 s 720p 1300+; Seedance 2.5 Flash 10 s 720p 1700+.

## Calling the models

The repository does not depend on a specific provider. The example was run through fal's hosted endpoints; you can call them from any client, from a web UI, or use another provider with equivalent models. Upload inputs so the model can read them (public or signed URLs for hosted APIs).
