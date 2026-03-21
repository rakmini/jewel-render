# JewelRender Features v4 (Detailed Specs)

## Style Presets System

### Current Presets

#### Cool Blue (Priority)
- Signature Instagram look, softly lit baby blue background
- Replicates real physical photography setup
- RIL teaches AI how light behaves in soft baby blue environment

#### White Retail
- Clean white lightbox photography
- Specs from retail partners
- New retail partners become new named presets

#### Yashica Film (Future)
- AI-generated models wearing jewelry (Sora-style)
- Yashica T4 / Carl Zeiss T* film look
- Warm tones, lifted blacks, subtle grain, soft vignette, halation

### Preset Management
- **+** button to add new preset
- **Duplicate** — starting point for variations
- **Delete** — per preset
- **Rename** — inline editable name field
- Tab switcher at top to select active preset

---

## Three Core Export Modes

All modes available in every preset.

### 1. Image Edit Mode

Upload existing jewelry photos and selectively modify:
- **Background color** — determined by preset (Cool Blue = baby blue, White Retail = white)
- **Metal type** — toggle buttons: White Gold, Rose Gold, Yellow Gold (with colored dots)
- **Metal karat** — sub-pills: 10k, 14k, 18k (modifies metal saturation only, NOT geometry)
- **Gemstone color** — Diamond, Ruby, Sapphire (Blue/Pink/Yellow/White), Emerald, Pearl; AI references real photos from RIL for true light behavior — not a color overlay
- **Size in frame** — Recede slider (0–50%)

**Key Guarantee**: Jewelry, reflection, stone appearance stay pixel-perfect. Only requested elements change.

### 2. Image Generation Mode (Sora-Style)

Create new jewelry images from scratch:
- **Text prompt** — words map to RIL folder names ("invisible setting white gold diamond ring" pulls from those RIL folders)
- **Optional reference image upload**
- Full access to ALL RIL folders across all categories

### 3. 360 Video Mode

Generate seamless rotating loops:
- Upload key angle JPGs (Front, Side, 3/4 view + optional Top/Lower)
- AI fills in all frames between key angles for smooth rotation
- Video Recede: same outpainting concept applied to all video frames
- Export aspect ratios: 9:16 (stories/reels), 1:1 (square), 4:5 (post)
- Duration: 3s, FPS: 24, Loop: Seamless, Format: MP4
- Model: SV3D_p (primary), WAN 2.1 (fallback)

---

## Material Controls (Workspace)

### Metal Type
Three toggle pills (mutually exclusive) with colored dots:
- ⚪ **White Gold** (light grey dot)
- 🟡 **Yellow Gold** (amber dot)
- 🩷 **Rose Gold** (pink dot)

### Karat Sub-Pills
Shown below Metal Type (mutually exclusive):
- **10k** — 41.7% gold, highest durability
- **14k** — 58.5% gold, standard
- **18k** — 75% gold, richest color saturation

Karat modifies metal saturation only — geometry/form is unchanged.

### Gemstone
Toggle pills with colored dots (mutually exclusive):
- ◻ **Diamond** (clear/white dot)
- 🔴 **Ruby** (red dot)
- 🔵 **Sapphire** (shows sub-color pills: Blue / Pink / Yellow / White)
- 🟢 **Emerald** (dark green dot)
- 🤍 **Pearl** (cream dot)

AI references real photos from RIL — not a color overlay.

### Product Type
Toggle pills (used for RIL tagging at export):
Ring / Necklace / Bracelet / Earrings / Watch / Grillz

---

## Post-Render Studio

### Overview
Full-screen split view that opens after "Render All" or clicking a rendered image. Split: image preview left, controls right. Close button returns to Workspace.

### Left Half — Image Preview

**Overlay controls:**
- **Top-left**: Before/After pill, Brush pill
- **Top-right**: ← 1/N → history nav + History button
  - History panel opens with full archive, filters, stats, per-item export

**Image**: 340px wide, rounded top corners, shadow. Displayed against `#e8e6e2` background.

**Below image (flush, same width)**: Amendments textarea + Apply button

**Bottom**: Filename + prev/next image navigation

### Right Half — Controls

#### GREEN ZONE — "● Live — changes apply instantly"
Sliders update preview in real-time, no re-render needed:
- Temperature, Saturation, Contrast, Sharpness, Grain
- All centered at 0, drag left/right
- **Export button** (full width) — exports and auto-files to RIL. Page stays open.
- Hint: "Happy with what you see? Export now. Auto-files to RIL."

#### AMBER ZONE — "◆ Re-render — AI regenerates image"
Changes here require AI to regenerate:
- Metal Type pills + Karat sub-pills
- Gemstone pills (with Sapphire sub-colors)
- Recede slider (0–50%)
- **Re-render button** — greyed until something changes, then activates

#### Below Zones
- **Product Type** — Ring, Necklace, Bracelet, Earrings, Watch, Grillz (for RIL tagging)
- **Generate Views** — Side, Top, Lower, 3/4 (multi-select pills) + Generate button
- **Open Editor** button — for Crop / deep adjustment

---

## Render History (Permanent Archive)

Every render is saved permanently — exported or not. Nothing is ever deleted during a session.

### Per Entry
- Label (description of what changed)
- Timestamp
- Tag: `initial`, `amendment`, `re-render`, `brush`
- Exported status (boolean)
- Material snapshot at time of render (metal, karat, gemstone, product type)

### Features
- Back/forward arrows to navigate versions (← 1/N →)
- History panel: scrollable list with filter tabs
- Filter tabs: All / Exported / Amended / Re-renders
- Stats bar: total renders, total exported
- Export button (↓) on hover for any version — retroactive export from old versions
- Green ✓ badge on exported items
- Material line per entry (e.g., "Rose Gold · 18k · Bracelet")
- Color-coded tags: green=exported, amber=amendment, blue=re-render

### RIL Filing
When exported, image files to correct RIL folders based on **that version's material snapshot** — not current controls. A Rose Gold 18k render files to Rose Gold + Diamond + Bracelet even if you've since switched to White Gold.

### Toast Notification
On export: "✓ Exported → RIL: Rose Gold + Diamond + Bracelet"
Auto-dismisses after 2.2s.

---

## Amendments Prompt

Text area below image in Post-Render Studio:
- Broad image-level changes: "make background slightly darker", "add soft shadow underneath", "smooth the links on the left"
- AI regenerates in place; all controls stay
- Version saved to History with `amendment` tag

---

## Selection Brush Tool

Targeted post-generation cleanup:
1. Enable brush (top-left pill in Post-Render Studio)
2. Adjust brush size (slider with live preview dot)
3. Paint over area to mark
4. Describe fix: "remove shadow", "smooth edge", "fix reflection"
5. AI only touches marked area
6. Version saved to History with `brush` tag

---

## Recede (AI Outpainting)

Solves "shot too tight" problem without reshooting.

1. Set Recede slider (0–50%)
2. AI regenerates with jewelry at smaller scale in frame
3. Background extends outward; jewelry rendering stays pixel-perfect
4. Output stays 1170×2532
5. **Video Recede**: same concept applied to all video frames

Visual feedback: slider activates button showing "Recede X%". During processing: "Regenerating..."

---

## Reference Image Library (RIL)

Two purposes:
1. **AI training library** — teaches materials, lighting, styles per environment
2. **Searchable database** — find any approved image/video fast

### Folder Categories (per preset)

**Materials**: White Gold, Yellow Gold, Rose Gold

**Gemstones**: White Diamond, Ruby, Sapphire (Blue/Pink/Yellow/White), Emerald, Pearl

**Product Types**: Rings, Bracelets, Necklaces, Earrings, Watches, Grillz

**Setting Styles**: Invisible, Prong, Bezel, Channel, Pave, Tension (expandable)

### Auto-Filing
Export = only approval path. On export, image auto-files to MULTIPLE folders simultaneously. Example: Rose Gold 18k Diamond Ring → files to Rose Gold + White Diamond + Rings.

### Compounding Loop
Generate → Edit → Export → RIL folders → next batch smarter → repeat.

---

## Upload Centre

Central hub for seeding the RIL with reference photos.

### Phase 1: Manual Seeding (one-time setup)
- Drop batch into staging area
- Drag images into folder target pills (Materials / Gemstones / Product Types / Setting Styles)
- Single photo can go into multiple folders
- ~5-15 examples per folder to seed

### Phase 2: AI-Suggested Sorting
- AI analyzes uploads, suggests folder tags
- User confirms or corrects
- Gets smarter over time

---

## RIL Browser

Searchable database view:
- **Search bar** — text maps to folder names ("cool blue diamond necklace white gold")
- **Left sidebar** — folder navigation (Presets, Materials, Gemstones, Product Types, Setting Styles)
- **Image/Video toggle** — switch between still and video archives
- **Thumbnail grid** — 4-column, multi-tag labels on each thumbnail
- Export directly from browser

---

## Generate Additional Views

From Post-Render Studio controls panel:
- Multi-select pills: Side / Top / Lower / 3/4
- AI generates anatomically identical views of same object
- Views feed into 360 Video assembly
- Hint: "AI generates identical object from selected angles"

---

## Cross-Preset Pipeline

1. Generate 50 images in Cool Blue style
2. Take finished renders to White Retail preset in Edit mode
3. Only background/lighting changes — jewelry stays identical
4. Same physical object, different environment
5. Avoids regeneration from scratch

---

## Per-Preset Adjust Sliders (Workspace)

Always visible in preset tab, apply to entire batch:
- Temperature (±)
- Saturation (±)
- Contrast (±)
- Sharpness (±)
- Grain (±)

All centered at 0. These define the preset's default baseline look.

---

## VSCO-Style Image Editor (Deep Edit)

Opened via "Open Editor" in Post-Render Studio, or by clicking an image in the queue.
Full-width panel slides out from right.

### Adjust Tab

**Light**: Exposure, Contrast, Highlights, Shadows

**Color**: Temperature, Tint, Saturation, Vibrance

**Detail**: Sharpness, Clarity

**Film**: Grain, Fade, Vignette

### Crop Tab

**Aspect Ratio Pills**: Free / 1:1 / 4:5 / 9:16 / 16:9

**Straighten**: ±45° slider

**Transform**: Rotate L/R, Flip H/V

**Rule-of-thirds grid** with corner drag handles

### Controls
- Before/After compare toggle
- Prev/Next image navigation
- Reset all adjustments
- Apply / Cancel
- Export Image button

---

## Export

### In Post-Render Studio (GREEN ZONE)
- Export button (full width)
- Saves to configured export folder as JPEG 95
- Auto-files to multiple RIL folders based on current version's material snapshot
- Page stays open — keep working (assembly line)
- Toast notification confirms RIL folders targeted

### Export Path
- Shown in bottom bar (Workspace)
- Clickable to change folder
- Default: `~/Desktop/JewelRender Exports`

---

## Batch Processing & Progress

### Render All Button
- Renders all images in queue (as many as ComfyUI allows simultaneously)
- Progress bar at bottom (0–100%)
- Bottom bar shows: Active preset + mode (e.g., "Cool Blue · Edit")

---

## Settings Tab

### ComfyUI Connection
- Host (default: `127.0.0.1`)
- Port (default: `8188`)
- Test connection button + status dot

### Checkpoint
- Current: `sd_xl_base_1.0.safetensors`

### Output Settings
- Dimensions: 1170×2532 (locked)
- JPEG quality: 95 (locked)

### Video Output
- Format: MP4
- Model: SV3D_p / WAN 2.1 selector

### RIL & Export Toggles
- **Auto-deposit exports to RIL** (default: ON)
- **Auto-file by material/gem/type** (default: ON)
- **Parameter logging on +/−** (default: ON)

### Setting Styles (RIL Category)
Toggle pills to manage active Setting Style categories:
Invisible / Prong / Bezel / Channel / Pave / Tension / + Add

---

## Not Yet Implemented (Needs Wiring)

- Wire to ComfyUI API (127.0.0.1:8188)
- Real drag-and-drop file handling
- Cross-preset pipeline
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

See `JEWELRENDER_SPEC_v4.md` for the authoritative spec.
