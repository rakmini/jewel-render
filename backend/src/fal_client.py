"""Fal.AI Image Edit Client for JewelRender MVP

Uses the OpenAI-compatible API exposed by Fal.AI (https://fal.run/v1).
The openai SDK is used as the HTTP client — no Fal-specific SDK required.
"""

import base64
import io
import logging

from openai import AsyncOpenAI, APIError, RateLimitError, AuthenticationError
from PIL import Image

from config import FAL_API_KEY, FAL_BASE_URL, FAL_MODEL, FAL_IMAGE_SIZE

logger = logging.getLogger(__name__)

# Lazy-init client pointing at Fal.AI's OpenAI-compatible endpoint
_client: AsyncOpenAI | None = None


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(
            api_key=FAL_API_KEY,
            base_url=FAL_BASE_URL,
        )
    return _client


def _to_png_bytes(image_bytes: bytes) -> bytes:
    """Convert any image format to PNG bytes for the Fal.AI API."""
    img = Image.open(io.BytesIO(image_bytes))
    if img.mode == 'RGBA':
        pass  # keep alpha
    elif img.mode != 'RGB':
        img = img.convert('RGB')
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()


async def edit_image(image_bytes: bytes, prompt: str) -> bytes:
    """
    Send an image + prompt to Fal.AI's image edit endpoint.
    Returns edited image as PNG bytes.
    """
    client = _get_client()
    png_bytes = _to_png_bytes(image_bytes)

    logger.info(
        f'Calling Fal.AI image edit '
        f'(model={FAL_MODEL}, size={FAL_IMAGE_SIZE}, '
        f'{len(png_bytes)} bytes, prompt={prompt[:80]}...)'
    )

    response = await client.images.edit(
        model=FAL_MODEL,
        # Explicit filename + MIME type prevents application/octet-stream on upload
        image=('image.png', png_bytes, 'image/png'),
        prompt=prompt,
        size=FAL_IMAGE_SIZE,
        response_format='b64_json',
    )

    b64_data = response.data[0].b64_json
    result_bytes = base64.b64decode(b64_data)

    logger.info(f'Fal.AI returned {len(result_bytes)} bytes')
    return result_bytes


async def test_api_key() -> bool:
    """Quick check that the Fal.AI API key is valid."""
    try:
        client = _get_client()
        await client.models.list()
        return True
    except AuthenticationError:
        return False
    except Exception:
        return False
