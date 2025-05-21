#!/usr/bin/env python3
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
import pyautogui

from uaibot.utils import run_command

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
                return "No supported browser (Safari, Firefox) appears to be running."
                
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

    def perform_search(self, url: str, query: str, wait_time: float = 2.0) -> str:
        """
        Open the default browser, navigate to a URL, and perform a search using PyAutoGUI.
        Args:
            url (str): The URL to open (e.g., 'https://www.duckduckgo.com')
            query (str): The search query to type
            wait_time (float): Seconds to wait for the browser to load
        Returns:
            str: Status message
        """
        import subprocess
        import time
        import webbrowser

        try:
            # Open the browser to the URL
            webbrowser.open(url)
            time.sleep(wait_time)

            # Try to find the search bar visually (optional: can be improved)
            # For now, just focus the window and type
            pyautogui.hotkey('ctrl', 'l')  # Focus address bar
            time.sleep(0.2)
            pyautogui.typewrite(url)
            pyautogui.press('enter')
            time.sleep(wait_time)

            # For DuckDuckGo, the search bar is focused by default, so type the query
            pyautogui.typewrite(query)
            pyautogui.press('enter')
            return f"Opened {url} and searched for '{query}'."
        except Exception as e:
            return f"Error performing browser search: {str(e)}"

class BrowserAutomationHandler:
    """Executes browser automation actions based on AI-provided JSON."""
    def __init__(self):
        import pyautogui
        self.pyautogui = pyautogui
        self.default_wait = 2
        self.available_browsers = ["firefox", "safari", "edge"]
        self.current_browser_index = 0
        self.last_opened_browser = None
        self.last_window_details = None

    def open_browser(self, browser: str, url: str):
        import webbrowser
        import subprocess
        print(f"[BrowserAutomationHandler] Attempting to open browser: {browser} with URL: {url}")
        
        # If no specific browser is requested, try browsers in order
        if not browser:
            browser = self.available_browsers[self.current_browser_index]
            self.current_browser_index = (self.current_browser_index + 1) % len(self.available_browsers)
        
        try:
            browser = browser.lower()
            if browser in ["firefox", "mozilla firefox"]:
                print("[BrowserAutomationHandler] Using firefox")
                try:
                    webbrowser.get("firefox").open(url)
                except webbrowser.Error:
                    print("[BrowserAutomationHandler] firefox not registered, trying next browser")
                    return self.open_browser(None, url)  # Try next browser
            elif browser in ["safari"]:
                print("[BrowserAutomationHandler] Using safari")
                try:
                    webbrowser.get("safari").open(url)
                except webbrowser.Error:
                    print("[BrowserAutomationHandler] safari not registered, trying next browser")
                    return self.open_browser(None, url)  # Try next browser
            elif browser in ["edge", "microsoft edge"]:
                print("[BrowserAutomationHandler] Using microsoft-edge")
                try:
                    webbrowser.get("microsoft-edge").open(url)
                except webbrowser.Error:
                    print("[BrowserAutomationHandler] microsoft-edge not registered, trying next browser")
                    return self.open_browser(None, url)  # Try next browser
            elif browser in ["chrome", "google chrome"]:
                print("[BrowserAutomationHandler] Using chrome")
                import sys
                if sys.platform == "darwin":
                    try:
                        subprocess.run(['open', '-a', 'Google Chrome', url], check=True)
                    except Exception as e:
                        print(f"[BrowserAutomationHandler] Failed to open Chrome with subprocess: {e}. Falling back to default webbrowser.open.")
                        webbrowser.open(url)
                else:
                    try:
                        webbrowser.get("chrome").open(url)
                    except webbrowser.Error:
                        print("[BrowserAutomationHandler] chrome not registered, falling back to default webbrowser.open")
                        webbrowser.open(url)
            else:
                print("[BrowserAutomationHandler] Using default webbrowser.open")
                webbrowser.open(url)
            self.last_opened_browser = browser
            # TODO: Persist last_window_details to disk after opening a browser, and load it on initialization, so that sequential commands in separate processes can share window state.
            # Capture the window details of the newly opened browser window
            import time
            time.sleep(1)  # Wait for the window to open
            try:
                if sys.platform == "darwin":
                    import subprocess
                    script = """
                    tell application \"System Events\"
                        set frontApp to first application process whose frontmost is true
                        set frontAppName to name of frontApp
                        set frontWindow to first window of frontApp
                        set windowTitle to name of frontWindow
                        set windowPosition to position of frontWindow
                        set windowSize to size of frontWindow
                        return frontAppName & "," & windowTitle & "," & windowPosition & "," & windowSize
                    end tell
                    """
                    result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
                    if result.returncode == 0:
                        raw = result.stdout.strip()
                        details = raw.split(',')
                        try:
                            if len(details) >= 6:
                                app_name = details[0]
                                title = details[1]
                                left = int(details[2])
                                top = int(details[3])
                                width = int(details[4])
                                height = int(details[5])
                                self.last_window_details = {
                                    "title": title,
                                    "left": left,
                                    "top": top,
                                    "width": width,
                                    "height": height
                                }
                                print(f"[BrowserAutomationHandler] Captured window details: {self.last_window_details}")
                            else:
                                print(f"[BrowserAutomationHandler] AppleScript output incomplete: '{raw}', window details not captured.")
                        except Exception as e:
                            print(f"[BrowserAutomationHandler] Error parsing AppleScript output: '{raw}', error: {e}")
                    else:
                        print(f"[BrowserAutomationHandler] AppleScript failed with return code {result.returncode}.")
                else:
                    # For non-macOS platforms, use PyAutoGUI if available
                    try:
                        window = self.pyautogui.getActiveWindow()
                        if window:
                            self.last_window_details = {
                                "title": window.title,
                                "left": window.left,
                                "top": window.top,
                                "width": window.width,
                                "height": window.height
                            }
                            print(f"[BrowserAutomationHandler] Captured window details: {self.last_window_details}")
                    except Exception as e:
                        print(f"[BrowserAutomationHandler] Failed to capture window details with PyAutoGUI: {e}")
            except Exception as e:
                print(f"[BrowserAutomationHandler] Failed to capture window details: {e}")
        except Exception as e:
            print(f"[BrowserAutomationHandler] Exception occurred: {e}. Trying next browser.")
            return self.open_browser(None, url)  # Try next browser

    def execute_actions(self, browser: str, url: str, actions: list):
        import time
        print(f"[BrowserAutomationHandler] execute_actions called with browser={browser}, url={url}, actions={actions}")
        
        # Try to execute actions with the specified browser
        try:
            self.open_browser(browser, url)
            print(f"[BrowserAutomationHandler] Waiting {self.default_wait} seconds for browser to open...")
            time.sleep(self.default_wait)
            
            for action in actions:
                atype = action.get("type")
                print(f"[BrowserAutomationHandler] Performing action: {action}")
                if atype == "wait":
                    print(f"[BrowserAutomationHandler] Waiting {action.get('seconds', 1)} seconds")
                    time.sleep(action.get("seconds", 1))
                elif atype == "click":
                    if "x" in action and "y" in action:
                        print(f"[BrowserAutomationHandler] Moving to ({action['x']}, {action['y']}) and clicking")
                        self.pyautogui.moveTo(action["x"], action["y"], duration=0.2)
                        self.pyautogui.click()
                    elif "target" in action:
                        img = action["target"]
                        print(f"[BrowserAutomationHandler] Looking for image target: {img}")
                        if img.endswith(".png") and os.path.exists(img):
                            loc = self.pyautogui.locateOnScreen(img, confidence=0.8)
                            if loc:
                                center = self.pyautogui.center(loc)
                                self.pyautogui.moveTo(center.x, center.y, duration=0.2)
                                self.pyautogui.click()
                    else:
                        w, h = self.pyautogui.size()
                        print(f"[BrowserAutomationHandler] Clicking center of screen at ({w//2}, {h//2})")
                        self.pyautogui.moveTo(w//2, h//2, duration=0.2)
                        self.pyautogui.click()
                elif atype == "type":
                    print(f"[BrowserAutomationHandler] Typing text: {action.get('text', '')}")
                    self.pyautogui.write(action.get("text", ""), interval=0.08)
                elif atype == "press":
                    print(f"[BrowserAutomationHandler] Pressing key: {action.get('key', 'enter')}")
                    self.pyautogui.press(action.get("key", "enter"))
                elif atype == "hotkey":
                    keys = action.get("keys", [])
                    print(f"[BrowserAutomationHandler] Pressing hotkey: {keys}")
                    if keys:
                        self.pyautogui.hotkey(*keys)
                elif atype == "screenshot":
                    fname = action.get("filename", "screenshot.png")
                    print(f"[BrowserAutomationHandler] Taking screenshot and saving to {fname}")
                    self.pyautogui.screenshot(fname)
                elif atype == "type_in_address_bar":
                    text = action.get("text")
                    if text:
                        # Check if we have last_window_details and activate the window
                        if self.last_window_details:
                            window = self.last_window_details
                            self.pyautogui.moveTo(window["left"] + window["width"] // 2, window["top"] + 10)
                            self.pyautogui.click()
                            time.sleep(0.2)
                        else:
                            # Fallback: move to top center of main screen
                            screen_w, screen_h = self.pyautogui.size()
                            self.pyautogui.moveTo(screen_w // 2, 10)
                            self.pyautogui.click()
                            time.sleep(0.2)
                        pyautogui.hotkey('ctrl', 'l')  # Focus address bar
                        time.sleep(0.2)
                        pyautogui.typewrite(text)
                        logger.debug(f"Typed in address bar: {text}")
                        return {"status": "success", "message": f"Typed {text} in address bar"}
                    else:
                        return {"status": "error", "message": "Missing text for type_in_address_bar operation"}
                elif atype == "type_in_search_bar":
                    text = action.get("text")
                    if text:
                        # Check if we have last_window_details and activate the window
                        if self.last_window_details:
                            window = self.last_window_details
                            self.pyautogui.moveTo(window["left"] + window["width"] // 2, window["top"] + 10)
                            self.pyautogui.click()
                            time.sleep(0.2)
                        else:
                            # Fallback: move to top center of main screen
                            screen_w, screen_h = self.pyautogui.size()
                            self.pyautogui.moveTo(screen_w // 2, 10)
                            self.pyautogui.click()
                            time.sleep(0.2)
                        pyautogui.hotkey('ctrl', 'l')  # Focus search bar
                        time.sleep(0.2)
                        pyautogui.typewrite(text)
                        logger.debug(f"Typed in search bar: {text}")
                        return {"status": "success", "message": f"Typed {text} in search bar"}
                    else:
                        return {"status": "error", "message": "Missing text for type_in_search_bar operation"}
            
            print("[BrowserAutomationHandler] All actions completed.")
            return "Browser automation actions completed."
            
        except Exception as e:
            print(f"[BrowserAutomationHandler] Error with current browser: {e}")
            if browser:  # If we were using a specific browser, try without specifying one
                print("[BrowserAutomationHandler] Trying with a different browser...")
                return self.execute_actions(None, url, actions)
            else:
                print("[BrowserAutomationHandler] All browsers failed.")
                return f"Error: All browsers failed. Last error: {str(e)}" 