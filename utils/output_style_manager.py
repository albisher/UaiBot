#!/usr/bin/env python3
"""
Output Style Manager for UaiBot

Handles loading and applying output formatting styles based on user preferences
and system capabilities. This provides a centralized way to manage appearance
across the application.
"""

import os
import json
import shutil
import platform

from pathlib import Path

class OutputStyleManager:
    """Manages output styling preferences for UaiBot."""
    
    def __init__(self, config_path=None, theme="default", auto_detect=True):
        """
        Initialize the style manager.
        
        Args:
            config_path (str): Path to the output styles config file.
                Default is config/output_styles.json in the project root.
            theme (str): The theme to use (default, minimal, professional).
            auto_detect (bool): If True, auto-detects terminal capabilities.
        """
        self.project_root = self._get_project_root()
        
        # Default config path if not provided
        if config_path is None:
            config_path = os.path.join(self.project_root, "config", "output_styles.json")
            
        self.config_path = config_path
        self.config = self._load_config()
        self.theme_name = theme
        
        # Load the selected theme or fall back to default
        if theme in self.config.get("themes", {}):
            self.theme = self.config["themes"][theme]
        else:
            self.theme = self.config["themes"]["default"]
            
        # Get styles for the selected theme
        self.emoji_set = self._get_emoji_set()
        self.box_style = self._get_box_style()
        
        # Get general output settings
        self.output_styles = self.config.get("output_styles", {})
        
        # Auto-detect terminal capabilities if requested
        if auto_detect:
            self._detect_terminal_capabilities()
            
    def _get_project_root(self):
        """Get the path to the project root directory."""
        return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            
    def _load_config(self):
        """Load styling configuration from file."""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading output styles config: {e}")
            # Return minimal default configuration with extended emoji set
            return {
                "output_styles": {"use_emojis": True, "use_color": True},
                "emoji_sets": {
                    "default": {
                        "success": "✅",
                        "warning": "⚠️",
                        "error": "❌",
                        "info": "ℹ️",
                        "robot": "🤖",
                        "stats": "📊",
                        "folder": "📁",
                        "file": "📄",
                        "time": "🕒",
                        "green": "🟢",
                        "yellow": "🟡",
                        "red": "🔴",
                        "document": "📝",
                        "computer": "💻",
                        "mobile": "📱",
                        "search": "🔍",
                        "tip": "💡",
                        "question": "❓",
                        "thinking": "🤔",
                        "command": "📌",
                        "explanation": "💬"
                    },
                    "minimal": {
                        "success": "+",
                        "warning": "!",
                        "error": "x",
                        "info": "i",
                        "robot": "R",
                        "stats": "#",
                        "folder": "D",
                        "file": "F",
                        "time": "T",
                        "green": "o",
                        "yellow": "o",
                        "red": "o",
                        "document": "D",
                        "computer": "C",
                        "mobile": "M",
                        "search": "S",
                        "tip": "*",
                        "question": "?",
                        "thinking": "?",
                        "command": ">",
                        "explanation": "="
                    }
                },
                "box_styles": {"default": {}, "ascii": {}},
                "themes": {"default": {"emoji_set": "default", "box_style": "default"}}
            }
            
    def _get_emoji_set(self):
        """Get the emoji set for the current theme."""
        emoji_set_name = self.theme.get("emoji_set", "default")
        return self.config.get("emoji_sets", {}).get(emoji_set_name, {})
        
    def _get_box_style(self):
        """Get the box style for the current theme."""
        box_style_name = self.theme.get("box_style", "default")
        return self.config.get("box_styles", {}).get(box_style_name, {})
        
    def _detect_terminal_capabilities(self):
        """Auto-detect terminal capabilities and adjust settings."""
        # Check if we're in a TTY and determine terminal width
        try:
            is_tty = os.isatty(1)  # 1 = stdout
            if is_tty:
                # Get terminal size
                columns, _ = shutil.get_terminal_size()
                # Only update if set to auto
                if self.output_styles.get("terminal_width") == "auto":
                    self.output_styles["terminal_width"] = columns
                    
                # Check if we're in Windows command prompt (limited emoji support)
                if platform.system() == "Windows" and "TERM" not in os.environ:
                    # Using cmd.exe or PowerShell with limited capabilities
                    self.output_styles["use_emojis"] = False
            else:
                # Not a TTY, disable fancy formatting
                self.output_styles["use_emojis"] = False
                self.output_styles["use_boxes"] = False
                # Set a safe default width
                self.output_styles["terminal_width"] = 80
                
        except Exception:
            # Fallback to safe defaults on error
            self.output_styles["terminal_width"] = 80
            
    def get_emoji(self, key, fallback=""):
        """
        Get an emoji by key, respecting user preferences.
        
        Args:
            key (str): The emoji key, e.g., "success", "warning"
            fallback (str): Fallback character if emoji not found or disabled
            
        Returns:
            str: The emoji or fallback character
        """
        if not self.output_styles.get("use_emojis", True):
            # If emojis are disabled, use plain text symbols
            return self.output_styles.get("default_symbols", {}).get(key, fallback)
            
        return self.emoji_set.get(key, fallback)
        
    def get_box_char(self, key, fallback=""):
        """
        Get a box drawing character by key.
        
        Args:
            key (str): Character type: top_left, horizontal, etc.
            fallback (str): Fallback character if not found
            
        Returns:
            str: The box drawing character
        """
        if not self.output_styles.get("use_boxes", True):
            # If fancy boxes are disabled, use ASCII
            return self.config.get("box_styles", {}).get("ascii", {}).get(key, fallback)
            
        return self.box_style.get(key, fallback)
        
    def get_terminal_width(self):
        """Get the terminal width to use for formatting."""
        width = self.output_styles.get("terminal_width", "auto")
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
        if theme_name in self.config.get("themes", {}):
            self.theme_name = theme_name
            self.theme = self.config["themes"][theme_name]
            self.emoji_set = self._get_emoji_set()
            self.box_style = self._get_box_style()
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
        # Skip box formatting if boxes are disabled
        if not self.output_styles.get("use_boxes", True):
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
        prefix = ""
        if status_key:
            emoji = self.get_emoji(status_key)
            if emoji:
                prefix = emoji + " "
                
        if message:
            return f"{prefix}{label}: {message}"
        return f"{prefix}{label}"

    def format_list(self, items, bullet_type="symbol", bullet="•"):
        """
        Format a list of items with consistent bullets.
        
        Args:
            items (list): The items to format
            bullet_type (str): Type of bullet: 'symbol', 'number', or 'letter'
            bullet (str): Bullet character to use for symbol type
            
        Returns:
            str: Formatted list as a string
        """
        result = ""
        for i, item in enumerate(items):
            if bullet_type == "number":
                prefix = f"{i+1}. "
            elif bullet_type == "letter":
                prefix = f"{chr(97+i)}. "  # a, b, c...
            else:
                prefix = f"{bullet} "
                
            result += f"{prefix}{item}\n"
        return result
    
    def format_thinking(self, content):
        """
        Format thinking content with appropriate styling.
        
        Args:
            content (str): The thinking content to display
            
        Returns:
            str: Formatted thinking block
        """
        emoji = self.get_emoji("thinking", "🤔")
        return f"{emoji} {self.format_box(content, title='Thinking')}"
    
    def format_command(self, command):
        """
        Format a command with appropriate styling.
        
        Args:
            command (str): The command to display
            
        Returns:
            str: Formatted command line
        """
        emoji = self.get_emoji("command", "📌")
        return f"{emoji} Executing: {command}"
    
    def format_result(self, success, message):
        """
        Format a result message with success/failure styling.
        
        Args:
            success (bool): Whether the operation was successful
            message (str): The result message to display
            
        Returns:
            str: Formatted result message
        """
        status_key = "success" if success else "error"
        emoji = self.get_emoji(status_key)
        return f"{emoji} {message}"
    
    def format_explanation(self, message):
        """
        Format an explanation message.
        
        Args:
            message (str): The explanation to display
            
        Returns:
            str: Formatted explanation
        """
        emoji = self.get_emoji("explanation", "💬")
        return f"{emoji} {message}"

# Simple test if run directly
if __name__ == "__main__":
    # Create style manager with default settings
    style_mgr = OutputStyleManager()
    
    # Show available themes
    themes = list(style_mgr.config.get("themes", {}).keys())
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
