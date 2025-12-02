"""
Image processing utilities using Pillow and OpenCV.
"""

from pathlib import Path
from typing import Tuple, Optional, Union
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

try:
    import cv2
    HAS_OPENCV = True
except ImportError:
    HAS_OPENCV = False


class ImageProcessor:
    """Handles image loading, processing, and optimization."""
    
    SUPPORTED_FORMATS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.tiff', '.ico'}
    
    def __init__(self, image_path: Union[str, Path]):
        self.image_path = Path(image_path)
        self._validate_image()
        self.original_image = Image.open(self.image_path).convert("RGB")
        self.processed_image = self.original_image.copy()
    
    @classmethod
    def from_image(cls, image: Image.Image) -> "ImageProcessor":
        """Create processor from an existing PIL Image."""
        processor = object.__new__(cls)
        processor.image_path = None
        processor.original_image = image.convert("RGB")
        processor.processed_image = processor.original_image.copy()
        return processor
    
    def _validate_image(self) -> None:
        """Validate image file exists and is supported."""
        if not self.image_path.exists():
            raise FileNotFoundError(f"Image not found: {self.image_path}")
        if self.image_path.suffix.lower() not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {self.image_path.suffix}")
    
    def resize(
        self, 
        width: int = 100, 
        height: Optional[int] = None,
        maintain_aspect: bool = True,
        char_aspect_ratio: float = 0.5
    ) -> "ImageProcessor":
        """
        Resize image for ASCII conversion.
        
        Args:
            width: Target width in characters
            height: Target height (auto-calculated if None)
            maintain_aspect: Whether to maintain aspect ratio
            char_aspect_ratio: Character height/width ratio (0.5 for ASCII, 1.0 for emoji)
        """
        original_width, original_height = self.processed_image.size
        
        if maintain_aspect:
            # Calculate proper aspect ratio
            # ASCII chars are typically ~2x taller than wide (height/width ≈ 2)
            # Emoji are approximately square (height/width ≈ 1)
            image_aspect = original_height / original_width
            height = int(width * image_aspect * char_aspect_ratio)
        elif height is None:
            height = width
        
        # Ensure minimum dimensions
        height = max(1, height)
        width = max(1, width)
        
        self.processed_image = self.processed_image.resize(
            (width, height), 
            Image.Resampling.LANCZOS
        )
        return self
    
    def to_grayscale(self) -> "ImageProcessor":
        """Convert image to grayscale."""
        self.processed_image = self.processed_image.convert("L")
        return self
    
    def adjust_contrast(self, factor: float = 1.5) -> "ImageProcessor":
        """
        Adjust image contrast for better ASCII output.
        
        Args:
            factor: Contrast multiplier (1.0 = no change)
        """
        enhancer = ImageEnhance.Contrast(self.processed_image)
        self.processed_image = enhancer.enhance(factor)
        return self
    
    def adjust_brightness(self, factor: float = 1.0) -> "ImageProcessor":
        """Adjust image brightness."""
        enhancer = ImageEnhance.Brightness(self.processed_image)
        self.processed_image = enhancer.enhance(factor)
        return self
    
    def adjust_saturation(self, factor: float = 1.0) -> "ImageProcessor":
        """Adjust image saturation."""
        enhancer = ImageEnhance.Color(self.processed_image)
        self.processed_image = enhancer.enhance(factor)
        return self
    
    def sharpen(self, factor: float = 1.5) -> "ImageProcessor":
        """Sharpen image for clearer edges."""
        enhancer = ImageEnhance.Sharpness(self.processed_image)
        self.processed_image = enhancer.enhance(factor)
        return self
    
    def blur(self, radius: float = 2.0) -> "ImageProcessor":
        """Apply Gaussian blur."""
        self.processed_image = self.processed_image.filter(
            ImageFilter.GaussianBlur(radius=radius)
        )
        return self
    
    def edge_detection(self) -> "ImageProcessor":
        """Apply edge detection for outline-style ASCII art."""
        if HAS_OPENCV:
            # Convert to numpy array for OpenCV processing
            img_array = np.array(self.processed_image.convert("L"))
            
            # Apply Canny edge detection
            edges = cv2.Canny(img_array, 100, 200)
            
            # Invert so edges are dark
            edges = 255 - edges
            
            self.processed_image = Image.fromarray(edges)
        else:
            # Fallback to PIL edge detection
            self.processed_image = self.processed_image.convert("L").filter(
                ImageFilter.FIND_EDGES
            )
            self.processed_image = ImageOps.invert(self.processed_image)
        
        return self
    
    def emboss(self) -> "ImageProcessor":
        """Apply emboss effect."""
        self.processed_image = self.processed_image.filter(ImageFilter.EMBOSS)
        return self
    
    def contour(self) -> "ImageProcessor":
        """Apply contour effect."""
        self.processed_image = self.processed_image.filter(ImageFilter.CONTOUR)
        return self
    
    def posterize(self, bits: int = 4) -> "ImageProcessor":
        """Reduce color levels for a poster effect."""
        self.processed_image = ImageOps.posterize(self.processed_image.convert("RGB"), bits)
        return self
    
    def denoise(self) -> "ImageProcessor":
        """Remove noise from image."""
        if HAS_OPENCV:
            img_array = np.array(self.processed_image)
            
            if len(img_array.shape) == 2:
                # Grayscale
                denoised = cv2.bilateralFilter(img_array, 9, 75, 75)
            else:
                # Color
                denoised = cv2.bilateralFilter(img_array, 9, 75, 75)
            
            self.processed_image = Image.fromarray(denoised)
        else:
            # Fallback to slight blur for denoising
            self.processed_image = self.processed_image.filter(
                ImageFilter.MedianFilter(size=3)
            )
        
        return self
    
    def auto_enhance(self) -> "ImageProcessor":
        """Apply automatic contrast and brightness enhancement."""
        self.processed_image = ImageOps.autocontrast(self.processed_image)
        return self
    
    def equalize(self) -> "ImageProcessor":
        """Apply histogram equalization."""
        if self.processed_image.mode == "RGB":
            self.processed_image = ImageOps.equalize(self.processed_image)
        else:
            self.processed_image = ImageOps.equalize(self.processed_image.convert("L"))
        return self
    
    def invert(self) -> "ImageProcessor":
        """Invert image colors."""
        if self.processed_image.mode == "RGBA":
            # Handle RGBA separately
            r, g, b, a = self.processed_image.split()
            rgb = Image.merge("RGB", (r, g, b))
            rgb = ImageOps.invert(rgb)
            r, g, b = rgb.split()
            self.processed_image = Image.merge("RGBA", (r, g, b, a))
        else:
            self.processed_image = ImageOps.invert(self.processed_image.convert("RGB"))
        return self
    
    def rotate(self, angle: float) -> "ImageProcessor":
        """Rotate image by angle degrees."""
        self.processed_image = self.processed_image.rotate(angle, expand=True)
        return self
    
    def flip_horizontal(self) -> "ImageProcessor":
        """Flip image horizontally."""
        self.processed_image = self.processed_image.transpose(Image.FLIP_LEFT_RIGHT)
        return self
    
    def flip_vertical(self) -> "ImageProcessor":
        """Flip image vertically."""
        self.processed_image = self.processed_image.transpose(Image.FLIP_TOP_BOTTOM)
        return self
    
    def crop_center(self, ratio: float = 0.8) -> "ImageProcessor":
        """Crop to center portion of image."""
        width, height = self.processed_image.size
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        
        left = (width - new_width) // 2
        top = (height - new_height) // 2
        right = left + new_width
        bottom = top + new_height
        
        self.processed_image = self.processed_image.crop((left, top, right, bottom))
        return self
    
    def get_pixel_matrix(self) -> np.ndarray:
        """Get pixel values as numpy array."""
        if self.processed_image.mode != "L":
            return np.array(self.processed_image.convert("L"))
        return np.array(self.processed_image)
    
    def get_color_matrix(self) -> np.ndarray:
        """Get RGB color values for colored ASCII output."""
        rgb_image = self.original_image.convert("RGB")
        resized = rgb_image.resize(self.processed_image.size, Image.Resampling.LANCZOS)
        return np.array(resized)
    
    @property
    def size(self) -> Tuple[int, int]:
        """Get current image dimensions."""
        return self.processed_image.size
    
    def reset(self) -> "ImageProcessor":
        """Reset to original image."""
        self.processed_image = self.original_image.copy()
        return self
    
    def save(self, path: Union[str, Path]) -> None:
        """Save processed image to file."""
        self.processed_image.save(path)
    
    def get_thumbnail(self, size: Tuple[int, int] = (100, 100)) -> Image.Image:
        """Get a thumbnail of the processed image."""
        thumb = self.processed_image.copy()
        thumb.thumbnail(size, Image.Resampling.LANCZOS)
        return thumb
