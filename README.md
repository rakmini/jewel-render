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
   - Local: `http://localhost:5000`
   - Remote iPhone: `http://<mac-mini-ip>:5000`

## Tech Stack

- **Frontend**: HTML5, CSS3, vanilla JavaScript (single-file, no framework)
- **Backend**: Python 3.10+, FastAPI/Flask
- **AI**: ComfyUI (Mac Mini M4), SDXL base 1.0
- **Output**: JPEG 95 quality, 1170×2532 (iPhone portrait)
- **Video**: MP4, SV3D_p / WAN 2.1 models

## Key Features

- **Modular Style Presets** — Cool Blue, White Retail, Yashica Film (user-expandable)
- **Cross-Preset Pipeline** — Render in one style, edit in another (jewelry stays identical)
- **Reference Image Library** — Per-preset persistent image cloud with auto-deposit on export
- **VSCO-Style Editor** — Adjust (light/color/detail/film) + Crop (rule-of-thirds, aspect ratio)
- **Recede Control** — AI outpainting to extend background when shot too tight
- **Feedback System** — +/− buttons per image feed training loop & parameter logging
- **Batch Processing** — Render multiple images with progress tracking

## Documentation

See the `docs/` folder:
- [Architecture](docs/ARCHITECTURE.md) — System design, data flow, preset system
- [API Reference](docs/API.md) — Endpoint specifications and ComfyUI integration
- [Setup Guide](docs/SETUP.md) — Development environment, dependencies, Mac Mini config
- [Features](docs/FEATURES.md) — Detailed specs for every feature

## Development

All context and decisions are in `docs/ARCHITECTURE.md` and `docs/FEATURES.md`. Do not ask for re-explanations — read these files first.

## Owner & Contact

Jonathan — [jhrworldwide@gmail.com](mailto:jhrworldwide@gmail.com)

## License

(To be defined)
