"""OpenAI API Client for JewelRender

Handles all communication with OpenAI's APIs:
- GPT Image 1.5: Image generation (/v1/images/generations) and editing (/v1/images/edits)
- GPT-4.1-mini: Vision analysis for the AI brain
- Sora 2: Video generation (/v1/videos)
"""

import base64
import logging
from typing import Optional

from openai import AsyncOpenAI

from config import (
    OPENAI_API_KEY, OPENAI_BRAIN_MODEL, OPENAI_IMAGE_MODEL,
    OPENAI_VIDEO_MODEL, OPENAI_TIMEOUT, OPENAI_VIDEO_TIMEOUT,
    OUTPUT_WIDTH, OUTPUT_HEIGHT
)

logger = logging.getLogger(__name__)

# ============================================================================
# Client Initialization
# ============================================================================

_client: Optional[AsyncOpenAI] = None


def get_client() -> AsyncOpenAI:
    """Get or create the OpenAI async client."""
    global _client
    if _client is None:
        _client = AsyncOpenAI(
            api_key=OPENAI_API_KEY,
            timeout=OPENAI_TIMEOUT,
        )
    return _client


# ============================================================================
# Connection Test
# ============================================================================

async def test_openai_connection() -> dict:
    """Test that the OpenAI API key is valid and models are accessible."""
    if not OPENAI_API_KEY:
        return {
            'connected': False,
            'error': 'OPENAI_API_KEY not configured. Set it in .env file.',
        }
    try:
        client = get_client()
        # Lightweight call to verify the key works
        models = await client.models.list()
        model_ids = [m.id for m in models.data]
        return {
            'connected': True,
            'brain_model': OPENAI_BRAIN_MODEL,
            'image_model': OPENAI_IMAGE_MODEL,
            'video_model': OPENAI_VIDEO_MODEL,
            'brain_available': OPENAI_BRAIN_MODEL in model_ids,
            'image_available': OPENAI_IMAGE_MODEL in model_ids,
        }
    except Exception as e:
        logger.error(f'OpenAI connection test failed: {e}')
        return {
            'connected': False,
            'error': str(e),
        }


# ============================================================================
# Image Generation (Generate Mode)
# ============================================================================

async def generate_image(
    prompt: str,
    size: str = f'{OUTPUT_WIDTH}x{OUTPUT_HEIGHT}',
    quality: str = 'high',
    n: int = 1,
) -> list[dict]:
    """Generate images from a text prompt using GPT Image 1.5.

    Args:
        prompt: Text description of the image to generate.
        size: Image dimensions (WxH string).
        quality: 'low', 'medium', or 'high'.
        n: Number of images to generate.

    Returns:
        List of dicts with 'b64_json' key containing base64 image data.
    """
    client = get_client()
    response = await client.images.generate(
        model=OPENAI_IMAGE_MODEL,
        prompt=prompt,
        n=n,
        size=size,
        quality=quality,
        response_format='b64_json',
    )
    return [{'b64_json': img.b64_json} for img in response.data]


# ============================================================================
# Image Editing (Edit Mode)
# ============================================================================

async def edit_image(
    image_b64: str,
    prompt: str,
    mask_b64: Optional[str] = None,
    size: str = f'{OUTPUT_WIDTH}x{OUTPUT_HEIGHT}',
) -> list[dict]:
    """Edit an existing image using GPT Image 1.5.

    Used for: background changes, metal/gemstone swaps, cross-preset pipeline,
    and Recede (outpainting).

    Args:
        image_b64: Base64-encoded source image.
        prompt: Description of the edit (e.g. "change background to baby blue").
        mask_b64: Optional base64 mask — white areas will be edited.
        size: Output dimensions.

    Returns:
        List of dicts with 'b64_json' key containing base64 image data.
    """
    client = get_client()

    # Convert base64 strings to bytes for the API
    image_bytes = base64.b64decode(image_b64)

    kwargs = {
        'model': OPENAI_IMAGE_MODEL,
        'image': image_bytes,
        'prompt': prompt,
        'size': size,
        'response_format': 'b64_json',
    }

    if mask_b64:
        kwargs['mask'] = base64.b64decode(mask_b64)

    response = await client.images.edit(**kwargs)
    return [{'b64_json': img.b64_json} for img in response.data]


# ============================================================================
# Video Generation (360 Mode via Sora 2)
# ============================================================================

async def generate_video(
    prompt: str,
    reference_image_b64: Optional[str] = None,
    duration_seconds: int = 5,
) -> dict:
    """Generate a 360 rotation video using Sora 2 API.

    Args:
        prompt: Description of the video (e.g. "smooth 360 rotation of diamond ring").
        reference_image_b64: Optional base64 reference image.
        duration_seconds: Video length in seconds.

    Returns:
        Dict with video generation job info.
    """
    client = get_client()

    # Sora 2 video generation via the responses API
    input_content = [{"type": "text", "text": prompt}]

    if reference_image_b64:
        input_content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{reference_image_b64}"}
        })

    response = await client.responses.create(
        model=OPENAI_VIDEO_MODEL,
        input=input_content,
    )

    return {
        'response_id': response.id,
        'status': 'processing',
    }
