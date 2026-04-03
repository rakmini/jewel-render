# JewelRender

A batch jewelry rendering application for product image generation and editing in multiple visual styles. Powered by OpenAI's cloud APIs (GPT Image 1.5, GPT-4.1-mini, Sora 2). Runs on Mac Mini M4, accessed remotely from iPhone via local network or Tailscale.

## What This Project Does

JewelRender uses OpenAI's APIs to process jewelry product images in multiple styles, with a persistent AI brain that gets smarter over time. The app supports three core workflows:

- **Image Edit Mode** — Submit an existing photo and selectively change specific elements (background, metal color, etc.) while preserving everything else. Uses OpenAI Images Edit API.
- **Image Generation Mode** — Create entirely new images from scratch using text prompts combined with reference images. Uses OpenAI Images Generate API.
- **360 Video Mode** — Generate seamless rotating loops from key angle uploads. Uses Sora 2 API.

A **GPT-4.1-mini AI brain** analyzes every image that enters the system — classifying metal type, gemstone, product type, setting style — and drives auto-tagging, quality assessment, and parameter recommendations.

All output is iPhone portrait aspect ratio (1170 x 2532). The phone is just a remote control; the Mac Mini serves the app and OpenAI's cloud handles AI processing.

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
│   │   ├── main.py        # FastAPI app entry
│   │   ├── openai_client.py  # OpenAI API client (generate, edit, video)
│   │   ├── brain.py       # AI brain (GPT-4.1-mini vision analysis)
│   │   ├── utils/         # Image processing utilities (Pillow/OpenCV)
│   │   └── models.py      # Data models
│   ├── tests/             # Unit tests
│   ├── config.py          # Configuration
│   └── requirements.txt   # Python dependencies
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

2. **Configure OpenAI API key**
   ```bash
   cp backend/.env.example backend/.env
   # Edit .env and set OPENAI_API_KEY=sk-your-key-here
   ```
   Get your API key at [platform.openai.com](https://platform.openai.com) (separate from ChatGPT subscription).

3. **Run backend**
   ```bash
   python backend/src/main.py
   ```

4. **Open frontend**
   - Local: `http://localhost:5000`
   - Remote iPhone: `http://<mac-mini-ip>:5000`

## Tech Stack

- **Frontend**: HTML5, CSS3, vanilla JavaScript (single-file, no framework)
- **Backend**: Python 3.10+, FastAPI
- **AI Brain**: GPT-4.1-mini (vision analysis, tagging, quality assessment — runs on every image)
- **Image AI**: GPT Image 1.5 (generation & editing — runs on render)
- **Video AI**: Sora 2 (360 rotation loops — runs on video render)
- **Local Processing**: Pillow/OpenCV (crop, exposure, temperature adjustments)
- **Output**: JPEG 95 quality, 1170x2532 (iPhone portrait)

## Key Features

- **Modular Style Presets** — Cool Blue, White Retail, Yashica Film (user-expandable)
- **Cross-Preset Pipeline** — Render in one style, edit in another (jewelry stays identical)
- **Reference Image Library** — Per-preset persistent image cloud with auto-deposit on export
- **AI Brain** — GPT-4.1-mini auto-classifies every image (metal, gem, product type, quality)
- **VSCO-Style Editor** — Adjust (light/color/detail/film) + Crop (rule-of-thirds, aspect ratio)
- **Recede Control** — AI outpainting to extend background when shot too tight
- **Feedback System** — +/- buttons per image feed training loop & parameter logging
- **Batch Processing** — Render multiple images with progress tracking

## Documentation

See the `docs/` folder:
- [Architecture](docs/ARCHITECTURE.md) — System design, AI models, data flow
- [API Reference](docs/API.md) — Endpoint specifications and OpenAI integration
- [Setup Guide](docs/SETUP.md) — Development environment, API key setup, iPhone access
- [Features](docs/FEATURES.md) — Detailed specs for every feature

## Development

All context and decisions are in `docs/ARCHITECTURE.md` and `docs/FEATURES.md`. Do not ask for re-explanations — read these files first.

## Owner & Contact

Jonathan — [jhrworldwide@gmail.com](mailto:jhrworldwide@gmail.com)

## License

(To be defined)
