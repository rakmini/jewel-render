"""JewelRender Configuration

AI Engine: OpenAI APIs (cloud)
- GPT-4.1-mini: Persistent brain (vision analysis, RIL tagging, quality assessment)
- GPT Image 1.5: Image generation and editing
- Sora 2: Video generation (360 rotations)
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================================
# OpenAI API Configuration
# ============================================================================

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

# Brain model — always-on vision analysis, classification, tagging
OPENAI_BRAIN_MODEL = os.getenv('OPENAI_BRAIN_MODEL', 'gpt-4.1-mini')

# Image generation/editing model
OPENAI_IMAGE_MODEL = os.getenv('OPENAI_IMAGE_MODEL', 'gpt-image-1')

# Video generation model
OPENAI_VIDEO_MODEL = os.getenv('OPENAI_VIDEO_MODEL', 'sora-2')

# API timeouts (seconds)
OPENAI_TIMEOUT = int(os.getenv('OPENAI_TIMEOUT', '120'))
OPENAI_VIDEO_TIMEOUT = int(os.getenv('OPENAI_VIDEO_TIMEOUT', '600'))

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

MAX_CONCURRENT_RENDERS = 3  # OpenAI API supports concurrent requests
RENDER_TIMEOUT_SECONDS = 120  # Faster than local GPU
