"""
ASCII Art Generator - Convert images to ASCII art and emoji art.
"""

from .ascii_converter import (
    ASCIIConverter,
    ASCIIArt,
    ConversionSettings,
    convert_image,
    convert_to_emoji,
    image_to_ascii,
    image_to_emoji,
)
from .character_sets import (
    CharacterSet,
    EmojiSet,
    CharacterMapper,
    get_charset_by_name,
    get_emoji_set_by_name,
    list_available_charsets,
    list_available_emoji_sets,
)
from .color_handler import (
    RGB,
    ColorMode,
    ColorHandler,
    quantize_color,
)
from .image_processor import ImageProcessor
from .gui import ASCIIArtGUI


__version__ = "1.0.0"
__author__ = "ASCII Art Generator"
__all__ = [
    # Main converter
    "ASCIIConverter",
    "ASCIIArt",
    "ConversionSettings",
    "convert_image",
    "convert_to_emoji",
    "image_to_ascii",
    "image_to_emoji",
    
    # Character sets
    "CharacterSet",
    "EmojiSet",
    "CharacterMapper",
    "get_charset_by_name",
    "get_emoji_set_by_name",
    "list_available_charsets",
    "list_available_emoji_sets",
    
    # Colors
    "RGB",
    "ColorMode",
    "ColorHandler",
    "quantize_color",
    
    # Image processing
    "ImageProcessor",
]
