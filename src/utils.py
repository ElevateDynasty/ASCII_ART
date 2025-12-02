"""
Utility functions for ASCII Art Generator.
"""

from pathlib import Path
from typing import Union, Optional, Tuple, List
import os
import sys


def get_terminal_size() -> Tuple[int, int]:
    """Get terminal size (columns, rows)."""
    try:
        size = os.get_terminal_size()
        return size.columns, size.lines
    except OSError:
        return 80, 24  # Default fallback


def calculate_optimal_width(
    image_width: int,
    image_height: int,
    max_width: Optional[int] = None,
    max_height: Optional[int] = None
) -> int:
    """
    Calculate optimal ASCII art width based on constraints.
    
    Args:
        image_width: Original image width
        image_height: Original image height
        max_width: Maximum allowed width
        max_height: Maximum allowed height
        
    Returns:
        Optimal width in characters
    """
    if max_width is None:
        max_width, _ = get_terminal_size()
        max_width = max_width - 2  # Leave margin
    
    if max_height is None:
        _, max_height = get_terminal_size()
        max_height = max_height - 4  # Leave margin for UI
    
    # Calculate aspect ratio adjusted for character dimensions
    aspect_ratio = image_height / image_width * 0.55
    
    # Try max width first
    width = max_width
    height = int(width * aspect_ratio)
    
    # If height exceeds max, calculate based on height
    if height > max_height:
        height = max_height
        width = int(height / aspect_ratio)
    
    return max(1, min(width, max_width))


def ensure_dir(path: Union[str, Path]) -> Path:
    """Ensure directory exists, create if not."""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent


def get_output_dir() -> Path:
    """Get the output directory, create if not exists."""
    output_dir = get_project_root() / "output"
    return ensure_dir(output_dir)


def get_assets_dir() -> Path:
    """Get the assets directory."""
    return get_project_root() / "assets"


def get_sample_images_dir() -> Path:
    """Get sample images directory."""
    return get_assets_dir() / "sample_images"


def is_valid_image(filepath: Union[str, Path]) -> bool:
    """Check if filepath is a valid supported image."""
    supported = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.tiff', '.ico'}
    path = Path(filepath)
    return path.exists() and path.is_file() and path.suffix.lower() in supported


def list_images_in_dir(directory: Union[str, Path]) -> List[Path]:
    """List all valid images in a directory."""
    directory = Path(directory)
    if not directory.is_dir():
        return []
    
    supported = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.tiff', '.ico'}
    return [
        f for f in directory.iterdir()
        if f.is_file() and f.suffix.lower() in supported
    ]


def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing invalid characters."""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename


def generate_output_filename(
    input_path: Union[str, Path],
    suffix: str = "_ascii",
    extension: str = ".txt"
) -> Path:
    """Generate output filename based on input."""
    input_path = Path(input_path)
    output_dir = get_output_dir()
    
    base_name = sanitize_filename(input_path.stem)
    output_name = f"{base_name}{suffix}{extension}"
    
    return output_dir / output_name


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def get_image_info(filepath: Union[str, Path]) -> dict:
    """Get basic image information."""
    from PIL import Image
    
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")
    
    with Image.open(path) as img:
        return {
            "path": str(path.absolute()),
            "filename": path.name,
            "format": img.format,
            "mode": img.mode,
            "size": img.size,
            "width": img.size[0],
            "height": img.size[1],
            "file_size": format_file_size(path.stat().st_size),
        }


def print_progress(current: int, total: int, prefix: str = "", length: int = 40) -> None:
    """Print a progress bar."""
    percent = current / total
    filled = int(length * percent)
    bar = '█' * filled + '░' * (length - filled)
    sys.stdout.write(f'\r{prefix} |{bar}| {percent*100:.1f}%')
    sys.stdout.flush()
    if current >= total:
        print()


class Timer:
    """Simple timer context manager."""
    
    def __init__(self, name: str = "Operation"):
        self.name = name
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        import time
        self.start_time = time.time()
        return self
    
    def __exit__(self, *args):
        import time
        self.end_time = time.time()
    
    @property
    def elapsed(self) -> float:
        """Get elapsed time in seconds."""
        if self.end_time is None:
            import time
            return time.time() - self.start_time
        return self.end_time - self.start_time
    
    def __str__(self) -> str:
        return f"{self.name}: {self.elapsed:.3f}s"


def clear_screen() -> None:
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def supports_color() -> bool:
    """Check if terminal supports colors."""
    if os.name == 'nt':
        # Windows 10+ supports ANSI
        return True
    return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()


def enable_windows_ansi() -> None:
    """Enable ANSI escape codes on Windows."""
    if os.name == 'nt':
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
