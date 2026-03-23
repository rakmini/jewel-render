# Migration Plan: ComfyUI → OpenAI API

**Date**: 2026-03-23
**Status**: Draft
**Goal**: Replace ComfyUI backend with OpenAI Images API as the primary AI engine.

---

## Why

- ComfyUI requires a local GPU, model downloads, workflow maintenance, and Python node dependencies
- OpenAI's image models (gpt-image-1 / DALL·E) handle generation + editing via a single API
- Eliminates the Mac Mini M4 as a hard dependency — app can run from anywhere
- Simpler backend: no ComfyUI process management, no checkpoint loading, no workflow JSON

## What Changes

| Concern | Before (ComfyUI) | After (OpenAI API) |
|---|---|---|
| Image generation | Local SDXL via ComfyUI workflow | `POST /v1/images/generations` |
| Image editing | Local inpainting workflow | `POST /v1/images/edits` (mask + prompt) |
| Outpainting (Recede) | ComfyUI outpaint node | OpenAI edit with extended canvas + mask |
| 360 Video | SV3D_p / WAN 2.1 local models | **Deferred** — no OpenAI video API yet |
| Settings: ComfyUI host/port | Required | Removed — replaced with API key config |
| Cost model | Free after hardware | Pay-per-image via OpenAI API billing |

## What Stays the Same

- Frontend UI (presets, queue, editor, RIL, feedback, export)
- Preset system (style axis × mode axis)
- Cross-preset pipeline concept
- Local file storage for presets, renders, RIL, exports
- FastAPI backend serving frontend + managing data
- VSCO-style editor (adjust/crop — these are client-side image transforms)

---

## Deliverables

### Phase 1 — Backend: Strip ComfyUI, Add OpenAI Client

- [ ] **1.1** Remove all ComfyUI references from `config.py`
  - Remove `COMFYUI_HOST`, `COMFYUI_PORT`, `COMFYUI_URL`, `COMFYUI_TIMEOUT`
  - Remove `DEFAULT_CHECKPOINT`, `CHECKPOINT`
  - Add `OPENAI_API_KEY` (from env var or `.env`)
  - Add `OPENAI_MODEL` default (e.g. `gpt-image-1`)
  - Add `OPENAI_IMAGE_SIZE` default (e.g. `1024x1536` — closest to portrait)
  - Add `OPENAI_IMAGE_QUALITY` setting (`high` / `standard`)

- [ ] **1.2** Create `backend/src/openai_client.py` — thin wrapper around OpenAI Images API
  - `generate_image(prompt, size, quality, n)` → calls `/v1/images/generations`
  - `edit_image(image_bytes, mask_bytes, prompt, size)` → calls `/v1/images/edits`
  - Handle API errors, rate limits, retries with backoff
  - Return image bytes (or b64) + metadata
  - Accept reference images as additional context in the prompt (describe style from preset)

- [ ] **1.3** Rewrite render endpoints in `main.py`
  - `POST /api/render` — route to `generate_image()` or `edit_image()` based on `mode`
  - For **generate** mode: build prompt from preset style + user prompt + reference descriptions
  - For **edit** mode: send source image + mask + preset-aware prompt
  - Save output to preset's `renders/` directory
  - Return image URL + metadata
  - Remove `POST /api/comfyui/test` endpoint

- [ ] **1.4** Rewrite render queue/progress system
  - Current: placeholder job IDs with no real processing
  - New: actual async job processing (background task or queue)
  - OpenAI calls are ~5–15s, not minutes — simpler progress model
  - Option A: `asyncio.create_task` + in-memory job store
  - Option B: synchronous per-request (simpler, fine for single user)
  - `GET /api/render/{job_id}` returns real status

- [ ] **1.5** Implement Recede via OpenAI edit
  - Take source image, extend canvas by recede %, fill extended area with transparent mask
  - Send to OpenAI edit endpoint with preset-style prompt
  - Save result back to renders

- [ ] **1.6** Update settings endpoints
  - Remove ComfyUI host/port/checkpoint from settings schema
  - Add OpenAI API key field (stored locally, never sent to frontend)
  - Add model selection (if multiple OpenAI models available)
  - Add `POST /api/openai/test` — validates API key with a lightweight call
  - Update `GET /api/settings` and `PUT /api/settings` response shapes

- [ ] **1.7** Update `requirements.txt`
  - Add `openai>=1.0` (official Python SDK)
  - Remove any ComfyUI-specific dependencies if present

### Phase 2 — Frontend: Update UI for OpenAI Backend

- [ ] **2.1** Update Settings overlay
  - Remove ComfyUI host/port/checkpoint fields
  - Add OpenAI API key input (password-masked)
  - Add model selector dropdown
  - Add image quality selector (high / standard)
  - "Test Connection" button → calls `POST /api/openai/test`

- [ ] **2.2** Update render flow in `app.js`
  - Adapt `handleRenderAll()` for new response shape
  - Handle OpenAI-specific errors (rate limit, content policy, invalid key)
  - Show meaningful error messages to user

- [ ] **2.3** Update prompt UI for Generate mode
  - Prompt textarea already exists — no structural change
  - Consider adding a "style hint" preview that shows the combined prompt (preset style + user prompt)
  - Reference images: send as descriptions or filenames (OpenAI edit accepts image input)

- [ ] **2.4** Update connection status indicator
  - Currently checks `/api/health` which reports ComfyUI status
  - Change to show: API key valid + backend reachable
  - Health endpoint should return `openai_status` instead of `comfyui_url`

### Phase 3 — Docs & Config Cleanup

- [ ] **3.1** Rewrite `docs/ARCHITECTURE.md`
  - Replace ComfyUI sections with OpenAI API architecture
  - Update system diagram
  - Remove Mac Mini M4 as hard requirement
  - Document cost model (pay-per-image)

- [ ] **3.2** Rewrite `docs/API.md`
  - Remove ComfyUI workflow examples
  - Update render endpoint request/response schemas
  - Update settings schemas
  - Remove WebSocket section (not needed for short API calls)

- [ ] **3.3** Update `docs/SETUP.md`
  - Setup = get OpenAI API key, set env var, `pip install`, run
  - Remove ComfyUI installation/model download steps

- [ ] **3.4** Update `README.md`
  - New tech stack description
  - Simpler quick start (no ComfyUI)
  - Cost note (OpenAI API billing)

- [ ] **3.5** Update `config/settings.json` and `config/presets.json`
  - Remove ComfyUI fields
  - Add OpenAI defaults

- [ ] **3.6** Create `.env.example` with `OPENAI_API_KEY=sk-...`

### Phase 4 — 360 Video (Deferred)

- [ ] **4.1** Research OpenAI video API availability (Sora API, if/when released)
- [ ] **4.2** Evaluate alternatives: Runway API, Stability Video, Kling API
- [ ] **4.3** Design pluggable video provider interface so we can swap in later
- [ ] **4.4** Keep Video mode in UI but show "Coming soon" or disable render button

---

## Output Format Considerations

- OpenAI generates at fixed sizes (e.g. `1024x1024`, `1024x1536`, `1536x1024`)
- JewelRender target is `1170×2532` (iPhone portrait)
- **Strategy**: Generate at `1024x1536` (closest portrait), then resize/crop to `1170×2532` server-side
- Use Pillow for the resize step in the backend
- This is lossless for the user — they always get the target dimensions

## Cost Estimation

| Operation | OpenAI Price (approx) | JewelRender Usage |
|---|---|---|
| Image generation (high quality) | ~$0.04–0.08/image | Per render |
| Image edit | ~$0.04–0.08/image | Per edit/recede |
| Batch of 50 renders | ~$2–4 | Typical session |

Budget-conscious users can use `standard` quality at lower cost.

## Migration Order

```
Phase 1 (backend) → Phase 2 (frontend) → Phase 3 (docs) → Phase 4 (video, later)
```

Phases 1 and 2 can be worked in parallel once 1.1–1.2 are done (API client exists).
Phase 3 can happen anytime after Phase 1.
Phase 4 is independent and deferred.

---

## Open Questions

1. **Should we support multiple AI providers?** (e.g. OpenAI now, Stability later) — if yes, build a provider interface in 1.2
2. **Image size**: Is `1024x1536` acceptable as the generation size before resize, or do we need higher?
3. **Reference images in prompts**: OpenAI edit accepts one image — for multi-reference, we need to composite or describe them in text. Strategy TBD.
4. **API key storage**: Local `.env` file only, or let user paste in Settings UI and persist to `settings.json`?
5. **Rate limits**: OpenAI has per-minute limits — do we need a queue/throttle for batch renders?
