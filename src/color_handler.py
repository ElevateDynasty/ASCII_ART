"""
Color handling for terminal and HTML ASCII art output.
"""

from typing import Tuple, Optional
from enum import Enum
from dataclasses import dataclass
import colorsys


@dataclass
class RGB:
    """RGB color representation."""
    r: int
    g: int
    b: int
    
    def to_ansi_fg(self) -> str:
        """Convert to ANSI foreground color code."""
        return f"\033[38;2;{self.r};{self.g};{self.b}m"
    
    def to_ansi_bg(self) -> str:
        """Convert to ANSI background color code."""
        return f"\033[48;2;{self.r};{self.g};{self.b}m"
    
    def to_html(self) -> str:
        """Convert to HTML hex color."""
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"
    
    def to_tuple(self) -> Tuple[int, int, int]:
        """Convert to tuple."""
        return (self.r, self.g, self.b)
    
    def brightness(self) -> float:
        """Calculate perceived brightness (0-255)."""
        # Using relative luminance formula
        return 0.299 * self.r + 0.587 * self.g + 0.114 * self.b
    
    def to_hsl(self) -> Tuple[float, float, float]:
        """Convert to HSL color space."""
        r, g, b = self.r / 255, self.g / 255, self.b / 255
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        return (h * 360, s * 100, l * 100)
    
    def to_hsv(self) -> Tuple[float, float, float]:
        """Convert to HSV color space."""
        r, g, b = self.r / 255, self.g / 255, self.b / 255
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        return (h * 360, s * 100, v * 100)
    
    def get_complementary(self) -> "RGB":
        """Get complementary color."""
        return RGB(255 - self.r, 255 - self.g, 255 - self.b)
    
    def get_grayscale(self) -> "RGB":
        """Convert to grayscale."""
        gray = int(self.brightness())
        return RGB(gray, gray, gray)
    
    @classmethod
    def from_hex(cls, hex_color: str) -> "RGB":
        """Create RGB from hex string."""
        hex_color = hex_color.lstrip('#')
        return cls(
            r=int(hex_color[0:2], 16),
            g=int(hex_color[2:4], 16),
            b=int(hex_color[4:6], 16)
        )
    
    @classmethod
    def from_hsl(cls, h: float, s: float, l: float) -> "RGB":
        """Create RGB from HSL values."""
        h, s, l = h / 360, s / 100, l / 100
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        return cls(int(r * 255), int(g * 255), int(b * 255))


class ColorMode(Enum):
    """Output color modes."""
    NONE = "none"           # No color (plain text)
    ANSI = "ansi"           # Terminal ANSI colors
    ANSI_BG = "ansi_bg"     # ANSI with background colors
    HTML = "html"           # HTML output with colors
    HTML_BG = "html_bg"     # HTML with background colors


class ColorHandler:
    """Handles color conversion and output formatting."""
    
    RESET = "\033[0m"
    
    def __init__(self, mode: ColorMode = ColorMode.NONE):
        self.mode = mode
    
    def format_character(
        self, 
        char: str, 
        color: Optional[RGB] = None
    ) -> str:
        """
        Format a character with color if applicable.
        
        Args:
            char: ASCII character
            color: RGB color for the character
            
        Returns:
            Formatted string with color codes if applicable
        """
        if color is None or self.mode == ColorMode.NONE:
            return char
        
        if self.mode == ColorMode.ANSI:
            return f"{color.to_ansi_fg()}{char}{self.RESET}"
        
        elif self.mode == ColorMode.ANSI_BG:
            # Use contrasting text color for readability
            text_color = RGB(255, 255, 255) if color.brightness() < 128 else RGB(0, 0, 0)
            return f"{color.to_ansi_bg()}{text_color.to_ansi_fg()}{char}{self.RESET}"
        
        elif self.mode == ColorMode.HTML:
            # Escape HTML special characters
            if char == '<':
                char = '&lt;'
            elif char == '>':
                char = '&gt;'
            elif char == '&':
                char = '&amp;'
            elif char == '"':
                char = '&quot;'
            elif char == ' ':
                char = '&nbsp;'
            return f'<span style="color:{color.to_html()}">{char}</span>'
        
        elif self.mode == ColorMode.HTML_BG:
            text_color = "#ffffff" if color.brightness() < 128 else "#000000"
            if char == ' ':
                char = '&nbsp;'
            return f'<span style="background:{color.to_html()};color:{text_color}">{char}</span>'
        
        return char
    
    def format_emoji(self, emoji: str, color: Optional[RGB] = None) -> str:
        """
        Format an emoji (colors don't apply to emojis in most cases).
        
        Args:
            emoji: Emoji character
            color: Optional color (mostly ignored for emojis)
            
        Returns:
            Formatted emoji string
        """
        if self.mode in (ColorMode.HTML, ColorMode.HTML_BG):
            return f'<span class="emoji">{emoji}</span>'
        return emoji
    
    def format_line(self, line: str) -> str:
        """Format a complete line (for HTML mode, wrap in div)."""
        if self.mode in (ColorMode.HTML, ColorMode.HTML_BG):
            return f'<div class="ascii-line">{line}</div>'
        return line
    
    def wrap_output(self, content: str, is_emoji: bool = False) -> str:
        """Wrap complete output (for HTML mode, add full structure)."""
        if self.mode in (ColorMode.HTML, ColorMode.HTML_BG):
            font_size = "16px" if is_emoji else "10px"
            line_height = "18px" if is_emoji else "10px"
            letter_spacing = "2px" if is_emoji else "0px"
            
            return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ASCII Art</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            background: #1a1a2e;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }}
        .ascii-container {{
            background: #16213e;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
            overflow-x: auto;
        }}
        .ascii-art {{
            font-family: 'Courier New', 'Monaco', 'Menlo', monospace;
            font-size: {font_size};
            line-height: {line_height};
            letter-spacing: {letter_spacing};
            white-space: pre;
        }}
        .ascii-line {{
            display: block;
        }}
        .emoji {{
            display: inline;
        }}
    </style>
</head>
<body>
    <div class="ascii-container">
        <div class="ascii-art">
{content}
        </div>
    </div>
</body>
</html>"""
        return content


def quantize_color(color: RGB, levels: int = 8) -> RGB:
    """
    Reduce color to fewer levels for cleaner output.
    
    Args:
        color: Original RGB color
        levels: Number of levels per channel
    """
    step = 256 // levels
    return RGB(
        r=(color.r // step) * step,
        g=(color.g // step) * step,
        b=(color.b // step) * step
    )


def get_dominant_color_name(color: RGB) -> str:
    """Get the name of the dominant color."""
    h, s, l = color.to_hsl()
    
    if l < 15:
        return "black"
    elif l > 85:
        return "white"
    elif s < 15:
        return "gray"
    
    # Determine hue-based color
    if h < 15 or h >= 345:
        return "red"
    elif h < 45:
        return "orange"
    elif h < 75:
        return "yellow"
    elif h < 150:
        return "green"
    elif h < 210:
        return "cyan"
    elif h < 270:
        return "blue"
    elif h < 330:
        return "purple"
    else:
        return "red"


# Predefined color palettes
class ColorPalette:
    """Predefined color palettes for ASCII art."""
    
    GRAYSCALE = [RGB(i, i, i) for i in range(0, 256, 32)]
    
    RETRO = [
        RGB(0, 0, 0),
        RGB(157, 157, 157),
        RGB(255, 255, 255),
        RGB(190, 38, 51),
        RGB(224, 111, 139),
        RGB(73, 60, 43),
        RGB(164, 100, 34),
        RGB(235, 137, 49),
        RGB(247, 226, 107),
        RGB(47, 72, 78),
        RGB(68, 137, 26),
        RGB(163, 206, 39),
        RGB(27, 38, 50),
        RGB(0, 87, 132),
        RGB(49, 162, 242),
        RGB(178, 220, 239),
    ]
    
    NEON = [
        RGB(255, 0, 102),
        RGB(255, 102, 0),
        RGB(255, 255, 0),
        RGB(0, 255, 102),
        RGB(0, 255, 255),
        RGB(102, 0, 255),
        RGB(255, 0, 255),
    ]
    
    PASTEL = [
        RGB(255, 179, 186),
        RGB(255, 223, 186),
        RGB(255, 255, 186),
        RGB(186, 255, 201),
        RGB(186, 225, 255),
        RGB(223, 186, 255),
    ]
