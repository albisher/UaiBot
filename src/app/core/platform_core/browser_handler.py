"""Browser interaction and automation handler for the Labeeb platform.

This module provides functionality for:
- Browser automation and control
- Web page interaction and navigation
- Form filling and data extraction
- Browser state management
- Cross-platform browser compatibility
- RTL language support (Arabic.)

The module implements platform-specific browser handling while maintaining
a consistent interface across different operating systems.
"""

import os
import platform
import subprocess
import json
import tempfile
import time
import re
import pyautogui
from typing import Dict, Any, List, Optional
from ...utils import run_command
import arabic_reshaper
from bidi.algorithm import get_display

class BaseBrowserHandler:
    """Base class for platform-specific browser handlers."""
    
    def __init__(self, shell_handler=None):
        """Initialize the browser handler.
        
        Args:
            shell_handler: Optional shell handler instance for executing commands
        """
        self.shell_handler = shell_handler
        self.system = platform.system().lower()
        self._rtl_support = False
        self._text_direction = 'ltr'
    
    def initialize(self) -> bool:
        """Initialize the browser handler.
        
        Returns:
            bool: True if initialization was successful, False otherwise.
        """
        try:
            self._initialize_rtl_support()
            return True
        except Exception as e:
            print(f"Failed to initialize browser handler: {e}")
            return False
    
    def _initialize_rtl_support(self) -> None:
        """Initialize RTL language support.
        
        This method should be overridden by platform-specific implementations
        to properly initialize RTL support based on system settings.
        """
        self._rtl_support = False
        self._text_direction = 'ltr'
    
    def _process_rtl_text(self, text: str) -> str:
        """Process text for RTL display if RTL support is enabled.
        
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
    
    def get_content(self, browser_name: Optional[str] = None) -> str:
        """Get content from browser tabs (titles and URLs).
        
        Args:
            browser_name: Specific browser to target ("chrome", "firefox", "safari", "edge")
            
        Returns:
            Formatted browser content or error message
        """
        raise NotImplementedError("Platform-specific implementation required")
        
    def perform_search(self, url: str, query: str, wait_time: float = 2.0) -> str:
        """Open the default browser, navigate to a URL, and perform a search.
        
        Args:
            url: The URL to open (e.g., 'https://www.google.com')
            query: The search query to type
            wait_time: Seconds to wait for the browser to load
            
        Returns:
            Status message
        """
        try:
            # Process RTL text if needed
            if self._rtl_support:
                url = self._process_rtl_text(url)
                query = self._process_rtl_text(query)
            
            # Open the browser to the URL
            import webbrowser
            webbrowser.open(url)
            time.sleep(wait_time)
            
            # Try to find the search bar visually
            pyautogui.hotkey('ctrl', 'l')  # Focus address bar
            time.sleep(0.2)
            pyautogui.typewrite(url)
            pyautogui.press('enter')
            time.sleep(wait_time)
            
            # For Google, the search bar is focused by default, so type the query
            pyautogui.typewrite(query)
            pyautogui.press('enter')
            return f"Opened {url} and searched for '{query}'."
        except Exception as e:
            return f"Error performing browser search: {str(e)}"
            
    def execute_actions(self, browser: str, url: str, actions: List[Dict[str, Any]]) -> str:
        """Execute a series of browser automation actions.
        
        Args:
            browser: Browser to use
            url: URL to navigate to
            actions: List of actions to perform
            
        Returns:
            Status message
        """
        raise NotImplementedError("Platform-specific implementation required")
    
    def get_text_direction(self) -> str:
        """Get the current text direction.
        
        Returns:
            str: Text direction ('ltr' or 'rtl').
        """
        return self._text_direction
    
    def set_text_direction(self, direction: str) -> bool:
        """Set the text direction.
        
        Args:
            direction: Text direction ('ltr' or 'rtl').
            
        Returns:
            bool: True if direction was set successfully, False otherwise.
        """
        if direction not in ('ltr', 'rtl'):
            return False
        
        self._text_direction = direction
        return True 