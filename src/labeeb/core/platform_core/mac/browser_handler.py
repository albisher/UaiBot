"""
Browser handler for macOS platform.

This module provides functionality for interacting with web browsers on macOS.
"""
import os
import sys
import logging
from typing import Dict, Any, Optional, List
from ..common.base_handler import BaseHandler
from labeeb.core.utils import run_command
import time
import arabic_reshaper
from bidi.algorithm import get_display

logger = logging.getLogger(__name__)

class MacBrowserHandler(BaseHandler):
    """Handler for browser interactions on macOS."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the browser handler.
        
        Args:
            config: Configuration dictionary
        """
        super().__init__(config)
        self._initialized = False
        self._supported_browsers = {
            'safari': 'Safari',
            'chrome': 'Google Chrome',
            'firefox': 'Firefox',
            'edge': 'Microsoft Edge'
        }
        self._rtl_support = False
        self._text_direction = 'ltr'
    
    def initialize(self) -> bool:
        """Initialize the browser handler.
        
        Returns:
            bool: True if initialization was successful
        """
        if self._initialized:
            return True
            
        try:
            # Check for supported browsers
            self._available_browsers = self._get_available_browsers()
            self._initialized = True
            return True
        except Exception as e:
            logger.error(f"Failed to initialize MacBrowserHandler: {e}")
            return False
    
    def cleanup(self) -> None:
        """Clean up browser handler resources."""
        self._initialized = False
    
    def _get_available_browsers(self) -> List[str]:
        """Get list of available browsers.
        
        Returns:
            List[str]: List of available browser names
        """
        available = []
        for browser_id, browser_name in self._supported_browsers.items():
            if self._is_browser_installed(browser_id):
                available.append(browser_id)
        return available
    
    def _is_browser_installed(self, browser_id: str) -> bool:
        """Check if a browser is installed.
        
        Args:
            browser_id: Browser identifier
            
        Returns:
            bool: True if browser is installed
        """
        browser_name = self._supported_browsers.get(browser_id)
        if not browser_name:
            return False
            
        # Check if browser is installed in Applications
        app_path = f"/Applications/{browser_name}.app"
        return os.path.exists(app_path)
    
    def open_url(self, url: str, browser_id: Optional[str] = None) -> bool:
        """Open a URL in the specified browser.
        
        Args:
            url: URL to open
            browser_id: Optional browser identifier
            
        Returns:
            bool: True if URL was opened successfully
        """
        if not self._initialized:
            return False
            
        try:
            if browser_id and browser_id in self._available_browsers:
                browser_name = self._supported_browsers[browser_id]
                cmd = f'open -a "{browser_name}" "{url}"'
            else:
                cmd = f'open "{url}"'
                
            result = run_command(cmd)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Failed to open URL: {e}")
            return False
    
    def get_available_browsers(self) -> List[str]:
        """Get list of available browsers.
        
        Returns:
            List[str]: List of available browser identifiers
        """
        return self._available_browsers.copy()
    
    def is_browser_available(self, browser_id: str) -> bool:
        """Check if a browser is available.
        
        Args:
            browser_id: Browser identifier
            
        Returns:
            bool: True if browser is available
        """
        return browser_id in self._available_browsers
    
    def _initialize_rtl_support(self) -> None:
        """Initialize RTL language support."""
        try:
            from ..platform_manager import platform_manager
            self._rtl_support = platform_manager.rtl_support
            self._text_direction = 'rtl' if self._rtl_support else 'ltr'
        except Exception as e:
            print(f"Failed to initialize RTL support: {e}")
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
        """Get content from browser tabs on macOS using AppleScript.
        
        Args:
            browser_name: Specific browser to target ("chrome", "firefox", "safari", "edge")
            
        Returns:
            Formatted browser content or error message
        """
        try:
            if browser_name:
                browser_name = browser_name.lower()
            
            if not browser_name or browser_name == "safari":
                # Try Safari first if no specific browser requested or Safari explicitly requested
                safari_script = """
                tell application "Safari"
                    set windowList to every window
                    set tabData to ""
                    repeat with w in windowList
                        set tabList to every tab of w
                        repeat with t in tabList
                            set tabData to tabData & "• " & (name of t) & " - " & (URL of t) & "\n"
                        end repeat
                    end repeat
                    return tabData
                end tell
                """
                result = run_command(['osascript', '-e', safari_script], capture_output=True, text=True)
                if result['success'] and result['stdout'].strip():
                    content = "Open tabs in Safari:\n\n" + result['stdout']
                    return self._process_rtl_text(content)
            
            if not browser_name or browser_name in ["chrome", "google chrome"]:
                # Try Chrome if no specific browser requested or Chrome explicitly requested
                chrome_script = """
                tell application "Google Chrome"
                    set windowList to every window
                    set tabData to ""
                    repeat with w in windowList
                        set tabList to every tab of w
                        repeat with t in tabList
                            set tabData to tabData & "• " & (title of t) & " - " & (URL of t) & "\n"
                        end repeat
                    end repeat
                    return tabData
                end tell
                """
                result = run_command(['osascript', '-e', chrome_script], capture_output=True, text=True)
                if result['success'] and result['stdout'].strip():
                    content = "Open tabs in Google Chrome:\n\n" + result['stdout']
                    return self._process_rtl_text(content)
            
            if not browser_name or browser_name in ["firefox", "mozilla firefox"]:
                # Try Firefox if no specific browser requested or Firefox explicitly requested
                firefox_script = """
                tell application "Firefox"
                    activate
                    delay 0.5
                    set tabData to ""
                    
                    -- Create temporary JavaScript file
                    set tempFile to (path to temporary items as string) & "firefox_tabs.txt"
                    do shell script "touch " & quoted form of POSIX path of tempFile
                    
                    -- Execute JavaScript to get tabs
                    tell application "System Events"
                        keystroke "j" using {command down, option down, shift down}
                        delay 0.5
                        keystroke "var tabs = ''; for (let win of Services.wm.getEnumerator('navigator:browser')) { for (let browser of win.gBrowser.browsers) { tabs += '• ' + browser.contentTitle + ' - ' + browser.currentURI.spec + '\\n'; } } require('resource://devtools/shared/DevToolsUtils.js').dumpn(tabs); undefined;"
                        keystroke return
                        delay 0.5
                        keystroke "w" using {command down, option down, shift down}
                    end tell
                    
                    -- Read from Browser Console output
                    delay 1
                    set tabData to do shell script "cat /tmp/firefox-browser-console.log | tail -n 20 | grep -v '\\[\\|JavaScript'  | grep -v '};'" as string
                    
                    return tabData
                end tell
                """
                result = run_command(['osascript', '-e', firefox_script], capture_output=True, text=True)
                if result['success'] and result['stdout'].strip():
                    content = "Open tabs in Firefox:\n\n" + result['stdout']
                    return self._process_rtl_text(content)
            
            # Return error if no browser found or specified browser not found
            if browser_name:
                return f"Could not access {browser_name.title()}. Make sure it's running and you've granted necessary permissions."
            else:
                return "No supported browser (Safari, Chrome, Firefox) appears to be running."
                
        except Exception as e:
            return f"Error reading browser content: {str(e)}"
            
    def execute_actions(self, browser: str, url: str, actions: List[Dict[str, Any]]) -> str:
        """Execute a series of browser automation actions on macOS.
        
        Args:
            browser: Browser to use
            url: URL to navigate to
            actions: List of actions to perform
            
        Returns:
            Status message
        """
        try:
            # Process URL for RTL if needed
            if self._rtl_support:
                url = self._process_rtl_text(url)
            
            # Open the browser
            if browser.lower() in ["chrome", "google chrome"]:
                script = f'tell application "Google Chrome" to open location "{url}"'
            elif browser.lower() == "safari":
                script = f'tell application "Safari" to open location "{url}"'
            elif browser.lower() in ["firefox", "mozilla firefox"]:
                script = f'tell application "Firefox" to open location "{url}"'
            else:
                return f"Unsupported browser: {browser}"
                
            result = run_command(['osascript', '-e', script], capture_output=True, text=True)
            if not result['success']:
                return f"Failed to open {browser}: {result['stderr']}"
                
            # Wait for browser to load
            time.sleep(2)
            
            # Execute each action
            for action in actions:
                action_type = action.get('type')
                if action_type == 'click':
                    x, y = action.get('x'), action.get('y')
                    if x is not None and y is not None:
                        import pyautogui
                        pyautogui.click(x, y)
                elif action_type == 'type':
                    text = action.get('text', '')
                    if text:
                        # Process RTL text if needed
                        if self._rtl_support:
                            text = self._process_rtl_text(text)
                        import pyautogui
                        pyautogui.typewrite(text)
                elif action_type == 'key':
                    key = action.get('key')
                    if key:
                        import pyautogui
                        pyautogui.press(key)
                        
            return f"Successfully executed {len(actions)} actions in {browser}"
            
        except Exception as e:
            return f"Error executing browser actions: {str(e)}"
    
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