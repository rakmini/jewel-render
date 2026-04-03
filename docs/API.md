# JewelRender API Reference

## Overview

The JewelRender backend is a FastAPI server that:
- Serves the frontend HTML/CSS/JS
- Manages presets, render queues, and file storage
- Communicates with OpenAI APIs for image generation, editing, video, and AI analysis
- Handles local image adjustments (crop, exposure, etc.) via Pillow

**Base URL**: `http://localhost:5000` (local) or `http://<mac-ip>:5000` (iPhone)

All endpoints return JSON. File uploads use `multipart/form-data`.

---

## Health & Connection

### GET /health

Check server status.

**Response**:
```json
{
  "status": "ok",
  "service": "JewelRender API",
  "version": "0.2.0",
  "ai_engine": "openai",
  "models": {
    "brain": "gpt-4.1-mini",
    "image": "gpt-image-1",
    "video": "sora-2"
  },
  "api_key_configured": true,
  "user_data_dir": "/Users/jonathan/JewelRender"
}
```

### GET /api/health

Detailed health check with OpenAI connection test.

**Response**:
```json
{
  "status": "ok",
  "openai": {
    "connected": true,
    "brain_model": "gpt-4.1-mini",
    "image_model": "gpt-image-1",
    "video_model": "sora-2",
    "brain_available": true,
    "image_available": true
  },
  "storage": {
    "user_dir": "/Users/jonathan/JewelRender"
  }
}
```

---

## Presets

### GET /api/presets

List all presets.

**Response**:
```json
{
  "presets": [
    {
      "id": "cool-blue",
      "name": "Cool Blue",
      "style": "baby-blue background, softly lit",
      "mode": "generate",
      "defaults": {
        "temperature": 0,
        "saturation": 0,
        "contrast": 0,
        "sharpness": 0,
        "grain": 0
      },
      "library_count": 5,
      "renders_count": 12
    }
  ]
}
```

### POST /api/presets

Create new preset.

**Request Body**:
```json
{
  "name": "Soft Pink",
  "style": "soft pink background, romantic lighting",
  "template": "cool-blue"
}
```

### PATCH /api/presets/{preset_id}

Update preset (name, style, defaults, etc.).

### DELETE /api/presets/{preset_id}

Delete preset (and all associated renders, RIL, feedback).

### POST /api/presets/{preset_id}/duplicate

Duplicate a preset with new name.

---

## Rendering

### POST /api/render

Queue render job. Routes to the appropriate OpenAI API based on mode.

**Request Body (Generate mode)**:
```json
{
  "preset_id": "cool-blue",
  "mode": "generate",
  "params": {
    "prompt": "beautiful emerald ring on baby blue background, studio lighting",
    "reference_images": ["ref1.jpg", "ref2.jpg"],
    "temperature": 5,
    "saturation": 10
  }
}
```
*Calls: OpenAI `/v1/images/generations` (GPT Image 1.5)*

**Request Body (Edit mode)**:
```json
{
  "preset_id": "white-retail",
  "mode": "edit",
  "params": {
    "prompt": "change background to clean white, keep jewelry identical",
    "elements_to_change": ["background"]
  },
  "input_image": "base64-encoded-image",
  "mask": "base64-encoded-mask"
}
```
*Calls: OpenAI `/v1/images/edits` (GPT Image 1.5)*

**Request Body (Video mode)**:
```json
{
  "preset_id": "cool-blue",
  "mode": "video",
  "params": {
    "front_image": "base64",
    "rotation_direction": "clockwise",
    "video_length_seconds": 5
  }
}
```
*Calls: Sora 2 `/v1/videos`*

**Response**:
```json
{
  "job_id": "job-20260320-001",
  "preset_id": "cool-blue",
  "status": "queued"
}
```

### GET /api/render/{job_id}

Check render progress.

### POST /api/render/batch

Queue multiple renders at once.

### GET /api/render/queue

Get current render queue.

---

## AI Brain (GPT-4.1-mini Vision)

### POST /api/analyze

Analyze a jewelry image. Runs automatically on every image entry, but can also be called manually.

**Request Body** (multipart/form-data):
- `file`: JPEG/PNG image

**Response**:
```json
{
  "metal_type": "white gold",
  "metal_karat": "14k",
  "gemstone": "diamond",
  "gemstone_color": "clear",
  "product_type": "ring",
  "setting_style": "prong",
  "quality_score": 0.87,
  "suggested_preset": "cool-blue",
  "suggested_ril_folders": ["rings", "diamond", "white-gold", "prong-setting"],
  "description": "14k white gold diamond solitaire ring with prong setting"
}
```

### POST /api/analyze/quality

Assess whether a render matches the target preset style.

**Request Body**:
```json
{
  "image": "base64-encoded-image",
  "preset_id": "cool-blue"
}
```

**Response**:
```json
{
  "matches_style": true,
  "confidence": 0.92,
  "issues": [],
  "suggestions": ["slightly warmer temperature would match Cool Blue better"],
  "overall_quality": 0.88
}
```

### POST /api/recommend

Get parameter recommendations based on past successes.

**Request Body**:
```json
{
  "preset_id": "cool-blue",
  "product_description": "emerald cut diamond engagement ring"
}
```

**Response**:
```json
{
  "prompt": "emerald cut diamond engagement ring on baby blue background, soft studio lighting, high detail",
  "temperature": -5,
  "saturation": 8,
  "contrast": 3,
  "sharpness": 10,
  "grain": 0,
  "reasoning": "Based on 12 approved Cool Blue ring renders, slightly cool temperature with moderate saturation works best"
}
```

---

## Images

### GET /api/image/{preset_id}/{image_id}

Retrieve rendered image.

**Response**: Binary JPEG image (1170x2532, quality 95).

### POST /api/image/{preset_id}/{image_id}/edit

Apply editor adjustments (processed locally via Pillow — no API call).

### POST /api/image/{preset_id}/{image_id}/crop

Apply crop (processed locally via Pillow).

### POST /api/image/{preset_id}/{image_id}/feedback

Submit +/- feedback on an image.

---

## Reference Image Library (RIL)

### GET /api/presets/{preset_id}/ril

List all images in preset's RIL (includes AI brain analysis per image).

### POST /api/presets/{preset_id}/ril/upload

Add manual reference image to RIL. AI brain automatically analyzes on entry.

### POST /api/presets/{preset_id}/ril/add-render

Add existing render to RIL (export auto-deposit).

### DELETE /api/presets/{preset_id}/ril/{image_id}

Remove image from RIL.

---

## Recede (AI Outpainting)

### POST /api/image/{preset_id}/{image_id}/recede

Regenerate image with jewelry at smaller scale (extend background).

*Uses OpenAI Images Edit API with outpainting mask.*

**Request Body**:
```json
{
  "recede_percent": 25,
  "reference_images": ["ref-001", "ref-002"]
}
```

---

## Export

### POST /api/export

Export rendered image(s) to filesystem. Auto-deposits to RIL if toggle ON.

### POST /api/export/configure

Set default export folder.

---

## Settings

### GET /api/settings

Get current settings (includes OpenAI model configuration).

### PATCH /api/settings

Update settings.

### POST /api/settings/test-connection

Test OpenAI API connection.

**Response (Success)**:
```json
{
  "connected": true,
  "brain_model": "gpt-4.1-mini",
  "image_model": "gpt-image-1",
  "video_model": "sora-2",
  "brain_available": true,
  "image_available": true
}
```

**Response (Failure)**:
```json
{
  "connected": false,
  "error": "Invalid API key. Get one at platform.openai.com"
}
```

---

## Error Responses

All errors return JSON with appropriate HTTP status:

```json
{
  "error": "Preset not found",
  "code": "PRESET_NOT_FOUND",
  "status": 404
}
```

**Common Status Codes**:
- `200` — Success
- `201` — Created
- `400` — Bad request (invalid params)
- `404` — Not found (preset, image, etc.)
- `401` — OpenAI API key missing or invalid
- `429` — OpenAI rate limit hit
- `500` — Server error

---

## WebSocket (Real-Time Progress)

For real-time progress updates, connect WebSocket:

```javascript
const ws = new WebSocket('ws://localhost:5000/ws/render');

ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  // { job_id, status, progress, current_step }
};
```
