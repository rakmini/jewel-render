# JewelRender Architecture

## System Overview

JewelRender is a jewelry rendering application powered by OpenAI's cloud APIs:
- **Frontend**: Single-page app (HTML/CSS/JS) running on iPhone or Mac browser
- **Backend**: Python API server (FastAPI) on Mac Mini M4
- **AI Engine**: OpenAI APIs (cloud) — three models working together
- **Storage**: Local filesystem for presets, reference images, and outputs

The Mac Mini serves the app and handles local image processing (crop, adjust, export). All AI-powered rendering and analysis happens via OpenAI's cloud APIs.

## AI Architecture: Three Models, One API Key

### GPT-4.1-mini — The Brain (always-on)
- Runs on **every image** that enters the system (uploads, renders, exports)
- Vision analysis: identifies metal type, gemstone, product type, setting style
- Quality assessment: scores renders against target preset style
- RIL folder suggestions: auto-tags images for Reference Image Library sorting
- Parameter recommendations: suggests render settings based on past successes
- Cost: cheap per call (~$0.003/image), designed to run constantly

### GPT Image 1.5 — The Hands (on-demand)
- Image generation: `/v1/images/generations` — create jewelry shots from text prompts + references
- Image editing: `/v1/images/edits` — modify existing images (background swap, metal/gem changes)
- Handles Edit mode, Generate mode, Recede (outpainting), and cross-preset pipeline
- Cost: $0.02-$0.20 per image depending on quality/size

### Sora 2 — The Videographer (on-demand)
- Video generation: `/v1/videos` — 360 rotation loops from reference images
- Only activated for Video mode renders
- Cost: higher per-generation, used sparingly

All three use the same OpenAI Platform API key. One bill, one ecosystem.

## Core Architecture: Two Independent Axes

### Style Axis (Presets)
Modular, user-expandable library of visual styles. Currently:
- **Cool Blue** — Signature Instagram look, baby blue background
- **White Retail** — Clean white for retail partner submissions
- **Yashica Film** — AI-generated models wearing jewelry, Yashica T4 film aesthetic

Users can create unlimited new presets.

### Export Axis (Modes)
Available in every preset:
- **Image Edit Mode** — Selectively change elements (background, metal, stone) via OpenAI Images Edit API
- **Image Generation Mode** — Create new images from scratch via OpenAI Images Generate API
- **360 Video Mode** — Seamless rotating loops via Sora 2 API

**Key Design**: Style x Mode = any valid combination. This matrix is the entire feature set.

## Cross-Preset Pipeline (Critical Workflow)

A user can:
1. Generate 50 jewelry images in **Cool Blue** style
2. Drag those finished renders into **White Retail** (switch to Edit mode)
3. Only the background changes from baby blue to white
4. Jewelry, metal, and stone rendering stay **identical**
5. Avoids regeneration from scratch

This works because Edit mode uses OpenAI's image editing with masks to only modify what the target preset requires.

## Data Model

### Preset Structure
```json
{
  "id": "cool-blue",
  "name": "Cool Blue",
  "style": "baby-blue background, softly lit",
  "defaults": {
    "temperature": 0,
    "saturation": 0,
    "contrast": 0,
    "sharpness": 0,
    "grain": 0
  },
  "referenceImageLibrary": ["image1.jpg", "image2.jpg"],
  "recede": 0,
  "modes": {
    "edit": { ... },
    "generate": { ... },
    "video": { ... }
  }
}
```

### Reference Image Library (RIL)
Per-preset persistent cloud of images that teach the AI what the preset should look like.

**Three entry paths**:
1. Manual upload (drag into RIL drop zone)
2. Auto-add approved images (Settings toggle)
3. Auto-deposit exported images (Settings toggle)

RIL files stored locally: `backend/storage/presets/{preset-id}/library/`

Every image entering the RIL is analyzed by GPT-4.1-mini and tagged automatically.

### Feedback & Training Loop
Each rendered image has +/- buttons:
- **(+) APPROVE** — "This is spot on, more like this"
- **(-) REJECT** — "This missed, steer away"

**How learning compounds**:
1. **Reference Curation** (primary) — Approved (+) images auto-add to RIL; rejected (-) images excluded
2. **Export Auto-Deposit** — Exported images auto-duplicate into RIL (export = ultimate approval)
3. **Parameter Logging** — Store exact settings/prompts that produce good vs. bad results
4. **AI Brain Analysis** — GPT-4.1-mini classifies every image, building a searchable knowledge base
5. **Parameter Recommendations** — Brain suggests settings based on what worked for similar products

All data stored locally as files — learning persists across sessions.

## Feature: Recede (AI Outpainting)

Opposite of crop. When a product photo is shot too tight/zoomed:
1. User sets **Recede slider** (0-50%)
2. Clicks **Recede button**
3. OpenAI Images Edit API extends the background outward
4. Jewelry rendering stays identical, background fills naturally
5. Output stays 1170x2532

## Feature: VSCO-Style Editor

Slide-out panel opens when clicking any rendered image.

**Adjust Tab** — Per-image fine-tuning (processed locally via Pillow):
- Light: Exposure, Contrast, Highlights, Shadows
- Color: Temperature, Tint, Saturation, Vibrance, Skin Tone
- Detail: Sharpness, Clarity
- Film: Grain, Fade, Vignette

**Crop Tab** — Visual crop tool:
- Rule-of-thirds grid
- Aspect ratio pills: Free, 1:1, 4:5, 9:16, 16:9
- Straighten +/-45 degrees
- Transform: Rotate L/R, Flip H/V

All sliders centered at 0. Before/After compare, prev/next navigation, Reset All, Apply buttons.

## Export & Auto-Deposit

**Export Button** (bottom bar next to Render All):
- Configurable export path (clickable to change)
- When clicked: image saved to export folder + auto-duplicated into active preset's RIL

This creates a **closed feedback loop**:
```
Render -> Edit -> Export -> image enters RIL -> brain analyzes -> next batch is smarter
```

## Output Specifications

- **Dimensions**: 1170 x 2532 (iPhone portrait)
- **Format**: JPEG quality 95
- **Video**: MP4 via Sora 2

## File Organization

### User Data
```
~/JewelRender/
├── presets/                          # Per-preset data
│   ├── cool-blue/
│   │   ├── config.json
│   │   ├── library/                  # Reference Image Library
│   │   │   └── *.jpg
│   │   ├── renders/
│   │   │   └── *.jpg
│   │   └── feedback.json             # Approval/rejection log
│   ├── white-retail/
│   └── yashica-film/
├── exports/                          # User-configured export folder
│   └── *.jpg
└── feedback_log.json                 # Global parameter logging
```

## OpenAI API Integration

**API Key**: Set in `.env` as `OPENAI_API_KEY`
**Platform**: platform.openai.com (separate from ChatGPT subscription)
**Billing**: Pay-as-you-go API credits

**Endpoints Used**:
- `POST /v1/images/generations` — Generate mode (GPT Image 1.5)
- `POST /v1/images/edits` — Edit mode + Recede (GPT Image 1.5)
- `POST /v1/chat/completions` — Brain analysis (GPT-4.1-mini with vision)
- `POST /v1/videos` — 360 Video mode (Sora 2)

Backend communicates via the official `openai` Python SDK. Each mode has a corresponding API call pattern.

## Session Persistence

**Everything is local, nothing depends on a chat session**:
- Presets: `~/JewelRender/presets/`
- Renders: Per-preset `renders/` folder
- RIL: Per-preset `library/` folder
- Feedback: Per-preset `feedback.json` + global `feedback_log.json`
- Brain analyses: Stored alongside images as `{image_id}.analysis.json`

Closing the app = progress saved. Re-opening = everything intact.

## iPhone Access (Remote Control)

**Two ways to connect**:
1. **Local Network** — Same Wi-Fi as Mac Mini
2. **Tailscale** — iPhone on different network, still connects securely

Phone opens frontend at `http://<mac-mini-ip>:5000` (or Tailscale IP).

No files transfer to phone. The Mac Mini runs the server, OpenAI's cloud does the AI processing, and the phone just sends commands and receives preview images.

## Technology Choices (Documented)

- **Frontend**: Single HTML file (no framework) to minimize dependencies
- **Backend**: Python because the OpenAI SDK is Python-native, FastAPI for speed
- **AI Engine**: OpenAI APIs — no local GPU needed for AI; Mac Mini just serves the app
- **Storage**: Local filesystem to keep everything on the Mac Mini, no cloud sync
- **Image Processing**: Pillow/OpenCV for local adjustments (crop, exposure, etc.)

## Next Steps (Not Yet Built)

- Wire controls to OpenAI API endpoints
- Implement real drag-and-drop file handling
- Build cross-preset pipeline with edit masks
- RIL persistence backend (local folder structure)
- Batch processing queue with progress tracking
- AI brain auto-analysis on every image entry point
- Mobile responsive layout for iPhone access
- PWA manifest for home screen app experience

See `PROGRESS.md` for session-by-session evolution.
