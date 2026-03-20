"""Image Processing Utilities

Handles image adjustments, crops, and transformations.
"""

import logging
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image, ImageEnhance
import io
import base64

logger = logging.getLogger(__name__)


class ImageProcessor:
    """Process and transform images."""

    @staticmethod
    def load_from_file(filepath: str) -> Optional[Image.Image]:
        """Load image from file.

        Args:
            filepath: Path to image file

        Returns:
            PIL Image or None if failed
        """
        try:
            img = Image.open(filepath)
            logger.info(f'Loaded image: {filepath}')
            return img
        except Exception as e:
            logger.error(f'Failed to load image: {e}')
            return None

    @staticmethod
    def load_from_base64(base64_str: str) -> Optional[Image.Image]:
        """Load image from base64 string.

        Args:
            base64_str: Base64 encoded image

        Returns:
            PIL Image or None if failed
        """
        try:
            # Remove data URL prefix if present
            if base64_str.startswith('data:'):
                base64_str = base64_str.split(',')[1]

            img_data = base64.b64decode(base64_str)
            img = Image.open(io.BytesIO(img_data))
            logger.info('Loaded image from base64')
            return img
        except Exception as e:
            logger.error(f'Failed to load image from base64: {e}')
            return None

    @staticmethod
    def save_to_file(
        img: Image.Image,
        filepath: str,
        quality: int = 95,
        format: str = 'JPEG'
    ) -> bool:
        """Save image to file.

        Args:
            img: PIL Image
            filepath: Output file path
            quality: JPEG quality (1-100)
            format: Image format ('JPEG', 'PNG', etc.)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Create parent directory if needed
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)

            # Convert RGBA to RGB if saving as JPEG
            if format.upper() == 'JPEG' and img.mode == 'RGBA':
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img.split()[3])
                img = rgb_img

            if format.upper() == 'JPEG':
                img.save(filepath, format=format, quality=quality)
            else:
                img.save(filepath, format=format)

            logger.info(f'Saved image: {filepath}')
            return True
        except Exception as e:
            logger.error(f'Failed to save image: {e}')
            return False

    @staticmethod
    def to_base64(img: Image.Image, format: str = 'JPEG', quality: int = 95) -> str:
        """Convert image to base64 string.

        Args:
            img: PIL Image
            format: Image format
            quality: JPEG quality

        Returns:
            Base64 encoded string
        """
        try:
            buffer = io.BytesIO()
            if format.upper() == 'JPEG':
                img.save(buffer, format=format, quality=quality)
            else:
                img.save(buffer, format=format)

            buffer.seek(0)
            img_data = base64.b64encode(buffer.getvalue()).decode()
            return img_data
        except Exception as e:
            logger.error(f'Failed to convert image to base64: {e}')
            return ''

    @staticmethod
    def apply_adjustments(
        img: Image.Image,
        exposure: int = 0,
        contrast: int = 0,
        saturation: int = 0,
        sharpness: int = 0,
        temperature: int = 0,
    ) -> Image.Image:
        """Apply adjustment filters to image.

        Args:
            img: Input image
            exposure: Brightness adjustment (-100 to 100)
            contrast: Contrast adjustment (-100 to 100)
            saturation: Saturation adjustment (-100 to 100)
            sharpness: Sharpness adjustment (-100 to 100)
            temperature: Temperature adjustment (-100 to 100)

        Returns:
            Adjusted image
        """
        try:
            result = img.copy()

            # Brightness (exposure)
            if exposure != 0:
                enhancer = ImageEnhance.Brightness(result)
                factor = 1.0 + (exposure / 100.0)
                result = enhancer.enhance(factor)

            # Contrast
            if contrast != 0:
                enhancer = ImageEnhance.Contrast(result)
                factor = 1.0 + (contrast / 100.0)
                result = enhancer.enhance(factor)

            # Saturation
            if saturation != 0:
                enhancer = ImageEnhance.Color(result)
                factor = 1.0 + (saturation / 100.0)
                result = enhancer.enhance(factor)

            # Sharpness
            if sharpness != 0:
                enhancer = ImageEnhance.Sharpness(result)
                factor = 1.0 + (sharpness / 100.0)
                result = enhancer.enhance(factor)

            # Temperature (simplified: shift colors towards warm/cool)
            if temperature != 0:
                result = ImageProcessor._adjust_temperature(result, temperature)

            return result
        except Exception as e:
            logger.error(f'Failed to apply adjustments: {e}')
            return img

    @staticmethod
    def _adjust_temperature(img: Image.Image, adjustment: int) -> Image.Image:
        """Adjust image temperature (warm/cool).

        Args:
            img: Input image
            adjustment: Temperature adjustment (-100 to 100)
                       negative = cooler (more blue)
                       positive = warmer (more red/yellow)

        Returns:
            Adjusted image
        """
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Simple temperature adjustment by shifting color channels
        factor = adjustment / 100.0
        r, g, b = img.split()

        if factor > 0:  # Warmer
            r = r.point(lambda x: min(255, int(x * (1 + factor * 0.1))))
            b = b.point(lambda x: max(0, int(x * (1 - factor * 0.1))))
        else:  # Cooler
            factor = abs(factor)
            b = b.point(lambda x: min(255, int(x * (1 + factor * 0.1))))
            r = r.point(lambda x: max(0, int(x * (1 - factor * 0.1))))

        return Image.merge('RGB', (r, g, b))

    @staticmethod
    def crop(
        img: Image.Image,
        box: Tuple[int, int, int, int]
    ) -> Image.Image:
        """Crop image.

        Args:
            img: Input image
            box: Crop box (left, top, right, bottom)

        Returns:
            Cropped image
        """
        try:
            return img.crop(box)
        except Exception as e:
            logger.error(f'Failed to crop image: {e}')
            return img

    @staticmethod
    def resize(
        img: Image.Image,
        size: Tuple[int, int],
        maintain_aspect: bool = True
    ) -> Image.Image:
        """Resize image.

        Args:
            img: Input image
            size: Target size (width, height)
            maintain_aspect: Maintain aspect ratio

        Returns:
            Resized image
        """
        try:
            if maintain_aspect:
                img.thumbnail(size, Image.Resampling.LANCZOS)
            else:
                img = img.resize(size, Image.Resampling.LANCZOS)
            return img
        except Exception as e:
            logger.error(f'Failed to resize image: {e}')
            return img

    @staticmethod
    def rotate(img: Image.Image, angle: float) -> Image.Image:
        """Rotate image.

        Args:
            img: Input image
            angle: Rotation angle in degrees

        Returns:
            Rotated image
        """
        try:
            return img.rotate(angle, expand=True)
        except Exception as e:
            logger.error(f'Failed to rotate image: {e}')
            return img

    @staticmethod
    def flip(img: Image.Image, direction: str = 'h') -> Image.Image:
        """Flip image.

        Args:
            img: Input image
            direction: 'h' for horizontal, 'v' for vertical

        Returns:
            Flipped image
        """
        try:
            if direction == 'h':
                return img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            elif direction == 'v':
                return img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
            else:
                return img
        except Exception as e:
            logger.error(f'Failed to flip image: {e}')
            return img
