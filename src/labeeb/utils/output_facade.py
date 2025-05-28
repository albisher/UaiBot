#!/usr/bin/env python3
"""
Output Facade for Labeeb

A singleton implementation of the Facade pattern for all output operations
that unifies and standardizes the app's output handling system.

Output Philosophy & Flow:
- Show 'thinking' only if no direct command is found or user asks for explanation.
- Always show the command to be executed (in a clear line/box).
- Always show the result of the command (in a result box/section).
- Only show AI explanation if user asks for it or no direct command is possible.
- Never show duplicate outputs of any type.
- Support RTL languages (Arabic, Hebrew, etc.) with proper text reshaping and display.
"""

import sys
import os
from typing import Optional, Any, Dict, Union, List
from src.app.logging_config import get_logger
from pathlib import Path
import arabic_reshaper
from bidi.algorithm import get_display

# Import the OutputHandler as our implementation class
from src.app.utils.output_handler import OutputHandler

logger = get_logger(__name__)

class OutputFacade:
    """Facade for handling different types of output in the application.
    
    This class provides a unified interface for displaying various types of output
    including commands, results, explanations, and status messages. It supports
    different output handlers and formats while maintaining a consistent interface.
    It also supports RTL languages with proper text reshaping and display.
    
    Attributes:
        _handler: The current output handler instance
        _formatter: The output formatter instance
        _rtl_support: Whether RTL language support is enabled
    """
    
    # Singleton instance
    _instance = None
    
    @classmethod
    def get_instance(cls, theme: str = "default", verbosity: str = "normal"):
        """Get or create the singleton instance."""
        if cls._instance is None:
            cls._instance = cls(theme, verbosity)
        return cls._instance
    
    def __init__(self, theme: str = "default", verbosity: str = "normal"):
        """
        Initialize the output facade.
        
        Args:
            theme: The theme to use for styling
            verbosity: Output verbosity level (minimal, normal, verbose, debug)
        """
        if OutputFacade._instance is not None:
            raise RuntimeError("Use OutputFacade.get_instance() to get the singleton instance")
            
        # Create the actual handler that will implement our output operations
        self._handler = OutputHandler(theme=theme)
        
        # Set verbosity level
        self._set_verbosity(verbosity)
        
        # Track sequence ID for grouping related outputs
        self._sequence_id = 0
        
        # RTL support
        self._rtl_support = False
    
    def set_rtl_support(self, enabled: bool) -> None:
        """
        Enable or disable RTL language support.
        
        Args:
            enabled: Whether to enable RTL support
        """
        self._rtl_support = enabled
    
    def _process_rtl_text(self, text: str) -> str:
        """
        Process text for RTL display if RTL support is enabled.
        
        Args:
            text: The text to process
            
        Returns:
            str: The processed text
        """
        if not self._rtl_support:
            return text
            
        # Check if text contains Arabic characters
        if any('\u0600' <= c <= '\u06FF' for c in text):
            text = arabic_reshaper.reshape(text)
            text = get_display(text)
        return text
    
    def _set_verbosity(self, verbosity: str) -> None:
        """
        Set the verbosity level.
        
        Args:
            verbosity: Output verbosity level (minimal, normal, verbose, debug)
        """
        # Convert verbosity string to appropriate flags
        verbosity = verbosity.lower()
        
        if verbosity == "minimal":
            self._handler.verbose_mode = False
            self._handler.debug_mode = False
        elif verbosity == "normal":  # Default
            self._handler.verbose_mode = False
            self._handler.debug_mode = False
        elif verbosity == "verbose":
            self._handler.verbose_mode = True
            self._handler.debug_mode = False
        elif verbosity == "debug":
            self._handler.verbose_mode = True
            self._handler.debug_mode = True
        else:
            # Default to normal if invalid
            self._handler.verbose_mode = False
            self._handler.debug_mode = False
    
    def set_theme(self, theme: str) -> None:
        """
        Change the output theme.
        
        Args:
            theme: Name of the theme to use
        """
        self._handler.style_mgr.set_theme(theme)
    
    def new_sequence(self) -> None:
        """
        Start a new output sequence, resetting state for thinking/command/result tracking.
        Use this when starting a completely new user interaction.
        """
        self._sequence_id += 1
        self._handler.thinking_shown = False
        self._handler.command_shown = False
        self._handler.result_shown = False
    
    # -- Main output flow methods --
    
    def thinking(self, message: str) -> Optional[str]:
        """
        Display thinking message.
        
        Args:
            message: The thinking content to display
            
        Returns:
            str or None: The formatted output if shown, None if skipped
        """
        message = self._process_rtl_text(message)
        return self._handler.thinking(message)
    
    def command(self, cmd: str) -> Optional[str]:
        """
        Display command to be executed.
        
        Args:
            cmd: The command string to display
            
        Returns:
            str or None: The formatted output if shown, None if skipped
        """
        cmd = self._process_rtl_text(cmd)
        return self._handler.command(cmd)
        
    def result(self, success: bool, message: str) -> Optional[str]:
        """
        Display result message.
        
        Args:
            success: Whether the operation was successful
            message: The result message to display
            
        Returns:
            str or None: The formatted output if shown, None if skipped
        """
        message = self._process_rtl_text(message)
        return self._handler.result(success, message)
    
    def explanation(self, message: str) -> str:
        """
        Display explanation text.
        
        Args:
            message: The explanation to display
            
        Returns:
            str: The formatted output
        """
        message = self._process_rtl_text(message)
        return self._handler.explanation(message)
    
    # -- Helper output methods --
    
    def status(self, message: str, status_key: str = "info") -> str:
        """
        Display a status message with appropriate indicator.
        
        Args:
            message: The status message
            status_key: Key for the status type (success, warning, error, info)
            
        Returns:
            str: The formatted output
        """
        message = self._process_rtl_text(message)
        return self._handler.status(message, status_key)
    
    def warning(self, message: str) -> str:
        """
        Display a warning message.
        
        Args:
            message: The warning message to display
            
        Returns:
            str: The formatted warning output
        """
        message = self._process_rtl_text(message)
        return self._handler.status(message, "warning")
    
    def error(self, message: str) -> str:
        """
        Display an error message.
        
        Args:
            message: The error message to display
            
        Returns:
            str: The formatted error output
        """
        message = self._process_rtl_text(message)
        return self._handler.status(message, "error")
    
    def success(self, message: str) -> str:
        """
        Display a success message.
        
        Args:
            message: The success message to display
            
        Returns:
            str: The formatted success output
        """
        message = self._process_rtl_text(message)
        return self._handler.status(message, "success")
    
    def info(self, message: str) -> str:
        """Display an info message."""
        message = self._process_rtl_text(message)
        return self._handler.status(message, "info")
    
    # -- Formatting methods --
    
    def header(self, text: str, emoji_key: Optional[str] = None) -> str:
        """Display a section header."""
        text = self._process_rtl_text(text)
        return self._handler.header(text, emoji_key)
    
    def divider(self, style: str = "partial") -> str:
        """Display a divider line."""
        return self._handler.divider(style)
    
    def box(self, content: str, title: Optional[str] = None, 
            width: Optional[int] = None) -> str:
        """Display content in a formatted box."""
        content = self._process_rtl_text(content)
        if title:
            title = self._process_rtl_text(title)
        return self._handler.box(content, title, width)
    
    def table(self, headers: List[str], rows: List[List[Any]], 
              title: Optional[str] = None) -> str:
        """Display data in a formatted table."""
        if self._rtl_support:
            headers = [self._process_rtl_text(h) for h in headers]
            rows = [[self._process_rtl_text(str(cell)) for cell in row] for row in rows]
            if title:
                title = self._process_rtl_text(title)
        return self._handler.table(headers, rows, title)
    
    def list_items(self, items: List[str], 
                   bullet_type: str = "symbol",
                   title: Optional[str] = None) -> str:
        """Display a formatted list of items."""
        if self._rtl_support:
            items = [self._process_rtl_text(item) for item in items]
            if title:
                title = self._process_rtl_text(title)
        return self._handler.list_items(items, bullet_type, title)
    
    # -- Testing support --
    
    def start_capture(self) -> None:
        """Start capturing output for testing."""
        self._handler.start_capture()
    
    def stop_capture(self) -> str:
        """Stop capturing output and return captured text."""
        return self._handler.stop_capture()
    
    def set_verbosity(self, verbosity: str) -> None:
        """Set the verbosity level."""
        self._set_verbosity(verbosity)

# Create a global instance for easy access
output = OutputFacade.get_instance()

__all__ = ["OutputFacade", "output"]
