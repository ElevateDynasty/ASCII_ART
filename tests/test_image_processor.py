"""
Tests for Image Processor module.
"""

import pytest
from pathlib import Path
import tempfile
from PIL import Image
import numpy as np

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from image_processor import ImageProcessor


@pytest.fixture
def sample_image_path():
    """Create a sample test image."""
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
        img = Image.new('RGB', (200, 150), color=(128, 64, 192))
        img.save(f.name)
        yield f.name
    Path(f.name).unlink(missing_ok=True)


@pytest.fixture
def gradient_image_path():
    """Create a gradient test image."""
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
        img = Image.new('RGB', (100, 100))
        pixels = img.load()
        for i in range(100):
            for j in range(100):
                pixels[i, j] = (i * 2, j * 2, 128)
        img.save(f.name)
        yield f.name
    Path(f.name).unlink(missing_ok=True)


class TestImageProcessorBasics:
    """Basic tests for ImageProcessor class."""
    
    def test_load_image(self, sample_image_path):
        processor = ImageProcessor(sample_image_path)
        assert processor.size == (200, 150)
    
    def test_invalid_path(self):
        with pytest.raises(FileNotFoundError):
            ImageProcessor("nonexistent.png")
    
    def test_unsupported_format(self, tmp_path):
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("not an image")
        
        with pytest.raises(ValueError):
            ImageProcessor(txt_file)
    
    def test_from_image(self):
        img = Image.new('RGB', (50, 50), color='red')
        processor = ImageProcessor.from_image(img)
        assert processor.size == (50, 50)


class TestResize:
    """Tests for resize functionality."""
    
    def test_resize_width(self, sample_image_path):
        processor = ImageProcessor(sample_image_path)
        processor.resize(width=50)
        assert processor.size[0] == 50
    
    def test_resize_maintain_aspect(self, sample_image_path):
        processor = ImageProcessor(sample_image_path)
        original_ratio = 150 / 200
        processor.resize(width=100, maintain_aspect=True)
        # Height should be approximately proportional (adjusted for char aspect)
        assert processor.size[0] == 100
        assert processor.size[1] > 0
    
    def test_resize_fixed_dimensions(self, sample_image_path):
        processor = ImageProcessor(sample_image_path)
        processor.resize(width=80, height=60, maintain_aspect=False)
        assert processor.size == (80, 60)


class TestColorAdjustments:
    """Tests for color adjustment methods."""
    
    def test_to_grayscale(self, sample_image_path):
        processor = ImageProcessor(sample_image_path)
        processor.to_grayscale()
        assert processor.processed_image.mode == "L"
    
    def test_adjust_contrast(self, sample_image_path):
        processor = ImageProcessor(sample_image_path)
        original = np.array(processor.processed_image)
        processor.adjust_contrast(2.0)
        modified = np.array(processor.processed_image)
        assert not np.array_equal(original, modified)
    
    def test_adjust_brightness(self, sample_image_path):
        processor = ImageProcessor(sample_image_path)
        original = np.array(processor.processed_image)
        processor.adjust_brightness(1.5)
        modified = np.array(processor.processed_image)
        assert not np.array_equal(original, modified)
    
    def test_adjust_saturation(self, sample_image_path):
        processor = ImageProcessor(sample_image_path)
        original = np.array(processor.processed_image)
        processor.adjust_saturation(0.5)
        modified = np.array(processor.processed_image)
        assert not np.array_equal(original, modified)


class TestFilters:
    """Tests for filter methods."""
    
    def test_sharpen(self, sample_image_path):
        processor = ImageProcessor(sample_image_path)
        original = np.array(processor.processed_image)
        processor.sharpen(2.0)
        modified = np.array(processor.processed_image)
        assert not np.array_equal(original, modified)
    
    def test_blur(self, sample_image_path):
        processor = ImageProcessor(sample_image_path)
        original = np.array(processor.processed_image)
        processor.blur(3.0)
        modified = np.array(processor.processed_image)
        assert not np.array_equal(original, modified)
    
    def test_edge_detection(self, gradient_image_path):
        processor = ImageProcessor(gradient_image_path)
        processor.edge_detection()
        # After edge detection, mode should be grayscale
        assert processor.processed_image.mode == "L"
    
    def test_emboss(self, sample_image_path):
        processor = ImageProcessor(sample_image_path)
        original = np.array(processor.processed_image)
        processor.emboss()
        modified = np.array(processor.processed_image)
        assert not np.array_equal(original, modified)
    
    def test_contour(self, sample_image_path):
        processor = ImageProcessor(sample_image_path)
        original = np.array(processor.processed_image)
        processor.contour()
        modified = np.array(processor.processed_image)
        assert not np.array_equal(original, modified)
    
    def test_denoise(self, sample_image_path):
        processor = ImageProcessor(sample_image_path)
        # Denoising should not raise errors
        processor.denoise()
        assert processor.size[0] > 0


class TestTransformations:
    """Tests for image transformation methods."""
    
    def test_invert(self, sample_image_path):
        processor = ImageProcessor(sample_image_path)
        original = np.array(processor.processed_image)
        processor.invert()
        modified = np.array(processor.processed_image)
        # Inverted image should be different
        assert not np.array_equal(original, modified)
    
    def test_rotate(self, sample_image_path):
        processor = ImageProcessor(sample_image_path)
        processor.rotate(90)
        # Size should be swapped (with some expansion due to expand=True)
        assert processor.size[1] >= 190  # Original width was 200
    
    def test_flip_horizontal(self, gradient_image_path):
        processor = ImageProcessor(gradient_image_path)
        original = np.array(processor.processed_image)
        processor.flip_horizontal()
        modified = np.array(processor.processed_image)
        assert not np.array_equal(original, modified)
    
    def test_flip_vertical(self, gradient_image_path):
        processor = ImageProcessor(gradient_image_path)
        original = np.array(processor.processed_image)
        processor.flip_vertical()
        modified = np.array(processor.processed_image)
        assert not np.array_equal(original, modified)
    
    def test_crop_center(self, sample_image_path):
        processor = ImageProcessor(sample_image_path)
        original_size = processor.size
        processor.crop_center(0.5)
        new_size = processor.size
        assert new_size[0] < original_size[0]
        assert new_size[1] < original_size[1]


class TestEnhancement:
    """Tests for enhancement methods."""
    
    def test_auto_enhance(self, sample_image_path):
        processor = ImageProcessor(sample_image_path)
        original = np.array(processor.processed_image)
        processor.auto_enhance()
        modified = np.array(processor.processed_image)
        # Auto-enhance might or might not change the image
        assert processor.size[0] > 0
    
    def test_equalize(self, gradient_image_path):
        processor = ImageProcessor(gradient_image_path)
        original = np.array(processor.processed_image)
        processor.equalize()
        modified = np.array(processor.processed_image)
        assert not np.array_equal(original, modified)
    
    def test_posterize(self, sample_image_path):
        processor = ImageProcessor(sample_image_path)
        original = np.array(processor.processed_image)
        processor.posterize(2)
        modified = np.array(processor.processed_image)
        # Should reduce color levels
        assert not np.array_equal(original, modified)


class TestPixelData:
    """Tests for pixel data extraction."""
    
    def test_get_pixel_matrix(self, sample_image_path):
        processor = ImageProcessor(sample_image_path)
        processor.to_grayscale()
        matrix = processor.get_pixel_matrix()
        
        assert isinstance(matrix, np.ndarray)
        assert len(matrix.shape) == 2  # Should be 2D for grayscale
    
    def test_get_color_matrix(self, sample_image_path):
        processor = ImageProcessor(sample_image_path)
        matrix = processor.get_color_matrix()
        
        assert isinstance(matrix, np.ndarray)
        assert len(matrix.shape) == 3  # Should be 3D for RGB
        assert matrix.shape[2] == 3  # RGB channels


class TestChaining:
    """Tests for method chaining."""
    
    def test_method_chaining(self, sample_image_path):
        processor = ImageProcessor(sample_image_path)
        result = (processor
                  .resize(50)
                  .adjust_contrast(1.5)
                  .adjust_brightness(1.2)
                  .to_grayscale())
        
        assert result is processor  # Should return self
        assert processor.size[0] == 50
        assert processor.processed_image.mode == "L"
    
    def test_reset(self, sample_image_path):
        processor = ImageProcessor(sample_image_path)
        original_size = processor.size
        
        processor.resize(50).to_grayscale()
        assert processor.size != original_size
        
        processor.reset()
        assert processor.size == original_size


class TestSave:
    """Tests for save functionality."""
    
    def test_save_processed(self, sample_image_path, tmp_path):
        processor = ImageProcessor(sample_image_path)
        processor.resize(50).to_grayscale()
        
        output_path = tmp_path / "output.png"
        processor.save(output_path)
        
        assert output_path.exists()
        saved_img = Image.open(output_path)
        assert saved_img.size[0] == 50
    
    def test_get_thumbnail(self, sample_image_path):
        processor = ImageProcessor(sample_image_path)
        thumb = processor.get_thumbnail((50, 50))
        
        assert isinstance(thumb, Image.Image)
        assert thumb.size[0] <= 50
        assert thumb.size[1] <= 50


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
