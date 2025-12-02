"""
Core ASCII art conversion engine with emoji support.
"""

from pathlib import Path
from typing import Optional, Union, List
from dataclasses import dataclass, field
import numpy as np

from .image_processor import ImageProcessor
from .character_sets import (
    CharacterMapper, CharacterSet, EmojiSet,
    get_charset_by_name, get_emoji_set_by_name
)
from .color_handler import ColorHandler, ColorMode, RGB


@dataclass
class ConversionSettings:
    """Configuration for ASCII art conversion."""
    width: int = 100
    height: Optional[int] = None
    charset: CharacterSet = CharacterSet.DETAILED
    color_mode: ColorMode = ColorMode.NONE
    invert: bool = False
    contrast: float = 1.2
    brightness: float = 1.0
    edge_detection: bool = False
    denoise: bool = True
    
    # Emoji settings
    use_emoji: bool = False
    emoji_set: EmojiSet = EmojiSet.BRIGHTNESS
    color_emoji: bool = False  # Use color-based emoji mapping
    
    # Advanced settings
    dithering: bool = False
    sharpen: float = 1.0
    auto_enhance: bool = False


@dataclass
class ASCIIArt:
    """Container for generated ASCII art."""
    art: str
    width: int
    height: int
    colored: bool
    is_emoji: bool
    settings: ConversionSettings
    
    def save(self, filepath: Union[str, Path]) -> None:
        """Save ASCII art to file."""
        filepath = Path(filepath)
        
        # Determine file extension based on color mode
        if self.colored and self.settings.color_mode in (ColorMode.HTML, ColorMode.HTML_BG):
            if filepath.suffix.lower() != '.html':
                filepath = filepath.with_suffix('.html')
        elif not filepath.suffix:
            filepath = filepath.with_suffix('.txt')
        
        # Ensure parent directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        filepath.write_text(self.art, encoding='utf-8')
        print(f"✅ Saved to: {filepath}")
    
    def print(self) -> None:
        """Print the ASCII art to console."""
        print(self.art)
    
    def __str__(self) -> str:
        return self.art
    
    def __repr__(self) -> str:
        return f"ASCIIArt(width={self.width}, height={self.height}, emoji={self.is_emoji})"


class ASCIIConverter:
    """
    Main converter class for generating ASCII art from images.
    
    Supports both traditional ASCII characters and emoji output.
    
    Example:
        converter = ASCIIConverter("image.png")
        
        # Traditional ASCII
        art = converter.convert(width=80)
        print(art)
        
        # Emoji art
        art = converter.convert(width=50, use_emoji=True, emoji_set="hearts")
        print(art)
    """
    
    def __init__(self, image_path: Union[str, Path]):
        self.image_path = Path(image_path)
        self.processor: Optional[ImageProcessor] = None
        self.settings: Optional[ConversionSettings] = None
    
    def convert(
        self,
        settings: Optional[ConversionSettings] = None,
        **kwargs
    ) -> ASCIIArt:
        """
        Convert image to ASCII art.
        
        Args:
            settings: Conversion settings object
            **kwargs: Override individual settings
            
        Returns:
            ASCIIArt object containing the result
        """
        # Build settings
        if settings is None:
            settings = ConversionSettings()
        
        # Handle string-based charset/emoji_set names
        if 'charset' in kwargs and isinstance(kwargs['charset'], str):
            kwargs['charset'] = get_charset_by_name(kwargs['charset'])
        if 'emoji_set' in kwargs and isinstance(kwargs['emoji_set'], str):
            kwargs['emoji_set'] = get_emoji_set_by_name(kwargs['emoji_set'])
        if 'color_mode' in kwargs and isinstance(kwargs['color_mode'], str):
            kwargs['color_mode'] = ColorMode(kwargs['color_mode'])
        
        # Override with any provided kwargs
        for key, value in kwargs.items():
            if hasattr(settings, key):
                setattr(settings, key, value)
        
        self.settings = settings
        
        # Process image
        self.processor = ImageProcessor(self.image_path)
        self._apply_preprocessing()
        
        # Generate ASCII
        ascii_lines = self._generate_ascii()
        
        # Apply color formatting
        color_handler = ColorHandler(settings.color_mode)
        formatted_art = color_handler.wrap_output(
            '\n'.join(ascii_lines),
            is_emoji=settings.use_emoji
        )
        
        return ASCIIArt(
            art=formatted_art,
            width=self.processor.size[0],
            height=self.processor.size[1],
            colored=settings.color_mode != ColorMode.NONE,
            is_emoji=settings.use_emoji,
            settings=settings
        )
    
    def _apply_preprocessing(self) -> None:
        """Apply image preprocessing based on settings."""
        settings = self.settings
        
        # Apply denoising early (on full resolution image)
        if settings.denoise:
            self.processor.denoise()
        
        # Adjust contrast and brightness before resize for better quality
        if settings.contrast != 1.0:
            self.processor.adjust_contrast(settings.contrast)
        
        if settings.brightness != 1.0:
            self.processor.adjust_brightness(settings.brightness)
        
        # Auto enhance
        if settings.auto_enhance:
            self.processor.auto_enhance()
        
        # Sharpen before resize
        if settings.sharpen != 1.0:
            self.processor.sharpen(settings.sharpen)
        
        # Resize with proper aspect ratio for ASCII vs emoji
        # Emoji characters are roughly square, ASCII chars are taller than wide
        char_aspect = 1.0 if settings.use_emoji else 0.5
        self.processor.resize(
            width=settings.width,
            height=settings.height,
            maintain_aspect=settings.height is None,
            char_aspect_ratio=char_aspect
        )
        
        # Edge detection mode (not for emoji)
        if settings.edge_detection and not settings.use_emoji:
            self.processor.edge_detection()
        elif not settings.use_emoji:
            self.processor.to_grayscale()
    
    def _generate_ascii(self) -> List[str]:
        """Generate ASCII art lines from processed image."""
        settings = self.settings
        
        # Get pixel data
        grayscale_matrix = self.processor.get_pixel_matrix()
        
        # Get color data if needed
        color_matrix = None
        if settings.color_mode != ColorMode.NONE or settings.color_emoji:
            color_matrix = self.processor.get_color_matrix()
        
        # Setup character mapper
        mapper = CharacterMapper(
            charset=settings.charset,
            emoji_set=settings.emoji_set if settings.use_emoji else None,
            use_emoji=settings.use_emoji
        )
        
        # Setup color handler
        color_handler = ColorHandler(settings.color_mode)
        
        # Generate ASCII
        lines = []
        height, width = grayscale_matrix.shape[:2]
        
        for y in range(height):
            line_chars = []
            for x in range(width):
                # Get brightness
                brightness = float(grayscale_matrix[y, x])
                
                # Get character or emoji
                if settings.use_emoji and settings.color_emoji and color_matrix is not None:
                    # Color-based emoji mapping
                    r, g, b = color_matrix[y, x]
                    char = mapper.get_colored_emoji(int(r), int(g), int(b))
                elif settings.invert:
                    char = mapper.get_inverted_character(brightness)
                else:
                    char = mapper.get_character(brightness)
                
                # Apply color if enabled (for non-emoji)
                if color_matrix is not None and settings.color_mode != ColorMode.NONE:
                    r, g, b = color_matrix[y, x]
                    color = RGB(int(r), int(g), int(b))
                    
                    if settings.use_emoji:
                        char = color_handler.format_emoji(char, color)
                    else:
                        char = color_handler.format_character(char, color)
                
                line_chars.append(char)
            
            line = ''.join(line_chars)
            line = color_handler.format_line(line) if settings.color_mode in (ColorMode.HTML, ColorMode.HTML_BG) else line
            lines.append(line)
        
        return lines
    
    def preview(self, width: int = 60) -> str:
        """Generate a quick preview with default settings."""
        art = self.convert(width=width, color_mode=ColorMode.NONE)
        return str(art)
    
    def preview_emoji(self, width: int = 40, emoji_set: str = "brightness") -> str:
        """Generate a quick emoji preview."""
        art = self.convert(
            width=width,
            use_emoji=True,
            emoji_set=get_emoji_set_by_name(emoji_set)
        )
        return str(art)


def convert_image(
    image_path: Union[str, Path],
    output_path: Optional[Union[str, Path]] = None,
    **settings
) -> ASCIIArt:
    """
    Convenience function for quick conversion.
    
    Args:
        image_path: Path to input image
        output_path: Optional path to save output
        **settings: Conversion settings
        
    Returns:
        Generated ASCII art
    """
    converter = ASCIIConverter(image_path)
    art = converter.convert(**settings)
    
    if output_path:
        art.save(output_path)
    
    return art


def convert_to_emoji(
    image_path: Union[str, Path],
    output_path: Optional[Union[str, Path]] = None,
    emoji_set: str = "brightness",
    width: int = 50,
    **settings
) -> ASCIIArt:
    """
    Convenience function for emoji art conversion.
    
    Args:
        image_path: Path to input image
        output_path: Optional path to save output
        emoji_set: Name of emoji set to use
        width: Output width
        **settings: Additional conversion settings
        
    Returns:
        Generated emoji art
    """
    converter = ASCIIConverter(image_path)
    art = converter.convert(
        use_emoji=True,
        emoji_set=get_emoji_set_by_name(emoji_set),
        width=width,
        **settings
    )
    
    if output_path:
        art.save(output_path)
    
    return art


# Quick conversion functions
def image_to_ascii(image_path: str, width: int = 80) -> str:
    """Quick function to convert image to ASCII string."""
    return str(convert_image(image_path, width=width))


def image_to_emoji(image_path: str, width: int = 40, emoji_set: str = "brightness") -> str:
    """Quick function to convert image to emoji string."""
    return str(convert_to_emoji(image_path, width=width, emoji_set=emoji_set))
