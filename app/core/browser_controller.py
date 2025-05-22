import os
import shlex
import logging
from typing import Dict, Any, Optional, List
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
        
        # Try to import Playwright, but don't fail if not available
        try:
            from playwright.sync_api import sync_playwright
            self.playwright_available = True
            self.sync_playwright = sync_playwright
        except ImportError:
            logger.warning("Playwright not available. Some features may be limited.")
            self.playwright_available = False
    
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
    
    def open_browser(self, browser: str, url: Optional[str] = None, profile_path: Optional[str] = None, incognito: bool = False) -> str:
        """
        Open browser using AppleScript (macOS) or Playwright (cross-platform).
        Supports profile_path and incognito/private mode for Playwright.
        """
        if os.name == 'posix' and os.path.exists('/Applications'):
            mapped_browser = self._normalize_browser_name(browser)
            # AppleScript: Incognito/profile not natively supported, but can try for Chrome
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
                if incognito:
                    script = f'''
                        tell application "Google Chrome"
                            activate
                            make new window with properties {{mode:"incognito"}}
                            if "{url}" is not "" then
                                set URL of active tab of front window to "{url}"
                            end if
                        end tell
                    '''
                else:
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
            if not self.playwright_available:
                return "Error: Playwright not available for cross-platform browser automation"
            try:
                if not self.playwright:
                    self.playwright = self.sync_playwright().start()
                browser_type = 'chromium' if 'chrome' in browser.lower() else browser.lower()
                launch_args = {}
                context_args = {}
                if profile_path:
                    context_args['user_data_dir'] = profile_path
                if incognito:
                    context_args['is_incognito'] = True
                self.browser = getattr(self.playwright, browser_type).launch()
                if context_args.get('user_data_dir'):
                    self.context = self.browser.new_context(user_data_dir=context_args['user_data_dir'])
                elif context_args.get('is_incognito'):
                    self.context = self.browser.new_context()
                else:
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
            result = self._execute_applescript(script)
            # Only treat as error if result contains 'error' (case-insensitive)
            if result and 'error' in result.lower():
                return f"Error: {result}"
            # If result is empty, treat as success (AppleScript does not return JS result)
            return result if result else "OK"
        else:
            if not self.playwright_available:
                return "Error: Playwright not available for JavaScript execution"
            try:
                if self.page:
                    return self.page.evaluate(js_code)
                return "Error: No active page"
            except Exception as e:
                logger.error(f"Playwright JavaScript error: {str(e)}")
                return f"Error: {str(e)}"
    
    def click_element(self, browser: str, selector: str) -> str:
        """Click an element using CSS selector. Returns error if not found."""
        js_code = f"""
        (function() {{
            var el = document.querySelector({repr(selector)});
            if (el) {{ el.click(); return 'clicked'; }}
            else {{ return 'not found'; }}
        }})()
        """
        if os.name == 'posix' and os.path.exists('/Applications'):
            result = self.execute_javascript(browser, js_code)
            if result.strip() == 'clicked':
                return f"Clicked element {selector}"
            elif result.strip() == 'not found':
                return f"Error: Could not find element with selector {selector}"
            elif result.startswith("Error"):
                return result
            return f"Unknown result: {result}"
        else:
            if not self.playwright_available or not self.page:
                return "Error: Playwright not available or no active page for click_element"
            try:
                res = self.page.evaluate(js_code)
                if res == 'clicked':
                    return f"Clicked element {selector}"
                elif res == 'not found':
                    return f"Error: Could not find element with selector {selector}"
                return f"Unknown result: {res}"
            except Exception as e:
                logger.error(f"Playwright click error: {str(e)}")
                return f"Error: {str(e)}"
    
    def upload_file(self, selector: str, file_path: str) -> str:
        """
        Upload a file using a file input selector (Playwright only).
        """
        if not self.playwright_available or not self.page:
            return "Error: Playwright not available or no active page for file upload"
        try:
            self.page.set_input_files(selector, file_path)
            return f"Uploaded {file_path} to {selector}"
        except Exception as e:
            logger.error(f"File upload error: {str(e)}")
            return f"Error: {str(e)}"
    
    def download_file(self, url: str, download_path: str) -> str:
        """
        Download a file from a URL (Playwright only).
        """
        if not self.playwright_available or not self.page:
            return "Error: Playwright not available or no active page for download"
        try:
            with self.page.expect_download() as download_info:
                self.page.goto(url)
            download = download_info.value
            download.save_as(download_path)
            return f"Downloaded {url} to {download_path}"
        except Exception as e:
            logger.error(f"Download error: {str(e)}")
            return f"Error: {str(e)}"
    
    def screenshot(self, path: str = "screenshot.png") -> str:
        """
        Take a screenshot of the current page (Playwright only).
        """
        if not self.playwright_available or not self.page:
            return "Error: Playwright not available or no active page for screenshot"
        try:
            self.page.screenshot(path=path)
            return f"Screenshot saved to {path}"
        except Exception as e:
            logger.error(f"Screenshot error: {str(e)}")
            return f"Error: {str(e)}"
    
    def close(self):
        """Close browser and cleanup resources."""
        try:
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
        except Exception as e:
            logger.error(f"Error closing browser: {str(e)}") 