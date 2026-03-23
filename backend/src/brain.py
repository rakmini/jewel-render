"""AI Brain Service — GPT-4.1-mini Vision Analysis

The persistent AI brain that runs on every image flowing through JewelRender.
Handles classification, tagging, quality assessment, and RIL folder suggestions.

This is what makes the app get smarter over time:
- Every uploaded image gets analyzed
- Every rendered image gets analyzed
- Every exported image gets analyzed
- Analysis results drive RIL folder suggestions and parameter recommendations
"""

import base64
import json
import logging
from typing import Optional

from openai import AsyncOpenAI

from config import OPENAI_API_KEY, OPENAI_BRAIN_MODEL, OPENAI_TIMEOUT
from models import ImageAnalysis

logger = logging.getLogger(__name__)


def _get_client() -> AsyncOpenAI:
    """Get OpenAI client for brain operations."""
    return AsyncOpenAI(api_key=OPENAI_API_KEY, timeout=OPENAI_TIMEOUT)


# ============================================================================
# Image Analysis
# ============================================================================

ANALYSIS_SYSTEM_PROMPT = """You are JewelRender's AI brain — an expert jewelry analyst.

When shown a jewelry image, analyze it and return a JSON object with these fields:
- metal_type: The metal type (e.g. "white gold", "yellow gold", "rose gold", "platinum", "silver")
- metal_karat: The karat if visible/inferrable (e.g. "10k", "14k", "18k", "24k") or null
- gemstone: Primary gemstone (e.g. "diamond", "emerald", "sapphire", "ruby") or null
- gemstone_color: Gemstone color if applicable (e.g. "blue", "green", "red", "clear")
- product_type: Product category (e.g. "ring", "necklace", "bracelet", "earrings", "watch", "grillz", "pendant")
- setting_style: Setting style (e.g. "prong", "bezel", "channel", "pave", "tension", "invisible") or null
- quality_score: Image quality from 0.0 to 1.0 (lighting, focus, composition, background)
- suggested_preset: Which JewelRender preset this fits best ("cool-blue", "white-retail", "yashica-film") or null
- suggested_ril_folders: List of RIL folder tags this image should be filed under
- description: One-sentence description of the piece

Return ONLY valid JSON, no markdown or explanation."""


async def analyze_image(image_b64: str) -> ImageAnalysis:
    """Analyze a jewelry image using GPT-4.1-mini vision.

    This runs on every image that enters the system — uploads, renders, exports.
    Results are stored alongside the image for RIL sorting and parameter suggestions.

    Args:
        image_b64: Base64-encoded image data.

    Returns:
        ImageAnalysis with classification results.
    """
    client = _get_client()

    response = await client.chat.completions.create(
        model=OPENAI_BRAIN_MODEL,
        messages=[
            {'role': 'system', 'content': ANALYSIS_SYSTEM_PROMPT},
            {
                'role': 'user',
                'content': [
                    {
                        'type': 'image_url',
                        'image_url': {
                            'url': f'data:image/jpeg;base64,{image_b64}',
                            'detail': 'low',  # Cheaper, sufficient for classification
                        },
                    },
                    {
                        'type': 'text',
                        'text': 'Analyze this jewelry image.',
                    },
                ],
            },
        ],
        response_format={'type': 'json_object'},
        max_tokens=500,
    )

    raw = response.choices[0].message.content
    try:
        data = json.loads(raw)
        return ImageAnalysis(**data)
    except (json.JSONDecodeError, Exception) as e:
        logger.error(f'Brain analysis parse error: {e}, raw: {raw}')
        return ImageAnalysis(description='Analysis failed')


# ============================================================================
# Quality Assessment
# ============================================================================

async def assess_render_quality(
    image_b64: str,
    preset_style: str,
    prompt_used: Optional[str] = None,
) -> dict:
    """Assess whether a render matches the target preset style.

    Used to auto-suggest approve/reject and guide parameter tuning.

    Args:
        image_b64: Base64-encoded rendered image.
        preset_style: The target style description (e.g. "baby-blue background, softly lit").
        prompt_used: The prompt that was used to generate this image.

    Returns:
        Dict with quality assessment results.
    """
    client = _get_client()

    assessment_prompt = f"""Assess this rendered jewelry image against the target style.

Target style: "{preset_style}"
{f'Generation prompt: "{prompt_used}"' if prompt_used else ''}

Return JSON with:
- matches_style: true/false — does this image match the target style?
- confidence: 0.0 to 1.0
- issues: list of strings describing any problems (empty if good)
- suggestions: list of strings for improvement (empty if perfect)
- overall_quality: 0.0 to 1.0"""

    response = await client.chat.completions.create(
        model=OPENAI_BRAIN_MODEL,
        messages=[
            {'role': 'system', 'content': 'You are a jewelry photography quality assessor. Return only valid JSON.'},
            {
                'role': 'user',
                'content': [
                    {
                        'type': 'image_url',
                        'image_url': {
                            'url': f'data:image/jpeg;base64,{image_b64}',
                            'detail': 'low',
                        },
                    },
                    {
                        'type': 'text',
                        'text': assessment_prompt,
                    },
                ],
            },
        ],
        response_format={'type': 'json_object'},
        max_tokens=500,
    )

    try:
        return json.loads(response.choices[0].message.content)
    except (json.JSONDecodeError, Exception) as e:
        logger.error(f'Quality assessment parse error: {e}')
        return {'matches_style': None, 'error': str(e)}


# ============================================================================
# Parameter Recommendation
# ============================================================================

async def recommend_parameters(
    preset_style: str,
    product_description: str,
    past_successes: Optional[list[dict]] = None,
) -> dict:
    """Recommend render parameters based on preset style and past successes.

    Learns from the parameter log — pulls what worked before and suggests
    similar settings for new renders.

    Args:
        preset_style: Target style description.
        product_description: What the user wants to render.
        past_successes: List of parameter sets that produced approved results.

    Returns:
        Dict with recommended parameters.
    """
    client = _get_client()

    context = f"""Recommend render parameters for JewelRender.

Target preset style: "{preset_style}"
Product to render: "{product_description}"
"""
    if past_successes:
        context += f"\nPast successful parameters (approved renders):\n{json.dumps(past_successes[:5], indent=2)}"

    context += """

Return JSON with:
- prompt: suggested text prompt for image generation
- temperature: -100 to 100 (post-render color temperature adjustment)
- saturation: -100 to 100
- contrast: -100 to 100
- sharpness: -100 to 100
- grain: -100 to 100
- reasoning: one sentence explaining the recommendation"""

    response = await client.chat.completions.create(
        model=OPENAI_BRAIN_MODEL,
        messages=[
            {'role': 'system', 'content': 'You are a jewelry photography expert. Return only valid JSON.'},
            {'role': 'user', 'content': context},
        ],
        response_format={'type': 'json_object'},
        max_tokens=500,
    )

    try:
        return json.loads(response.choices[0].message.content)
    except (json.JSONDecodeError, Exception) as e:
        logger.error(f'Parameter recommendation parse error: {e}')
        return {'error': str(e)}
