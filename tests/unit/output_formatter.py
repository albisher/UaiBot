#!/usr/bin/env python3
"""
Output formatter for UaiBot test files.
Formats output consistently for file operation tests to make logs readable.
"""

import os
import sys
import shutil
import logging
import platform
from typing import Optional, List, Dict, Any, Union

# Add project root to sys.path to enable imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# Try to import the proper output formatter
try:
    from app.utils.output_style_manager import OutputStyleManager
    STYLE_MGR_AVAILABLE = True
except ImportError:
    STYLE_MGR_AVAILABLE = False
    
class TestOutputFormatter:
    """
    Simple formatter for test outputs that follows UaiBot styling guidelines.
    Falls back to basic formatting if OutputStyleManager isn't available.
    """
    
    def __init__(self, theme="default", log_to_file=False, log_file=None):
        """Initialize with the specified theme and logging options."""
        self.style_mgr = None
        if STYLE_MGR_AVAILABLE:
            try:
                self.style_mgr = OutputStyleManager(theme=theme)
            except Exception as e:
                print(f"Warning: Could not initialize OutputStyleManager: {e}")
                
        # Get system info for emoji compatibility
        self.is_windows = platform.system() == 'Windows'
        
        # Basic emojis for fallback mode (with Windows fallbacks)
        self.emojis = {
            "success": "✅" if not self.is_windows else "[OK]",
            "error": "❌" if not self.is_windows else "[ERROR]",
            "warning": "⚠️" if not self.is_windows else "[WARN]", 
            "info": "ℹ️" if not self.is_windows else "[INFO]",
            "search": "🔍" if not self.is_windows else "[SEARCH]",
            "file": "📄" if not self.is_windows else "[FILE]",
            "folder": "📁" if not self.is_windows else "[DIR]",
            "question": "❓" if not self.is_windows else "[?]",
            "thinking": "🤔" if not self.is_windows else "[THINKING]",
            "command": "📌" if not self.is_windows else "[CMD]"
        }
        
        self.output_shown = False
        self.setup_logging(log_to_file, log_file)
            
    def setup_logging(self, log_to_file: bool, log_file: Optional[str]):
        """Set up logging configuration."""
        log_level = logging.INFO
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        
        # Clear any existing handlers
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Configure logging
        logging.basicConfig(
            level=log_level,
            format=log_format,
            handlers=[logging.StreamHandler(sys.stdout)] if not log_to_file else []
        )
        
        # Add file handler if requested
        if log_to_file and log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(logging.Formatter(log_format))
            logging.getLogger().addHandler(file_handler)
    
    def format_command_output(self, command: str, stdout: str, stderr: str, return_code: int) -> str:
        """Format command execution output in a standardized way."""
        output_lines = []
        output_lines.append(f"Command: {command}")
        output_lines.append("")
        
        output_lines.append("STDOUT:")
        output_lines.append(stdout.strip() if stdout else "(No output)")
        output_lines.append("")
        
        if stderr:
            output_lines.append("STDERR:")
            output_lines.append(stderr.strip())
            output_lines.append("")
        
        output_lines.append(f"Exit code: {return_code}")
        
        return "\n".join(output_lines)
    
    def print_thinking_box(self, message: str):
        """Print a thinking box with the given message."""
        if self.output_shown:
            return
            
        width = max(len(line) for line in message.split('\n')) + 4
        horizontal_line = "┌" + "─" * (width - 2) + "┐"
        closing_line = "└" + "─" * (width - 2) + "┘"
        
        lines = [horizontal_line]
        for line in message.split('\n'):
            lines.append(f"│ {line:<{width-4}} │")
        lines.append(closing_line)
        
        formatted_box = "\n".join(lines)
        print(f"🤔 Thinking...\n{formatted_box}")
        logging.info(f"🤔 Thinking...\n{formatted_box}")
    
    def print_result(self, result_type: str, message: str):
        """Print a result message with appropriate emoji."""
        if self.output_shown:
            return
            
        emoji = self._get_emoji_for_result(result_type)
        print(f"{emoji} {message}")
        logging.info(f"{emoji} {message}")
        self.output_shown = True
    
    def reset_output_status(self):
        """Reset the output status to allow new output."""
        self.output_shown = False
    
    def _get_emoji_for_result(self, result_type: str) -> str:
        """Get an appropriate emoji for the result type."""
        emoji_map = self.emojis
        return emoji_map.get(result_type.lower(), '•')
    
    def format_header(self, text: str, emoji_key: Optional[str] = None) -> str:
        """Format a header with optional emoji."""
        if self.style_mgr:
            return self.style_mgr.format_header(text, emoji_key)
            
        # Basic fallback formatting
        emoji = ""
        if emoji_key and emoji_key in self.emojis:
            emoji = f"{self.emojis[emoji_key]} "
            
        return f"{emoji}{text}\n{'-' * len(text)}\n"
    
    def format_status(self, message: str, status: str = "info") -> str:
        """Format a status message with appropriate emoji."""
        if self.style_mgr:
            return self.style_mgr.format_status_line(message, status)
            
        # Basic fallback formatting
        emoji = self.emojis.get(status, "")
        if emoji:
            return f"{emoji} {message}"
        return message
        
    def format_box(self, content: str, title: Optional[str] = None, width: Optional[int] = None) -> str:
        """Format content in a box with optional title."""
        if self.style_mgr:
            return self.style_mgr.format_box(content, title, width)
            
        # Basic fallback box formatting
        if not width:
            try:
                width = shutil.get_terminal_size().columns - 4
            except:
                width = 80
                
        # Simple ASCII box
        result = []
        if title:
            result.append(f"┌─── {title} {'─' * (width - len(title) - 6)}┐")
        else:
            result.append(f"┌{'─' * (width - 2)}┐")
            
        for line in content.split('\n'):
            if len(line) > width - 4:
                line = line[:width-7] + '...'
            result.append(f"│ {line}{' ' * (width - len(line) - 3)}│")
            
        result.append(f"└{'─' * (width - 2)}┘")
        return '\n'.join(result)
    
    def format_file_operation_result(self, operation: str, success: bool, 
                                    message: str, details: Optional[str] = None) -> str:
        """Format the result of a file operation in a consistent way."""
        status = "success" if success else "error"
        result = self.format_status(f"{operation}: {message}", status)
        
        if details:
            # Add indented details if provided
            result += "\n  " + "\n  ".join(details.split("\n"))
            
        return result
    
    def get_platform_info(self) -> Dict[str, str]:
        """Return information about the current platform for reporting."""
        return {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "python": platform.python_version(),
            "emoji_support": "Limited" if self.is_windows else "Full"
        }
    
# Create a singleton instance for import elsewhere
formatter = TestOutputFormatter()

def format_header(text, emoji_key=None):
    """Convenience function for formatting headers."""
    return formatter.format_header(text, emoji_key)
    
def format_status(message, status="info"):
    """Convenience function for formatting status messages."""
    return formatter.format_status(message, status)
    
def format_box(content, title=None, width=None):
    """Convenience function for formatting content in a box."""
    return formatter.format_box(content, title, width)
    
def format_file_operation(operation, success, message, details=None):
    """Convenience function for formatting file operation results."""
    return formatter.format_file_operation_result(operation, success, message, details)
    
def format_command_output(command, stdout, stderr=None, exit_code=None):
    """Convenience function for formatting command execution output."""
    return formatter.format_command_output(command, stdout, stderr, exit_code)
