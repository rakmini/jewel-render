# JewelRender

A batch jewelry rendering application for product image generation and editing in multiple visual styles. Runs on Mac Mini M4 with ComfyUI backend, accessed remotely from iPhone via local network or Tailscale.

## What This Project Does

JewelRender connects to ComfyUI to process jewelry product images in multiple styles. The app supports three core workflows:

- **Image Edit Mode** — Submit an existing photo and selectively change specific elements (background, metal color, etc.) while preserving everything else
- **Image Generation Mode** — Create entirely new images from scratch using text prompts combined with reference images
- **360 Video Mode** — Generate seamless rotating loops from key angle uploads using SV3D_p or WAN 2.1

All output is iPhone portrait aspect ratio (1170 × 2532). The phone is just a remote control; the Mac Mini M4 does all GPU processing.

## Project Structure

```
jewelrender/
├── frontend/              # Web UI (HTML/CSS/JS)
│   ├── src/
│   │   ├── index.html     # Main application
│   │   ├── css/           # Stylesheets
│   │   ├── js/            # Frontend logic
│   │   └── assets/        # Icons, images, fonts
│   └── public/            # Static files
├── backend/               # Python API server
│   ├── src/
│   │   ├── main.py        # Flask/FastAPI app entry
│   │   ├── comfyui/       # ComfyUI client & workflows
│   │   ├── utils/         # Shared utilities
│   │   └── models.py      # Data models
│   ├── tests/             # Unit tests
│   ├── config.py          # Configuration
│   └── requirements.txt    # Python dependencies
├── docs/                  # Documentation
│   ├── ARCHITECTURE.md    # System design
│   ├── API.md             # Backend API reference
│   ├── SETUP.md           # Development environment setup
│   └── FEATURES.md        # Detailed feature specs
├── config/                # Configuration files
│   ├── presets.json       # Style preset definitions
│   └── settings.json      # User settings template
└── .github/               # GitHub workflows & CI
    └── workflows/
```

## Quick Start

1. **Clone & install**
   ```bash
   git clone https://github.com/[username]/jewelrender.git
   cd jewelrender
   pip install -r backend/requirements.txt
   ```

2. **Configure**
   - Copy `config/settings.json.example` to `config/settings.json`
   - Update ComfyUI host/port (default: `127.0.0.1:8188`)

3. **Run backend**
   ```bash
   python backend/src/main.py
   ```

4. **Open frontend**
   - Local: `http://localhost:8080`
   - Remote iPhone: `http://<mac-mini-ip>:8080`
   - Or open `frontend/src/index.html` directly in a browser (no server needed)

## Tech Stack

- **Frontend**: HTML5, CSS3, vanilla JavaScript (single-file, no framework)
- **Backend**: Python 3.10+, FastAPI/Flask
- **AI**: ComfyUI (Mac Mini M4), SDXL base 1.0
- **Output**: JPEG 95 quality, 1170×2532 (iPhone portrait)
- **Video**: MP4, SV3D_p / WAN 2.1 models

## Key Features

- **Modular Style Presets** — Cool Blue, White Retail, Yashica Film (user-expandable)
- **Material Controls** — Metal type (WG/YG/RG) + karat (10k/14k/18k), gemstone, product type
- **Post-Render Studio** — Full split-screen editor: live adjust (instant) + re-render zone (AI)
- **Render History** — Permanent archive every version, material metadata, retroactive export
- **Amendments Prompt** — Describe changes in text; AI regenerates in place
- **Selection Brush** — Paint area, describe fix; AI touches only marked region
- **Cross-Preset Pipeline** — Render in one style, edit in another (jewelry stays identical)
- **Reference Image Library** — Per-preset, 4 folder categories (Materials/Gemstones/Product Types/Setting Styles); auto-files on export
- **Upload Centre** — Batch seed RIL with drag-to-folder sorting + AI suggestions
- **RIL Browser** — Searchable database, folder sidebar, image/video toggle
- **Recede Control** — AI outpainting to extend background when shot too tight
- **VSCO-Style Editor** — Adjust (light/color/detail/film) + Crop (rule-of-thirds, aspect ratio)
- **360 Video** — Seamless rotating loops, 3 export aspect ratios, Video Recede
- **Batch Processing** — Render multiple images with progress tracking

## Documentation

See the `docs/` folder:
- [Spec v4](docs/JEWELRENDER_SPEC_v4.md) — **Single source of truth** — complete feature spec
- [Architecture](docs/ARCHITECTURE.md) — System design, data flow, pipeline, RIL structure
- [Features](docs/FEATURES.md) — Detailed specs for every feature
- [API Reference](docs/API.md) — Endpoint specifications and ComfyUI integration
- [Setup Guide](docs/SETUP.md) — Development environment, dependencies, Mac Mini config

## Development

`docs/JEWELRENDER_SPEC_v4.md` is the single source of truth. Read it fully before making changes. All architectural context is in `docs/ARCHITECTURE.md` and `docs/FEATURES.md`.

## Owner & Contact

Jonathan — [jhrworldwide@gmail.com](mailto:jhrworldwide@gmail.com)

## License

(To be defined)
