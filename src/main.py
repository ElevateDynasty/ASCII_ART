"""
CLI interface for ASCII Art Generator.
"""

import click
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint

from .ascii_converter import ASCIIConverter, ConversionSettings, convert_image, convert_to_emoji
from .character_sets import (
    CharacterSet, EmojiSet,
    get_charset_by_name, get_emoji_set_by_name,
    list_available_charsets, list_available_emoji_sets
)
from .color_handler import ColorMode
from .utils import (
    get_image_info, is_valid_image, list_images_in_dir,
    generate_output_filename, enable_windows_ansi, Timer
)


console = Console()


@click.group()
@click.version_option(version="1.0.0", prog_name="ASCII Art Generator")
def cli():
    """🎨 ASCII Art Generator - Convert images to ASCII art and emoji art."""
    # Enable ANSI colors on Windows
    enable_windows_ansi()


@cli.command()
@click.argument("image_path", type=click.Path(exists=True))
@click.option("-w", "--width", default=100, help="Output width in characters")
@click.option("-c", "--charset", default="detailed", 
              type=click.Choice(["standard", "detailed", "simple", "blocks", "numbers", "letters"]),
              help="Character set to use")
@click.option("--color", default="none",
              type=click.Choice(["none", "ansi", "ansi_bg", "html", "html_bg"]),
              help="Color output mode")
@click.option("-i", "--invert", is_flag=True, help="Invert brightness")
@click.option("-o", "--output", type=click.Path(), help="Save to file")
@click.option("--contrast", default=1.2, type=float, help="Contrast adjustment (1.0 = no change)")
@click.option("--brightness", default=1.0, type=float, help="Brightness adjustment")
@click.option("--edge", is_flag=True, help="Use edge detection mode")
@click.option("--no-denoise", is_flag=True, help="Disable denoising")
@click.option("--sharpen", default=1.0, type=float, help="Sharpen factor")
def convert(image_path, width, charset, color, invert, output, contrast, brightness, edge, no_denoise, sharpen):
    """Convert an image to ASCII art."""
    
    console.print(f"\n[bold blue]🖼️  Processing:[/] {image_path}\n")
    
    with Timer("Conversion") as timer:
        # Build settings
        settings = ConversionSettings(
            width=width,
            charset=get_charset_by_name(charset),
            color_mode=ColorMode(color),
            invert=invert,
            contrast=contrast,
            brightness=brightness,
            edge_detection=edge,
            denoise=not no_denoise,
            sharpen=sharpen
        )
        
        # Convert
        converter = ASCIIConverter(image_path)
        art = converter.convert(settings=settings)
    
    # Output
    if output:
        art.save(output)
        console.print(f"[bold green]✅ Saved to:[/] {output}")
    else:
        if color == "none":
            console.print(Panel(str(art), title="ASCII Art", border_style="cyan"))
        else:
            print(str(art))
    
    console.print(f"\n[dim]Dimensions: {art.width}x{art.height} | {timer}[/dim]\n")


@cli.command()
@click.argument("image_path", type=click.Path(exists=True))
@click.option("-w", "--width", default=50, help="Output width in emojis")
@click.option("-e", "--emoji-set", default="brightness",
              type=click.Choice([
                  "brightness", "grayscale", "hearts", "squares", "nature",
                  "space", "ocean", "food", "faces", "weather", "fire", "geometric"
              ]),
              help="Emoji set to use")
@click.option("--color-emoji", is_flag=True, help="Use color-based emoji mapping")
@click.option("-o", "--output", type=click.Path(), help="Save to file")
@click.option("--contrast", default=1.2, type=float, help="Contrast adjustment")
@click.option("--html", is_flag=True, help="Output as HTML file")
def emoji(image_path, width, emoji_set, color_emoji, output, contrast, html):
    """Convert an image to emoji art. 🎨"""
    
    console.print(f"\n[bold magenta]🎭 Converting to Emoji Art:[/] {image_path}\n")
    
    with Timer("Conversion") as timer:
        color_mode = ColorMode.HTML if html else ColorMode.NONE
        
        art = convert_to_emoji(
            image_path,
            emoji_set=emoji_set,
            width=width,
            color_emoji=color_emoji,
            contrast=contrast,
            color_mode=color_mode
        )
    
    # Output
    if output:
        art.save(output)
        console.print(f"[bold green]✅ Saved to:[/] {output}")
    elif html:
        # Auto-generate HTML output
        output_path = generate_output_filename(image_path, "_emoji", ".html")
        art.save(output_path)
        console.print(f"[bold green]✅ Saved to:[/] {output_path}")
    else:
        console.print(Panel(str(art), title=f"Emoji Art ({emoji_set})", border_style="magenta"))
    
    console.print(f"\n[dim]Dimensions: {art.width}x{art.height} | {timer}[/dim]\n")


@cli.command()
@click.argument("image_path", type=click.Path(exists=True))
@click.option("-w", "--width", default=60, help="Preview width")
@click.option("--emoji", is_flag=True, help="Preview as emoji art")
def preview(image_path, width, emoji):
    """Quick preview of an image as ASCII/emoji art."""
    
    converter = ASCIIConverter(image_path)
    
    if emoji:
        art = converter.preview_emoji(width=width)
        title = f"Emoji Preview: {Path(image_path).name}"
        style = "magenta"
    else:
        art = converter.preview(width=width)
        title = f"ASCII Preview: {Path(image_path).name}"
        style = "green"
    
    console.print(Panel(art, title=title, border_style=style))


@cli.command()
def charsets():
    """Display available character sets."""
    
    console.print("\n[bold cyan]📝 Available Character Sets:[/bold cyan]\n")
    
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Name", style="green")
    table.add_column("Characters", style="dim")
    table.add_column("Description")
    
    sets = [
        ("standard", CharacterSet.STANDARD.value, "Balanced 10-level set"),
        ("detailed", CharacterSet.DETAILED.value[:25] + "...", "High precision 70-level set"),
        ("simple", CharacterSet.SIMPLE.value, "Basic 5-level set"),
        ("blocks", CharacterSet.BLOCKS.value, "Block characters"),
        ("numbers", CharacterSet.NUMBERS.value, "Numeric characters"),
        ("letters", CharacterSet.LETTERS.value, "Letter characters"),
    ]
    
    for name, chars, desc in sets:
        table.add_row(name, chars, desc)
    
    console.print(table)
    console.print()


@cli.command()
def emojisets():
    """Display available emoji sets. 🎨"""
    
    console.print("\n[bold magenta]🎭 Available Emoji Sets:[/bold magenta]\n")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Name", style="green")
    table.add_column("Emojis", style="dim", width=40)
    table.add_column("Theme")
    
    sets = [
        ("brightness", EmojiSet.BRIGHTNESS.value, "Brightness-based squares"),
        ("grayscale", EmojiSet.GRAYSCALE.value, "Colored circles"),
        ("hearts", EmojiSet.HEARTS.value, "Heart emojis"),
        ("squares", EmojiSet.SQUARES.value, "Colored squares"),
        ("nature", EmojiSet.NATURE.value, "Nature theme"),
        ("space", EmojiSet.SPACE.value, "Space/celestial"),
        ("ocean", EmojiSet.OCEAN.value, "Ocean creatures"),
        ("food", EmojiSet.FOOD.value, "Food & sweets"),
        ("faces", EmojiSet.FACES.value, "Face expressions"),
        ("weather", EmojiSet.WEATHER.value, "Weather icons"),
        ("fire", EmojiSet.FIRE.value, "Fire & energy"),
        ("geometric", EmojiSet.GEOMETRIC.value, "Geometric shapes"),
    ]
    
    for name, emojis, theme in sets:
        emoji_str = ' '.join(emojis[:6]) + "..."
        table.add_row(name, emoji_str, theme)
    
    console.print(table)
    console.print()


@cli.command()
@click.argument("image_path", type=click.Path(exists=True))
def info(image_path):
    """Display information about an image."""
    
    try:
        info_data = get_image_info(image_path)
        
        console.print(f"\n[bold blue]📷 Image Information:[/bold blue]\n")
        
        table = Table(show_header=False, box=None)
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("File", info_data['filename'])
        table.add_row("Format", info_data['format'])
        table.add_row("Mode", info_data['mode'])
        table.add_row("Size", f"{info_data['width']} x {info_data['height']} pixels")
        table.add_row("File Size", info_data['file_size'])
        
        console.print(table)
        console.print()
        
    except Exception as e:
        console.print(f"[bold red]Error:[/] {e}")


@cli.command()
@click.argument("directory", type=click.Path(exists=True), default=".")
@click.option("-w", "--width", default=80, help="Output width")
@click.option("-o", "--output-dir", type=click.Path(), help="Output directory")
@click.option("--emoji", is_flag=True, help="Convert to emoji art")
@click.option("--emoji-set", default="brightness", help="Emoji set to use")
def batch(directory, width, output_dir, emoji, emoji_set):
    """Batch convert all images in a directory."""
    
    images = list_images_in_dir(directory)
    
    if not images:
        console.print(f"[yellow]No images found in {directory}[/yellow]")
        return
    
    console.print(f"\n[bold blue]📁 Found {len(images)} images[/bold blue]\n")
    
    for i, img_path in enumerate(images, 1):
        console.print(f"[dim]Processing ({i}/{len(images)}):[/] {img_path.name}")
        
        try:
            if emoji:
                art = convert_to_emoji(img_path, width=width, emoji_set=emoji_set)
                suffix = f"_emoji_{emoji_set}"
            else:
                art = convert_image(img_path, width=width)
                suffix = "_ascii"
            
            # Determine output path
            if output_dir:
                out_path = Path(output_dir) / f"{img_path.stem}{suffix}.txt"
            else:
                out_path = generate_output_filename(img_path, suffix, ".txt")
            
            art.save(out_path)
            
        except Exception as e:
            console.print(f"[red]  Error: {e}[/red]")
    
    console.print(f"\n[bold green]✅ Batch conversion complete![/bold green]\n")


@cli.command()
def about():
    """Display information about this tool."""
    
    about_text = """
[bold cyan]🎨 ASCII Art Generator[/bold cyan]
[dim]Version 1.0.0[/dim]

A powerful tool to convert images into ASCII art and emoji art.

[bold]Features:[/bold]
  • Multiple character sets for different detail levels
  • 12+ themed emoji sets for creative output
  • Color output (ANSI terminal & HTML)
  • Edge detection mode for outlines
  • Contrast, brightness & sharpness adjustment
  • Automatic aspect ratio correction
  • Batch processing support
  • HTML export with styling

[bold]Quick Examples:[/bold]
  [dim]# Basic ASCII conversion[/dim]
  ascii-art convert image.png -w 80

  [dim]# Emoji art with hearts theme[/dim]
  ascii-art emoji image.png -e hearts

  [dim]# Colored HTML output[/dim]
  ascii-art convert image.png --color html -o output.html

  [dim]# Batch convert folder[/dim]
  ascii-art batch ./images --emoji

[bold cyan]Made with ❤️ for creative coding[/bold cyan]
"""
    
    console.print(Panel(about_text, border_style="cyan", title="About", title_align="center"))


def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
