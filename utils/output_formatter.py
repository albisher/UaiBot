#!/usr/bin/env python3
"""
Output Formatter - Utility functions for formatting UaiBot's output consistently.

This module implements the formatting guidelines from enhance_output.txt
to create an intuitive, visually pleasing, and accessible user experience.
"""

import shutil

# Emoji dictionary for consistent usage across the application
EMOJI = {
    # Status emojis
    "success": "✅",
    "warning": "⚠️", 
    "error": "❌",
    "info": "ℹ️",
    "loading": "🔄",
    
    # System emojis
    "robot": "🤖",
    "settings": "⚙️",
    "security": "🔐",
    "stats": "📊",
    
    # Device emojis
    "computer": "💻",
    "mobile": "📱",
    "printer": "🖨️",
    "camera": "📷",
    "controller": "🎮",
    
    # File emojis
    "folder": "📁",
    "file": "📄",
    "document": "📝",
    "code": "📜",
    
    # Network emojis
    "web": "🌐",
    "signal": "📡",
    "wifi": "📶",
    "lock": "🔒",
    
    # Status indicators
    "green": "🟢",
    "yellow": "🟡",
    "red": "🔴",
    "blue": "🔵",
    
    # Action emojis
    "search": "🔍",
    "play": "▶️",
    "pause": "⏸️",
    "stop": "⏹️",
    
    # Miscellaneous
    "tip": "💡",
    "time": "🕒",
    "question": "❓",
    "thinking": "🤔",
}

def format_header(text, emoji=""):
    """Format a section header with optional emoji"""
    if emoji:
        return f"{emoji} {text}\n{'-' * (len(text) + 3)}\n"
    return f"{text}\n{'-' * len(text)}\n"

def format_table_row(label, value, width=20):
    """Format a table row with consistent spacing"""
    return f"{label:<{width}} {value}"

def get_terminal_width():
    """Get the current terminal width"""
    try:
        term_width, _ = shutil.get_terminal_size()
        return term_width
    except Exception:
        return 80  # Default fallback width

def create_divider(style="full", width=None):
    """
    Create a visual divider line.
    
    Args:
        style (str): "full" (═════), "partial" (─────), "dots" (·····) or "box" (box drawing)
        width (int): Custom width, otherwise uses terminal width
    
    Returns:
        str: The divider line
    """
    width = width or get_terminal_width()
    
    if style == "full":
        return "═" * width
    elif style == "partial":
        return "─" * width
    elif style == "dots":
        return "·" * width
    elif style == "box":
        return "┌" + "─" * (width - 2) + "┐"
    else:
        return "-" * width

def format_box(content, title=None, width=None):
    """
    Create a box around content with an optional title.
    
    Args:
        content (str): The text content to place in the box
        title (str): Optional title to display at the top of the box
        width (int): Custom width, otherwise uses terminal width - 4
        
    Returns:
        str: Content formatted in a box
    """
    term_width = width or get_terminal_width() - 4
    lines = content.split('\n')
    
    # Create the box
    if title:
        title_str = f" {title} "
        top = f"╭─{title_str}" + "─" * (term_width - len(title_str) - 2) + "╮"
    else:
        top = "╭" + "─" * term_width + "╮"
        
    bottom = "╰" + "─" * term_width + "╯"
    
    # Format the content
    formatted_lines = []
    for line in lines:
        formatted_lines.append(f"│ {line:<{term_width-2}} │")
            
    # Combine everything
    return top + "\n" + "\n".join(formatted_lines) + "\n" + bottom

def format_status_line(label, status, value=None, emoji=True):
    """
    Format a status line with appropriate status emoji.
    
    Args:
        label (str): The label for the status item
        status (str): One of "success", "warning", "error", "info"
        value (str): Optional value or message
        emoji (bool): Whether to include the emoji
        
    Returns:
        str: Formatted status line
    """
    status_emoji = EMOJI.get(status, "")
    
    if value:
        if emoji and status_emoji:
            return f"{status_emoji} {label}: {value}"
        return f"{label}: {value}"
    else:
        if emoji and status_emoji:
            return f"{status_emoji} {label}"
        return label

def format_list(items, bullet_type="emoji", emoji_key=None):
    """
    Format a list of items with consistent bullets.
    
    Args:
        items (list): List of items to format
        bullet_type (str): One of "emoji", "dash", "bullet", "number"
        emoji_key (str): Key to use from EMOJI dict if bullet_type is "emoji"
        
    Returns:
        str: Formatted list
    """
    result = []
    
    for i, item in enumerate(items):
        if bullet_type == "emoji" and emoji_key and emoji_key in EMOJI:
            result.append(f"{EMOJI[emoji_key]} {item}")
        elif bullet_type == "emoji":
            # Default to the info emoji
            result.append(f"{EMOJI['info']} {item}")
        elif bullet_type == "dash":
            result.append(f"- {item}")
        elif bullet_type == "bullet":
            result.append(f"• {item}")
        elif bullet_type == "number":
            result.append(f"{i+1}. {item}")
            
    return "\n".join(result)

# Example usage:
if __name__ == "__main__":
    print(format_header("UaiBot Status Report", emoji=EMOJI["robot"]))
    
    print(format_status_line("System", "success", "Online"))
    print(format_status_line("Database", "warning", "Slow connection"))
    print(format_status_line("Network", "error", "Disconnected"))
    
    devices = ["Arduino (COM3)", "Webcam C920", "External Drive"]
    print("\n" + format_header("Connected Devices", emoji=EMOJI["device"]))
    print(format_list(devices, bullet_type="emoji", emoji_key="green"))
    
    print("\n" + format_box("CPU: 45% utilization\nRAM: 3.2GB/8GB used\nDisk: 120GB free", 
                          title="System Resources"))
