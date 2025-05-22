import os
import shlex
import logging
from typing import Dict, Any, Optional, List
from playwright.sync_api import sync_playwright
import subprocess

logger = logging.getLogger(__name__)

class BrowserController:
    """Handles browser automation using Playwright and AppleScript."""
    
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.macos_browser_map = {
            'chrome': 'Google Chrome',
            'google chrome': 'Google Chrome',
            'safari': 'Safari',
            'firefox': 'Firefox',
            'mozilla firefox': 'Firefox',
        }
    
    def _normalize_browser_name(self, browser: str) -> str:
        """Normalize browser name for macOS."""
        browser_lc = browser.lower().strip()
        return self.macos_browser_map.get(browser_lc, browser_lc)
    
    def _execute_applescript(self, script: str) -> str:
        """Execute AppleScript command."""
        try:
            cmd = f'osascript -e {shlex.quote(script)}'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.stdout.strip()
        except Exception as e:
            logger.error(f"AppleScript execution error: {str(e)}")
            return f"Error: {str(e)}"
    
    def open_browser(self, browser: str, url: Optional[str] = None) -> str:
        """Open browser using AppleScript (macOS) or Playwright (cross-platform)."""
        if os.name == 'posix' and os.path.exists('/Applications'):
            # macOS: Use AppleScript
            mapped_browser = self._normalize_browser_name(browser)
            
            if mapped_browser == 'Safari':
                script = f'''
                    tell application "Safari"
                        activate
                        if (count of windows) = 0 then
                            make new document
                        end if
                        if "{url}" is not "" then
                            set URL of front document to "{url}"
                        end if
                    end tell
                '''
            elif mapped_browser == 'Google Chrome':
                script = f'''
                    tell application "Google Chrome"
                        activate
                        if (count of windows) = 0 then
                            make new window
                        end if
                        if "{url}" is not "" then
                            set URL of active tab of front window to "{url}"
                        end if
                    end tell
                '''
            else:
                # Fallback for Firefox and others
                script = f'''
                    tell application "{mapped_browser}"
                        activate
                        if "{url}" is not "" then
                            open location "{url}"
                        end if
                    end tell
                '''
            
            return self._execute_applescript(script)
        else:
            # Cross-platform: Use Playwright
            try:
                if not self.playwright:
                    self.playwright = sync_playwright().start()
                
                browser_type = 'chromium' if 'chrome' in browser.lower() else browser.lower()
                self.browser = getattr(self.playwright, browser_type).launch()
                self.context = self.browser.new_context()
                self.page = self.context.new_page()
                
                if url:
                    self.page.goto(url)
                
                return f"Opened {browser} using Playwright"
            except Exception as e:
                logger.error(f"Playwright error: {str(e)}")
                return f"Error: {str(e)}"
    
    def execute_javascript(self, browser: str, js_code: str) -> str:
        """Execute JavaScript in the active browser tab."""
        if os.name == 'posix' and os.path.exists('/Applications'):
            mapped_browser = self._normalize_browser_name(browser)
            
            if mapped_browser == 'Safari':
                script = f'''
                    tell application "Safari"
                        activate
                        tell front document
                            do JavaScript {shlex.quote(js_code)}
                        end tell
                    end tell
                '''
            elif mapped_browser == 'Google Chrome':
                script = f'''
                    tell application "Google Chrome"
                        activate
                        tell front window
                            execute active tab javascript {shlex.quote(js_code)}
                        end tell
                    end tell
                '''
            else:
                return "JavaScript execution not supported for this browser"
            
            return self._execute_applescript(script)
        else:
            # Cross-platform: Use Playwright
            try:
                if self.page:
                    return self.page.evaluate(js_code)
                return "No active page"
            except Exception as e:
                logger.error(f"Playwright JavaScript error: {str(e)}")
                return f"Error: {str(e)}"
    
    def click_element(self, browser: str, selector: str) -> str:
        """Click an element using CSS selector."""
        js_code = f'document.querySelector({shlex.quote(selector)}).click();'
        return self.execute_javascript(browser, js_code)
    
    def close(self):
        """Close browser and cleanup resources."""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop() 