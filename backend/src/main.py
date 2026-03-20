"""JewelRender API Server

A batch jewelry rendering application with ComfyUI backend.
Frontend: HTML/CSS/JS single-page app
Backend: FastAPI Python server
GPU: ComfyUI on Mac Mini M4
Storage: Local filesystem
"""

import logging
import socket
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import uvicorn

from config import (
    API_HOST, API_PORT, API_DEBUG, CORS_ORIGINS,
    COMFYUI_URL, USER_DATA_DIR, LOG_LEVEL
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
# Health & Status Endpoints
# ============================================================================

@app.get('/health')
async def health_check():
    """Check server health and ComfyUI connection."""
    return {
        'status': 'ok',
        'service': 'JewelRender API',
        'version': '0.1.0',
        'comfyui_url': COMFYUI_URL,
        'user_data_dir': str(USER_DATA_DIR),
    }


@app.get('/api/health')
async def api_health():
    """API endpoint for health check."""
    return {
        'status': 'ok',
        'comfyui': {
            'url': COMFYUI_URL,
            # TODO: Check actual ComfyUI connection
            'connected': None,
        },
        'storage': {
            'user_dir': str(USER_DATA_DIR),
            # TODO: Check available disk space
        },
    }

# ============================================================================
# Placeholder Endpoints (to be implemented)
# ============================================================================

@app.get('/api/presets')
async def list_presets():
    """List all style presets."""
    # TODO: Implement preset listing
    return {
        'presets': [],
        'total': 0,
    }


@app.get('/api/settings')
async def get_settings():
    """Get current application settings."""
    # TODO: Implement settings retrieval
    return {
        'comfyui': {
            'host': '127.0.0.1',
            'port': 8188,
        },
        'output': {
            'width': 1170,
            'height': 2532,
            'jpeg_quality': 95,
        },
    }


@app.post('/api/render')
async def queue_render():
    """Queue a render job."""
    # TODO: Implement render queueing
    return {
        'job_id': 'job-placeholder',
        'status': 'queued',
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

def _get_local_ip() -> str:
    """Detect the machine's LAN IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'


@app.on_event('startup')
async def startup_event():
    """Run on server startup."""
    local_ip = _get_local_ip()
    logger.info('JewelRender API starting up...')
    logger.info(f'ComfyUI URL: {COMFYUI_URL}')
    logger.info(f'User data directory: {USER_DATA_DIR}')
    logger.info(f'Local:   http://localhost:{API_PORT}')
    logger.info(f'Network: http://{local_ip}:{API_PORT}  <-- use this on other devices')
    # TODO: Verify ComfyUI connection
    # TODO: Initialize presets
    # TODO: Load settings


@app.on_event('shutdown')
async def shutdown_event():
    """Run on server shutdown."""
    logger.info('JewelRender API shutting down...')
    # TODO: Cleanup resources

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
