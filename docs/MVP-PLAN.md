# MVP Plan: Cool Blue Metal Swap

**Date**: 2026-03-23
**Goal**: Ship a testable UI today. Upload a Raksha jewelry photo, pick a metal type, get an AI-edited result in Cool Blue style. Keep the geometry of the jewelry product exactly the same.

---

## The Feature

One workflow, one screen:

1. User uploads an existing Raksha jewelry photo
2. User picks metal type: **Yellow Gold**, **White Gold**, or **Rose Gold**
3. User clicks **Render**
4. OpenAI edits the image using a master prompt
5. Result appears on screen — user can download it

### Master Prompt Template

```
Render this image in 14k {metal_type} gold. Suspend in a softly lit baby blue color background.
```

Where `{metal_type}` = `yellow` | `white` | `rose`

---

## Design Principles

- **Keep all existing work** — nothing gets deleted. The full UI (`index.html`), CSS (`styles.css`), JS modules (`api.js`, `state.js`, `ui.js`, `app.js`), and mockups all stay in place.
- **Same visual language** — the MVP page uses the existing `styles.css` (dark theme, Inter font, accent colors, pill buttons, panels, drop zone styling). It must look and feel like the same app, just focused on one task.
- **Standalone route** — MVP lives at `/mvp` alongside the full UI at `/`. No refactoring of existing frontend code.
- **Reusable later** — the backend endpoint and OpenAI client we build now will be consumed by the full UI when we wire it up post-MVP.

---

## What We Build (4 deliverables)

### 1. Backend: OpenAI config + client

**File**: `backend/src/openai_client.py` (new)
**File**: `backend/.env` (new, from .env.example)

- Read `OPENAI_API_KEY` from env
- Use `openai.AsyncOpenAI` client (async — won't block the FastAPI event loop)
- Single function: `async edit_image(image_bytes: bytes, prompt: str) -> bytes`
  - Converts input bytes to PNG via Pillow if needed (OpenAI may require PNG)
  - Wraps bytes in a file-like object with filename (OpenAI SDK requires this)
  - Calls `client.images.edit(model="gpt-image-1", image=..., prompt=...)` with `response_format="b64_json"`
  - Decodes b64 response → returns PNG bytes
- Handle errors: invalid key (`401`), rate limit (`429`), content policy (`400`), timeout
- No retry logic, no queue — one call per request

### 2. Backend: Single render endpoint

**File**: `backend/src/main.py` (modify — add one endpoint)
**File**: `backend/src/config.py` (modify — add `RENDERS_DIR`)

- Add `RENDERS_DIR = USER_DATA_DIR / 'renders'` to config, `mkdir` at startup
- Mount `RENDERS_DIR` as static files at `/renders/` **before** the existing catch-all `/` static mount (order matters — catch-all shadows later mounts)
- `POST /api/edit` — accepts multipart form:
  - `file`: the source jewelry image (JPEG/PNG, max 20MB, validated)
  - `metal`: one of `yellow`, `white`, `rose` (validated — reject others)
- Validates input, converts to bytes, builds prompt from template + metal selection
- Calls `await openai_client.edit_image()` (async, non-blocking)
- Saves result to `~/JewelRender/renders/{timestamp}_{metal}.png`
- **Success response** (200): `{ "image_url": "/renders/{filename}", "prompt": "...", "metal": "..." }`
- **Error response** (4xx/5xx): `{ "error": "Human-readable message", "code": "RATE_LIMIT|CONTENT_POLICY|INVALID_KEY|UPLOAD_ERROR|AI_ERROR" }`
- Request blocks from the caller's perspective (~5–15s) but uses async so the server isn't frozen

### 3. Frontend: MVP page

**File**: `frontend/src/mvp.html` (new — placed in `frontend/src/` so the existing `StaticFiles(html=True)` mount at `/` serves it automatically at `/mvp`. No new route needed.)

Uses the existing stylesheet and design system. Links `css/styles.css`. Reuses the same component patterns from the full UI: `.panel`, `.drop-zone`, `.mode-pill`, `.btn`, `.btn-primary`, `.header`, etc. The page wraps content in a scrollable container with `overflow-y: auto` to override the `overflow: hidden` on `body` (which is designed for the full 3-panel desktop layout).

**Layout** (mobile-first, works on iPhone):
```
┌─────────────────────────────────────────┐
│  JewelRender  ·  Cool Blue Metal Swap   │  ← .header (same as full UI)
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────────────────────────┐    │
│  │                                 │    │
│  │   [Upload / Drop Zone]         │    │  ← .drop-zone (existing class)
│  │   (shows uploaded thumbnail)   │    │
│  │                                 │    │
│  └─────────────────────────────────┘    │
│                                         │
│  Metal Type                             │
│  [Yellow Gold] [White Gold] [Rose Gold] │  ← .mode-pill buttons (existing)
│                                         │
│  [         Render         ]             │  ← .btn.btn-primary (existing)
│                                         │
│  ┌─────────────────────────────────┐    │
│  │                                 │    │
│  │   [Result Image]               │    │  ← .preview-image (existing)
│  │   (appears after render)       │    │
│  │                                 │    │
│  └─────────────────────────────────┘    │
│                                         │
│  [Download]                             │  ← .btn.btn-secondary (existing)
│                                         │
└─────────────────────────────────────────┘
```

**Behavior**:
- Drop zone accepts single image (click or drag) — reuses `.drop-zone` pattern from full UI
- Shows thumbnail of uploaded image inside the drop zone
- Metal type: 3 pill buttons using `.mode-pill` class, one selected at a time (default: Yellow Gold)
- Render button: `.btn-primary`, disabled until image uploaded
- On click: shows loading state (spinner or pulsing text), POST to `/api/edit`, displays result
- Download button: `.btn-secondary`, appears after render, downloads the result image
- Error state: show message if API fails (using `--red` color var)

### 4. Wiring + deps

**File**: `backend/requirements.txt` (modify)
**File**: `backend/.env.example` (modify — add `OPENAI_API_KEY`)

- Add `openai>=1.0` and `python-multipart` to requirements (`Pillow` already present)
- `/renders/` static mount + `mvp.html` routing handled in deliverables 2 and 3 above
- Existing frontend mount at `/` unchanged — full UI still accessible at `/`
- Health endpoint: just return `{ "status": "ok" }` — no ComfyUI check

---

## What We Do NOT Build Today

- ❌ Preset system / preset tabs
- ❌ Generate mode / Video mode
- ❌ Reference Image Library (RIL)
- ❌ Feedback (+/−) system
- ❌ VSCO editor (adjust/crop sliders)
- ❌ Export pipeline
- ❌ Recede / outpainting
- ❌ Batch processing / queue
- ❌ Settings overlay
- ❌ Connection polling
- ❌ Cross-preset pipeline
- ❌ Doc rewrites

All of the above lives untouched in the existing UI. The MVP page is additive — nothing is deleted or modified in the current frontend.

---

## Execution Order

```
Step 1:  Add `openai` to requirements, create .env         (~2 min)
Step 2:  Write openai_client.py                             (~10 min)
Step 3:  Add POST /api/edit endpoint + mount renders        (~10 min)
Step 4:  Build mvp.html (using existing styles.css)         (~15 min)
Step 5:  Test end-to-end with a real Raksha photo           (~5 min)
```

**Total: ~2 hours** (including OpenAI SDK integration, static mount ordering, and end-to-end debugging)

---

## Open Questions (answer now or default)

| Question | Default (if no answer) |
|---|---|
| Karat in prompt — always 14k? | Yes, hardcode 14k |
| Output size — resize to 1170×2532? | No, return OpenAI's native output for MVP |
| Multiple renders — keep history? | Yes, save all to renders/ folder with timestamps |
| Auth on the endpoint? | No — local network only for MVP |

---

## After MVP (if testing goes well)

1. Add karat selector (10k, 14k, 18k)
2. Add background style selector (Cool Blue, White Retail, etc.)
3. Add batch mode (upload multiple photos, render all)
4. Wire results back into the full UI
5. Integrate feedback loop
6. Resume the full migration plan from MIGRATION-OPENAI-API.md
