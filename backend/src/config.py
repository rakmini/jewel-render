"""JewelRender Configuration"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================================
# ComfyUI Connection
# ============================================================================

COMFYUI_HOST = os.getenv('COMFYUI_HOST', '127.0.0.1')
COMFYUI_PORT = int(os.getenv('COMFYUI_PORT', '8188'))
COMFYUI_URL = f'http://{COMFYUI_HOST}:{COMFYUI_PORT}'
COMFYUI_TIMEOUT = int(os.getenv('COMFYUI_TIMEOUT', '600'))

# ============================================================================
# Output Settings
# ============================================================================

OUTPUT_WIDTH = 1170
OUTPUT_HEIGHT = 2532
JPEG_QUALITY = 95
OUTPUT_FORMAT = 'jpeg'

# ============================================================================
# Video Settings
# ============================================================================

VIDEO_FORMAT = 'mp4'
VIDEO_MODEL = 'sv3d_p'  # or 'wan_2_1'
VIDEO_CODEC = 'h264'
VIDEO_BITRATE = '5000k'

# ============================================================================
# Storage Paths
# ============================================================================

# Base user data directory
USER_DATA_DIR = Path.home() / 'JewelRender'

# Preset-specific directories
PRESETS_DIR = USER_DATA_DIR / 'presets'
EXPORTS_DIR = USER_DATA_DIR / 'exports'

# Create directories if they don't exist
USER_DATA_DIR.mkdir(exist_ok=True)
PRESETS_DIR.mkdir(exist_ok=True)
EXPORTS_DIR.mkdir(exist_ok=True)

# ============================================================================
# Default Presets
# ============================================================================

DEFAULT_PRESETS = [
    {
        'id': 'cool-blue',
        'name': 'Cool Blue',
        'style': 'baby-blue background, softly lit',
    },
    {
        'id': 'white-retail',
        'name': 'White Retail',
        'style': 'clean white background',
    },
    {
        'id': 'yashica-film',
        'name': 'Yashica Film',
        'style': 'AI models, Yashica T4 aesthetic',
    },
]

# ============================================================================
# Feature Toggles (from user settings, defaults)
# ============================================================================

AUTO_ADD_APPROVED_TO_RIL = True
AUTO_DEPOSIT_EXPORTS_TO_RIL = True
PARAMETER_LOGGING = True

# ============================================================================
# Server Settings
# ============================================================================

API_HOST = os.getenv('API_HOST', '0.0.0.0')
API_PORT = int(os.getenv('API_PORT', '5000'))
API_DEBUG = os.getenv('API_DEBUG', 'false').lower() == 'true'

# ============================================================================
# Logging
# ============================================================================

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = USER_DATA_DIR / 'jewelrender.log'

# ============================================================================
# Checkpoint (ComfyUI Model)
# ============================================================================

DEFAULT_CHECKPOINT = 'sd_xl_base_1.0.safetensors'
CHECKPOINT = os.getenv('CHECKPOINT', DEFAULT_CHECKPOINT)

# ============================================================================
# CORS Settings
# ============================================================================

CORS_ORIGINS = [
    'http://localhost',
    'http://localhost:5000',
    'http://127.0.0.1',
    'http://127.0.0.1:5000',
    # Add IPv4 ranges for local network access
    '*',  # Allow all for local network (restrict in production)
]

# ============================================================================
# Render Queue Settings
# ============================================================================

MAX_CONCURRENT_RENDERS = 1  # ComfyUI typically handles 1 at a time
RENDER_TIMEOUT_SECONDS = 600  # 10 minutes default timeout
