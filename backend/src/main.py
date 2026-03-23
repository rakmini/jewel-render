"""JewelRender API Server

MVP: Upload jewelry photo → pick metal type → AI edits image.
Backend: FastAPI + Fal.AI Images API (OpenAI-compatible)
Works locally and on Vercel serverless.
"""

import base64
import logging
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import uvicorn

from config import (
    API_HOST, API_PORT, API_DEBUG, CORS_ORIGINS,
    USER_DATA_DIR, RENDERS_DIR, LOG_LEVEL, IS_VERCEL,
)
from fal_client import edit_image, test_api_key

# ============================================================================
# Logging
# ============================================================================

logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# Constants
# ============================================================================

VALID_METALS = {'yellow', 'white', 'rose'}
MAX_UPLOAD_BYTES = 20 * 1024 * 1024  # 20MB
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}

PROMPT_TEMPLATE = (
    'Render this image in 14k {metal} gold. '
    'Suspend in a softly lit baby blue color background. '
    'Preserve the exact shape, geometry, and proportions of the jewelry piece.'
)

# ============================================================================
# App
# ============================================================================

app = FastAPI(
    title='JewelRender API',
    description='MVP: Cool Blue metal swap for jewelry photos',
    version='0.2.0',
    docs_url='/api/docs',
    redoc_url=None,
    openapi_url='/api/openapi.json',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# ============================================================================
# Health
# ============================================================================

@app.get('/health')
@app.get('/api/health')
async def health_check():
    return {
        'status': 'ok',
        'service': 'JewelRender MVP',
        'version': '0.2.0',
        'environment': 'vercel' if IS_VERCEL else 'local',
    }

# ============================================================================
# MVP Edit Endpoint
# ============================================================================

@app.post('/api/edit')
async def edit_jewelry(
    file: UploadFile = File(...),
    metal: str = Form('yellow'),
):
    """Upload a jewelry photo, pick metal type, get AI-edited result."""

    # Validate metal
    metal = metal.strip().lower()
    if metal not in VALID_METALS:
        raise HTTPException(
            status_code=400,
            detail={'error': f'Invalid metal type. Must be one of: {", ".join(VALID_METALS)}', 'code': 'INVALID_METAL'},
        )

    # Validate file extension
    filename = file.filename or 'upload.jpg'
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail={'error': 'Unsupported file type. Use JPG, PNG, or WebP.', 'code': 'INVALID_FILE_TYPE'},
        )

    # Read + validate size
    image_bytes = await file.read()
    if len(image_bytes) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail={'error': 'File too large (max 20MB).', 'code': 'FILE_TOO_LARGE'},
        )
    if len(image_bytes) == 0:
        raise HTTPException(
            status_code=400,
            detail={'error': 'Empty file.', 'code': 'EMPTY_FILE'},
        )

    # Build prompt
    prompt = PROMPT_TEMPLATE.format(metal=metal)

    # Call Fal.AI
    try:
        result_bytes = await edit_image(image_bytes, prompt)
    except Exception as e:
        error_msg = str(e)
        code = 'AI_ERROR'

        if 'authentication' in error_msg.lower() or '401' in error_msg:
            code = 'INVALID_KEY'
            error_msg = 'Invalid Fal.AI API key. Check your .env file.'
        elif 'rate' in error_msg.lower() or '429' in error_msg:
            code = 'RATE_LIMIT'
            error_msg = 'Rate limited by Fal.AI. Please wait and try again.'
        elif 'content_policy' in error_msg.lower() or 'safety' in error_msg.lower():
            code = 'CONTENT_POLICY'
            error_msg = 'Image was rejected by content policy.'

        logger.error(f'Fal.AI edit failed: {e}', exc_info=True)
        raise HTTPException(
            status_code=502,
            detail={'error': error_msg, 'code': code},
        )

    # Build response with base64 image data (works on both local and Vercel)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    out_filename = f'{timestamp}_{metal}_gold.png'
    b64_image = base64.b64encode(result_bytes).decode('utf-8')

    # Also save locally if not on Vercel (for local history)
    if not IS_VERCEL:
        out_path = RENDERS_DIR / out_filename
        out_path.write_bytes(result_bytes)
        logger.info(f'Saved render: {out_path} ({len(result_bytes)} bytes)')

    logger.info(f'Render complete: {out_filename} ({len(result_bytes)} bytes)')

    return {
        'image_data': b64_image,
        'prompt': prompt,
        'metal': metal,
        'filename': out_filename,
    }

# ============================================================================
# API Key Test
# ============================================================================

@app.get('/api/fal/test')
async def test_fal():
    ok = await test_api_key()
    if ok:
        return {'status': 'ok', 'message': 'Fal.AI API key is valid'}
    raise HTTPException(status_code=401, detail={'error': 'Invalid Fal.AI API key', 'code': 'INVALID_KEY'})


# Backward-compatible alias
@app.get('/api/openai/test')
async def test_openai():
    return await test_fal()

# ============================================================================
# Static Files — local only (Vercel serves static via CDN)
# ============================================================================

if not IS_VERCEL:
    # Renders directory (generated images)
    if RENDERS_DIR.exists():
        app.mount('/renders', StaticFiles(directory=str(RENDERS_DIR)), name='renders')
        logger.info(f'Renders mounted from: {RENDERS_DIR}')

    # Frontend (catch-all — must be last)
    frontend_dir = Path(__file__).parent.parent.parent / 'frontend' / 'src'
    if frontend_dir.exists():
        app.mount('/', StaticFiles(directory=str(frontend_dir), html=True), name='static')
        logger.info(f'Frontend mounted from: {frontend_dir}')
    else:
        logger.warning(f'Frontend directory not found: {frontend_dir}')

# ============================================================================
# Error Handler
# ============================================================================

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f'Unhandled exception: {exc}', exc_info=True)
    return JSONResponse(
        status_code=500,
        content={'error': 'Internal server error', 'code': 'INTERNAL_ERROR'},
    )

# ============================================================================
# Startup / Shutdown
# ============================================================================

@app.on_event('startup')
async def startup_event():
    logger.info(f'JewelRender MVP starting up ({"Vercel" if IS_VERCEL else "local"})...')
    logger.info(f'User data: {USER_DATA_DIR}')

@app.on_event('shutdown')
async def shutdown_event():
    logger.info('JewelRender MVP shutting down...')

# ============================================================================
# Main (local only)
# ============================================================================

if __name__ == '__main__':
    logger.info(f'Starting JewelRender on {API_HOST}:{API_PORT}')
    uvicorn.run(
        'main:app',
        host=API_HOST,
        port=API_PORT,
        reload=API_DEBUG,
        log_level=LOG_LEVEL.lower(),
    )
