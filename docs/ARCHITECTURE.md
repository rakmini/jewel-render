# JewelRender Architecture (v4)

## System Overview

JewelRender is a distributed jewelry rendering system:
- **Frontend**: Single-page app (HTML/CSS/JS) running on iPhone or Mac browser
- **Backend**: Python API server (FastAPI) on Mac Mini M4, port 8080
- **AI Engine**: ComfyUI running locally at `127.0.0.1:8188`
- **Storage**: Local filesystem for presets, reference images, and outputs

The phone acts as a **remote control only**. All GPU processing happens on the Mac Mini M4.

---

## App Navigation (Three Top-Level Views)

### 1. Workspace
The main editing environment. Contains preset tabs, mode switcher, image queue, material controls, and the Render All / Export bar.

### 2. Upload Centre
Hub for seeding the Reference Image Library with reference photos. Drag-and-drop staging area, folder targets organized by category, AI-suggested sorting.

### 3. RIL Browser
Searchable database view of all approved images and videos in the RIL. Folder sidebar, image/video toggle, thumbnail grid with material tags.

### Post-Render Studio (Overlay)
Full-screen split view that opens after rendering. Not a top-level nav item — it overlays the Workspace. Close button returns to Workspace.

---

## Core Architecture: Two Independent Axes

### Style Axis (Presets)
Modular, user-expandable library of visual styles:
- **Cool Blue** — Signature Instagram look, softly lit baby blue background
- **White Retail** — Clean white for retail partner submissions
- **Yashica Film** — AI-generated models wearing jewelry, Yashica T4 film aesthetic

Users can create unlimited new presets (duplicate + rename).

### Export Axis (Modes)
Available in every preset:
- **Image Edit Mode** — Modify specific elements while preserving everything else
- **Image Generation Mode** — Create new images from scratch using text prompts + RIL
- **360 Video Mode** — Seamless rotating loops from key angle uploads (SV3D_p / WAN 2.1)

**Key Design**: Style × Mode = any valid combination. This matrix is the entire feature set.

---

## The Complete Pipeline

1. Image generated or edited
2. **Post-Render Studio opens** — split-screen, image left, controls right
3. **Live adjustments** (instant, no re-render): Temperature, Saturation, Contrast, Sharpness, Grain
4. **Amendments prompt** — text area below image for broad changes; AI regenerates in place
5. **Selection brush** — paint area, describe fix, AI touches only marked region
6. **Material swaps** (require re-render): Metal type, karat, gemstone; Re-render button activates only when changed
7. **Export** — saves to desktop folder + auto-files to correct RIL folders; page stays open
8. **Continue workflow** — switch materials, re-render, export again — assembly line, never leaves page
9. **Generate additional views** — AI creates identical side, top, lower, 3/4 views
10. **360 Video** — assembled from views into seamless rotating loop

### Key Principles
- Live sliders = instant preview, no waiting
- Material changes = require AI re-render
- Export = only path into RIL (quality gate)
- Export doesn't close anything — stay on page, keep working
- Every render saved to History permanently (session-persistent)

---

## Post-Render Studio Layout

### Left Half — Image Preview
- Background: `#e8e6e2`
- Image: 340px wide, max 68vh, rounded top corners (16px), shadow
- **Overlay controls on image:**
  - Top-left: Before/After pill, Brush pill
  - Top-right: History nav arrows (← 1/N →) + History button
  - History panel opens from top-right
  - Brush panel opens from top-left
- **Below image (flush, same width):** Amendments textarea + Apply button
- **Bottom of image area:** Filename, prev/next image navigation

### Right Half — Controls Panel (380px)
- Scrollable, `#f5f3f0` background
- **GREEN ZONE** — Live adjustments (instant): Temperature, Saturation, Contrast, Sharpness, Grain + Export button
- **AMBER ZONE** — Re-render controls (AI required): Metal Type, Karat, Gemstone, Recede slider, Re-render button (greyed until something changes)
- Product Type (for RIL tagging)
- Generate Views (Side/Top/Lower/3/4 multi-select + Generate button)
- Open Editor (Crop / deep adjust)

---

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
  "materials": {
    "metal": "White Gold",
    "karat": "14k",
    "gemstone": "Diamond",
    "productType": "Ring"
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

### Render History Entry
Per render (in-memory, session-persistent):
```json
{
  "label": "Rose Gold 18k + Diamond",
  "time": "14:32:05",
  "tag": "re-render",
  "exported": false,
  "materials": {
    "metal": "Rose Gold",
    "karat": "18k",
    "gem": "Diamond",
    "type": "Ring"
  }
}
```

Tags: `initial`, `amendment`, `re-render`, `brush`

### Reference Image Library (RIL) Folder Structure

Per preset, organized into four categories:

```
~/JewelRender/presets/{preset-id}/library/
├── materials/
│   ├── white-gold/
│   ├── yellow-gold/
│   └── rose-gold/
├── gemstones/
│   ├── white-diamond/
│   ├── ruby/
│   ├── sapphire-blue/
│   ├── sapphire-pink/
│   ├── sapphire-yellow/
│   ├── sapphire-white/
│   ├── emerald/
│   └── pearl/
├── product-types/
│   ├── rings/
│   ├── necklaces/
│   ├── bracelets/
│   ├── earrings/
│   ├── watches/
│   └── grillz/
└── setting-styles/
    ├── invisible/
    ├── prong/
    ├── bezel/
    ├── channel/
    ├── pave/
    └── tension/
```

**Auto-Filing on Export**: Image files to MULTIPLE folders simultaneously based on the version's material snapshot. A Rose Gold 18k Diamond Ring image files to: `rose-gold/` + `white-diamond/` + `rings/`.

---

## Feature: Recede (AI Outpainting)

1. User sets **Recede slider** (0–50%)
2. AI regenerates with jewelry at smaller scale in frame
3. Background extends outward while jewelry stays identical
4. Output stays 1170×2532
5. Video Recede applies same concept to all video frames

---

## Feature: Generate Additional Views

From Post-Render Studio controls:
- Multi-select pills: Side, Top, Lower, 3/4
- AI generates anatomically identical views of the same object
- Views feed into 360 Video assembly

---

## Feature: VSCO-Style Editor (Deep Edit)

Opened from "Open Editor" button in Post-Render Studio, or by clicking an image in the queue.

**Adjust Tab**: Exposure, Contrast, Highlights, Shadows, Temperature, Tint, Saturation, Vibrance, Sharpness, Clarity, Grain, Fade, Vignette

**Crop Tab**: Aspect ratio pills (Free/1:1/4:5/9:16/16:9), rule-of-thirds grid, straighten ±45°, rotate, flip

---

## Export & RIL Auto-Filing

Export is the only path into the RIL. On export:
1. Image saved to configured export folder
2. Image auto-filed into multiple RIL folders based on version's material snapshot
3. Page stays open (assembly line)

This creates a closed feedback loop: Render → Edit → Export → RIL → next batch smarter.

---

## Upload Centre

### Phase 1: Manual Seeding
- Drop photos into staging area
- Drag into folder targets (Materials / Gemstones / Product Types / Setting Styles)
- One photo can go into multiple folders

### Phase 2: AI-Suggested Sorting
- AI analyzes uploads, suggests folder tags
- User confirms or corrects
- Gets smarter over time

---

## Output Specifications

- **Dimensions**: 1170 × 2532 (iPhone portrait)
- **Format**: JPEG quality 95
- **Video**: MP4, SV3D_p or WAN 2.1 models, 3s, 24fps, seamless loop
- **Video export aspect ratios**: 9:16 (stories/reels), 1:1 (square), 4:5 (post)

---

## File Organization

### User Data
```
~/JewelRender/
├── presets/                          # Per-preset data
│   ├── cool-blue/
│   │   ├── config.json
│   │   ├── library/                  # Reference Image Library
│   │   │   ├── materials/
│   │   │   ├── gemstones/
│   │   │   ├── product-types/
│   │   │   └── setting-styles/
│   │   ├── renders/
│   │   └── feedback.json
│   ├── white-retail/
│   └── yashica-film/
├── exports/                          # User-configured export folder
└── feedback_log.json                 # Global parameter logging
```

---

## ComfyUI Integration

**Connection**: Host `127.0.0.1`, Port `8188`
**Checkpoint**: `sd_xl_base_1.0.safetensors`

**Workflows**:
- Image generation (SDXL base)
- Image editing — selective element modification (background, metal, stone)
- Video generation (SV3D_p / WAN 2.1 for 360 rotations)
- Outpainting (Recede feature — still images and all video frames)
- Multi-angle generation (Side/Top/Lower/3/4 views from approved still)
- Amendments (img2img from text description)
- Brush inpainting (selective area fix)

Backend communicates via ComfyUI HTTP API. Each mode has a corresponding workflow template.

---

## iPhone Access (Remote Control)

1. **Local Network** — Same Wi-Fi as Mac Mini
2. **Tailscale** — iPhone on different network, still connects securely

Phone opens frontend at `http://<mac-mini-ip>:8080` (or Tailscale IP).

---

## Technology Choices

- **Frontend**: Single HTML file (no framework) to minimize dependencies
- **Backend**: Python FastAPI, port 8080; ComfyUI is Python-native
- **Storage**: Local filesystem — everything on Mac Mini, no cloud sync
- **ComfyUI**: Native Mac Silicon support (M4 compatible)

---

## Session Persistence

- Presets: `~/JewelRender/presets/`
- Renders: Per-preset `renders/` folder
- RIL: Per-preset `library/` folder (4 categories)
- Feedback: Per-preset `feedback.json` + global `feedback_log.json`
- Render History: In-memory per session (resets when page reloads)

---

## Next Steps (Not Yet Wired)

- Wire controls to ComfyUI API (127.0.0.1:8188)
- Real drag-and-drop file handling
- Cross-preset pipeline validation
- RIL persistence backend (local folder structure)
- RIL search functionality
- Upload Centre drag-to-folder
- AI-suggested sorting
- Batch processing with real progress
- Rotating Video (SV3D_p / WAN 2.1)
- Wire live sliders to CSS filters / image processing
- Wire amendments prompt to img2img
- Wire brush tool to inpainting
- Wire material swaps to selective regeneration
- Multi-angle view generation
- Export auto-filing to multiple RIL folders
- Mobile responsive for iPhone
- PWA manifest

See `JEWELRENDER_SPEC_v4.md` for authoritative feature specs.
