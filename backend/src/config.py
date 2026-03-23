"""JewelRender Configuration — MVP"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================================
# Environment Detection
# ============================================================================

IS_VERCEL = bool(os.environ.get('VERCEL'))

# ============================================================================
# OpenAI
# ============================================================================

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

# ============================================================================
# Storage Paths
# ============================================================================

if IS_VERCEL:
    USER_DATA_DIR = Path('/tmp/JewelRender')
else:
    USER_DATA_DIR = Path.home() / 'JewelRender'

PRESETS_DIR = USER_DATA_DIR / 'presets'
EXPORTS_DIR = USER_DATA_DIR / 'exports'
RENDERS_DIR = USER_DATA_DIR / 'renders'

# Create directories
USER_DATA_DIR.mkdir(exist_ok=True)
PRESETS_DIR.mkdir(exist_ok=True)
EXPORTS_DIR.mkdir(exist_ok=True)
RENDERS_DIR.mkdir(exist_ok=True)

# ============================================================================
# Server
# ============================================================================

API_HOST = os.getenv('API_HOST', '0.0.0.0')
API_PORT = int(os.getenv('API_PORT', '5050'))
API_DEBUG = os.getenv('API_DEBUG', 'false').lower() == 'true'

# ============================================================================
# Logging
# ============================================================================

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# ============================================================================
# CORS
# ============================================================================

CORS_ORIGINS = [
    'http://localhost',
    'http://localhost:5050',
    'http://127.0.0.1',
    'http://127.0.0.1:5050',
]
