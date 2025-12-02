"""
Character sets for ASCII art generation.
Includes traditional ASCII, block characters, and emoji sets.
"""

from enum import Enum
from typing import List, Dict, Optional


class CharacterSet(Enum):
    """Predefined character sets ordered by density (dark to light)."""
    
    # Standard - 10 levels
    STANDARD = "@%#*+=-:. "
    
    # Detailed - 70 levels for high precision
    DETAILED = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. "
    
    # Simple - 5 levels for basic output
    SIMPLE = "@#*:. "
    
    # Blocks - Using block characters
    BLOCKS = "█▓▒░ "
    
    # Numbers only
    NUMBERS = "0123456789 "
    
    # Letters only
    LETTERS = "MWNXK0Okxdolc:;,. "


class EmojiSet(Enum):
    """Emoji character sets for creative ASCII art."""
    
    # Brightness-based emoji (dark to light)
    BRIGHTNESS = ["⬛", "🟫", "🟥", "🟧", "🟨", "🟩", "🟦", "🟪", "⬜"]
    
    # Grayscale circles
    GRAYSCALE = ["⚫", "🔴", "🟤", "🟠", "🟡", "🟢", "🔵", "🟣", "⚪"]
    
    # Hearts (dark to light feeling)
    HEARTS = ["🖤", "❤️", "🧡", "💛", "💚", "💙", "💜", "🤍", "💗"]
    
    # Squares only
    SQUARES = ["⬛", "🟫", "🟥", "🟧", "🟨", "🟩", "🟦", "🟪", "⬜"]
    
    # Nature theme
    NATURE = ["🌑", "🌲", "🌳", "🌴", "🌿", "🍀", "🌸", "🌼", "☀️"]
    
    # Space theme
    SPACE = ["⬛", "🌑", "🌙", "⭐", "✨", "💫", "🌟", "⚡", "☀️"]
    
    # Ocean theme
    OCEAN = ["🌊", "🐳", "🐬", "🐠", "🐟", "🦈", "🐙", "🦑", "💎"]
    
    # Food theme
    FOOD = ["🍫", "🍩", "🍪", "🧁", "🍰", "🍨", "🍦", "🎂", "🍬"]
    
    # Faces
    FACES = ["😈", "👿", "😠", "😐", "🙂", "😊", "😄", "😁", "🌟"]
    
    # Weather
    WEATHER = ["🌑", "☁️", "🌧️", "⛈️", "🌤️", "⛅", "🌥️", "☀️", "✨"]
    
    # Fire theme
    FIRE = ["⬛", "🟤", "🔴", "🟠", "🟡", "🔥", "💥", "⭐", "💫"]
    
    # Custom geometric
    GEOMETRIC = ["◼️", "◾", "▪️", "◽", "◻️", "⬜", "🔲", "🔳", "💠"]


class CharacterMapper:
    """Maps pixel brightness to ASCII characters or emojis."""
    
    def __init__(
        self, 
        charset: CharacterSet = CharacterSet.DETAILED,
        emoji_set: Optional[EmojiSet] = None,
        use_emoji: bool = False
    ):
        self.use_emoji = use_emoji
        
        if use_emoji and emoji_set:
            self.characters = emoji_set.value
            self.is_emoji = True
        else:
            self.characters = charset.value
            self.is_emoji = False
        
        self.num_chars = len(self.characters)
    
    def get_character(self, brightness: float) -> str:
        """
        Convert brightness (0-255) to ASCII character or emoji.
        
        Args:
            brightness: Pixel brightness value (0=black, 255=white)
            
        Returns:
            Corresponding ASCII character or emoji
        """
        # Clamp brightness to valid range
        brightness = max(0, min(255, brightness))
        
        # Map brightness to character index
        # Dark pixels (low brightness) -> first characters (dense)
        # Light pixels (high brightness) -> last characters (sparse)
        normalized = brightness / 255.0
        index = int(normalized * (self.num_chars - 1) + 0.5)  # Round to nearest
        index = max(0, min(index, self.num_chars - 1))
        return self.characters[index]
    
    def get_inverted_character(self, brightness: float) -> str:
        """Get character with inverted brightness mapping."""
        return self.get_character(255 - brightness)
    
    def get_colored_emoji(self, r: int, g: int, b: int) -> str:
        """
        Get emoji based on dominant color.
        
        Args:
            r, g, b: RGB color values
            
        Returns:
            Color-appropriate emoji
        """
        # Color to emoji mapping
        color_emojis = {
            'red': '🟥',
            'orange': '🟧', 
            'yellow': '🟨',
            'green': '🟩',
            'blue': '🟦',
            'purple': '🟪',
            'brown': '🟫',
            'black': '⬛',
            'white': '⬜',
        }
        
        # Determine dominant color
        brightness = (r + g + b) / 3
        
        if brightness < 30:
            return color_emojis['black']
        elif brightness > 225:
            return color_emojis['white']
        
        # Check for dominant color
        max_channel = max(r, g, b)
        
        if r == max_channel:
            if g > 150 and r > 200:
                return color_emojis['yellow']
            elif g > 100:
                return color_emojis['orange']
            else:
                return color_emojis['red']
        elif g == max_channel:
            return color_emojis['green']
        else:  # blue is max
            if r > 150:
                return color_emojis['purple']
            return color_emojis['blue']


def get_charset_by_name(name: str) -> CharacterSet:
    """Get character set by name string."""
    name_map = {
        "standard": CharacterSet.STANDARD,
        "detailed": CharacterSet.DETAILED,
        "simple": CharacterSet.SIMPLE,
        "blocks": CharacterSet.BLOCKS,
        "numbers": CharacterSet.NUMBERS,
        "letters": CharacterSet.LETTERS,
    }
    return name_map.get(name.lower(), CharacterSet.DETAILED)


def get_emoji_set_by_name(name: str) -> EmojiSet:
    """Get emoji set by name string."""
    name_map = {
        "brightness": EmojiSet.BRIGHTNESS,
        "grayscale": EmojiSet.GRAYSCALE,
        "hearts": EmojiSet.HEARTS,
        "squares": EmojiSet.SQUARES,
        "nature": EmojiSet.NATURE,
        "space": EmojiSet.SPACE,
        "ocean": EmojiSet.OCEAN,
        "food": EmojiSet.FOOD,
        "faces": EmojiSet.FACES,
        "weather": EmojiSet.WEATHER,
        "fire": EmojiSet.FIRE,
        "geometric": EmojiSet.GEOMETRIC,
    }
    return name_map.get(name.lower(), EmojiSet.BRIGHTNESS)


def list_available_charsets() -> List[str]:
    """List all available character set names."""
    return ["standard", "detailed", "simple", "blocks", "numbers", "letters"]


def list_available_emoji_sets() -> List[str]:
    """List all available emoji set names."""
    return [
        "brightness", "grayscale", "hearts", "squares", "nature",
        "space", "ocean", "food", "faces", "weather", "fire", "geometric"
    ]
