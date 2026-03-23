"""OpenAI Image Edit Client for JewelRender MVP"""

import base64
import io
import logging

from openai import AsyncOpenAI, APIError, RateLimitError, AuthenticationError
from PIL import Image

logger = logging.getLogger(__name__)

# Lazy-init client (reads OPENAI_API_KEY from env automatically)
_client: AsyncOpenAI | None = None


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI()
    return _client


def _to_png_bytes(image_bytes: bytes) -> bytes:
    """Convert any image format to PNG bytes for OpenAI API."""
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
    Send an image + prompt to OpenAI's image edit endpoint.
    Returns edited image as PNG bytes.
    """
    client = _get_client()
    png_bytes = _to_png_bytes(image_bytes)

    logger.info(f'Calling OpenAI image edit ({len(png_bytes)} bytes, prompt={prompt[:80]}...)')

    response = await client.images.edit(
        model='dall-e-2',
        image=io.BytesIO(png_bytes),
        prompt=prompt,
        size='1024x1024',
        response_format='b64_json',
    )

    b64_data = response.data[0].b64_json
    result_bytes = base64.b64decode(b64_data)

    logger.info(f'OpenAI returned {len(result_bytes)} bytes')
    return result_bytes


async def test_api_key() -> bool:
    """Quick check that the API key is valid."""
    try:
        client = _get_client()
        await client.models.list()
        return True
    except AuthenticationError:
        return False
    except Exception:
        return False
