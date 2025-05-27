#!/usr/bin/env python3
"""
Basic Output Formatter for Labeeb

This is a simplified version of the output formatting system that provides
basic styling capabilities without complex dependencies.
"""

import os
import json
import shutil

class BasicOutputFormatter:
    """
    A simple output formatter that provides basic styling without complex dependencies.
    """
    
    def __init__(self, theme="default"):
        """
        Initialize with the specified theme.
        
        Args:
            theme (str): The theme to use: default, minimal, or professional
        """
        self.theme = theme
        self._load_styles()
    
    def _load_styles(self):
        """Load the styles from the configuration file or use defaults."""
        self.emojis = {
            # Default emoji set
            "success": "✅",
            "warning": "⚠️",
            "error": "❌",
            "info": "ℹ️",
            "robot": "🤖",
            "stats": "📊",
            "folder": "📁",
            "time": "🕒",
            "green": "🟢",
            "document": "📝",
            "computer": "💻",
        }
        
        # Override for minimal theme
        if self.theme == "minimal":
            self.emojis = {
                "success": "+",
                "warning": "!",
                "error": "x",
                "info": "i",
                "robot": "R",
                "stats": "#",
                "folder": "D",
                "time": "T",
                "green": "O",
                "document": "f",
                "computer": "C",
            }
        
        # Override for professional theme
        elif self.theme == "professional":
            self.emojis = {
                "success": "[OK]",
                "warning": "[!]",
                "error": "[X]",
                "info": "[i]",
                "robot": "[BOT]",
                "stats": "[STATS]",
                "folder": "[DIR]",
                "time": "[TIME]",
                "green": "[+]",
                "document": "[DOC]",
                "computer": "[PC]",
            }
    
    def get_emoji(self, key):
        """Get an emoji by key for the current theme."""
        return self.emojis.get(key, "")
    
    def format_header(self, text, emoji_key=None):
        """Format a header with optional emoji."""
        emoji = ""
        if emoji_key:
            emoji = self.get_emoji(emoji_key) + " "
        
        return f"{emoji}{text}\n{'-' * (len(text) + (1 if emoji else 0))}\n"
    
    def format_status(self, message, status="info"):
        """Format a status message with appropriate indicator."""
        emoji = self.get_emoji(status)
        if emoji:
            return f"{emoji} {message}"
        return message
    
    def format_list(self, items, bullet="•"):
        """Format a list of items with consistent bullets."""
        result = ""
        for item in items:
            result += f"{bullet} {item}\n"
        return result
    
    def format_box(self, content, title=None, width=None):
        """
        Format content in a box with optional title.
        
        Args:
            content (str): The content to put in the box
            title (str): Optional title for the box
            width (int): Width of box, default is terminal width - 10
        """
        # Box drawing characters based on theme
        if self.theme == "minimal":
            tl, tr, bl, br, h, v = "+", "+", "+", "+", "-", "|"
        elif self.theme == "professional":
            tl, tr, bl, br, h, v = "╭", "╮", "╰", "╯", "─", "│"
        else:  # default
            tl, tr, bl, br, h, v = "╭", "╮", "╰", "╯", "─", "│"
        
        # Get terminal width if not specified
        if not width:
            try:
                width = shutil.get_terminal_size().columns - 10
            except:
                width = 70
        
        # Create the box
        if title:
            title_str = f" {title} "
            top = f"{tl}{h}{title_str}" + h * (width - len(title_str) - 2) + f"{tr}"
        else:
            top = f"{tl}" + h * width + f"{tr}"
            
        bottom = f"{bl}" + h * width + f"{br}"
        
        # Format the content
        formatted_lines = []
        for line in content.split('\n'):
            if len(line) > width - 2:
                line = line[:width-5] + "..."
            formatted_lines.append(f"{v} {line:<{width-2}} {v}")
                
        # Combine everything
        return top + "\n" + "\n".join(formatted_lines) + "\n" + bottom
    
    def process_command_output(self, command, output):
        """
        Process command output based on the command type.
        
        Args:
            command (str): The command that was run
            output (str): The raw output from the command
            
        Returns:
            str: Formatted output
        """
        if command == "uptime":
            return self.format_status(f"Uptime: {output.strip()}", "time")
        
        elif command == "disk":
            header = self.format_header("Disk Space", "folder")
            return header + output
        
        elif command == "status":
            header = self.format_header("System Status", "robot")
            
            # Try to parse as JSON
            try:
                data = json.loads(output)
                result = ""
                for key, value in data.items():
                    if key == "warnings":
                        for warning in value:
                            result += self.format_status(warning, "warning") + "\n"
                    elif key == "errors":
                        for error in value:
                            result += self.format_status(error, "error") + "\n"
                    else:
                        result += self.format_status(f"{key}: {value}", "success") + "\n"
                        
                return header + result
            except:
                # Not JSON, just format as text
                return header + output
        
        else:
            # Generic processing
            return output

# Simple test if run directly
if __name__ == "__main__":
    formatter = BasicOutputFormatter()
    
    print("Testing basic output formatter\n")
    
    # Test with default theme
    print("Default theme:")
    print(formatter.format_header("System Status", "robot"))
    print(formatter.format_status("Database connected", "success"))
    print(formatter.format_status("Memory usage high", "warning"))
    print(formatter.format_status("Network disconnected", "error"))
    
    content = "CPU: 45% utilization\nRAM: 3.2GB/8GB used\nDisk: 120GB free"
    print("\n" + formatter.format_box(content, title="System Resources"))
    
    # Test with minimal theme
    formatter = BasicOutputFormatter(theme="minimal")
    print("\n\nMinimal theme:")
    print(formatter.format_header("System Status", "robot"))
    print(formatter.format_status("Database connected", "success"))
    
    # Test with professional theme
    formatter = BasicOutputFormatter(theme="professional")
    print("\n\nProfessional theme:")
    print(formatter.format_header("System Status", "robot"))
    print(formatter.format_status("Database connected", "success"))
