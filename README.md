# myskills

A collection of [Claude](https://claude.ai) skills, mostly for AI product imagery. Each skill is a self-contained folder with a `SKILL.md` (the instructions Claude follows), local helper scripts and its own documentation.

## Skills

| Skill | What it does | Output |
|---|---|---|
| [render-reskin](render-reskin) | Turns a grey 3D product render into a photorealistic packshot using real product photos, keeping the geometry pixel-exact, with a position check and optional transparent cutout | Packshot on white or transparent PNG |
| [render-to-product-video](render-to-product-video) | From a grey 3D render and product photos, creates a re-skin, a start frame in a described scene and a video that follows a reference camera move | Re-skin, start frame, video |
| [ramble-to-brief](ramble-to-brief) | Turns a free-form ramble about a job (typed or dictated) into a complete brief, shows what it understood, asks all open questions in one round, then runs the job autonomously after an explicit go | Brief, then the finished job |
| [scene-reskin](scene-reskin) | Replaces the grey 3D stand-in placed in a photo of an environment (a `_SCENE` export from the 3D viewer) with the real product, same position and perspective, re-skinned from real photos and then integrated with AI-made shadows and reflections and the scene's light, with position checks | Final image |

The three imagery skills share the same principle: **the render's geometry is never regenerated.** A multi-image editing model only paints real materials onto it, and a local check (silhouette IoU plus a 50% overlay) confirms that nothing moved before the result is shown.

## Requirements

- Claude with skills enabled: claude.ai, the Claude desktop app or Claude Code, with code execution.
- A generative-AI connector (MCP) such as fal, Magnific, Replicate or a Google Gemini connector, offering a multi-image editing model (Nano Banana 2.1 or 2 recommended) and, for video, a start-image + motion-reference video model (Seedance 2.5 reference-to-video recommended).
- Python 3 with `numpy`, `Pillow` and `scipy`; `ffmpeg` for video. The scripts run locally and cost no credits.

## Connectors and credits

Generations are paid on the connector you use (money on fal, credits on Magnific). The skills were first built on fal and later run on Magnific, where the same steps wasted credits: the model and the aspect ratio were left on Magnific's `auto` default, the re-skin came back mirrored and enlarged, and Claude tried other tools (crop and paste back, replace background, outpaint, 4K) to rescue it. The credits ran out before the video. Since then `render-reskin` and `render-to-product-video` follow these rules on every connector:

| Rule | What Claude does |
|---|---|
| Cost first | Reads the balance and the price of the whole job before the first generation (for video, the video step first: it is by far the most expensive). If it does not fit, it says so and generates nothing. |
| Nothing on `auto` | Model, aspect ratio and resolution are always set explicitly. |
| Only the skill's steps | No extra tools to rescue a failed step. |
| Stop after two failures | If the same step fails its check twice, Claude stops, shows what went wrong and asks, with the cost of each option. |
| Cost before each call | One line with the price before every paid generation. |

Each skill's README has a "Connectors and credits" section with the exact parameters for fal and Magnific and the prices seen so far.

## Installation

### claude.ai / Claude desktop app

1. Download the skill's zip from the [latest release](../../releases/latest).
2. In Claude's settings, open the **Skills** section and upload the zip.

### Claude Code

```bash
git clone https://github.com/Bagareal/myskills.git
mkdir -p ~/.claude/skills
cp -r myskills/ramble-to-brief myskills/render-reskin myskills/render-to-product-video myskills/scene-reskin ~/.claude/skills/
```

### Building the zips yourself

Each zip contains the skill folder at its root. The `render-to-product-video` zip leaves out `examples/` (screenshots and video, only useful on GitHub):

```bash
cd myskills
zip -r render-reskin.zip render-reskin -x '*/__pycache__/*'
zip -r render-to-product-video.zip render-to-product-video -x '*/__pycache__/*' 'render-to-product-video/examples/*'
zip -r scene-reskin.zip scene-reskin -x '*/__pycache__/*'
zip -r ramble-to-brief.zip ramble-to-brief
```

## Repository layout

```
myskills/
├── ramble-to-brief/
│   ├── SKILL.md
│   └── README.md
├── render-reskin/
│   ├── SKILL.md            # instructions for Claude
│   ├── README.md           # documentation
│   └── scripts/
│       ├── pad_to_ratio.py
│       ├── compare.py
│       └── cutout.py
├── render-to-product-video/
│   ├── SKILL.md
│   ├── README.md
│   ├── DISCLAIMER.md       # terms of the example media
│   ├── scripts/
│   │   ├── pad_to_ratio.py
│   │   ├── compare.py
│   │   └── contact_sheet.py
│   ├── docs/               # workflow, prompts, verification, models, troubleshooting
│   └── examples/
│       └── kitchen-orbit/  # complete worked example with screenshots and video
└── scene-reskin/
    ├── SKILL.md
    ├── README.md
    └── scripts/
        ├── unpack_scene.py
        ├── crop_product.py
        ├── compare.py
        ├── cutout.py
        ├── paste_back.py
        ├── fit_canvas.py
        ├── lock_background.py
        └── compare_scene.py
```

`pad_to_ratio.py`, `compare.py` and `cutout.py` are duplicated on purpose, so that each skill folder works on its own.

## License

[MIT](LICENSE). The example media in `render-to-product-video/examples/` are not covered by the license: see [DISCLAIMER.md](render-to-product-video/DISCLAIMER.md).
