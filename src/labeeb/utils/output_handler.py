#!/usr/bin/env python3
"""
OutputHandler for Labeeb

A unified facade for output operations that enforces the output flow and
prevents duplicate outputs. Acts as the central component of the output system.

Output Philosophy & Flow:
- Show 'thinking' only if no direct command is found or user asks for explanation.
- Always show the command to be executed (in a clear line/box).
- Always show the result of the command (in a result box/section).
- Only show AI explanation if user asks for it or no direct command is possible.
- Never show duplicate outputs of any type.
- Support RTL languages (Arabic) with proper text reshaping and display.
"""

import sys
import re
import os
from datetime import datetime
from typing import List, Dict, Any, Optional, Union, Tuple
from pathlib import Path
import arabic_reshaper
from bidi.algorithm import get_display

# Import the style manager
from labeeb.utils.output_style_manager import OutputStyleManager
from labeeb.core.logging_config import get_logger

logger = get_logger(__name__)

class OutputHandler:
    """
    The central facade for all Labeeb output operations.
    
    This class:
    1. Enforces the output flow (thinking → command → result)
    2. Prevents duplicate outputs
    3. Provides consistent styling using OutputStyleManager
    4. Supports output capture for testing and redirection
    5. Handles RTL languages with proper text reshaping and display
    """
    
    def __init__(self, theme: str = "default") -> None:
        """
        Initialize the output handler.
        
        Args:
            theme: The theme to use for styling
        """
        # State tracking
        self.capture_mode = False
        self.captured_output = []
        self.thinking_shown = False
        self.command_shown = False
        self.result_shown = False
        
        # Core styling engine
        self.style_mgr = OutputStyleManager(theme=theme, config_path=str(Path(__file__).parent.parent.parent / 'config' / 'output_styles.json'))
        
        # Special display flags
        self.verbose_mode = False  # When True, shows more details
        self.debug_mode = False    # When True, shows debugging information
        self.verbosity = 'normal'  # Default verbosity level
        self.rtl_support = False   # RTL language support
    
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
    
    def start_capture(self) -> None:
        """Start capturing output for later retrieval."""
        self.capture_mode = True
        self.captured_output = []
    
    def stop_capture(self) -> str:
        """
        Stop capturing output and return the captured content.
        
        Returns:
            str: All captured output as a single string
        """
        self.capture_mode = False
        return "\n".join(self.captured_output)
    
    def capture_print(self, *args, **kwargs) -> str:
        """
        Custom print function that captures output during capture mode.
        
        Args:
            *args: Standard print arguments
            **kwargs: Standard print keyword arguments
            
        Returns:
            str: The string that was printed
        """
        # Process RTL text in args
        if self.rtl_support:
            args = [self._process_rtl_text(str(arg)) for arg in args]
            
        output = " ".join(map(str, args))
        
        if self.capture_mode:
            self.captured_output.append(output)
        else:
            print(output, **kwargs)
        
        return output
    
    def thinking(self, message: str) -> Optional[str]:
        """
        Display thinking message (only once per sequence).
        
        Args:
            message: The thinking content to display
            
        Returns:
            str or None: The formatted output if shown, None if skipped
        """
        if self.thinking_shown and not self.debug_mode:
            return None
            
        self.thinking_shown = True
        
        # Process RTL text
        message = self._process_rtl_text(message)
        
        # Format thinking box using style manager
        formatted_box = self.style_mgr.format_box(
            content=message, 
            title="Thinking" if not self.rtl_support else "جاري التفكير"
        )
        
        emoji = self.style_mgr.get_emoji("thinking", "🤔")
        output = f"{emoji} {formatted_box}"
        
        return self.capture_print(output)
    
    def command(self, cmd: str) -> Optional[str]:
        """
        Display command to be executed (only once per sequence).
        
        Args:
            cmd: The command string to display
            
        Returns:
            str or None: The formatted output if shown, None if skipped
        """
        if self.command_shown and not self.debug_mode:
            return None
            
        self.command_shown = True
        
        # Process RTL text
        cmd = self._process_rtl_text(cmd)
        
        emoji = self.style_mgr.get_emoji("command", "📌")
        prefix = "Executing" if not self.rtl_support else "جاري التنفيذ"
        output = f"{emoji} {prefix}: {cmd}"
        
        return self.capture_print(output)
    
    def result(self, success: bool, message: str) -> Optional[str]:
        """
        Display result message (only once per sequence).
        
        Args:
            success: Whether the operation was successful
            message: The result message to display
            
        Returns:
            str or None: The formatted output if shown, None if skipped
        """
        if self.result_shown and not self.debug_mode:
            return None
            
        self.result_shown = True
        
        # Process RTL text
        message = self._process_rtl_text(message)
        
        status_key = "success" if success else "error"
        emoji = self.style_mgr.get_emoji(status_key)
        output = f"{emoji} {message}"
        
        return self.capture_print(output)
    
    def explanation(self, message: str) -> str:
        """
        Display explanation text.
        
        Args:
            message: The explanation to display
            
        Returns:
            str: The formatted output
        """
        # Process RTL text
        message = self._process_rtl_text(message)
        
        emoji = self.style_mgr.get_emoji("info", "💬")
        output = f"{emoji} {message}"
        
        return self.capture_print(output)
    
    def status(self, message: str, status_key: str = "info") -> str:
        """
        Display a status message with appropriate indicator.
        
        Args:
            message: The status message
            status_key: Key for the status type (success, warning, error, info)
            
        Returns:
            str: The formatted output
        """
        # Process RTL text
        message = self._process_rtl_text(message)
        
        return self.capture_print(
            self.style_mgr.format_status_line(message, status_key)
        )
    
    def header(self, text: str, emoji_key: Optional[str] = None) -> str:
        """
        Display a section header.
        
        Args:
            text: The header text
            emoji_key: Optional emoji key to use
            
        Returns:
            str: The formatted header
        """
        # Process RTL text
        text = self._process_rtl_text(text)
        
        return self.capture_print(
            self.style_mgr.format_header(text, emoji_key)
        )
    
    def box(self, content: str, title: Optional[str] = None, width: Optional[int] = None) -> str:
        """
        Display content in a box.
        
        Args:
            content: The content to display
            title: Optional box title
            width: Optional box width
            
        Returns:
            str: The formatted box
        """
        # Process RTL text
        content = self._process_rtl_text(content)
        if title:
            title = self._process_rtl_text(title)
        
        return self.capture_print(
            self.style_mgr.format_box(content, title, width)
        )
    
    def divider(self, style: str = "partial") -> str:
        """
        Display a divider line.
        
        Args:
            style: The divider style (full, partial, dotted)
            
        Returns:
            str: The formatted divider
        """
        return self.capture_print(
            self.style_mgr.create_divider(style)
        )
        
    def table(self, headers: List[str], rows: List[List[Any]], 
            title: Optional[str] = None) -> str:
        """
        Display data in a formatted table.
        
        Args:
            headers: List of column headers
            rows: List of row data (list of lists)
            title: Optional table title
            
        Returns:
            str: The formatted table
        """
        # Process RTL text
        if self.rtl_support:
            headers = [self._process_rtl_text(h) for h in headers]
            rows = [[self._process_rtl_text(str(cell)) for cell in row] for row in rows]
            if title:
                title = self._process_rtl_text(title)
        
        return self.capture_print(
            self.style_mgr.format_table(headers, rows, title)
        )
    
    def list_items(self, items: List[str], 
                   bullet_type: str = "symbol",
                   title: Optional[str] = None) -> str:
        """
        Display a formatted list of items.
        
        Args:
            items: List of items to display
            bullet_type: Type of bullet to use (symbol, number, letter)
            title: Optional list title
            
        Returns:
            str: The formatted list
        """
        # Process RTL text
        if self.rtl_support:
            items = [self._process_rtl_text(item) for item in items]
            if title:
                title = self._process_rtl_text(title)
        
        return self.capture_print(
            self.style_mgr.format_list(items, bullet_type, title)
        )
    
    def reset(self) -> None:
        """Reset the output handler state."""
        self.thinking_shown = False
        self.command_shown = False
        self.result_shown = False
        self.capture_mode = False
        self.captured_output = []
    
    def set_theme(self, theme: str) -> bool:
        """
        Set the output theme.
        
        Args:
            theme: Name of the theme to use
            
        Returns:
            bool: True if theme was set successfully
        """
        return self.style_mgr.set_theme(theme)
    
    def set_verbose(self, verbose: bool) -> None:
        """
        Set verbose mode.
        
        Args:
            verbose: Whether to enable verbose mode
        """
        self.verbose_mode = verbose
    
    def set_debug(self, debug: bool) -> None:
        """
        Set debug mode.
        
        Args:
            debug: Whether to enable debug mode
        """
        self.debug_mode = debug
    
    def filter_duplicate_outputs(self, output: str) -> str:
        """
        Filter out duplicate outputs.
        
        Args:
            output: The output to filter
            
        Returns:
            str: The filtered output
        """
        # Process RTL text
        output = self._process_rtl_text(output)
        
        # Remove duplicate lines
        lines = output.split('\n')
        unique_lines = []
        seen = set()
        
        for line in lines:
            if line not in seen:
                seen.add(line)
                unique_lines.append(line)
        
        return '\n'.join(unique_lines)
    
    def set_verbosity(self, level: str) -> None:
        """
        Set the verbosity level.
        
        Args:
            level: Verbosity level (minimal, normal, verbose, debug)
        """
        level = level.lower()
        if level == "minimal":
            self.verbose_mode = False
            self.debug_mode = False
        elif level == "normal":
            self.verbose_mode = False
            self.debug_mode = False
        elif level == "verbose":
            self.verbose_mode = True
            self.debug_mode = False
        elif level == "debug":
            self.verbose_mode = True
            self.debug_mode = True
        else:
            # Default to normal if invalid
            self.verbose_mode = False
            self.debug_mode = False
        
        self.verbosity = level
    
    def info(self, message: str) -> None:
        """Display an info message."""
        self.status(message, "info")
    
    def success(self, message: str) -> None:
        """Display a success message."""
        self.status(message, "success")
    
    def error(self, message: str) -> None:
        """Display an error message."""
        self.status(message, "error")
    
    def warning(self, message: str) -> None:
        """Display a warning message."""
        self.status(message, "warning")


# Create a singleton instance
output_handler = OutputHandler()


# Example usage when run directly
if __name__ == "__main__":
    # Test the output handler
    print("\nTesting OutputHandler:\n")
    
    # Reset for a clean state
    output_handler.reset()
    
    # Start a sample sequence
    output_handler.thinking("I need to check the system uptime...")
    output_handler.command("uptime")
    output_handler.result(True, "System has been up for 3 days, 4 hours")
    
    # Try to show thinking again (should be ignored)
    output_handler.thinking("Let me think more about this...")
    
    # Show an explanation
    output_handler.explanation("The system has been running well for several days.")
    
    # Test other formatting functions
    output_handler.header("System Information", "computer")
    output_handler.status("All services running", "success")
    output_handler.status("Memory usage: 85%", "warning")
    output_handler.box("CPU: 45%\nMemory: 3.2GB/8GB", "Resource Usage")
    
    # Reset and try with a different theme
    output_handler.reset()
    output_handler.set_theme("minimal")
    output_handler.thinking("Checking available disk space...")
    output_handler.command("df -h")
    output_handler.result(True, "Storage information retrieved")
