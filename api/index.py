"""Vercel serverless entry point — wraps the FastAPI app."""
import sys
from pathlib import Path

# Add backend/src to Python path so imports work
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend' / 'src'))

from main import app  # noqa: E402

# Vercel picks up the `app` variable automatically for ASGI
