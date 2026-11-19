# render-to-product-video

A Claude skill that turns a **grey 3D product render** into a **product video**: it re-skins the render with the real materials from product photos, places the product in a scene described by the user, then animates it with a camera move copied from a reference video.

The product geometry comes from the render at every step and is never regenerated. Each step is checked before the next one starts, and the start frame must be approved before any video credits are spent.

## Why

Asking a video model to "show this product" redraws the product: proportions drift and details change between frames. This skill splits the job into three controlled generations:

1. **Re-skin** on the render's plain background, so the geometry stays locked to the render.
2. **Start frame**: the same image with only the environment and light changed.
3. **Video**: the start frame as the exact first frame, a reference clip for the camera path only, and the product photos to keep unseen sides consistent.

Changing materials and scene in a single edit shifts the perspective; doing them one at a time does not.

## How it works

```
grey render ──► pad ──► re-skin ──► check ──► start frame in scene ──► approval ──► video ──► inspection
                          ▲                        ▲                                  ▲
product photos ──► materials list           scene + light                 reference camera move
                                                                     (read every 0.5 s)
```

| Step | What happens | Where |
|---|---|---|
| 0. Inputs | Render, product photos, reference video, optional environment photos; finds usable connectors | chat |
| 1. Settings | Image model, video model, aspect ratio, duration and resolution | form |
| 2. Scene | Environment, concrete light, scene content, audio | form |
| 3. Materials | Claude lists material and colour of each part; the user confirms or corrects | form |
| 4. Canvas | Render padded (never cropped) to the target ratio | local script |
| 5. Re-skin | Editing model on a plain background, checked with a 50% overlay | connector + local script |
| 6. Start frame | Environment and light added, product untouched; user approval | connector + form |
| 7. Camera reference | Reference video read every 0.5 s and described interval by interval | local script |
| 8. Video | Video model with start frame, product photos and motion reference | connector |
| 9. Inspection | Contact sheet of the result; accept, regenerate or fix | local script + form |

Every choice is asked through multiple-choice forms; Claude talks to the user in their own language.

## Requirements

- **Claude** with skills enabled (claude.ai, Claude desktop app, or Claude Code).
- **A generative-AI connector** (MCP), for example fal, Replicate or a Google Gemini connector, offering:
  - a multi-image **editing model**: **Nano Banana 2.1** recommended, then **Nano Banana 2**;
  - a **video model** that takes a start image plus a motion-reference video: **Seedance 2.5 reference-to-video** recommended.

  If either is missing, the skill suggests a connector.
- **Python 3** with `numpy` and `Pillow`, and **ffmpeg**, in the environment where Claude runs code. The scripts cost no credits.

## Installation

### claude.ai / Claude desktop app

1. Download `render-to-product-video.zip` from the [latest release](../../releases/latest).
2. In Claude's settings, open the **Skills** section and upload the zip.
3. Make sure code execution and file creation are enabled.

### Claude Code

```bash
git clone https://github.com/Bagareal/myskills.git
mkdir -p ~/.claude/skills
cp -r myskills/render-to-product-video ~/.claude/skills/
```

For a single project, copy it into `.claude/skills/` inside that project instead.

## Usage

Invoke it by name or describe the task:

```
/render-to-product-video
```

```
Make a product video from this render: kitchen counter in the morning, same camera move as this clip.
```

Then attach:

1. **The grey render** on a plain, uniform background.
2. **Real photos of the product.** More angles give better results, especially for the sides the camera reveals during the move.
3. **The camera reference video**: any clip whose camera path you want to copy (an orbit, a push-in, a crane). Its look, background and framing are ignored.
4. **Optional environment photos** for the scene.

## Settings

| Setting | Options | Default |
|---|---|---|
| Image model | Every available editing model | Nano Banana 2.1 |
| Video model | Every available start-image + motion-reference model | Seedance 2.5 reference-to-video |
| Aspect ratio | 16:9, 9:16 | 16:9 |
| Duration and resolution | Match the reference at 1080p or 720p, or typed | Match the reference, 1080p |
| Environment | Described by the user or from attached photos | - |
| Light | Concrete setups proposed for the scene, or typed | - |
| Scene content | Product only, or typed (a cup, steam, props) | Product only |
| Audio | Off, On | Off |

**Vertical (9:16) with a 16:9 reference:** the camera path is copied, but the framing may change and the product can look narrower or get cropped. A vertical reference avoids this.

**Duration:** the video matches the reference's length. Do not speed the reference up to shorten the video: the first frame drifts away from the approved start frame.

## Scripts

All scripts are in [`scripts/`](scripts) and can also be used on their own.

### `pad_to_ratio.py`

Pads an image to a target aspect ratio, centring it on a canvas filled with its own background colour. It never crops.

```bash
python3 -I scripts/pad_to_ratio.py render.png render_pad.png 16:9
```

### `compare.py`

Compares a generated image with its reference.

```bash
python3 -I scripts/compare.py render_pad.png reskin.png side.png blend.png
```

Prints the silhouette IoU and both bounding boxes, and writes a side-by-side image and a 50% overlay.

- **IoU** (1.0 = identical silhouettes) is a signal, not the verdict: a soft shadow lowers it even when the product is correct. On a scene or a dark background it is meaningless.
- **The overlay is the verdict.** Contours, seams and proportions must line up with no double edges.

### `contact_sheet.py`

Extracts frames at a given rate and tiles them four per row, each labelled with its time.

```bash
python3 -I scripts/contact_sheet.py reference.mp4 reference_sheet.png 2
```

Used twice: to read the reference camera move before writing the prompt (a move described from the first and last frame alone is usually wrong), and to inspect every half second of the generated video.

## Limits and known failure modes

| Problem | Cause | Fix |
|---|---|---|
| Product deforms | General image model | Editing model on the render |
| Perspective shifts | Materials and scene changed in one edit | Re-skin first on plain background, then the scene |
| Orbit stops early | Move described from first and last frame | Read the reference every 0.5 s |
| First frame drifts | Reference sped up | Use the original reference and a matching duration |
| Grey look or plain background in the video | Reference style leaks | Prompt states the reference is camera motion only |
| Random reflections, light streaks | Vague light description | Light attached to the product, slow, with direction and fall-off |
| Stray transparent objects, tiny coloured lights, lighter front at the end | Video model artefacts | Spotted on the contact sheet; regenerate |
| Unreadable panel text | 720p | Use 1080p |

Seedance 2.5 reference limits (check the schema of the model you use): 1.8-30.2 s, 300-6000 px per side, aspect ratio 0.4-2.5, 24-60 fps, up to 200 MB.

## License

[MIT](../LICENSE)
