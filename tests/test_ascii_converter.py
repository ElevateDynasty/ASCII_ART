"""
Tests for ASCII Converter module.
"""

import pytest
from pathlib import Path
import tempfile
from PIL import Image
import numpy as np

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ascii_converter import (
    ASCIIConverter,
    ConversionSettings,
    convert_image,
    convert_to_emoji,
    image_to_ascii,
    image_to_emoji,
)
from character_sets import (
    CharacterSet,
    EmojiSet,
    CharacterMapper,
    get_charset_by_name,
    get_emoji_set_by_name,
)
from color_handler import ColorMode, RGB


@pytest.fixture
def sample_image():
    """Create a sample test image."""
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
        # Create a simple gradient image
        img = Image.new('RGB', (100, 100))
        pixels = img.load()
        for i in range(100):
            for j in range(100):
                gray = int((i + j) / 2 * 2.55)
                pixels[i, j] = (gray, gray, gray)
        img.save(f.name)
        yield f.name
    # Cleanup
    Path(f.name).unlink(missing_ok=True)


@pytest.fixture
def color_image():
    """Create a sample color test image."""
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
        img = Image.new('RGB', (50, 50))
        pixels = img.load()
        for i in range(50):
            for j in range(50):
                pixels[i, j] = (i * 5, j * 5, 128)
        img.save(f.name)
        yield f.name
    Path(f.name).unlink(missing_ok=True)


class TestCharacterMapper:
    """Tests for CharacterMapper class."""
    
    def test_default_charset(self):
        mapper = CharacterMapper()
        assert mapper.num_chars == len(CharacterSet.DETAILED.value)
    
    def test_custom_charset(self):
        mapper = CharacterMapper(charset=CharacterSet.SIMPLE)
        assert mapper.num_chars == len(CharacterSet.SIMPLE.value)
    
    def test_brightness_mapping(self):
        mapper = CharacterMapper(charset=CharacterSet.SIMPLE)
        # Dark should give first character
        dark_char = mapper.get_character(0)
        # Light should give last character
        light_char = mapper.get_character(255)
        assert dark_char == CharacterSet.SIMPLE.value[0]
        assert light_char == CharacterSet.SIMPLE.value[-1]
    
    def test_inverted_mapping(self):
        mapper = CharacterMapper(charset=CharacterSet.SIMPLE)
        normal = mapper.get_character(0)
        inverted = mapper.get_inverted_character(0)
        assert normal != inverted
    
    def test_emoji_mapper(self):
        mapper = CharacterMapper(
            emoji_set=EmojiSet.BRIGHTNESS,
            use_emoji=True
        )
        assert mapper.is_emoji
        char = mapper.get_character(128)
        assert char in EmojiSet.BRIGHTNESS.value


class TestCharsetHelpers:
    """Tests for charset helper functions."""
    
    def test_get_charset_by_name(self):
        assert get_charset_by_name("standard") == CharacterSet.STANDARD
        assert get_charset_by_name("detailed") == CharacterSet.DETAILED
        assert get_charset_by_name("invalid") == CharacterSet.DETAILED
    
    def test_get_emoji_set_by_name(self):
        assert get_emoji_set_by_name("hearts") == EmojiSet.HEARTS
        assert get_emoji_set_by_name("space") == EmojiSet.SPACE
        assert get_emoji_set_by_name("invalid") == EmojiSet.BRIGHTNESS


class TestRGB:
    """Tests for RGB color class."""
    
    def test_rgb_creation(self):
        color = RGB(255, 128, 0)
        assert color.r == 255
        assert color.g == 128
        assert color.b == 0
    
    def test_brightness_calculation(self):
        white = RGB(255, 255, 255)
        black = RGB(0, 0, 0)
        assert white.brightness() > black.brightness()
    
    def test_to_html(self):
        color = RGB(255, 128, 64)
        assert color.to_html() == "#ff8040"
    
    def test_to_ansi(self):
        color = RGB(255, 128, 64)
        ansi = color.to_ansi_fg()
        assert "38;2;255;128;64" in ansi
    
    def test_from_hex(self):
        color = RGB.from_hex("#ff8040")
        assert color.r == 255
        assert color.g == 128
        assert color.b == 64


class TestConversionSettings:
    """Tests for ConversionSettings dataclass."""
    
    def test_default_settings(self):
        settings = ConversionSettings()
        assert settings.width == 100
        assert settings.charset == CharacterSet.DETAILED
        assert settings.color_mode == ColorMode.NONE
        assert not settings.use_emoji
    
    def test_custom_settings(self):
        settings = ConversionSettings(
            width=50,
            charset=CharacterSet.SIMPLE,
            use_emoji=True,
            emoji_set=EmojiSet.HEARTS
        )
        assert settings.width == 50
        assert settings.charset == CharacterSet.SIMPLE
        assert settings.use_emoji
        assert settings.emoji_set == EmojiSet.HEARTS


class TestASCIIConverter:
    """Tests for ASCIIConverter class."""
    
    def test_basic_conversion(self, sample_image):
        converter = ASCIIConverter(sample_image)
        art = converter.convert(width=20)
        
        assert art.width == 20
        assert art.height > 0
        assert len(str(art)) > 0
    
    def test_conversion_with_settings(self, sample_image):
        settings = ConversionSettings(
            width=30,
            charset=CharacterSet.SIMPLE,
            contrast=1.5
        )
        
        converter = ASCIIConverter(sample_image)
        art = converter.convert(settings=settings)
        
        assert art.width == 30
        assert art.settings.contrast == 1.5
    
    def test_emoji_conversion(self, sample_image):
        converter = ASCIIConverter(sample_image)
        art = converter.convert(
            width=20,
            use_emoji=True,
            emoji_set=EmojiSet.BRIGHTNESS
        )
        
        assert art.is_emoji
        # Check that output contains emoji characters
        art_str = str(art)
        assert any(c in art_str for c in EmojiSet.BRIGHTNESS.value)
    
    def test_preview(self, sample_image):
        converter = ASCIIConverter(sample_image)
        preview = converter.preview(width=30)
        
        assert isinstance(preview, str)
        assert len(preview) > 0
    
    def test_preview_emoji(self, sample_image):
        converter = ASCIIConverter(sample_image)
        preview = converter.preview_emoji(width=20)
        
        assert isinstance(preview, str)
        assert len(preview) > 0


class TestConvenienceFunctions:
    """Tests for convenience conversion functions."""
    
    def test_convert_image(self, sample_image):
        art = convert_image(sample_image, width=25)
        assert art.width == 25
    
    def test_convert_to_emoji(self, sample_image):
        art = convert_to_emoji(sample_image, width=15, emoji_set="hearts")
        assert art.is_emoji
        assert art.width == 15
    
    def test_image_to_ascii(self, sample_image):
        result = image_to_ascii(sample_image, width=20)
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_image_to_emoji(self, sample_image):
        result = image_to_emoji(sample_image, width=15)
        assert isinstance(result, str)


class TestASCIIArtOutput:
    """Tests for ASCIIArt output class."""
    
    def test_save_text(self, sample_image, tmp_path):
        art = convert_image(sample_image, width=20)
        output_path = tmp_path / "output.txt"
        art.save(output_path)
        
        assert output_path.exists()
        content = output_path.read_text(encoding='utf-8')
        assert len(content) > 0
    
    def test_save_html(self, sample_image, tmp_path):
        art = convert_image(
            sample_image, 
            width=20, 
            color_mode=ColorMode.HTML
        )
        output_path = tmp_path / "output.html"
        art.save(output_path)
        
        assert output_path.exists()
        content = output_path.read_text(encoding='utf-8')
        assert "<html" in content.lower()
    
    def test_str_representation(self, sample_image):
        art = convert_image(sample_image, width=20)
        str_repr = str(art)
        assert isinstance(str_repr, str)
        assert len(str_repr) > 0
    
    def test_repr(self, sample_image):
        art = convert_image(sample_image, width=20)
        repr_str = repr(art)
        assert "ASCIIArt" in repr_str
        assert "width=" in repr_str


class TestColorModes:
    """Tests for different color output modes."""
    
    def test_no_color(self, color_image):
        art = convert_image(color_image, width=20, color_mode=ColorMode.NONE)
        assert not art.colored
    
    def test_ansi_color(self, color_image):
        art = convert_image(color_image, width=20, color_mode=ColorMode.ANSI)
        assert art.colored
        # Check for ANSI escape codes
        assert "\033[" in str(art)
    
    def test_html_color(self, color_image):
        art = convert_image(color_image, width=20, color_mode=ColorMode.HTML)
        assert art.colored
        # Check for HTML structure
        art_str = str(art)
        assert "<html" in art_str.lower()
        assert "color:" in art_str


class TestEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_nonexistent_image(self):
        with pytest.raises(FileNotFoundError):
            ASCIIConverter("nonexistent_image.png")
    
    def test_very_small_width(self, sample_image):
        art = convert_image(sample_image, width=1)
        assert art.width >= 1
    
    def test_very_large_width(self, sample_image):
        art = convert_image(sample_image, width=500)
        assert art.width == 500
    
    def test_invert_option(self, sample_image):
        normal = convert_image(sample_image, width=20, invert=False)
        inverted = convert_image(sample_image, width=20, invert=True)
        # Output should be different
        assert str(normal) != str(inverted)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
