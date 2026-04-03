"""JewelRender API Server

AI Engine: OpenAI APIs (cloud)
- GPT-4.1-mini: Persistent brain (vision analysis, RIL tagging, quality assessment)
- GPT Image 1.5: Image generation and editing
- Sora 2: Video generation (360 rotations)

Frontend: HTML/CSS/JS single-page app
Backend: FastAPI Python server
Storage: Local filesystem
"""

import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import uvicorn

from config import (
    API_HOST, API_PORT, API_DEBUG, CORS_ORIGINS,
    OPENAI_API_KEY, OPENAI_BRAIN_MODEL, OPENAI_IMAGE_MODEL,
    OPENAI_VIDEO_MODEL, USER_DATA_DIR, LOG_LEVEL
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
    description='Batch jewelry rendering with OpenAI APIs (GPT Image 1.5, GPT-4.1-mini brain, Sora 2 video)',
    version='0.2.0',
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
# Health & Status Endpoints
# ============================================================================

@app.get('/health')
async def health_check():
    """Check server health and OpenAI API connection."""
    return {
        'status': 'ok',
        'service': 'JewelRender API',
        'version': '0.2.0',
        'ai_engine': 'openai',
        'models': {
            'brain': OPENAI_BRAIN_MODEL,
            'image': OPENAI_IMAGE_MODEL,
            'video': OPENAI_VIDEO_MODEL,
        },
        'api_key_configured': bool(OPENAI_API_KEY),
        'user_data_dir': str(USER_DATA_DIR),
    }


@app.get('/api/health')
async def api_health():
    """API endpoint for detailed health check."""
    from openai_client import test_openai_connection
    connection_status = await test_openai_connection()
    return {
        'status': 'ok',
        'openai': connection_status,
        'storage': {
            'user_dir': str(USER_DATA_DIR),
        },
    }

# ============================================================================
# Preset Endpoints
# ============================================================================

@app.get('/api/presets')
async def list_presets():
    """List all style presets."""
    # TODO: Implement preset listing from filesystem
    return {
        'presets': [],
        'total': 0,
    }

# ============================================================================
# Settings Endpoints
# ============================================================================

@app.get('/api/settings')
async def get_settings():
    """Get current application settings."""
    return {
        'openai': {
            'brain_model': OPENAI_BRAIN_MODEL,
            'image_model': OPENAI_IMAGE_MODEL,
            'video_model': OPENAI_VIDEO_MODEL,
            'api_key_configured': bool(OPENAI_API_KEY),
        },
        'output': {
            'width': 1170,
            'height': 2532,
            'jpeg_quality': 95,
        },
    }


@app.post('/api/settings/test-connection')
async def test_connection():
    """Test OpenAI API connection."""
    from openai_client import test_openai_connection
    result = await test_openai_connection()
    return result

# ============================================================================
# Render Endpoints
# ============================================================================

@app.post('/api/render')
async def queue_render():
    """Queue a render job via OpenAI Images API."""
    # TODO: Implement render queueing with OpenAI API
    return {
        'job_id': 'job-placeholder',
        'status': 'queued',
    }

# ============================================================================
# AI Brain Endpoints
# ============================================================================

@app.post('/api/analyze')
async def analyze_image():
    """Analyze an image using GPT-4.1-mini vision.

    Returns metal type, gemstone, product type, setting style,
    quality score, and suggested RIL folder tags.
    """
    # TODO: Implement with brain service
    return {
        'status': 'not_implemented',
        'message': 'AI brain analysis endpoint — uses GPT-4.1-mini vision',
    }

# ============================================================================
# Static Files (Frontend)
# ============================================================================

# Mount frontend static files
# This serves the HTML/CSS/JS at the root path
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
    """Handle unexpected exceptions."""
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
    """Run on server startup."""
    logger.info('JewelRender API starting up...')
    logger.info(f'AI Engine: OpenAI APIs')
    logger.info(f'Brain model: {OPENAI_BRAIN_MODEL}')
    logger.info(f'Image model: {OPENAI_IMAGE_MODEL}')
    logger.info(f'Video model: {OPENAI_VIDEO_MODEL}')
    logger.info(f'API key configured: {bool(OPENAI_API_KEY)}')
    logger.info(f'User data directory: {USER_DATA_DIR}')


@app.on_event('shutdown')
async def shutdown_event():
    """Run on server shutdown."""
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
