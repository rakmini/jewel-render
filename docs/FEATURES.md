# JewelRender Features (Detailed Specs)

## Style Presets System

### Current Presets

#### Cool Blue
- The company's signature Instagram look
- Softly lit baby blue background
- Core brand identity customers recognize
- Primary preset for social media

#### White Retail
- Clean white background
- Industry-standard format for retail partner submissions
- Used when converting Cool Blue renders via cross-preset pipeline

#### Yashica Film
- Jewelry shown on AI-generated models (Sora-style)
- Yashica T4 with Carl Zeiss T* lens aesthetic
- Warm tones, lifted blacks, subtle grain, soft vignette, halation
- Special: AI generates people wearing the jewelry

### Future Presets (Examples)
- Soft Pink — soft pink background variant
- Black Luxury — dark/black premium aesthetic
- (User can create any new preset as needed)

### Preset Management UI
- **+** button to add new preset
- **Duplicate** option for each preset (starting point for variations)
- **Delete** option per preset
- **Rename** presets inline
- Tab switcher at top to select active preset
- All presets independent — can work on multiple simultaneously

---

## Three Core Export Modes

All modes available in every preset. Choose one, render, then switch if needed.

### 1. Image Edit Mode

**Purpose**: Take an existing photo and selectively change specific elements only.

**Use Cases**:
- Product shot too tight? Use Recede to extend background
- Need background color changed? Recolor background while keeping jewelry identical
- Metal color adjustment? Change only metal appearance, preserve stone rendering
- Cross-preset conversion: render in Cool Blue, edit into White Retail (only background changes)

**Workflow**:
1. Upload existing image or drag from previous render
2. Select elements to modify (background, metal, stone, etc.)
3. Click Render
4. Review in editor, export when ready

**Key Guarantee**: Jewelry, reflection, stone appearance stay pixel-perfect. Only requested elements change.

### 2. Image Generation Mode (Sora-Style)

**Purpose**: Create entirely new images from scratch.

**Input**:
- Text prompt describing the jewelry and desired context
- Reference images (from RIL or upload new ones) to show style/aesthetic
- Angle/framing preferences

**Output**:
- Brand new photograph of jewelry in the preset's style
- Dimensions: 1170×2532 (iPhone portrait)
- Quality: JPEG 95

**Special Case - Yashica Film**:
- AI generates realistic-looking people wearing the jewelry
- Uses reference pool of model photos to maintain consistent "look"
- Critical for portfolio/marketing where jewelry shown on humans vs. plain background

**Workflow**:
1. Write text prompt ("delicate emerald ring on white background, soft lighting")
2. Upload or select reference images (optional but recommended)
3. Click Render
4. Review in editor, approve/reject (+/−), export when perfect

### 3. 360 Video Mode

**Purpose**: Generate seamless rotating loops of jewelry from multiple angles.

**The Problem It Solves**:
Seamless 360° looping has been a major frustration — traditional video editing and basic AI often fail to complete a full uninterrupted turn. JewelRender solves this.

**Input**:
- 3 key angle JPGs (Front, Side, 3/4 view) — upload into drag zones
- Reference video pool (optional) — company has 20+ existing rotation videos
- Video preferences: length, rotation speed, etc.

**Output**:
- MP4 video
- Seamless loop (ends connect perfectly to start)
- Jewelry smoothly rotates 360° with no jumps or inconsistencies
- All preset styles supported (Cool Blue rotation, White Retail rotation, etc.)

**AI Models**:
- Primary: SV3D_p (Stable Video 3D, latest variant)
- Fallback: WAN 2.1 if SV3D_p unavailable
- Training: Company's 20+ existing rotation videos provide reference data

**Workflow**:
1. Upload 3 key angles (front, side, 3/4 view)
2. Select rotation direction, speed, video length
3. Click Render
4. Review playback, export when ready

---

## Recede: AI Outpainting for Framing

**The Problem**: Product shot too tight/zoomed in → need more background breathing room.

**The Solution**: Recede is AI outpainting purpose-built for product photography.

**How It Works**:
1. User sets **Recede slider** (0–50%) — defines how much to pull back
2. Clicks **Recede button**
3. AI regenerates entire image with jewelry at smaller scale in frame
4. Background extends outward in preset's style
5. Jewelry rendering stays pixel-perfect, only background changes
6. Output stays 1170×2532

**Visual Feedback**:
- Slider starts at 0% (greyed out button)
- When slider moves, button becomes active
- Button shows "Recede 10%" (or current %)
- During processing: "Regenerating..."
- Completes when image appears in queue

**Why This Matters**:
- Avoids reshooting product photos
- Preserves jewelry quality (no scaling artifacts)
- Extends usable framing from tight/dramatic to airy/retail
- Much faster than manual retouching

---

## Reference Image Library (RIL)

### What It Is

A **persistent cloud of images per preset** that teaches the AI what that preset should look like. Images are tied to presets, not sessions. Once added, they stay permanently unless manually removed.

### Why It Matters

RIL creates a **compounding feedback loop**:
- Add reference examples → AI learns the style
- Export approved images → they enter RIL → next batch is smarter
- Keep only approved images → AI steadily improves
- More exports = smarter AI (zero extra effort)

### Three Ways Images Enter RIL

#### 1. Manual Upload
- Drag reference images into RIL drop zone
- Use existing photos, inspiration images, style examples
- Immediate effect on next render

#### 2. Auto-Add Approved Images
- Toggle in Settings: "Auto-add approved images to RIL" (default: ON)
- When you click **+** on a rendered image → it auto-enters RIL
- No extra steps — approval = auto-deposit

#### 3. Auto-Deposit Exports
- Toggle in Settings: "Auto-deposit exports to RIL" (default: ON)
- When you **Export** an image → it auto-duplicates into RIL
- Export = ultimate approval — you edited it, you're happy
- Creates closed loop: Render → Edit → Export → RIL

### Settings Toggles (in Settings Tab)

- **Auto-add approved to RIL** (default: ON)
- **Auto-deposit exports to RIL** (default: ON)
- **Parameter logging** (default: ON) — stores settings/prompts that work

### Storage

- RIL files stored locally: `~/JewelRender/presets/{preset-id}/library/`
- Each preset has independent RIL
- Cool Blue's library teaches one aesthetic, Yashica Film's teaches another
- Nothing on external servers — all local, all persistent

### Future Enhancement: LoRA Fine-Tuning

Periodically use approved images in RIL to train a small LoRA adapter. Compounds learning directly into the AI model. (Not yet implemented.)

---

## Feedback & Training System

### Per-Image Feedback Buttons

Every rendered image in the queue has **+** and **−** buttons:

- **+** (Approve) — "This is spot on, more like this"
- **−** (Reject) — "This missed, steer away"

### Visual Feedback

- Button state changes when clicked
- Approved/Rejected count shown in queue (e.g., "5 approved, 2 rejected")
- Approved images are candidates for RIL entry (if auto-add enabled)

### How Learning Compounds (Persists Across Sessions)

#### 1. Reference Curation (Primary)
- Approved (+) images → auto-add to RIL (if toggle ON)
- Rejected (−) images → excluded from RIL
- The "intelligence" lives in the curated image set on disk — never lost

#### 2. Export Auto-Deposit
- Every exported image enters RIL
- Export is the **ultimate approval**
- Creates: Render → Edit → Export → image teaches next batch

#### 3. Parameter Logging
- Store exact settings/prompts that produced good vs. bad results
- App favors settings/prompts that work over time
- Future: use this log to auto-suggest parameters

#### 4. Future: LoRA Fine-Tuning
- Periodically use approved image set to train small LoRA adapter
- Compounds real learning into the model weights
- (Planned, not yet implemented)

### All Data Stored Locally

- Nothing depends on a chat session staying alive
- Feedback stored: `~/JewelRender/presets/{preset-id}/feedback.json`
- Parameter log stored: `~/JewelRender/feedback_log.json`
- Learning is **permanent** and **compounds**

---

## VSCO-Style Image Editor

Slide-out overlay that opens when clicking any rendered image in the queue.

### Adjust Tab

**Per-image fine-tuning controls**. All sliders centered at 0, drag left to decrease, right to increase.

**Light Controls**:
- Exposure — overall brightness
- Contrast — difference between light and dark
- Highlights — brightest areas
- Shadows — darkest areas

**Color Controls**:
- Temperature — warm (right) / cool (left)
- Tint — magenta / cyan shift
- Saturation — color intensity
- Vibrance — natural color pop
- Skin Tone — shift for people photos

**Detail Controls**:
- Sharpness — edge definition
- Clarity — local contrast and texture

**Film Controls**:
- Grain — digital grain texture
- Fade — washed out look
- Vignette — dark corners

### Crop Tab

**Visual crop tool** with VSCO-style interface.

**Aspect Ratio Pills** (quick presets):
- Free — custom crop
- 1:1 — square
- 4:5 — Instagram portrait
- 9:16 — TikTok/Reels
- 16:9 — widescreen

**Crop Tools**:
- **Rule-of-thirds grid** — visual guide for composition
- **Corner drag handles** — adjust crop boundaries
- **Straighten slider** — ±45° rotation for fixing tilted shots
- **Transform buttons** — Rotate L/R, Flip H/V

### Navigation & Controls

- **Before/After compare** — toggle to see changes
- **Prev/Next buttons** — jump between images in queue
- **Reset All** — revert all adjustments to 0
- **Apply** — save adjustments to image
- **Export** — save image to export folder + auto-deposit to RIL

---

## Per-Preset Adjust Sliders (Always Visible)

Independent from the editor. These define the **preset's default look** and apply to entire batches.

**Available in every preset tab**:
- Temperature (±)
- Saturation (±)
- Contrast (±)
- Sharpness (±)
- Grain (±)

All centered at 0. Change these to adjust the baseline for all renders in that preset.

---

## Export

### Export Button (Bottom Bar)

Located next to "Render All" button at the bottom of the screen.

**Shows**:
- Current export folder path (clickable to change)
- Number of images ready to export

**On Click**:
1. All selected images save to export folder as JPEG 95
2. Each image auto-duplicates into active preset's RIL (if auto-deposit toggle ON)
3. Images can then be used elsewhere (social media, email, print)

### Configurable Export Path

- Click export path text to open file picker
- Change to any folder on Mac Mini
- Default: `~/JewelRender/exports/`

---

## Batch Processing & Progress

### Render All Button

- Renders all images in current queue simultaneously (as many as ComfyUI allows)
- Shows progress bar at bottom (0–100%)
- Real-time updates as images complete
- Can queue new images while rendering

### Progress Indicators

- Bottom bar shows: Active preset + mode (e.g., "Cool Blue / Generate")
- Progress bar: Percentage complete
- Queue shows: "5/12 rendered" or similar

---

## Settings Tab

Central location for configuration and toggles.

### ComfyUI Connection
- Host (default: `127.0.0.1`)
- Port (default: `8188`)
- Test connection button

### Checkpoint
- Current: `sd_xl_base_1.0.safetensors`
- Dropdown to select other checkpoints (when available)

### Output Settings
- Dimensions: 1170×2532 (locked, shown for reference)
- JPEG quality: 95 (locked, shown for reference)

### Video Output
- Video format: MP4
- Video model: SV3D_p / WAN 2.1 selector
- Video length/speed preferences

### Feedback & Training Toggles
- **Auto-add approved to RIL** (default: ON)
- **Auto-deposit exports to RIL** (default: ON)
- **Parameter logging** (default: ON)

### Saved Profiles (Future)
- Save/load preset configurations
- (Not yet implemented)

---

## User Interface Layout

### Header
- JewelRender logo + tagline
- Connection status indicator

### Preset Tabs (Top Center)
- One tab per preset
- **+** button to add new preset
- Per-preset: Duplicate, Delete, Rename options

### Mode Switcher (Per Preset)
- Pill toggle: Edit / Generate / 360 Video
- Changes available controls below

### Left Panel (Image Queue)
- Drag-and-drop zone for uploads
- File list with thumbnails
- +/− feedback buttons per image
- Approved/rejected counts

### Right Panel (Preset Controls)
- Mode-specific controls
- Recede slider + button
- Per-preset Adjust sliders
- Reference Image Library with thumbnails + management

### Settings Tab
- ComfyUI config, toggles, saved profiles

### Bottom Bar
- Active preset + mode indicator
- Render All button
- Export button + path
- Progress bar

### Editor Overlay (Modal)
- Opens on image click
- Adjust + Crop tabs
- Before/After, navigation, apply/reset/export buttons

---

## Data Persistence

All data lives locally on the Mac Mini. Nothing syncs to cloud.

```
~/JewelRender/
├── presets/
│   ├── cool-blue/
│   │   ├── config.json          # Preset metadata & settings
│   │   ├── library/             # Reference Image Library
│   │   │   ├── ref1.jpg
│   │   │   └── ref2.jpg
│   │   ├── renders/             # Generated images
│   │   │   └── *.jpg
│   │   └── feedback.json        # +/− log for this preset
│   ├── white-retail/
│   └── yashica-film/
├── exports/                     # User-configured export folder
│   └── *.jpg
└── feedback_log.json            # Global parameter logging
```

---

## Not Yet Implemented

- Real drag-and-drop file handling
- Batch processing queue with actual progress tracking
- Mobile responsive layout for iPhone
- PWA manifest for home screen app experience
- Saved profiles functionality
- LoRA fine-tuning from approved sets
- Video model testing on Apple Silicon

See `PROGRESS.md` for implementation roadmap.
