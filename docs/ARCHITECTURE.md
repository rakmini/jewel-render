# JewelRender Architecture

## System Overview

JewelRender is a distributed jewelry rendering system:
- **Frontend**: Single-page app (HTML/CSS/JS) running on iPhone or Mac browser
- **Backend**: Python API server (FastAPI/Flask) on Mac Mini M4
- **AI Engine**: ComfyUI running locally at `127.0.0.1:8188`
- **Storage**: Local filesystem for presets, reference images, and outputs

The phone acts as a **remote control only**. All GPU processing happens on the Mac Mini M4. Render speed is identical whether you control the app from local network or Tailscale.

## Core Architecture: Two Independent Axes

### Style Axis (Presets)
Modular, user-expandable library of visual styles. Currently:
- **Cool Blue** — Signature Instagram look, baby blue background
- **White Retail** — Clean white for retail partner submissions
- **Yashica Film** — AI-generated models wearing jewelry, Yashica T4 film aesthetic

Users can create unlimited new presets.

### Export Axis (Modes)
Available in every preset:
- **Image Edit Mode** — Selectively change elements (background, metal, stone) while preserving everything else
- **Image Generation Mode** — Create new images from scratch using text prompts + reference images
- **360 Video Mode** — Seamless rotating loops from key angle uploads (SV3D_p / WAN 2.1)

**Key Design**: Style × Mode = any valid combination. This matrix is the entire feature set.

## Cross-Preset Pipeline (Critical Workflow)

A user can:
1. Generate 50 jewelry images in **Cool Blue** style
2. Drag those finished renders into **White Retail** (switch to Edit mode)
3. Only the background changes from baby blue to white
4. Jewelry, metal, and stone rendering stay **identical**
5. Avoids regeneration from scratch

This works because Edit mode only modifies what the target preset requires.

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

The more you export, the smarter the AI gets — zero extra effort.

### Feedback & Training Loop
Each rendered image has +/− buttons:
- **(+) APPROVE** — "This is spot on, more like this"
- **(−) REJECT** — "This missed, steer away"

**How learning compounds**:
1. **Reference Curation** (primary) — Approved (+) images auto-add to RIL; rejected (−) images excluded
2. **Export Auto-Deposit** — Exported images auto-duplicate into RIL (export = ultimate approval)
3. **Parameter Logging** — Store exact settings/prompts that produce good vs. bad results
4. **Future: LoRA Fine-Tuning** — Periodically train small LoRA adapter from approved images

All data stored locally as files — learning persists across sessions.

## Feature: Recede (AI Outpainting)

Opposite of crop. When a product photo is shot too tight/zoomed:
1. User sets **Recede slider** (0–50%)
2. Clicks **Recede button**
3. AI regenerates with jewelry at smaller scale in frame
4. Background extends outward while jewelry rendering stays identical
5. Output stays 1170×2532, fully regenerated through ComfyUI

Solves the "shot too tight" problem without losing product quality.

## Feature: VSCO-Style Editor

Slide-out panel opens when clicking any rendered image.

**Adjust Tab** — Per-image fine-tuning:
- Light: Exposure, Contrast, Highlights, Shadows
- Color: Temperature, Tint, Saturation, Vibrance, Skin Tone
- Detail: Sharpness, Clarity
- Film: Grain, Fade, Vignette

**Crop Tab** — Visual crop tool:
- Rule-of-thirds grid
- Aspect ratio pills: Free, 1:1, 4:5, 9:16, 16:9
- Straighten ±45°
- Transform: Rotate L/R, Flip H/V

All sliders centered at 0. Before/After compare, prev/next navigation, Reset All, Apply buttons.

## Export & Auto-Deposit

**Export Button** (bottom bar next to Render All):
- Configurable export path (clickable to change)
- When clicked: image saved to export folder + auto-duplicated into active preset's RIL

This creates a **closed feedback loop**:
```
Render → Edit → Export → image enters RIL → next batch is smarter
```

## Output Specifications

- **Dimensions**: 1170 × 2532 (iPhone portrait)
- **Format**: JPEG quality 95
- **Video**: MP4, SV3D_p or WAN 2.1 models

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

## ComfyUI Integration

**Connection**:
- Host: `127.0.0.1`
- Port: `8188`
- Checkpoint: `sd_xl_base_1.0.safetensors`

**Workflows**:
- Image generation (SDXL base)
- Image editing (inpainting, style transfer)
- Video generation (SV3D_p / WAN 2.1 for 360 rotations)
- Outpainting (Recede feature)

Backend communicates via ComfyUI HTTP API. Each mode has a corresponding workflow template.

## Session Persistence

**Everything is local, nothing depends on a chat session**:
- Presets: `~/JewelRender/presets/`
- Renders: Per-preset `renders/` folder
- RIL: Per-preset `library/` folder
- Feedback: Per-preset `feedback.json` + global `feedback_log.json`

Closing the app = progress saved. Re-opening = everything intact.

## iPhone Access (Remote Control)

**Two ways to connect**:
1. **Local Network** — Same Wi-Fi as Mac Mini
2. **Tailscale** — iPhone on different network, still connects securely

Phone opens frontend at `http://<mac-mini-ip>:5000` (or Tailscale IP).

No files transfer to phone. All rendering stays on Mac Mini M4. Phone just sends commands and receives preview images.

## Technology Choices (Documented)

- **Frontend**: Single HTML file (no framework) to minimize dependencies
- **Backend**: Python because ComfyUI is Python-native, FastAPI for speed
- **Storage**: Local filesystem to keep everything on the Mac Mini, no cloud sync
- **ComfyUI**: Native Mac Silicon support needed (M4 compatible)

## Next Steps (Not Yet Built)

- Wire controls to ComfyUI API
- Implement real drag-and-drop file handling
- Build cross-preset pipeline validation
- RIL persistence backend (local folder structure)
- Batch processing queue with progress tracking
- Saved profiles functionality
- Test video models on Apple Silicon
- Mobile responsive layout for iPhone access
- PWA manifest for home screen app experience

See `PROGRESS.md` for session-by-session evolution.
