"""JewelRender API Server

A batch jewelry rendering application with ComfyUI backend.
Frontend: HTML/CSS/JS single-page app
Backend: FastAPI Python server
GPU: ComfyUI on Mac Mini M4
Storage: Local filesystem
"""

import json
import logging
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import uvicorn

from config import (
    API_HOST, API_PORT, API_DEBUG, CORS_ORIGINS,
    COMFYUI_URL, USER_DATA_DIR, PRESETS_DIR, EXPORTS_DIR,
    LOG_LEVEL, DEFAULT_PRESETS,
)

# ============================================================================
# Logging Setup
# ============================================================================

logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# FastAPI App
# ============================================================================

app = FastAPI(
    title='JewelRender API',
    description='Batch jewelry rendering with ComfyUI backend',
    version='0.1.0',
    docs_url='/api/docs',
    redoc_url='/api/redoc',
    openapi_url='/api/openapi.json',
)

# ============================================================================
# CORS Middleware
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# ============================================================================
# Preset Helpers
# ============================================================================

def _preset_dir(preset_id: str) -> Path:
    return PRESETS_DIR / preset_id

def _preset_config_path(preset_id: str) -> Path:
    return _preset_dir(preset_id) / 'config.json'

def _load_preset(preset_id: str) -> dict:
    path = _preset_config_path(preset_id)
    if not path.exists():
        raise HTTPException(status_code=404, detail=f'Preset not found: {preset_id}')
    return json.loads(path.read_text())

def _save_preset(preset: dict):
    d = _preset_dir(preset['id'])
    d.mkdir(parents=True, exist_ok=True)
    (d / 'library').mkdir(exist_ok=True)
    (d / 'renders').mkdir(exist_ok=True)
    _preset_config_path(preset['id']).write_text(json.dumps(preset, indent=2))

def _list_all_presets() -> list:
    presets = []
    if not PRESETS_DIR.exists():
        return presets
    for p in sorted(PRESETS_DIR.iterdir()):
        cfg = p / 'config.json'
        if cfg.exists():
            presets.append(json.loads(cfg.read_text()))
    return presets

def _init_default_presets():
    """Create default presets if none exist."""
    if _list_all_presets():
        return
    for p in DEFAULT_PRESETS:
        preset = {
            'id': p['id'],
            'name': p['name'],
            'style': p['style'],
            'defaults': {'temperature': 0, 'saturation': 0, 'contrast': 0, 'sharpness': 0, 'grain': 0},
            'created': datetime.now().isoformat(),
        }
        _save_preset(preset)
    logger.info(f'Initialized {len(DEFAULT_PRESETS)} default presets')

# ============================================================================
# Health Endpoints
# ============================================================================

@app.get('/api/health')
async def health_check():
    return {
        'status': 'ok',
        'service': 'JewelRender API',
        'version': '0.1.0',
        'comfyui_url': COMFYUI_URL,
        'user_data_dir': str(USER_DATA_DIR),
    }

# ============================================================================
# Preset CRUD
# ============================================================================

@app.get('/api/presets')
async def list_presets():
    presets = _list_all_presets()
    for p in presets:
        lib_dir = _preset_dir(p['id']) / 'library'
        renders_dir = _preset_dir(p['id']) / 'renders'
        p['library_count'] = len(list(lib_dir.glob('*.jpg'))) + len(list(lib_dir.glob('*.png'))) if lib_dir.exists() else 0
        p['renders_count'] = len(list(renders_dir.glob('*.jpg'))) + len(list(renders_dir.glob('*.png'))) if renders_dir.exists() else 0
    return {'presets': presets, 'total': len(presets)}


@app.get('/api/presets/{preset_id}')
async def get_preset(preset_id: str):
    return _load_preset(preset_id)


@app.post('/api/presets')
async def create_preset(data: dict):
    preset_id = data.get('id') or data.get('name', '').lower().replace(' ', '-')
    if _preset_config_path(preset_id).exists():
        raise HTTPException(status_code=409, detail='Preset already exists')
    preset = {
        'id': preset_id,
        'name': data.get('name', preset_id),
        'style': data.get('style', ''),
        'defaults': data.get('defaults', {'temperature': 0, 'saturation': 0, 'contrast': 0, 'sharpness': 0, 'grain': 0}),
        'created': datetime.now().isoformat(),
    }
    _save_preset(preset)
    return preset


@app.put('/api/presets/{preset_id}')
async def update_preset(preset_id: str, data: dict):
    preset = _load_preset(preset_id)
    if 'name' in data:
        preset['name'] = data['name']
    if 'style' in data:
        preset['style'] = data['style']
    if 'defaults' in data:
        preset['defaults'].update(data['defaults'])
    _save_preset(preset)
    return preset


@app.delete('/api/presets/{preset_id}')
async def delete_preset(preset_id: str):
    d = _preset_dir(preset_id)
    if not d.exists():
        raise HTTPException(status_code=404, detail='Preset not found')
    shutil.rmtree(d)
    return {'deleted': preset_id}


@app.post('/api/presets/{preset_id}/duplicate')
async def duplicate_preset(preset_id: str):
    source = _load_preset(preset_id)
    new_id = f"{preset_id}-copy-{uuid.uuid4().hex[:6]}"
    new_preset = {**source, 'id': new_id, 'name': f"{source['name']} Copy", 'created': datetime.now().isoformat()}
    _save_preset(new_preset)
    # Copy library files
    src_lib = _preset_dir(preset_id) / 'library'
    dst_lib = _preset_dir(new_id) / 'library'
    if src_lib.exists():
        for f in src_lib.iterdir():
            shutil.copy2(f, dst_lib / f.name)
    return new_preset

# ============================================================================
# Reference Image Library (RIL)
# ============================================================================

@app.get('/api/presets/{preset_id}/library')
async def list_ril(preset_id: str):
    lib_dir = _preset_dir(preset_id) / 'library'
    if not lib_dir.exists():
        return {'images': [], 'count': 0}
    images = []
    for f in sorted(lib_dir.iterdir()):
        if f.suffix.lower() in ('.jpg', '.jpeg', '.png', '.webp'):
            images.append({
                'id': f.stem,
                'filename': f.name,
                'url': f'/api/presets/{preset_id}/library/{f.name}',
                'source': 'manual',
            })
    return {'images': images, 'count': len(images)}


@app.post('/api/presets/{preset_id}/library')
async def add_to_ril(preset_id: str, file: UploadFile = File(...)):
    lib_dir = _preset_dir(preset_id) / 'library'
    lib_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex[:8]}_{file.filename}"
    filepath = lib_dir / filename
    content = await file.read()
    filepath.write_bytes(content)
    return {
        'id': filepath.stem,
        'filename': filename,
        'url': f'/api/presets/{preset_id}/library/{filename}',
        'source': 'manual',
    }


@app.delete('/api/presets/{preset_id}/library/{image_id}')
async def remove_from_ril(preset_id: str, image_id: str):
    lib_dir = _preset_dir(preset_id) / 'library'
    for f in lib_dir.iterdir():
        if f.stem == image_id:
            f.unlink()
            return {'deleted': image_id}
    raise HTTPException(status_code=404, detail='Image not found')

# ============================================================================
# Image Upload
# ============================================================================

@app.post('/api/presets/{preset_id}/images')
async def upload_image(preset_id: str, file: UploadFile = File(...), target: str = Form('queue')):
    if target == 'library':
        return await add_to_ril(preset_id, file)
    renders_dir = _preset_dir(preset_id) / 'renders'
    renders_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex[:8]}_{file.filename}"
    filepath = renders_dir / filename
    content = await file.read()
    filepath.write_bytes(content)
    return {
        'id': filepath.stem,
        'filename': filename,
        'url': f'/api/presets/{preset_id}/renders/{filename}',
    }

# ============================================================================
# Feedback
# ============================================================================

@app.post('/api/presets/{preset_id}/images/{image_id}/feedback')
async def submit_feedback(preset_id: str, image_id: str, data: dict):
    feedback_path = _preset_dir(preset_id) / 'feedback.json'
    feedback_log = {}
    if feedback_path.exists():
        feedback_log = json.loads(feedback_path.read_text())
    feedback_log[image_id] = {
        'feedback': data.get('feedback'),
        'timestamp': datetime.now().isoformat(),
    }
    feedback_path.write_text(json.dumps(feedback_log, indent=2))
    return {'status': 'ok', 'image_id': image_id, 'feedback': data.get('feedback')}

# ============================================================================
# Export
# ============================================================================

@app.post('/api/presets/{preset_id}/export')
async def export_images(preset_id: str, data: dict):
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    image_ids = data.get('image_ids', [])
    exported = []
    renders_dir = _preset_dir(preset_id) / 'renders'
    for img_id in image_ids:
        # Find matching file
        if renders_dir.exists():
            for f in renders_dir.iterdir():
                if f.stem == img_id:
                    dst = EXPORTS_DIR / f.name
                    shutil.copy2(f, dst)
                    exported.append(f.name)
                    break
    return {'exported': exported, 'count': len(exported), 'export_dir': str(EXPORTS_DIR)}

# ============================================================================
# Settings
# ============================================================================

_settings_path = USER_DATA_DIR / 'settings.json'

@app.get('/api/settings')
async def get_settings():
    if _settings_path.exists():
        return json.loads(_settings_path.read_text())
    return {
        'comfyui': {'host': '127.0.0.1', 'port': 8188, 'checkpoint': 'sd_xl_base_1.0.safetensors'},
        'output': {'width': 1170, 'height': 2532, 'jpeg_quality': 95},
        'video': {'model': 'sv3d_p'},
        'feedback': {'auto_add_approved_to_ril': True, 'auto_deposit_exports_to_ril': True, 'parameter_logging': True},
        'export_folder': str(EXPORTS_DIR),
    }


@app.put('/api/settings')
async def update_settings(data: dict):
    current = await get_settings()
    for key, val in data.items():
        if isinstance(val, dict) and key in current and isinstance(current[key], dict):
            current[key].update(val)
        else:
            current[key] = val
    _settings_path.parent.mkdir(parents=True, exist_ok=True)
    _settings_path.write_text(json.dumps(current, indent=2))
    return current

# ============================================================================
# ComfyUI Test
# ============================================================================

@app.post('/api/comfyui/test')
async def test_comfyui(data: dict):
    import httpx
    host = data.get('host', '127.0.0.1')
    port = data.get('port', 8188)
    url = f'http://{host}:{port}/system_stats'
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return {'status': 'connected', 'data': resp.json()}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f'Cannot reach ComfyUI: {e}')

# ============================================================================
# Render (placeholder — requires ComfyUI integration)
# ============================================================================

@app.post('/api/render')
async def queue_render(data: dict):
    job_id = f"job-{uuid.uuid4().hex[:8]}"
    return {
        'job_id': job_id,
        'preset_id': data.get('preset_id'),
        'mode': data.get('mode'),
        'status': 'queued',
    }


@app.get('/api/render/{job_id}')
async def get_render_status(job_id: str):
    return {
        'job_id': job_id,
        'status': 'queued',
        'progress': 0,
    }

# ============================================================================
# Static Files (Frontend) — must be last (catch-all mount)
# ============================================================================

frontend_dir = Path(__file__).parent.parent.parent / 'frontend' / 'src'

if frontend_dir.exists():
    app.mount(
        '/',
        StaticFiles(directory=str(frontend_dir), html=True),
        name='static'
    )
    logger.info(f'Frontend mounted from: {frontend_dir}')
else:
    logger.warning(f'Frontend directory not found: {frontend_dir}')

# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f'Unhandled exception: {exc}', exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            'error': 'Internal server error',
            'detail': str(exc) if API_DEBUG else 'An error occurred',
        },
    )

# ============================================================================
# Startup / Shutdown
# ============================================================================

@app.on_event('startup')
async def startup_event():
    logger.info('JewelRender API starting up...')
    logger.info(f'ComfyUI URL: {COMFYUI_URL}')
    logger.info(f'User data directory: {USER_DATA_DIR}')
    _init_default_presets()


@app.on_event('shutdown')
async def shutdown_event():
    logger.info('JewelRender API shutting down...')

# ============================================================================
# Main
# ============================================================================

if __name__ == '__main__':
    logger.info(f'Starting JewelRender API on {API_HOST}:{API_PORT}')
    uvicorn.run(
        'main:app',
        host=API_HOST,
        port=API_PORT,
        reload=API_DEBUG,
        log_level=LOG_LEVEL.lower(),
    )
