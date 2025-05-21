#!/usr/bin/env python3
"""
OutputHandler for UaiBot

A unified facade for output operations that enforces the output flow and
prevents duplicate outputs. Acts as the central component of the output system.

Output Philosophy & Flow:
- Show 'thinking' only if no direct command is found or user asks for explanation.
- Always show the command to be executed (in a clear line/box).
- Always show the result of the command (in a result box/section).
- Only show AI explanation if user asks for it or no direct command is possible.
- Never show duplicate outputs of any type.
"""

import sys
import re
import os
from datetime import datetime
from typing import List, Dict, Any, Optional, Union, Tuple

# Import the style manager
from uaibot.utils.output_style_manager import OutputStyleManager
from uaibot.core.logging_config import get_logger

logger = get_logger(__name__)

class OutputHandler:
    """
    The central facade for all UaiBot output operations.
    
    This class:
    1. Enforces the output flow (thinking → command → result)
    2. Prevents duplicate outputs
    3. Provides consistent styling using OutputStyleManager
    4. Supports output capture for testing and redirection
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
        self.style_mgr = OutputStyleManager(theme=theme)
        
        # Special display flags
        self.verbose_mode = False  # When True, shows more details
        self.debug_mode = False    # When True, shows debugging information
        self.verbosity = 'normal'  # Default verbosity level
    
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
        
        # Format thinking box using style manager
        formatted_box = self.style_mgr.format_box(
            content=message, 
            title="Thinking"
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
        
        emoji = self.style_mgr.get_emoji("command", "📌")
        output = f"{emoji} Executing: {cmd}"
        
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
        # Get max width for each column
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(cell)))
        
        # Build the table
        result = []
        
        # Add title if provided
        if title:
            result.append(f"{title}")
            result.append("-" * len(title))
        
        # Format headers
        header_row = " | ".join(f"{h:{w}}" for h, w in zip(headers, col_widths))
        result.append(header_row)
        
        # Add separator
        separator = "-+-".join("-" * w for w in col_widths)
        result.append(separator)
        
        # Add data rows
        for row in rows:
            row_str = " | ".join(f"{str(c):{w}}" for c, w in zip(row, col_widths))
            result.append(row_str)
        
        return self.capture_print("\n".join(result))
    
    def list_items(self, items: List[str], 
                 bullet_type: str = "symbol",
                 title: Optional[str] = None) -> str:
        """
        Display a formatted list of items.
        
        Args:
            items: List of items to display
            bullet_type: Type of bullet (symbol, number, letter)
            title: Optional list title
            
        Returns:
            str: The formatted list
        """
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
        
        return self.capture_print("\n".join(result))
    
    def reset(self) -> None:
        """Reset output handler state for new command sequence."""
        self.thinking_shown = False
        self.command_shown = False
        self.result_shown = False
        self.captured_output = []
    
    def set_theme(self, theme: str) -> bool:
        """
        Change the current styling theme.
        
        Args:
            theme: The theme name to use
            
        Returns:
            bool: True if theme was changed, False if invalid
        """
        return self.style_mgr.set_theme(theme)
    
    def set_verbose(self, verbose: bool) -> None:
        """
        Set verbose mode.
        
        Args:
            verbose: When True, shows more details in output
        """
        self.verbose_mode = verbose
    
    def set_debug(self, debug: bool) -> None:
        """
        Set debug mode.
        
        Args:
            debug: When True, shows all output regardless of state
        """
        self.debug_mode = debug
    
    def filter_duplicate_outputs(self, output: str) -> str:
        """
        Filter out duplicate outputs from text.
        
        Args:
            output: The text to filter
            
        Returns:
            str: Text with duplicates removed
        """
        # Remove duplicate thinking blocks
        thinking_pattern = r"(🤔.*?Thinking[\s\S]*?(?:\n\n|\Z))"
        thinking_matches = re.findall(thinking_pattern, output)
        if thinking_matches and len(thinking_matches) > 1:
            for match in thinking_matches[1:]:
                output = output.replace(match, "")
        
        # Remove duplicate command blocks
        command_pattern = r"(📌 Executing:.*?)(?=\n\n|\Z)"
        command_matches = re.findall(command_pattern, output)
        if command_matches and len(command_matches) > 1:
            for match in command_matches[1:]:
                output = output.replace(match, "")
        
        # Remove duplicate result blocks (success/error)
        result_pattern = r"((✅|❌|ℹ️) .*?)(?=\n\n|\Z)"
        result_matches = re.findall(result_pattern, output)
        if result_matches and len(result_matches) > 1:
            for match, _ in result_matches[1:]:
                output = output.replace(match, "")
        
        # Remove duplicate log lines that might be captured
        log_pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} - .*? - INFO - .*?\n"
        output = re.sub(log_pattern, "", output)
        
        return output.strip()
    
    def set_verbosity(self, level: str) -> None:
        """
        Set the verbosity level for output.
        
        Args:
            level: Verbosity level ('quiet', 'normal', 'verbose')
        """
        if level not in ['quiet', 'normal', 'verbose']:
            logger.warning(f"Invalid verbosity level: {level}. Using 'normal' instead.")
            level = 'normal'
        self.verbosity = level
    
    def info(self, message: str) -> None:
        """Display an informational message."""
        if self.verbosity != 'quiet':
            print(f"ℹ️  {message}")
    
    def success(self, message: str) -> None:
        """Display a success message."""
        if self.verbosity != 'quiet':
            print(f"✅ {message}")
    
    def error(self, message: str) -> None:
        """Display an error message."""
        print(f"❌ {message}")
    
    def warning(self, message: str) -> None:
        """Display a warning message."""
        if self.verbosity != 'quiet':
            print(f"⚠️  {message}")


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
