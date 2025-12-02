# 🎨 ASCII Art Generator

A powerful Python tool to convert images into ASCII art and emoji art with multiple themes and color options.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

- **🖥️ GUI Application**: User-friendly graphical interface with image preview
- **Multiple Character Sets**: 6 different ASCII character sets for various detail levels
- **12+ Emoji Themes**: Hearts, space, ocean, nature, food, faces, and more!
- **Color Output**: ANSI terminal colors and HTML export with full color support
- **Advanced Image Processing**: Edge detection, contrast/brightness adjustment, denoising
- **Batch Processing**: Convert entire folders of images at once
- **CLI Interface**: Easy-to-use command line tool with rich output
- **Python API**: Use as a library in your own projects

## 🖼️ Screenshots

### GUI Application
The GUI provides an intuitive interface with:
- Image browsing and preview
- Real-time parameter adjustment (width, contrast, brightness)
- ASCII/Emoji mode toggle
- Multiple character sets and emoji themes
- Save as TXT or HTML
- Copy to clipboard

## 📦 Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/ElevateDynasty/ASCII_ART.git
cd ASCII_ART

# Install dependencies
pip install -r requirements.txt

# Install the package (optional)
pip install -e .
```

## 🚀 Quick Start

### GUI Application

```bash
# Launch the graphical interface
python -m src.gui
```

### Command Line Usage

```bash
# Basic ASCII conversion
ascii-art convert image.png -w 80

# Emoji art with hearts theme
ascii-art emoji image.png -e hearts

# Preview an image
ascii-art preview image.png

# Colored terminal output
ascii-art convert image.png --color ansi

# Save as HTML with colors
ascii-art convert image.png --color html -o output.html

# Batch convert a folder
ascii-art batch ./images --emoji -e space
```

### Python API Usage

```python
from src import convert_image, convert_to_emoji, ASCIIConverter

# Simple ASCII conversion
art = convert_image("photo.jpg", width=80)
print(art)

# Emoji art
emoji_art = convert_to_emoji("photo.jpg", emoji_set="hearts", width=50)
print(emoji_art)

# Advanced usage with settings
from src import ASCIIConverter, ConversionSettings, ColorMode

converter = ASCIIConverter("photo.jpg")
settings = ConversionSettings(
    width=100,
    contrast=1.5,
    color_mode=ColorMode.HTML,
    use_emoji=False
)
art = converter.convert(settings=settings)
art.save("output.html")
```

## 🎨 Character Sets

| Name | Characters | Best For |
|------|------------|----------|
| `detailed` | 70 levels | High detail images |
| `standard` | 10 levels | General use |
| `simple` | 5 levels | Quick preview |
| `blocks` | █▓▒░ | Block-style art |
| `numbers` | 0-9 | Unique style |
| `letters` | A-Z subset | Text-based art |

## 🎭 Emoji Sets

| Name | Theme | Example |
|------|-------|---------|
| `brightness` | Colored squares | ⬛🟫🟥🟧🟨🟩🟦🟪⬜ |
| `hearts` | Heart emojis | 🖤❤️🧡💛💚💙💜🤍💗 |
| `space` | Celestial | ⬛🌑🌙⭐✨💫🌟⚡☀️ |
| `nature` | Plants & sun | 🌑🌲🌳🌴🌿🍀🌸🌼☀️ |
| `ocean` | Sea creatures | 🌊🐳🐬🐠🐟🦈🐙🦑💎 |
| `food` | Sweets | 🍫🍩🍪🧁🍰🍨🍦🎂🍬 |
| `faces` | Expressions | 😈👿😠😐🙂😊😄😁🌟 |
| `fire` | Fire & energy | ⬛🟤🔴🟠🟡🔥💥⭐💫 |
| `weather` | Weather icons | 🌑☁️🌧️⛈️🌤️⛅🌥️☀️✨ |
| `geometric` | Shapes | ◼️◾▪️◽◻️⬜🔲🔳💠 |
| `grayscale` | Circles | ⚫🔴🟤🟠🟡🟢🔵🟣⚪ |
| `squares` | Basic squares | ⬛🟫🟥🟧🟨🟩🟦🟪⬜ |

## 📋 CLI Commands

```
ascii-art convert   - Convert image to ASCII art
ascii-art emoji     - Convert image to emoji art
ascii-art preview   - Quick preview of an image
ascii-art batch     - Batch convert all images in a directory
ascii-art charsets  - Display available character sets
ascii-art emojisets - Display available emoji sets
ascii-art info      - Display image information
ascii-art about     - About this tool
```

### Convert Options

```
-w, --width      Output width in characters (default: 100)
-c, --charset    Character set to use
--color          Color mode: none, ansi, ansi_bg, html, html_bg
-i, --invert     Invert brightness
-o, --output     Save to file
--contrast       Contrast adjustment (default: 1.2)
--brightness     Brightness adjustment (default: 1.0)
--edge           Use edge detection mode
--no-denoise     Disable denoising
--sharpen        Sharpen factor
```

### Emoji Options

```
-w, --width       Output width in emojis (default: 50)
-e, --emoji-set   Emoji set to use
--color-emoji     Use color-based emoji mapping
-o, --output      Save to file
--html            Output as HTML file
```

## 🔧 Advanced Features

### Edge Detection Mode

```bash
ascii-art convert image.png --edge -w 80
```

Creates outline-style ASCII art using edge detection.

### Color-Based Emoji Mapping

```bash
ascii-art emoji image.png --color-emoji
```

Maps emojis based on pixel colors instead of brightness.

### HTML Export with Styling

```bash
ascii-art convert image.png --color html -o gallery.html
```

Creates a beautifully styled HTML page with your ASCII art.

## 📁 Project Structure

```
ASCII_ART/
├── src/
│   ├── __init__.py
│   ├── main.py              # CLI interface
│   ├── gui.py               # GUI application
│   ├── ascii_converter.py   # Main conversion engine
│   ├── image_processor.py   # Image processing utilities
│   ├── character_sets.py    # ASCII & emoji character sets
│   ├── color_handler.py     # Color output handling
│   └── utils.py             # Utility functions
├── tests/
│   ├── test_ascii_converter.py
│   └── test_image_processor.py
├── assets/
│   └── sample_images/
├── output/
├── requirements.txt
├── pyproject.toml
└── README.md
```

## 🧪 Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_ascii_converter.py -v
```

## 📝 Examples

### Basic ASCII Art

```python
from src import image_to_ascii

result = image_to_ascii("sunset.jpg", width=60)
print(result)
```

### Emoji Art with Hearts

```python
from src import image_to_emoji

result = image_to_emoji("portrait.png", width=40, emoji_set="hearts")
print(result)
```

### Colored HTML Output

```python
from src import convert_image, ColorMode

art = convert_image(
    "photo.jpg",
    width=100,
    color_mode=ColorMode.HTML,
    contrast=1.5
)
art.save("colored_art.html")
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by [Python-World/python-mini-projects](https://github.com/Python-World/python-mini-projects)
- Built with [Pillow](https://pillow.readthedocs.io/), [OpenCV](https://opencv.org/), [Click](https://click.palletsprojects.com/), and [Rich](https://rich.readthedocs.io/)

---

Made with ❤️ for creative coding
