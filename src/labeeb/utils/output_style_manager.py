#!/usr/bin/env python3
"""
Output Style Manager for Labeeb

Handles loading and applying output formatting styles based on user preferences
and system capabilities. This provides a centralized way to manage appearance
across the application.

Supports RTL languages (Arabic, Hebrew, etc.) with proper text reshaping and display.
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, Optional
import arabic_reshaper
from bidi.algorithm import get_display
from ..core.platform_core import get_platform_name

class OutputStyleManager:
    """Manages output styling preferences for Labeeb."""
    
    def __init__(self, config_path: Optional[str] = None, theme: str = "default", auto_detect: bool = True):
        """
        Initialize the style manager.
        
        Args:
            config_path (str): Path to the output styles config file.
                Default is config/output_styles.json in the project root.
            theme (str): The theme to use (default, minimal, professional).
            auto_detect (bool): If True, auto-detects terminal capabilities.
        """
        self.config_path = config_path
        self.theme = theme
        self.auto_detect = auto_detect
        self.style_settings = {}
        
        # Get platform information
        self.platform_name = get_platform_name()
        
        # RTL support
        self.rtl_support = False
        
        self._init_style_settings()
        
    def set_rtl_support(self, enabled: bool) -> None:
        """
        Enable or disable RTL language support.
        
        Args:
            enabled: Whether to enable RTL support
        """
        self.rtl_support = enabled
        
    def _process_rtl_text(self, text: str) -> str:
        """
        Process text for RTL display if RTL support is enabled.
        
        Args:
            text: The text to process
            
        Returns:
            str: The processed text
        """
        if not self.rtl_support:
            return text
            
        # Check if text contains Arabic characters
        if any('\u0600' <= c <= '\u06FF' for c in text):
            text = arabic_reshaper.reshape(text)
            text = get_display(text)
        return text
        
    def _init_style_settings(self):
        """Initialize style settings based on platform capabilities."""
        self.use_colors = True
        self.use_unicode = True
        
        # Check if we're on Windows without proper terminal support
        if self.platform_name == 'windows' and "TERM" not in os.environ:
            self.use_colors = False
            self.use_unicode = False
            
    def _get_project_root(self):
        """Get the path to the project root directory."""
        return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            
    def _load_config(self):
        """Load styling configuration from file."""
        if not self.config_path:
            self.config_path = os.path.join(self._get_project_root(), 'config', 'style.json')
            
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.style_settings = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.style_settings = {}
            
    def _get_emoji_set(self):
        """Get the emoji set for the current theme."""
        emoji_set_name = self.theme.get("emoji_set", "default")
        return self.style_settings.get("emoji_sets", {}).get(emoji_set_name, {})
        
    def _get_box_style(self):
        """Get the box style for the current theme."""
        box_style_name = self.theme.get("box_style", "default")
        return self.style_settings.get("box_styles", {}).get(box_style_name, {})
        
    def _detect_terminal_capabilities(self):
        """Auto-detect terminal capabilities and adjust settings."""
        # Check if we're in a TTY and determine terminal width
        try:
            is_tty = os.isatty(1)  # 1 = stdout
            if is_tty:
                # Get terminal size
                columns, _ = shutil.get_terminal_size()
                # Only update if set to auto
                if self.style_settings.get("terminal_width") == "auto":
                    self.style_settings["terminal_width"] = columns
                    
                # Check if we're in Windows command prompt (limited emoji support)
                if self.platform_name == 'windows' and "TERM" not in os.environ:
                    # Using cmd.exe or PowerShell with limited capabilities
                    self.style_settings["use_emojis"] = False
            else:
                # Not a TTY, disable fancy formatting
                self.style_settings["use_emojis"] = False
                self.style_settings["use_boxes"] = False
                # Set a safe default width
                self.style_settings["terminal_width"] = 80
                
        except Exception:
            # Fallback to safe defaults on error
            self.style_settings["terminal_width"] = 80
            
    def get_emoji(self, key, fallback=""):
        """
        Get an emoji by key, respecting user preferences.
        
        Args:
            key (str): The emoji key, e.g., "success", "warning"
            fallback (str): Fallback character if emoji not found or disabled
            
        Returns:
            str: The emoji or fallback character
        """
        if not self.style_settings.get("use_emojis", True):
            # If emojis are disabled, use plain text symbols
            return self.style_settings.get("default_symbols", {}).get(key, fallback)
            
        return self._get_emoji_set().get(key, fallback)
        
    def get_box_char(self, key, fallback=""):
        """
        Get a box drawing character by key.
        
        Args:
            key (str): Character type: top_left, horizontal, etc.
            fallback (str): Fallback character if not found
            
        Returns:
            str: The box drawing character
        """
        if not self.style_settings.get("use_boxes", True):
            # If fancy boxes are disabled, use ASCII
            return self.style_settings.get("box_styles", {}).get("ascii", {}).get(key, fallback)
            
        return self._get_box_style().get(key, fallback)
        
    def get_terminal_width(self):
        """Get the terminal width to use for formatting."""
        width = self.style_settings.get("terminal_width", "auto")
        if width == "auto" or not isinstance(width, int):
            # If not set or invalid, get from terminal or use default
            try:
                columns, _ = shutil.get_terminal_size()
                return columns
            except Exception:
                return 80
        return width
        
    def set_theme(self, theme_name):
        """
        Change the current theme.
        
        Args:
            theme_name (str): Name of the theme to use
            
        Returns:
            bool: True if successful, False otherwise
        """
        if theme_name in self.style_settings.get("themes", {}):
            self.theme = self.style_settings["themes"][theme_name]
            return True
        return False
        
    def format_box(self, content, title=None, width=None):
        """
        Create a box around content with an optional title.
        
        Args:
            content (str): The text content to place in the box
            title (str): Optional title to display at the top of the box
            width (int): Custom width, otherwise uses terminal width - 4
            
        Returns:
            str: Content formatted in a box
        """
        # Process RTL text
        content = self._process_rtl_text(content)
        if title:
            title = self._process_rtl_text(title)
            
        # Skip box formatting if boxes are disabled
        if not self.style_settings.get("use_boxes", True):
            if title:
                return f"{title}\n{'-' * len(title)}\n{content}"
            return content
            
        # Get box characters
        tl = self.get_box_char("top_left", "+")
        tr = self.get_box_char("top_right", "+")
        bl = self.get_box_char("bottom_left", "+")
        br = self.get_box_char("bottom_right", "+")
        h = self.get_box_char("horizontal", "-")
        v = self.get_box_char("vertical", "|")
        
        # Determine width
        term_width = width or (self.get_terminal_width() - 4)
        lines = content.split('\n')
        
        # Create the box
        if title:
            title_str = f" {title} "
            top = f"{tl}{h}{title_str}" + h * (term_width - len(title_str) - 2) + f"{tr}"
        else:
            top = f"{tl}" + h * term_width + f"{tr}"
            
        bottom = f"{bl}" + h * term_width + f"{br}"
        
        # Format the content
        formatted_lines = []
        for line in lines:
            # Handle long lines by truncating or wrapping
            if len(line) > term_width - 2:
                # Simple truncation for now - could be enhanced with actual wrapping
                line = line[:term_width-5] + "..."
            formatted_lines.append(f"{v} {line:<{term_width-2}} {v}")
                
        # Combine everything
        return top + "\n" + "\n".join(formatted_lines) + "\n" + bottom
        
    def format_header(self, text, emoji_key=None):
        """
        Format a section header with optional emoji.
        
        Args:
            text (str): The header text
            emoji_key (str): Optional emoji key to use
            
        Returns:
            str: Formatted header
        """
        # Process RTL text
        text = self._process_rtl_text(text)
        
        emoji = ""
        if emoji_key:
            emoji = self.get_emoji(emoji_key) + " "
            
        return f"{emoji}{text}\n{'-' * (len(text) + (1 if emoji else 0))}\n"
        
    def format_status_line(self, label, status_key=None, message=None):
        """
        Format a status line with appropriate status emoji.
        
        Args:
            label (str): The label for the status item
            status_key (str): Key for status emoji (success, warning, error, info)
            message (str): Optional status message or details
            
        Returns:
            str: Formatted status line
        """
        # Process RTL text
        label = self._process_rtl_text(label)
        if message:
            message = self._process_rtl_text(message)
            
        prefix = ""
        if status_key:
            emoji = self.get_emoji(status_key)
            if emoji:
                prefix = emoji + " "
                
        if message:
            return f"{prefix}{label}: {message}"
        return f"{prefix}{label}"
        
    def format_list(self, items, bullet_type="symbol", title=None):
        """
        Format a list of items with bullets.
        
        Args:
            items (list): List of items to format
            bullet_type (str): Type of bullet (symbol, number, letter)
            title (str): Optional list title
            
        Returns:
            str: Formatted list
        """
        # Process RTL text
        if self.rtl_support:
            items = [self._process_rtl_text(item) for item in items]
            if title:
                title = self._process_rtl_text(title)
                
        result = []
        
        # Add title if provided
        if title:
            result.append(f"{title}:")
        
        # Process each item
        for i, item in enumerate(items):
            if bullet_type == "number":
                prefix = f"{i+1}. "
            elif bullet_type == "letter":
                prefix = f"{chr(97+i)}. "
            else:
                prefix = "• "
            
            result.append(f"{prefix}{item}")
        
        return "\n".join(result)
        
    def format_thinking(self, content):
        """
        Format a thinking message.
        
        Args:
            content (str): The thinking content
            
        Returns:
            str: Formatted thinking message
        """
        # Process RTL text
        content = self._process_rtl_text(content)
        
        emoji = self.get_emoji("thinking", "🤔")
        title = "Thinking" if not self.rtl_support else "جاري التفكير"
        return self.format_box(content, title)
        
    def format_command(self, command):
        """
        Format a command to be executed.
        
        Args:
            command (str): The command to format
            
        Returns:
            str: Formatted command
        """
        # Process RTL text
        command = self._process_rtl_text(command)
        
        emoji = self.get_emoji("command", "📌")
        prefix = "Executing" if not self.rtl_support else "جاري التنفيذ"
        return f"{emoji} {prefix}: {command}"
        
    def format_result(self, success, message):
        """
        Format a result message.
        
        Args:
            success (bool): Whether the operation was successful
            message (str): The result message
            
        Returns:
            str: Formatted result
        """
        # Process RTL text
        message = self._process_rtl_text(message)
        
        status_key = "success" if success else "error"
        emoji = self.get_emoji(status_key)
        return f"{emoji} {message}"
        
    def format_explanation(self, message):
        """
        Format an explanation message.
        
        Args:
            message (str): The explanation to format
            
        Returns:
            str: Formatted explanation
        """
        # Process RTL text
        message = self._process_rtl_text(message)
        
        emoji = self.get_emoji("info", "💬")
        return f"{emoji} {message}"

# Simple test if run directly
if __name__ == "__main__":
    # Create style manager with default settings
    style_mgr = OutputStyleManager()
    
    # Show available themes
    themes = list(style_mgr.style_settings.get("themes", {}).keys())
    print(f"Available themes: {', '.join(themes)}")
    
    # Demo different themes
    for theme in themes:
        print(f"\nTheme: {theme}")
        style_mgr.set_theme(theme)
        
        # Show header
        print(style_mgr.format_header("System Status", "robot"))
        
        # Show status lines
        print(style_mgr.format_status_line("Database connection", "success", "Connected"))
        print(style_mgr.format_status_line("Memory usage", "warning", "85% used"))
        print(style_mgr.format_status_line("Network", "error", "Disconnected"))
        
        # Show a box
        content = "CPU: 45% utilization\nRAM: 3.2GB/8GB used\nDisk: 120GB free"
        print("\n" + style_mgr.format_box(content, title="System Resources"))
        
        # Show the new formatting methods
        print("\n" + style_mgr.format_thinking("I'm analyzing the system status..."))
        print("\n" + style_mgr.format_command("uptime"))
        print("\n" + style_mgr.format_result(True, "Command executed successfully"))
        print("\n" + style_mgr.format_explanation("The system has been running for 3 days."))
