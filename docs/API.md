# JewelRender API Reference

## Overview

The JewelRender backend is a FastAPI server that:
- Serves the frontend HTML/CSS/JS
- Manages presets, render queues, and file storage
- Communicates with ComfyUI to process renders
- Handles image editing and video generation

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
  "comfyui": {
    "connected": true,
    "host": "127.0.0.1",
    "port": 8188
  },
  "storage": {
    "user_dir": "/Users/jonathan/JewelRender",
    "free_space_gb": 250
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
    },
    {
      "id": "white-retail",
      "name": "White Retail",
      ...
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
  "template": "cool-blue"  // optional: copy defaults from existing preset
}
```

**Response**:
```json
{
  "id": "soft-pink",
  "name": "Soft Pink",
  "created": true
}
```

### PATCH /api/presets/{preset_id}

Update preset (name, style, defaults, etc.).

**Request Body**:
```json
{
  "name": "Cool Blue Updated",
  "defaults": {
    "temperature": 5,
    "saturation": 10
  }
}
```

**Response**:
```json
{
  "id": "cool-blue",
  "updated": true
}
```

### DELETE /api/presets/{preset_id}

Delete preset (and all associated renders, RIL, feedback).

**Response**:
```json
{
  "id": "cool-blue",
  "deleted": true,
  "renders_removed": 12,
  "library_images_removed": 5
}
```

### POST /api/presets/{preset_id}/duplicate

Duplicate a preset with new name.

**Request Body**:
```json
{
  "new_name": "Cool Blue v2"
}
```

**Response**:
```json
{
  "source_id": "cool-blue",
  "new_id": "cool-blue-v2",
  "new_name": "Cool Blue v2",
  "duplicated": true
}
```

---

## Rendering

### POST /api/render

Queue render job (works for all modes: Edit, Generate, 360 Video).

**Request Body**:
```json
{
  "preset_id": "cool-blue",
  "mode": "generate",  // "edit", "generate", or "video"
  "params": {
    "prompt": "beautiful emerald ring on white background, studio lighting",
    "reference_images": ["ref1.jpg", "ref2.jpg"],
    "temperature": 5,
    "saturation": 10
  },
  "input_image": "base64 or file upload"  // optional, required for edit mode
}
```

**Response**:
```json
{
  "job_id": "job-20260320-001",
  "preset_id": "cool-blue",
  "status": "queued",
  "queue_position": 3,
  "estimated_wait": 120
}
```

### GET /api/render/{job_id}

Check render progress.

**Response (Processing)**:
```json
{
  "job_id": "job-20260320-001",
  "status": "processing",
  "progress": 45,
  "elapsed": 87,
  "estimated_remaining": 120,
  "current_step": "generating image"
}
```

**Response (Complete)**:
```json
{
  "job_id": "job-20260320-001",
  "status": "complete",
  "progress": 100,
  "elapsed": 215,
  "output": {
    "image_url": "/api/image/cool-blue/job-20260320-001.jpg",
    "width": 1170,
    "height": 2532,
    "file_size": 245000
  }
}
```

### POST /api/render/batch

Queue multiple renders at once.

**Request Body**:
```json
{
  "preset_id": "cool-blue",
  "mode": "generate",
  "jobs": [
    { "prompt": "diamond ring, studio lighting" },
    { "prompt": "emerald ring, warm lighting" },
    { "prompt": "sapphire ring, cool lighting" }
  ]
}
```

**Response**:
```json
{
  "batch_id": "batch-20260320-001",
  "jobs": [
    { "job_id": "job-20260320-001", "status": "queued" },
    { "job_id": "job-20260320-002", "status": "queued" },
    { "job_id": "job-20260320-003", "status": "queued" }
  ],
  "total": 3
}
```

### GET /api/render/queue

Get current render queue.

**Response**:
```json
{
  "queue": [
    {
      "position": 1,
      "job_id": "job-20260320-001",
      "preset": "cool-blue",
      "mode": "generate",
      "status": "processing"
    },
    {
      "position": 2,
      "job_id": "job-20260320-002",
      "preset": "white-retail",
      "mode": "edit",
      "status": "queued"
    }
  ],
  "total": 2
}
```

---

## Images

### GET /api/image/{preset_id}/{image_id}

Retrieve rendered image.

**Response**: Binary JPEG image (1170×2532, quality 95).

### POST /api/image/{preset_id}/{image_id}/edit

Apply editor adjustments (Adjust tab controls) to an image.

**Request Body**:
```json
{
  "adjustments": {
    "exposure": 10,
    "contrast": -5,
    "highlights": 15,
    "shadows": -10,
    "temperature": 8,
    "saturation": 12,
    "sharpness": 5
  }
}
```

**Response**:
```json
{
  "image_id": "job-20260320-001",
  "adjusted": true,
  "preview_url": "/api/image/cool-blue/job-20260320-001-adjusted.jpg"
}
```

### POST /api/image/{preset_id}/{image_id}/crop

Apply crop (Crop tab controls) to an image.

**Request Body**:
```json
{
  "crop": {
    "aspect_ratio": "4:5",  // or "free", "1:1", "16:9", etc.
    "x": 100,
    "y": 150,
    "width": 900,
    "height": 1125
  },
  "rotation": 0,
  "flip_h": false,
  "flip_v": false
}
```

**Response**:
```json
{
  "image_id": "job-20260320-001",
  "cropped": true,
  "preview_url": "/api/image/cool-blue/job-20260320-001-cropped.jpg"
}
```

### POST /api/image/{preset_id}/{image_id}/feedback

Submit +/− feedback on an image.

**Request Body**:
```json
{
  "feedback": "approve"  // or "reject"
}
```

**Response**:
```json
{
  "image_id": "job-20260320-001",
  "feedback": "approve",
  "auto_added_to_ril": true
}
```

---

## Reference Image Library (RIL)

### GET /api/presets/{preset_id}/ril

List all images in preset's RIL.

**Response**:
```json
{
  "preset_id": "cool-blue",
  "images": [
    {
      "id": "ref-001",
      "filename": "example1.jpg",
      "added_date": "2026-03-20",
      "source": "manual",  // "manual", "approved", or "export"
      "url": "/api/ril/cool-blue/ref-001.jpg"
    },
    {
      "id": "ref-002",
      "filename": "example2.jpg",
      "added_date": "2026-03-19",
      "source": "export"
    }
  ],
  "total": 2
}
```

### POST /api/presets/{preset_id}/ril/upload

Add manual reference image to RIL.

**Request Body** (multipart/form-data):
- `file`: JPEG/PNG image
- `source`: "manual" (optional, defaults to manual)

**Response**:
```json
{
  "preset_id": "cool-blue",
  "image_id": "ref-003",
  "filename": "example3.jpg",
  "added": true
}
```

### POST /api/presets/{preset_id}/ril/add-render

Add existing render to RIL (export auto-deposit).

**Request Body**:
```json
{
  "render_job_id": "job-20260320-001",
  "source": "export"  // or "approved"
}
```

**Response**:
```json
{
  "preset_id": "cool-blue",
  "image_id": "ref-004",
  "render_id": "job-20260320-001",
  "added": true
}
```

### DELETE /api/presets/{preset_id}/ril/{image_id}

Remove image from RIL.

**Response**:
```json
{
  "preset_id": "cool-blue",
  "image_id": "ref-001",
  "deleted": true
}
```

---

## Recede (AI Outpainting)

### POST /api/image/{preset_id}/{image_id}/recede

Regenerate image with jewelry at smaller scale (extend background).

**Request Body**:
```json
{
  "recede_percent": 25,  // 0-50
  "reference_images": ["ref-001", "ref-002"]  // optional, preset's RIL
}
```

**Response**:
```json
{
  "source_image": "job-20260320-001",
  "recede_job_id": "job-20260320-001-recede-25",
  "recede_percent": 25,
  "queued": true
}
```

Then monitor with: `GET /api/render/job-20260320-001-recede-25`

---

## Export

### POST /api/export

Export rendered image(s) to filesystem.

**Request Body**:
```json
{
  "preset_id": "cool-blue",
  "image_ids": ["job-20260320-001", "job-20260320-002"],
  "folder": "/Users/jonathan/Pictures/exports"  // optional, uses default if not specified
}
```

**Response**:
```json
{
  "exported": 2,
  "folder": "/Users/jonathan/Pictures/exports",
  "files": [
    "cool-blue_20260320_001.jpg",
    "cool-blue_20260320_002.jpg"
  ],
  "auto_added_to_ril": 2  // if toggle ON
}
```

### POST /api/export/configure

Set default export folder.

**Request Body**:
```json
{
  "folder": "/Users/jonathan/Desktop/Renders"
}
```

**Response**:
```json
{
  "folder": "/Users/jonathan/Desktop/Renders",
  "saved": true
}
```

---

## Settings

### GET /api/settings

Get current settings.

**Response**:
```json
{
  "comfyui": {
    "host": "127.0.0.1",
    "port": 8188,
    "checkpoint": "sd_xl_base_1.0.safetensors"
  },
  "output": {
    "width": 1170,
    "height": 2532,
    "jpeg_quality": 95
  },
  "video": {
    "format": "mp4",
    "model": "sv3d_p"
  },
  "feedback": {
    "auto_add_approved_to_ril": true,
    "auto_deposit_exports_to_ril": true,
    "parameter_logging": true
  },
  "export": {
    "folder": "/Users/jonathan/JewelRender/exports"
  }
}
```

### PATCH /api/settings

Update settings.

**Request Body**:
```json
{
  "comfyui": {
    "host": "127.0.0.1",
    "port": 8188
  },
  "feedback": {
    "auto_add_approved_to_ril": false
  }
}
```

**Response**:
```json
{
  "updated": true,
  "settings": { ... }
}
```

### POST /api/settings/test-connection

Test ComfyUI connection.

**Response (Success)**:
```json
{
  "connected": true,
  "host": "127.0.0.1",
  "port": 8188,
  "models": ["sd_xl_base_1.0", "sd_xl_refiner_1.0"],
  "latency_ms": 12
}
```

**Response (Failure)**:
```json
{
  "connected": false,
  "error": "Connection refused",
  "host": "127.0.0.1",
  "port": 8188
}
```

---

## Video Generation (360 Mode)

### POST /api/render/video

Queue 360 video render.

**Request Body**:
```json
{
  "preset_id": "cool-blue",
  "mode": "video",
  "params": {
    "front_image": "base64 or file",
    "side_image": "base64 or file",
    "three_quarter_image": "base64 or file",
    "rotation_direction": "clockwise",  // or "counter-clockwise"
    "rotation_speed": "normal",  // "slow", "normal", "fast"
    "video_length_seconds": 5,
    "reference_videos": ["ref-video-001", "ref-video-002"]  // optional
  }
}
```

**Response**:
```json
{
  "job_id": "job-20260320-video-001",
  "preset_id": "cool-blue",
  "status": "queued",
  "estimated_wait": 180
}
```

### GET /api/render/video/{job_id}

Check video render progress.

**Response (Complete)**:
```json
{
  "job_id": "job-20260320-video-001",
  "status": "complete",
  "video_url": "/api/video/cool-blue/job-20260320-video-001.mp4",
  "duration_seconds": 5,
  "file_size": 8500000
}
```

### GET /api/video/{preset_id}/{video_id}

Download rendered video.

**Response**: Binary MP4 file.

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
- `500` — Server error (ComfyUI connection, etc.)

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

---

## ComfyUI Workflow Examples

### Image Generation Workflow

```json
{
  "1": {
    "class_type": "CheckpointLoaderSimple",
    "inputs": {
      "ckpt_name": "sd_xl_base_1.0.safetensors"
    }
  },
  "2": {
    "class_type": "CLIPTextEncode",
    "inputs": {
      "text": "beautiful emerald ring on white background, studio lighting",
      "clip": ["1", 0]
    }
  },
  "3": {
    "class_type": "CLIPTextEncode",
    "inputs": {
      "text": "ugly, distorted, blurry",
      "clip": ["1", 0]
    }
  },
  "4": {
    "class_type": "KSampler",
    "inputs": {
      "seed": 12345,
      "steps": 20,
      "cfg": 7.5,
      "sampler_name": "euler",
      "scheduler": "normal",
      "denoise": 1.0,
      "model": ["1", 0],
      "positive": ["2", 0],
      "negative": ["3", 0]
    }
  },
  "5": {
    "class_type": "VAEDecode",
    "inputs": {
      "samples": ["4", 0],
      "vae": ["1", 0]
    }
  },
  "6": {
    "class_type": "SaveImage",
    "inputs": {
      "filename_prefix": "jewelrender",
      "images": ["5", 0]
    }
  }
}
```

See ComfyUI documentation for additional workflows (inpainting, outpainting, video, etc.).
