"""
Browser integration for UaiBot.
Provides functionality to interact with web browsers, get open tabs,
and browser content.

Copyright (c) 2025 UaiBot Team
License: Custom license - free for personal and educational use.
Commercial use requires a paid license. See LICENSE file for details.
"""

import os
import platform
import subprocess
import json
import tempfile
import time
import re

from core.utils import run_command

class BrowserHandler:
    """Handler for browser interactions."""
    
    def __init__(self, shell_handler=None):
        self.shell_handler = shell_handler
        self.system = platform.system().lower()
    
    def get_browser_content(self, browser_name=None):
        """
        Get content from browser tabs (titles and URLs).
        
        Args:
            browser_name (str, optional): Specific browser to target
                                         ("chrome", "firefox", "safari", "edge")
        
        Returns:
            str: Formatted browser content or error message
        """
        if browser_name:
            browser_name = browser_name.lower()
        
        if self.system == "darwin":  # macOS
            return self._get_browser_content_macos(browser_name)
        elif self.system == "linux":
            return self._get_browser_content_linux(browser_name)
        elif self.system == "windows":
            return self._get_browser_content_windows(browser_name)
        else:
            return "Unsupported operating system for browser content retrieval."
            
    def _get_browser_content_macos(self, browser_name=None):
        """Get browser content on macOS using AppleScript."""
        try:
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
                    return "Open tabs in Safari:\n\n" + result['stdout']
            
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
                    return "Open tabs in Google Chrome:\n\n" + result['stdout']
            
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
                    return "Open tabs in Firefox:\n\n" + result['stdout']
            
            # Return error if no browser found or specified browser not found
            if browser_name:
                return f"Could not access {browser_name.title()}. Make sure it's running and you've granted necessary permissions."
            else:
                return "No supported browser (Safari, Chrome, Firefox) appears to be running."
                
        except Exception as e:
            return f"Error reading browser content: {str(e)}"
            
    def _get_browser_content_linux(self, browser_name=None):
        """Get browser content on Linux."""
        # Implementation for Linux browsers would go here
        return "Browser content retrieval is not yet implemented for Linux."
        
    def _get_browser_content_windows(self, browser_name=None):
        """Get browser content on Windows."""
        # Implementation for Windows browsers would go here
        return "Browser content retrieval is not yet implemented for Windows."
