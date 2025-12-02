"""
GUI interface for ASCII Art Generator using Tkinter.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
from PIL import Image, ImageTk
import threading
import os

from .ascii_converter import ASCIIConverter, ConversionSettings, convert_to_emoji
from .character_sets import (
    CharacterSet, EmojiSet,
    get_charset_by_name, get_emoji_set_by_name,
    list_available_charsets, list_available_emoji_sets
)
from .color_handler import ColorMode


class ASCIIArtGUI:
    """Main GUI application for ASCII Art Generator."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎨 ASCII Art Generator")
        self.root.geometry("1200x800")
        self.root.minsize(900, 600)
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Variables
        self.image_path = tk.StringVar()
        self.width_var = tk.IntVar(value=80)
        self.charset_var = tk.StringVar(value="detailed")
        self.emoji_set_var = tk.StringVar(value="brightness")
        self.use_emoji_var = tk.BooleanVar(value=False)
        self.invert_var = tk.BooleanVar(value=False)
        self.contrast_var = tk.DoubleVar(value=1.2)
        self.brightness_var = tk.DoubleVar(value=1.0)
        self.edge_detection_var = tk.BooleanVar(value=False)
        
        # Current image
        self.current_image = None
        self.current_art = None
        
        self._setup_ui()
        self._configure_styles()
    
    def _configure_styles(self):
        """Configure custom styles."""
        self.style.configure('Title.TLabel', font=('Helvetica', 16, 'bold'))
        self.style.configure('Header.TLabel', font=('Helvetica', 11, 'bold'))
        self.style.configure('TButton', padding=5)
        self.style.configure('Generate.TButton', font=('Helvetica', 10, 'bold'))
    
    def _setup_ui(self):
        """Setup the main UI layout."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(
            title_frame, 
            text="🎨 ASCII Art Generator",
            style='Title.TLabel'
        )
        title_label.pack(side=tk.LEFT)
        
        # Create horizontal paned window
        paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Controls
        left_frame = ttk.Frame(paned, padding="5")
        paned.add(left_frame, weight=1)
        
        # Right panel - Output
        right_frame = ttk.Frame(paned, padding="5")
        paned.add(right_frame, weight=2)
        
        self._setup_left_panel(left_frame)
        self._setup_right_panel(right_frame)
    
    def _setup_left_panel(self, parent):
        """Setup the left control panel."""
        # Image Selection Section
        img_frame = ttk.LabelFrame(parent, text="📷 Image Selection", padding="10")
        img_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Image path entry
        path_frame = ttk.Frame(img_frame)
        path_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.path_entry = ttk.Entry(path_frame, textvariable=self.image_path, width=30)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        browse_btn = ttk.Button(path_frame, text="Browse...", command=self._browse_image)
        browse_btn.pack(side=tk.RIGHT)
        
        # Image preview
        self.preview_frame = ttk.Frame(img_frame)
        self.preview_frame.pack(fill=tk.X, pady=5)
        
        self.preview_label = ttk.Label(self.preview_frame, text="No image selected")
        self.preview_label.pack()
        
        # Conversion Settings Section
        settings_frame = ttk.LabelFrame(parent, text="⚙️ Settings", padding="10")
        settings_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Mode selection (ASCII vs Emoji)
        mode_frame = ttk.Frame(settings_frame)
        mode_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(mode_frame, text="Mode:", style='Header.TLabel').pack(anchor=tk.W)
        
        mode_radio_frame = ttk.Frame(mode_frame)
        mode_radio_frame.pack(fill=tk.X)
        
        ttk.Radiobutton(
            mode_radio_frame, text="ASCII Art", 
            variable=self.use_emoji_var, value=False,
            command=self._on_mode_change
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Radiobutton(
            mode_radio_frame, text="Emoji Art 🎭", 
            variable=self.use_emoji_var, value=True,
            command=self._on_mode_change
        ).pack(side=tk.LEFT)
        
        # Width setting
        width_frame = ttk.Frame(settings_frame)
        width_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(width_frame, text="Width:").pack(side=tk.LEFT)
        self.width_scale = ttk.Scale(
            width_frame, from_=20, to=200, 
            variable=self.width_var, orient=tk.HORIZONTAL
        )
        self.width_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.width_label = ttk.Label(width_frame, text="80")
        self.width_label.pack(side=tk.RIGHT)
        self.width_var.trace('w', self._update_width_label)
        
        # Character set selection (for ASCII mode)
        self.charset_frame = ttk.Frame(settings_frame)
        self.charset_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(self.charset_frame, text="Character Set:").pack(anchor=tk.W)
        charset_combo = ttk.Combobox(
            self.charset_frame, 
            textvariable=self.charset_var,
            values=list_available_charsets(),
            state='readonly'
        )
        charset_combo.pack(fill=tk.X)
        
        # Emoji set selection (for Emoji mode)
        self.emoji_frame = ttk.Frame(settings_frame)
        
        ttk.Label(self.emoji_frame, text="Emoji Theme:").pack(anchor=tk.W)
        emoji_combo = ttk.Combobox(
            self.emoji_frame,
            textvariable=self.emoji_set_var,
            values=list_available_emoji_sets(),
            state='readonly'
        )
        emoji_combo.pack(fill=tk.X)
        
        # Image Adjustments Section
        adjust_frame = ttk.LabelFrame(parent, text="🔧 Adjustments", padding="10")
        adjust_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Contrast
        contrast_frame = ttk.Frame(adjust_frame)
        contrast_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(contrast_frame, text="Contrast:").pack(side=tk.LEFT)
        self.contrast_scale = ttk.Scale(
            contrast_frame, from_=0.5, to=3.0,
            variable=self.contrast_var, orient=tk.HORIZONTAL
        )
        self.contrast_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.contrast_label = ttk.Label(contrast_frame, text="1.2")
        self.contrast_label.pack(side=tk.RIGHT)
        self.contrast_var.trace('w', self._update_contrast_label)
        
        # Brightness
        brightness_frame = ttk.Frame(adjust_frame)
        brightness_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(brightness_frame, text="Brightness:").pack(side=tk.LEFT)
        self.brightness_scale = ttk.Scale(
            brightness_frame, from_=0.5, to=2.0,
            variable=self.brightness_var, orient=tk.HORIZONTAL
        )
        self.brightness_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.brightness_label = ttk.Label(brightness_frame, text="1.0")
        self.brightness_label.pack(side=tk.RIGHT)
        self.brightness_var.trace('w', self._update_brightness_label)
        
        # Checkboxes
        check_frame = ttk.Frame(adjust_frame)
        check_frame.pack(fill=tk.X, pady=5)
        
        ttk.Checkbutton(
            check_frame, text="Invert", 
            variable=self.invert_var
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Checkbutton(
            check_frame, text="Edge Detection",
            variable=self.edge_detection_var
        ).pack(side=tk.LEFT)
        
        # Generate Button
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, pady=10)
        
        self.generate_btn = ttk.Button(
            btn_frame, 
            text="🚀 Generate ASCII Art",
            style='Generate.TButton',
            command=self._generate_art
        )
        self.generate_btn.pack(fill=tk.X, ipady=10)
        
        # Save Buttons
        save_frame = ttk.Frame(parent)
        save_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(
            save_frame, text="💾 Save as TXT",
            command=self._save_txt
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))
        
        ttk.Button(
            save_frame, text="🌐 Save as HTML",
            command=self._save_html
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(2, 0))
        
        # Copy button
        ttk.Button(
            parent, text="📋 Copy to Clipboard",
            command=self._copy_to_clipboard
        ).pack(fill=tk.X, pady=5)
    
    def _setup_right_panel(self, parent):
        """Setup the right output panel."""
        # Output Section
        output_frame = ttk.LabelFrame(parent, text="📝 Output", padding="10")
        output_frame.pack(fill=tk.BOTH, expand=True)
        
        # ASCII Art display
        self.output_text = scrolledtext.ScrolledText(
            output_frame,
            wrap=tk.NONE,
            font=('Consolas', 8),
            bg='#1e1e1e',
            fg='#d4d4d4',
            insertbackground='white'
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # Horizontal scrollbar
        h_scroll = ttk.Scrollbar(output_frame, orient=tk.HORIZONTAL, command=self.output_text.xview)
        h_scroll.pack(fill=tk.X)
        self.output_text.configure(xscrollcommand=h_scroll.set)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(parent, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, pady=(5, 0))
    
    def _browse_image(self):
        """Open file dialog to select an image."""
        filetypes = [
            ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp *.tiff"),
            ("PNG files", "*.png"),
            ("JPEG files", "*.jpg *.jpeg"),
            ("All files", "*.*")
        ]
        
        filepath = filedialog.askopenfilename(
            title="Select an image",
            filetypes=filetypes
        )
        
        if filepath:
            self.image_path.set(filepath)
            self._load_preview(filepath)
    
    def _load_preview(self, filepath):
        """Load and display image preview."""
        try:
            img = Image.open(filepath)
            # Create thumbnail for preview
            img.thumbnail((200, 150), Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(img)
            self.preview_label.configure(image=photo, text="")
            self.preview_label.image = photo  # Keep reference
            
            self.current_image = filepath
            self.status_var.set(f"Loaded: {Path(filepath).name}")
            
        except Exception as e:
            self.preview_label.configure(image="", text=f"Error: {str(e)}")
            messagebox.showerror("Error", f"Could not load image:\n{str(e)}")
    
    def _on_mode_change(self):
        """Handle mode change between ASCII and Emoji."""
        if self.use_emoji_var.get():
            self.charset_frame.pack_forget()
            self.emoji_frame.pack(fill=tk.X, pady=5)
            self.generate_btn.configure(text="🚀 Generate Emoji Art")
        else:
            self.emoji_frame.pack_forget()
            self.charset_frame.pack(fill=tk.X, pady=5)
            self.generate_btn.configure(text="🚀 Generate ASCII Art")
    
    def _update_width_label(self, *args):
        """Update width display label."""
        self.width_label.configure(text=str(int(self.width_var.get())))
    
    def _update_contrast_label(self, *args):
        """Update contrast display label."""
        self.contrast_label.configure(text=f"{self.contrast_var.get():.1f}")
    
    def _update_brightness_label(self, *args):
        """Update brightness display label."""
        self.brightness_label.configure(text=f"{self.brightness_var.get():.1f}")
    
    def _generate_art(self):
        """Generate ASCII/Emoji art from the image."""
        if not self.image_path.get():
            messagebox.showwarning("Warning", "Please select an image first!")
            return
        
        if not Path(self.image_path.get()).exists():
            messagebox.showerror("Error", "Image file not found!")
            return
        
        self.status_var.set("Generating...")
        self.generate_btn.configure(state='disabled')
        
        # Run in thread to prevent UI freeze
        thread = threading.Thread(target=self._generate_art_thread)
        thread.start()
    
    def _generate_art_thread(self):
        """Generate art in background thread."""
        try:
            settings = ConversionSettings(
                width=int(self.width_var.get()),
                charset=get_charset_by_name(self.charset_var.get()),
                use_emoji=self.use_emoji_var.get(),
                emoji_set=get_emoji_set_by_name(self.emoji_set_var.get()),
                invert=self.invert_var.get(),
                contrast=self.contrast_var.get(),
                brightness=self.brightness_var.get(),
                edge_detection=self.edge_detection_var.get(),
                color_mode=ColorMode.NONE
            )
            
            converter = ASCIIConverter(self.image_path.get())
            art = converter.convert(settings=settings)
            self.current_art = art
            
            # Update UI in main thread
            self.root.after(0, self._display_art, str(art))
            
        except Exception as e:
            self.root.after(0, self._show_error, str(e))
    
    def _display_art(self, art_text):
        """Display the generated art."""
        self.output_text.configure(state='normal')
        self.output_text.delete('1.0', tk.END)
        self.output_text.insert('1.0', art_text)
        
        # Adjust font for better display
        if self.use_emoji_var.get():
            # Emoji needs larger font and special emoji font
            self.output_text.configure(
                font=('Segoe UI Emoji', 12),
                spacing1=0,
                spacing2=0,
                spacing3=0
            )
        else:
            # ASCII - use monospace with proper sizing
            # Calculate optimal font size based on width
            width = self.width_var.get()
            if width > 120:
                font_size = 6
            elif width > 80:
                font_size = 8
            else:
                font_size = 10
            
            self.output_text.configure(
                font=('Consolas', font_size),
                spacing1=0,
                spacing2=0, 
                spacing3=0
            )
        
        self.generate_btn.configure(state='normal')
        self.status_var.set(f"Generated! Size: {self.current_art.width}x{self.current_art.height}")
    
    def _show_error(self, error_msg):
        """Show error message."""
        self.generate_btn.configure(state='normal')
        self.status_var.set("Error occurred")
        messagebox.showerror("Error", f"Failed to generate art:\n{error_msg}")
    
    def _save_txt(self):
        """Save the art as a text file."""
        if not self.current_art:
            messagebox.showwarning("Warning", "Generate art first!")
            return
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save ASCII Art"
        )
        
        if filepath:
            try:
                Path(filepath).write_text(str(self.current_art), encoding='utf-8')
                self.status_var.set(f"Saved: {Path(filepath).name}")
                messagebox.showinfo("Success", f"Saved to:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file:\n{str(e)}")
    
    def _save_html(self):
        """Save the art as an HTML file with styling."""
        if not self.current_art:
            messagebox.showwarning("Warning", "Generate art first!")
            return
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML files", "*.html"), ("All files", "*.*")],
            title="Save as HTML"
        )
        
        if filepath:
            try:
                # Re-generate with HTML color mode
                settings = ConversionSettings(
                    width=int(self.width_var.get()),
                    charset=get_charset_by_name(self.charset_var.get()),
                    use_emoji=self.use_emoji_var.get(),
                    emoji_set=get_emoji_set_by_name(self.emoji_set_var.get()),
                    invert=self.invert_var.get(),
                    contrast=self.contrast_var.get(),
                    brightness=self.brightness_var.get(),
                    edge_detection=self.edge_detection_var.get(),
                    color_mode=ColorMode.HTML
                )
                
                converter = ASCIIConverter(self.image_path.get())
                art = converter.convert(settings=settings)
                
                Path(filepath).write_text(str(art), encoding='utf-8')
                self.status_var.set(f"Saved: {Path(filepath).name}")
                messagebox.showinfo("Success", f"Saved to:\n{filepath}")
                
                # Offer to open in browser
                if messagebox.askyesno("Open?", "Open in browser?"):
                    import webbrowser
                    webbrowser.open(f"file://{filepath}")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file:\n{str(e)}")
    
    def _copy_to_clipboard(self):
        """Copy the art to clipboard."""
        if not self.current_art:
            messagebox.showwarning("Warning", "Generate art first!")
            return
        
        self.root.clipboard_clear()
        self.root.clipboard_append(str(self.current_art))
        self.status_var.set("Copied to clipboard!")
    
    def run(self):
        """Start the GUI application."""
        self.root.mainloop()


def main():
    """Main entry point for GUI."""
    app = ASCIIArtGUI()
    app.run()


if __name__ == "__main__":
    main()
