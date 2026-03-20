"""Data Models for JewelRender API

Pydantic models for request/response validation.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


# ============================================================================
# Enums
# ============================================================================

class RenderMode(str, Enum):
    """Render modes."""
    EDIT = 'edit'
    GENERATE = 'generate'
    VIDEO = 'video'


class FeedbackType(str, Enum):
    """Image feedback."""
    APPROVE = 'approve'
    REJECT = 'reject'


class JobStatus(str, Enum):
    """Render job status."""
    QUEUED = 'queued'
    PROCESSING = 'processing'
    COMPLETE = 'complete'
    FAILED = 'failed'
    CANCELLED = 'cancelled'


# ============================================================================
# Preset Models
# ============================================================================

class PresetDefaults(BaseModel):
    """Per-preset adjustment defaults."""
    temperature: int = Field(default=0, ge=-100, le=100)
    saturation: int = Field(default=0, ge=-100, le=100)
    contrast: int = Field(default=0, ge=-100, le=100)
    sharpness: int = Field(default=0, ge=-100, le=100)
    grain: int = Field(default=0, ge=-100, le=100)


class PresetCreate(BaseModel):
    """Request to create new preset."""
    name: str
    style: str
    template: Optional[str] = None  # Copy defaults from existing preset


class PresetUpdate(BaseModel):
    """Request to update preset."""
    name: Optional[str] = None
    style: Optional[str] = None
    defaults: Optional[PresetDefaults] = None


class Preset(BaseModel):
    """Preset response model."""
    id: str
    name: str
    style: str
    defaults: PresetDefaults
    library_count: int = 0
    renders_count: int = 0
    created: datetime


# ============================================================================
# Render Models
# ============================================================================

class RenderParams(BaseModel):
    """Parameters for render job."""
    # Common
    preset_id: str
    mode: RenderMode

    # Generation mode
    prompt: Optional[str] = None
    reference_images: Optional[List[str]] = None

    # Edit mode
    input_image: Optional[str] = None  # base64 or file
    elements_to_change: Optional[List[str]] = None

    # Video mode
    front_image: Optional[str] = None
    side_image: Optional[str] = None
    three_quarter_image: Optional[str] = None
    rotation_direction: Optional[str] = 'clockwise'
    rotation_speed: Optional[str] = 'normal'
    video_length_seconds: Optional[int] = 5

    # Adjustments
    temperature: int = 0
    saturation: int = 0
    contrast: int = 0
    sharpness: int = 0
    grain: int = 0


class RenderRequest(BaseModel):
    """Request to queue render."""
    preset_id: str
    mode: RenderMode
    params: Dict[str, Any]


class RenderJob(BaseModel):
    """Render job response."""
    job_id: str
    preset_id: str
    mode: RenderMode
    status: JobStatus
    progress: int = 0
    queued_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


class RenderOutput(BaseModel):
    """Render output (image or video)."""
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    width: int = 1170
    height: int = 2532
    file_size: int
    created: datetime


# ============================================================================
# Image Models
# ============================================================================

class ImageAdjustment(BaseModel):
    """Editor adjustments."""
    exposure: int = 0
    contrast: int = 0
    highlights: int = 0
    shadows: int = 0
    temperature: int = 0
    tint: int = 0
    saturation: int = 0
    vibrance: int = 0
    skin_tone: int = 0
    sharpness: int = 0
    clarity: int = 0
    grain: int = 0
    fade: int = 0
    vignette: int = 0


class ImageCrop(BaseModel):
    """Crop parameters."""
    aspect_ratio: str = 'free'  # '1:1', '4:5', '9:16', '16:9', 'free'
    x: int = 0
    y: int = 0
    width: int = 1170
    height: int = 2532
    rotation: float = 0.0
    flip_h: bool = False
    flip_v: bool = False


class ImageFeedback(BaseModel):
    """Image feedback."""
    feedback: FeedbackType


# ============================================================================
# Reference Image Library (RIL)
# ============================================================================

class RILImage(BaseModel):
    """Image in Reference Image Library."""
    id: str
    filename: str
    added_date: datetime
    source: str  # 'manual', 'approved', 'export'
    url: str


class RILUpload(BaseModel):
    """Request to add image to RIL."""
    # File uploaded separately as multipart/form-data
    source: str = 'manual'


# ============================================================================
# Settings Models
# ============================================================================

class ComfyUISettings(BaseModel):
    """ComfyUI connection settings."""
    host: str = '127.0.0.1'
    port: int = 8188
    checkpoint: str = 'sd_xl_base_1.0.safetensors'
    timeout_seconds: int = 600


class OutputSettings(BaseModel):
    """Output format settings."""
    width: int = 1170
    height: int = 2532
    jpeg_quality: int = 95


class VideoSettings(BaseModel):
    """Video output settings."""
    format: str = 'mp4'
    model: str = 'sv3d_p'
    codec: str = 'h264'
    bitrate: str = '5000k'


class FeedbackSettings(BaseModel):
    """Feedback and training settings."""
    auto_add_approved_to_ril: bool = True
    auto_deposit_exports_to_ril: bool = True
    parameter_logging: bool = True


class Settings(BaseModel):
    """Application settings."""
    comfyui: ComfyUISettings
    output: OutputSettings
    video: VideoSettings
    feedback: FeedbackSettings
    export_folder: str = '~/JewelRender/exports'


# ============================================================================
# Health Check Models
# ============================================================================

class HealthCheck(BaseModel):
    """Server health status."""
    status: str
    comfyui: Dict[str, Any]
    storage: Dict[str, Any]


# ============================================================================
# Error Models
# ============================================================================

class ErrorResponse(BaseModel):
    """Error response."""
    error: str
    code: str
    detail: Optional[str] = None
