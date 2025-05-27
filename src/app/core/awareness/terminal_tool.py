"""
Labeeb Terminal Tool

This module provides terminal-related functionality for Labeeb.
It handles terminal output, formatting, and command execution capabilities.
"""
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass
import sys
import os
from colorama import init, Fore, Back, Style
from src.app.utils.output_style_manager import OutputStyleManager
from pathlib import Path
from src.app.core.platform_core.terminal_utils import clear_terminal

# Initialize colorama
init()

style_mgr = OutputStyleManager(config_path=str(Path(__file__).parent.parent.parent.parent / 'config' / 'output_styles.json'))

@dataclass
class TerminalConfig:
    """Configuration for terminal output."""
    use_colors: bool = True
    use_emoji: bool = True
    max_width: int = 80
    indent: int = 2

class TerminalTool:
    """Tool for displaying text in the terminal."""
    
    name = 'terminal'
    description = "Display text and formatted output in the terminal"
    
    def __init__(self):
        self.logger = logging.getLogger("TerminalTool")
        self.config = TerminalConfig()
        
    def _format_text(self, text: str, color: str = None, style: str = None) -> str:
        """Format text with colors and styles."""
        if not self.config.use_colors:
            return text
            
        formatted = text
        if color:
            formatted = getattr(Fore, color.upper(), '') + formatted
        if style:
            formatted = getattr(Style, style.upper(), '') + formatted
        if color or style:
            formatted += Style.RESET_ALL
        return formatted
        
    def _wrap_text(self, text: str, width: int = None) -> str:
        """Wrap text to fit terminal width."""
        if width is None:
            width = self.config.max_width
            
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 <= width:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
                
        if current_line:
            lines.append(' '.join(current_line))
            
        return '\n'.join(lines)
        
    async def show_text(self, text: str, color: str = None, style: str = None, indent: int = None, status_key: str = "info") -> bool:
        """Display text in the terminal."""
        try:
            emoji_text = style_mgr.format_status_line(text, status_key=status_key)
            formatted_text = self._format_text(emoji_text, color, style)
            wrapped_text = self._wrap_text(formatted_text)
            
            if indent is None:
                indent = self.config.indent
                
            indented_text = '\n'.join(' ' * indent + line for line in wrapped_text.split('\n'))
            print(indented_text)
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to show text: {e}")
            return False
            
    async def show_error(self, text: str) -> bool:
        """Display error text in the terminal."""
        return await self.show_text(text, color='red', style='bright', status_key='error')
        
    async def show_success(self, text: str) -> bool:
        """Display success text in the terminal."""
        return await self.show_text(text, color='green', style='bright', status_key='success')
        
    async def show_warning(self, text: str) -> bool:
        """Display warning text in the terminal."""
        return await self.show_text(text, color='yellow', style='bright', status_key='warning')
        
    async def show_info(self, text: str) -> bool:
        """Display info text in the terminal."""
        return await self.show_text(text, color='blue', status_key='info')
        
    def clear(self):
        clear_terminal()
            
    async def configure(self, **kwargs) -> bool:
        """Configure terminal settings."""
        try:
            for key, value in kwargs.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
            return True
        except Exception as e:
            self.logger.error(f"Failed to configure terminal: {e}")
            return False
            
    async def execute(self, action: str, **kwargs) -> Any:
        """Execute a terminal action."""
        try:
            actions = {
                "show_text": lambda: self.show_text(kwargs.get("text", ""), kwargs.get("color"), kwargs.get("style")),
                "show_error": lambda: self.show_error(kwargs.get("text", "")),
                "show_success": lambda: self.show_success(kwargs.get("text", "")),
                "show_warning": lambda: self.show_warning(kwargs.get("text", "")),
                "show_info": lambda: self.show_info(kwargs.get("text", "")),
                "clear": self.clear,
                "configure": lambda: self.configure(**kwargs)
            }
            if action not in actions:
                raise ValueError(f"Unknown action: {action}")
            result = await actions[action]()
            # Always return a string or dict with a message
            if isinstance(result, dict):
                for key in ("message", "output", "text"):
                    if key in result:
                        return result[key]
                return str(result)
            elif isinstance(result, str):
                return result
            elif result is True:
                return "✅ Done."
            elif result is False or result is None:
                return "⚠️ No output."
            else:
                return str(result)
        except Exception as e:
            self.logger.error(f"Error executing terminal action: {e}")
            return f"❌ Error: {e}" 