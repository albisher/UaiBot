#!/usr/bin/env python3
"""
Output formatter for UaiBot.
Provides consistent formatting for all UaiBot outputs.

Output Philosophy & Flow:
- Show 'thinking' only if no direct command is found or user asks for explanation.
- Always show the command to be executed (in a clear line/box).
- Always show the result of the command (in a result box/section).
- Only show AI explanation if user asks for it or no direct command is possible.
- Never show duplicate outputs of any type.
- This module should be used by all modules to enforce the above.
"""

import os
import shutil
import json
from pathlib import Path

# Define emoji constants for consistent usage across the application
EMOJI = {
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
    "question": "❓"
}

def get_terminal_width():
    """Get the terminal width with fallback."""
    try:
        return shutil.get_terminal_size().columns
    except:
        return 80

def format_header(text, emoji=None):
    """Format a section header with optional emoji."""
    if emoji:
        if isinstance(emoji, str) and emoji in EMOJI:
            emoji = EMOJI[emoji]
        header = f"{emoji} {text}"
    else:
        header = text
        
    return f"{header}\n{'-' * len(header)}\n"

def format_table_row(label, value, width=20):
    """Format a table row with consistent spacing."""
    return f"{label:<{width}} {value}"

def format_status_line(label, status=None, message=None, emoji=True):
    """Format a status line with appropriate emoji."""
    prefix = ""
    if status and emoji:
        status_emoji = EMOJI.get(status, "")
        if status_emoji:
            prefix = f"{status_emoji} "
            
    if message:
        return f"{prefix}{label}: {message}"
    return f"{prefix}{label}"

def format_list(items, bullet="•", bullet_type="symbol"):
    """
    Format a list with consistent bullets.
    
    Args:
        items: List of items to format
        bullet: Bullet character to use
        bullet_type: 'symbol', 'number', or 'letter'
    
    Returns:
        str: Formatted list
    """
    result = ""
    for i, item in enumerate(items):
        if bullet_type == "number":
            prefix = f"{i+1}. "
        elif bullet_type == "letter":
            prefix = f"{chr(97+i)}. "
        else:
            prefix = f"{bullet} "
            
        result += f"{prefix}{item}\n"
    return result

def format_box(content, title=None, width=None):
    """Format content in a box with optional title."""
    # Box drawing characters
    tl, tr, bl, br = "╭", "╮", "╰", "╯"
    h, v = "─", "│"
    
    # Determine width
    if not width:
        width = get_terminal_width() - 4
        
    # Split content into lines
    lines = content.strip().split('\n')
    
    # Create the box
    result = []
    if title:
        title_str = f" {title} "
        padding = width - len(title_str) - 2
        result.append(f"{tl}{h}{title_str}{h * padding}{tr}")
    else:
        result.append(f"{tl}{h * width}{tr}")
        
    # Add content lines
    for line in lines:
        if len(line) > width - 2:  # Account for box borders
            line = line[:width - 5] + "..."
        result.append(f"{v} {line.ljust(width - 2)} {v}")
        
    # Add bottom of box
    result.append(f"{bl}{h * width}{br}")
    
    return "\n".join(result)

def create_divider(style="partial", width=None):
    """Create a divider with specified style."""
    if not width:
        width = get_terminal_width()
        
    if style == "full":
        return "=" * width
    elif style == "partial":
        return "-" * width
    elif style == "dotted":
        return "·" * width
    else:
        return "-" * width

def process_command_output(command, output_type, raw_output):
    """
    Process command output based on output type.
    
    Args:
        command (str): The command that was run
        output_type (str): Type of output (e.g., 'uptime', 'disk', 'status')
        raw_output (str): Raw command output
        
    Returns:
        str: Formatted output
    """
    # Process based on output type
    if output_type == "uptime":
        return format_status_line(f"System uptime: {raw_output.strip()}", "time")
        
    elif output_type == "disk":
        header = format_header("Disk Space", "folder")
        return header + raw_output
        
    elif output_type == "status":
        # Try to parse as JSON
        try:
            data = json.loads(raw_output)
            result = format_header("System Status", "robot")
            
            # Process each key in the status data
            for key, value in data.items():
                if key == "warnings":
                    for warning in value:
                        result += format_status_line(warning, "warning") + "\n"
                elif key == "errors":
                    for error in value:
                        result += format_status_line(error, "error") + "\n"
                else:
                    result += format_status_line(f"{key}: {value}", "success") + "\n"
                    
            return result
        except:
            # Not JSON, just format as text
            return format_header("System Status", "robot") + raw_output
            
    # Default processing - just return the raw output
    return raw_output
