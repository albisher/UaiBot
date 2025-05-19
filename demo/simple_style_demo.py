#!/usr/bin/env python3
"""
UaiBot Output Style Demo

This is a simplified demonstration of the themes and styling capabilities
for UaiBot's output formatting system.
"""

import os
import sys
import json
import time
import shutil

# Ensure we're in the project root
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir))
sys.path.append(project_root)

# Print some debug information
print(f"Python version: {sys.version}")
print(f"Current directory: {current_dir}")
print(f"Python path: {sys.path}")

# Load the output style configuration
config_path = os.path.join(project_root, "config", "output_styles.json")
print(f"\nLoading config from: {config_path}")

try:
    with open(config_path, 'r') as f:
        config = json.load(f)
    print("Config loaded successfully")
    
    # Show available themes
    themes = list(config.get("themes", {}).keys())
    print(f"Available themes: {', '.join(themes)}")
    
    # Basic functions for formatting output
    def get_emoji(theme_name, emoji_key):
        """Get an emoji for the specified theme and key"""
        theme = config["themes"].get(theme_name, {})
        emoji_set_name = theme.get("emoji_set", "default")
        emoji_set = config.get("emoji_sets", {}).get(emoji_set_name, {})
        return emoji_set.get(emoji_key, "")
    
    def get_box_char(theme_name, char_key):
        """Get a box drawing character for the specified theme and key"""
        theme = config["themes"].get(theme_name, {})
        box_style_name = theme.get("box_style", "default")
        box_style = config.get("box_styles", {}).get(box_style_name, {})
        return box_style.get(char_key, "")
    
    def format_header(theme_name, text, emoji_key=None):
        """Format a header with optional emoji"""
        emoji = ""
        if emoji_key:
            emoji = get_emoji(theme_name, emoji_key) + " "
        
        return f"{emoji}{text}\n{'-' * (len(text) + (1 if emoji else 0))}\n"
    
    def format_status_line(theme_name, label, status_key=None, message=None):
        """Format a status line with appropriate emoji"""
        prefix = ""
        if status_key:
            emoji = get_emoji(theme_name, status_key)
            if emoji:
                prefix = emoji + " "
        
        if message:
            return f"{prefix}{label}: {message}"
        return f"{prefix}{label}"
    
    def format_box(theme_name, content, title=None):
        """Format content in a box with optional title"""
        tl = get_box_char(theme_name, "top_left") or "+"
        tr = get_box_char(theme_name, "top_right") or "+"
        bl = get_box_char(theme_name, "bottom_left") or "+"
        br = get_box_char(theme_name, "bottom_right") or "+"
        h = get_box_char(theme_name, "horizontal") or "-"
        v = get_box_char(theme_name, "vertical") or "|"
        
        # Get terminal width
        term_width = shutil.get_terminal_size().columns - 10
        
        # Create the box
        if title:
            title_str = f" {title} "
            top = f"{tl}{h}{title_str}" + h * (term_width - len(title_str) - 2) + f"{tr}"
        else:
            top = f"{tl}" + h * term_width + f"{tr}"
            
        bottom = f"{bl}" + h * term_width + f"{br}"
        
        # Format the content
        formatted_lines = []
        for line in content.split('\n'):
            if len(line) > term_width - 2:
                line = line[:term_width-5] + "..."
            formatted_lines.append(f"{v} {line:<{term_width-2}} {v}")
                
        # Combine everything
        return top + "\n" + "\n".join(formatted_lines) + "\n" + bottom
    
    # Demo each theme
    for theme in themes:
        divider = "=" * 80
        print(f"\n{divider}")
        print(f"Theme: {theme}")
        print(f"{divider}")
        
        # Show header
        print(format_header(theme, "System Status", "robot"))
        
        # Show status lines
        print(format_status_line(theme, "Database connection", "success", "Connected"))
        print(format_status_line(theme, "Memory usage", "warning", "85% used"))
        print(format_status_line(theme, "Network", "error", "Disconnected"))
        
        # Show a box
        content = "CPU: 45% utilization\nRAM: 3.2GB/8GB used\nDisk: 120GB free"
        print("\n" + format_box(theme, content, title="System Resources"))
        
        # Sleep briefly between themes
        time.sleep(0.5)
    
    print("\nDemo completed!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
