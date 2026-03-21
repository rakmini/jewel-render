# JEWELRENDER — Complete Project Specification v4

**Last updated:** March 20, 2026 (Session 3 — Final)
**Owner:** Jonathan — jewelry company owner, non-developer
**Builds with:** Claude (Cowork, Claude Code, Claude Desktop)

---

## INSTRUCTIONS FOR CLAUDE CODE

This document is the single source of truth. Read it fully before doing anything.
Do NOT ask Jonathan to re-explain anything documented here. He is not a developer —
explain technical choices simply. When building, wire to ComfyUI at 127.0.0.1:8188.
All output: 1170×2532 iPhone portrait. Preserve the minimal VSCO-inspired design
language throughout.

---

## PURPOSE

JewelRender is a batch jewelry rendering and image generation app for a jewelry
company. It connects to ComfyUI running locally on a Mac Mini M4. The app digitizes
Jonathan's real physical photography setups — each preset replicates how light
behaves in a specific environment (baby blue soft-lit setup, white lightbox, etc.).

Accessible remotely from iPhone via Tailscale. Phone is just the remote control —
Mac Mini does all GPU processing.

---

## THE TWO MAIN FUNCTIONS

### Function 1: Image Editor (Upload & Modify)

Upload existing jewelry photos and selectively modify specific elements while
preserving everything else:

- **Background color** — determined by preset (Cool Blue = baby blue, White Retail = white)
- **Metal type** — toggle buttons: White Gold, Rose Gold, Yellow Gold (with colored dots)
- **Metal karat** — sub-options: 10k, 14k, 18k. Modifies ONLY metal saturation, NOT geometry
- **Gemstone color** — toggle to swap: White Diamond, Ruby, Sapphire (blue/pink/yellow/white), Emerald, Pearl. AI references real photos from RIL for true light behavior — not a color overlay
- **Size in frame (Recede)** — AI outpainting, slider 0-50%, regenerates with smaller object in frame

### Function 2: Image Generator (Sora-style)

Create new jewelry images from scratch using:
- **Text description** — words map to RIL folder names ("invisible setting white gold diamond ring" pulls from those folders)
- **Optional reference image upload**

Generator has full access to ALL RIL folders across all categories.

---

## THE COMPLETE PIPELINE

1. **Image exists** (edited or generated)
2. **Post-Render Studio opens** — split-screen view, image left, controls right
3. **Live adjustments** (instant, no re-render): Temperature, Saturation, Contrast, Sharpness, Grain
4. **Amendments prompt** — text area below image for broad changes ("add subtle shadow", "make background warmer"). AI regenerates in place, all controls stay
5. **Selection brush** — mark specific areas for targeted fixes (remove shadow, smooth edge)
6. **Material swaps** (requires re-render): Metal type, karat, gemstone. Re-render button activates only when changed
7. **Export** — image goes to desktop folder + auto-files to correct RIL folders. Page stays open for continued work
8. **Continue workflow** — switch materials, re-render, export again. Assembly line. Never leaves the page
9. **Generate additional views** — AI creates anatomically identical side, top, lower, 3/4 views
10. **360 Video** — assembled from views into seamless rotating loop

### Key Principles
- Live sliders = instant preview, no waiting
- Material changes = require AI re-render
- Export = only path into RIL (quality gate)
- Export doesn't close anything — stay on page, keep working
- Every render saved to History permanently

---

## POST-RENDER STUDIO (Approved Layout)

This is the primary workspace after an image is generated or edited. Split-screen:

### Left Half — Image Preview
- Image displayed at iPhone portrait ratio (1170×2532)
- 380px wide, max 72vh height
- Rounded corners (16px top, 0 bottom where prompt meets)
- Centered on #e8e6e2 background with 32px padding
- Shadow: 0 -4px 40px rgba(0,0,0,0.1)

**Overlay controls on image:**
- Top-left: Before/After pill button, Brush pill button
- Top-right: History nav arrows (← 1/1 →) + History button
- History panel opens from top-right with filters, stats, and full archive
- Brush panel opens from top-left with size slider and text prompt

**Below image (flush, same width):**
- Amendments text area — white background, rounded bottom corners
- "Describe changes — AI applies to full image" hint
- Apply button

**Bottom of image area:**
- Filename display
- Prev/next navigation with counter

### Right Half — Controls Panel (440px)
- 36-40px padding all around
- Scrollable
- Background: #f5f3f0
- Border-left: 1px solid #e0ddd8

**Layout top to bottom:**

1. **Header** — "Cool Blue · Edit" + close button (28px circle)

2. **GREEN ZONE: "● Live — changes apply instantly"**
   - Adjust sliders: Temperature, Saturation, Contrast, Sharpness, Grain
   - All centered at 0, drag left/right
   - Slider labels: 12px, min-width 90px
   - Row spacing: 16px between each
   - Export button (full width, 14px padding, 24px radius)
   - Hint: "Happy with what you see? Export now. Auto-files to RIL."

3. **DIVIDER**

4. **AMBER ZONE: "◆ Re-render — AI regenerates image"**
   - Metal Type pills (White Gold, Rose Gold, Yellow Gold with colored dots)
   - Karat sub-pills (10k, 14k, 18k)
   - Gemstone pills (Diamond, Ruby, Sapphire, Emerald, Pearl with colored dots)
   - Recede slider (0-50%)
   - Re-render button — greyed out until something changes, then activates

5. **DIVIDER**

6. **Product Type** — Ring, Necklace, Bracelet, Earrings, Watch, Grillz

7. **DIVIDER**

8. **Generate Views** — Side, Top, Lower, 3/4 (multi-select pills) + Generate button

9. **DIVIDER**

10. **Open Editor button** — for Crop / Brush deep editing

---

## RENDER HISTORY (Permanent Archive)

Every render is saved permanently — exported or not. Nothing is ever deleted.

### Per entry stored:
- Label (description of what changed)
- Timestamp
- Tag (initial, amendment, re-render, brush)
- Exported status (boolean)
- Material snapshot at time of render (metal, karat, gemstone, product type)

### Features:
- Back/forward arrows to navigate versions
- History panel with full scrollable list
- Filter tabs: All, Exported, Amended, Re-renders
- Stats bar: total renders, total exported
- Export button (↓) on hover for any version — can export old versions retroactively
- Green ✓ badge on exported items
- Material metadata shown per entry (e.g. "Rose Gold · 18k · Bracelet")
- Toast notification on export: "✓ Exported → RIL: Rose Gold + Bracelet"

### RIL Filing:
When exported, the image files to the correct RIL folders based on THAT VERSION'S
materials — not whatever is currently selected. A Rose Gold 18k render files to
Rose Gold + Bracelet, even if you've since switched to White Gold on the controls.

---

## STYLE PRESETS (Modular, Expandable)

### Cool Blue (Priority — master this first)
- Signature Instagram look, softly lit baby blue background
- Replicates real physical photography setup
- RIL teaches AI how light behaves in soft baby blue environment

### White Retail
- Clean white lightbox photography
- Specs from retail partners
- New partners become new named presets

### Yashica Film (Future)
- AI-generated models wearing jewelry
- Yashica T4 / Carl Zeiss T* film look
- Warm tones, lifted blacks, subtle grain, soft vignette, halation

---

## REFERENCE IMAGE LIBRARY (RIL)

The brain of the app. Two purposes:
1. **AI training library** — teaches materials, lighting, styles per environment
2. **Searchable database** — find any approved image/video fast (works on iPhone)

### Folder Structure (per preset, images AND videos):

**Materials:** White Gold, Yellow Gold, Rose Gold

**Gemstones:** White Diamond, Ruby, Sapphire (Blue/Pink/Yellow/White), Emerald, Pearl

**Product Types:** Rings, Bracelets, Necklaces, Earrings, Watches, Grillz

**Setting Styles:** Invisible, Prong, Bezel, Channel, Pave, Tension (expandable)

### Auto-Filing:
Export = only approval path. On export, image auto-files into MULTIPLE folders
simultaneously. Example: Rose Gold 18k Diamond Ring → Rose Gold + Diamond + Ring.

### Compounding Loop:
Generate → Edit → Export → RIL folders → next batch smarter → repeat.

---

## UPLOAD CENTRE

Central hub for seeding the RIL with reference photos.

### Phase 1: Manual Seeding (one-time)
- Upload batch, manually drag into folders
- Single photo → multiple folders
- ~5-15 examples per folder to seed

### Phase 2: AI-Suggested Sorting
- AI analyzes uploads, suggests folder tags
- User confirms or corrects
- Gets smarter over time

---

## RIL BROWSER

Searchable database view with:
- Search bar (text maps to folder names)
- Left sidebar: folder navigation (Presets, Materials, Gemstones, Product Types, Settings)
- Image/Video toggle
- Thumbnail grid with multi-tag labels
- Can export directly from browser

---

## CROSS-PRESET PIPELINE

Generate 50 in Cool Blue → drag into White Retail in Edit mode → only background/lighting
changes. Jewelry stays identical. Same object, different physical environment.

---

## SELECTION BRUSH TOOL

For targeted post-generation cleanup:
1. Adjust brush size (slider with live preview dot)
2. Paint over area to mark
3. Describe fix: "remove shadow", "smooth edge", "fix reflection"
4. AI only touches marked area

---

## AMENDMENTS PROMPT

Text area below image in post-render studio for broad image-level changes:
- "make background slightly darker"
- "add soft shadow underneath"
- "smooth the links on the left"
- AI regenerates in place, all controls stay, version saved to History

---

## BUILT-IN IMAGE EDITOR (VSCO-style)

Deeper editing overlay with two tabs:

**Adjust:** Exposure, Contrast, Highlights, Shadows, Temperature, Tint, Saturation,
Vibrance, Sharpness, Clarity, Grain, Fade, Vignette

**Crop:** Aspect ratio pills (Free/1:1/4:5/9:16/16:9), rule-of-thirds grid,
straighten ±45°, rotate, flip

---

## 360 VIDEO

- Approve still → AI generates identical views → seamless 360 loop
- Export aspect ratios: 9:16 (stories/reels), 1:1 (square), 4:5 (post)
- Video Recede: same concept, applied to all frames
- Model: SV3D_p or WAN 2.1
- Duration: 3s, FPS: 24, Loop: Seamless, Format: MP4
- Videos auto-file to video section of RIL with same folder structure

---

## APPROVED VISUAL DESIGN LANGUAGE

### Foundation
- Font: Inter (300, 400, 500, 600)
- Background: #f5f3f0
- Text: #2c2c2c primary, #777 labels, #999 section titles, #bbb hints, #ccc placeholders
- Borders: #ddd default, #e8e6e2 dividers, #e0ddd8 panel borders
- Active/selected: #1a1a1a background, white text
- Hover: border-color #999, color #555

### Toggle Pills
- Font: 11px, padding 7px 16px, border-radius 22px, gap 8px
- Active: #1a1a1a bg, white text
- Karat sub-pills: 10px font, 4px 13px padding, border-radius 14px, #555 active bg

### Sliders
- Labels: 12px, #777, font-weight 300, min-width 90px
- Track: 2px height, #ddd
- Thumb: 12px circle, #1a1a1a
- Center mark: 1px wide, 8px tall, #ccc
- Values: 11px, #999, tabular-nums
- Row spacing: 16px

### Buttons
- Primary: 11px, letter-spacing 1.5px, uppercase, 14px padding, 24px radius, #1a1a1a bg
- Secondary: 11px, 12px padding, 22px radius, white bg, #ddd border
- Disabled: opacity 0.25, pointer-events none

### Section Titles
- 10px, letter-spacing 2px, uppercase, #999, margin-bottom 12px

### Zone Labels
- 10px, letter-spacing 1.5px, uppercase, font-weight 500, margin-bottom 18px
- Live: #5aa76a (green)
- Re-render: #d4a846 (amber)

### Dividers
- 1px, #e8e6e2, margin 24px vertical

### Sections
- margin-bottom: 26px

### Panel Spacing
- Controls panel: 36-40px padding all sides
- Controls header margin-bottom: 28px

### Image Preview Area
- Background: #e8e6e2
- Image: 380px wide, max 72vh, border-radius 16px (top), shadow
- Padding: 32px 48px around image area

### Toast Notifications
- Fixed bottom center, #1a1a1a bg, #f5f3f0 text, 24px radius
- 12px 28px padding, 11px font, shadow
- Auto-dismiss after 2.2s with fade

### History Panel
- 280px wide, max 60vh, white bg, 12px radius
- Items: thumbnail (36×62px, 4px radius), label, material line, time, tags
- Exported badge: 14px green circle with ✓
- Tags color-coded: green=exported, amber=amendment, blue=re-render

---

## TECH STACK

- Single-file HTML/CSS/JS (vanilla, no framework yet)
- ComfyUI backend: 127.0.0.1:8188, Mac Mini M4
- Checkpoint: sd_xl_base_1.0.safetensors
- Output: JPEG 95, 1170×2532, iPhone portrait
- Video: MP4, SV3D_p model

---

## DEV ENVIRONMENT

- Machine: Mac Mini M4 (hostname: Raks-Mac-mini)
- Claude Code: v2.1.80
- Plan: Claude Max 5x ($100/mo)
- GitHub: Account exists, repo setup in progress
- Remote Control: Enabled for iPhone handoff

---

## APP NAVIGATION

### Three Top-Level Views:
1. **Workspace** — preset tabs, mode switcher, image queue, controls, render
2. **Upload Centre** — bulk upload, drag-to-folder sorting, AI suggestions
3. **RIL Browser** — searchable database, folder sidebar, image/video toggle

### Post-Render Studio:
- Opens after Render All or clicking a rendered image
- Full-screen split view over the workspace
- Close button returns to workspace

---

## WHAT'S BUILT (UI Mockup Only)

- [x] Header with logo and tagline
- [x] Top nav: Workspace / Upload Centre / RIL Browser
- [x] Modular preset tabs (add/duplicate/delete/rename)
- [x] Edit / Generate / 360 Video mode switcher per preset
- [x] Image queue with drop zone, file list, +/- feedback
- [x] Metal type buttons with colored dots + karat sub-pills
- [x] Gemstone toggles with colored dots + sapphire sub-colors
- [x] Product type selector
- [x] Re-render with Changes button in workspace
- [x] Per-preset Adjust sliders
- [x] Recede slider + button
- [x] Post-render studio (approved split-screen layout)
- [x] Live adjust zone (green) vs Re-render zone (amber)
- [x] Amendments prompt below image
- [x] Selection brush tool (size slider, text prompt, apply)
- [x] Render History panel (permanent archive with material metadata)
- [x] History filters, stats, per-item export, toast notifications
- [x] Export stays on page (assembly line workflow)
- [x] Upload Centre with staging, folder targets, AI suggestions
- [x] RIL Browser with search, folder sidebar, image/video toggle
- [x] Setting Styles category
- [x] VSCO editor overlay (Adjust + Crop tabs)
- [x] Video export aspect ratios + video recede
- [x] Generate Views (Side, Top, Lower, 3/4)

## WHAT NEEDS WIRING

- [ ] Wire to ComfyUI API (127.0.0.1:8188)
- [ ] Real drag-and-drop file handling
- [ ] Cross-preset pipeline
- [ ] RIL persistence backend (local folders)
- [ ] RIL search functionality
- [ ] Upload Centre drag-to-folder
- [ ] AI-suggested sorting after seeding
- [ ] Batch processing with real progress
- [ ] Rotating Video (SV3D_p / WAN 2.1)
- [ ] Wire Recede to outpainting
- [ ] Wire live sliders to CSS filters / image processing
- [ ] Wire amendments prompt to img2img
- [ ] Wire brush tool to inpainting
- [ ] Wire material swaps to selective regeneration
- [ ] Additional view generation (multi-angle)
- [ ] Export auto-filing to multiple RIL folders
- [ ] Mobile responsive for iPhone
- [ ] PWA manifest

---

## SESSION LOG

### Session 1 (March 18, 2026)
Planning — defined purpose, presets, modes, RIL, feedback system, cross-preset pipeline

### Session 2 (March 18, 2026)
Built HTML mockup — mode switchers, editor overlay, recede, adjust sliders, export

### Session 3 (March 20, 2026)
- Clarified two main functions + complete pipeline
- Added metal type/karat/gemstone toggles
- Added Upload Centre + RIL Browser views
- Added selection brush tool
- Added setting styles category
- Separated live adjustments from re-render controls (green/amber zones)
- Removed material tab from editor (workspace handles materials, editor handles fine-tuning)
- Built post-render studio split-screen layout
- Added amendments prompt below image
- Added permanent render history with material metadata
- Added assembly line workflow (export stays on page)
- Added toast notifications for export
- Approved visual design: spacing, typography, sizing, colors
- Generated comprehensive spec for Claude Code handoff
