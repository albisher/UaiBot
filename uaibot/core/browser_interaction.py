import logging
from typing import Dict, Any, Optional, List
import webbrowser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import os

logger = logging.getLogger(__name__)

class BrowserInteractionHandler:
    """Handles browser interactions and automation."""
    
    def __init__(self):
        self.drivers = {}
        self.active_browser = None
        self.wait_timeout = 10
        self.supported_browsers = ["chrome", "firefox", "safari", "edge"]
    
    def _get_driver(self, browser: str) -> Optional[webdriver.Remote]:
        """Get or create a WebDriver instance for the specified browser."""
        if browser not in self.drivers:
            try:
                if browser == "chrome":
                    self.drivers[browser] = webdriver.Chrome()
                elif browser == "firefox":
                    self.drivers[browser] = webdriver.Firefox()
                elif browser == "safari":
                    self.drivers[browser] = webdriver.Safari()
                elif browser == "edge":
                    self.drivers[browser] = webdriver.Edge()
                else:
                    logger.error(f"Unsupported browser: {browser}")
                    return None
            except Exception as e:
                logger.error(f"Error creating WebDriver for {browser}: {str(e)}")
                return None
        
        self.active_browser = browser
        return self.drivers[browser]
    
    def click_element(self, browser: str, selector: str, selector_type: str = "css") -> Dict[str, Any]:
        """Click an element in the specified browser."""
        driver = self._get_driver(browser)
        if not driver:
            return {"status": "error", "message": f"Could not get driver for {browser}"}
        
        try:
            if selector_type == "css":
                element = WebDriverWait(driver, self.wait_timeout).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
            elif selector_type == "xpath":
                element = WebDriverWait(driver, self.wait_timeout).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
            else:
                return {"status": "error", "message": f"Unsupported selector type: {selector_type}"}
            
            element.click()
            return {"status": "success", "message": f"Clicked element {selector}"}
        except TimeoutException:
            return {"status": "error", "message": f"Timeout waiting for element {selector}"}
        except NoSuchElementException:
            return {"status": "error", "message": f"Element {selector} not found"}
        except Exception as e:
            return {"status": "error", "message": f"Error clicking element: {str(e)}"}
    
    def click_middle_link(self, browser: str) -> Dict[str, Any]:
        """Click the middle link on the current page."""
        if browser == "default":
            browser = "chrome"  # Fallback to Chrome for default
        if browser not in self.supported_browsers:
            return {"status": "error", "message": f"Unsupported browser: {browser}"}
        
        driver = self._get_driver(browser)
        if not driver:
            return {"status": "error", "message": f"Could not get driver for {browser}"}
        
        try:
            # Take a screenshot of the page
            screenshot = driver.get_screenshot_as_png()
            # Wait a fraction of a second to allow the page to settle
            time.sleep(0.5)
            # Log the page title before clicking
            page_title = driver.title
            logger.debug(f"Page title before clicking middle link: {page_title}")
            # TODO: Process the screenshot to visually determine the middle link
            # For now, fallback to the original method
            links = driver.find_elements(By.TAG_NAME, "a")
            if not links:
                return {"status": "error", "message": "No links found on the page"}
            
            # Get the middle link
            middle_index = len(links) // 2
            middle_link = links[middle_index]
            
            # Click the middle link
            middle_link.click()
            return {"status": "success", "message": "Clicked middle link"}
        except Exception as e:
            return {"status": "error", "message": f"Error clicking middle link: {str(e)}"}
    
    def focus_browser(self, browser: str) -> Dict[str, Any]:
        """Focus the browser window."""
        if browser == "default":
            browser = "chrome"  # Fallback to Chrome for default
        if browser not in self.supported_browsers:
            return {"status": "error", "message": f"Unsupported browser: {browser}"}
        
        driver = self._get_driver(browser)
        if not driver:
            return {"status": "error", "message": f"Could not get driver for {browser}"}
        
        try:
            # Maximize window
            driver.maximize_window()
            # Bring window to front
            driver.execute_script("window.focus();")
            return {"status": "success", "message": f"Focused {browser} window"}
        except Exception as e:
            return {"status": "error", "message": f"Error focusing browser: {str(e)}"}
    
    def set_volume(self, volume: int) -> Dict[str, Any]:
        """Set system volume (requires platform-specific implementation)."""
        try:
            # This is a placeholder - actual implementation would depend on the OS
            # For macOS, we could use osascript
            import subprocess
            subprocess.run(["osascript", "-e", f"set volume output volume {volume}"])
            return {"status": "success", "message": f"Set volume to {volume}%"}
        except Exception as e:
            return {"status": "error", "message": f"Error setting volume: {str(e)}"}
    
    def play_media(self, media_url: str) -> Dict[str, Any]:
        """Play media in the specified browser."""
        driver = self._get_driver(media_url.split("://")[0])
        if not driver:
            return {"status": "error", "message": f"Could not get driver for {media_url.split('://')[0]}"}
        
        try:
            driver.get(media_url)
            # Wait for media player to load
            WebDriverWait(driver, self.wait_timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "video"))
            )
            return {"status": "success", "message": "Started playing media"}
        except Exception as e:
            return {"status": "error", "message": f"Error playing media: {str(e)}"}
    
    def cast_to_tv(self, target: str) -> Dict[str, Any]:
        """Cast media to a TV (requires platform-specific implementation)."""
        try:
            # This is a placeholder - actual implementation would depend on the casting protocol
            # For example, using Chrome's casting API or a third-party library
            return {"status": "success", "message": f"Casting to {target}"}
        except Exception as e:
            return {"status": "error", "message": f"Error casting to TV: {str(e)}"}
    
    def close_browser(self, browser: str) -> Dict[str, Any]:
        """Close the specified browser."""
        if browser == "default":
            browser = "chrome"  # Fallback to Chrome for default
        if browser not in self.supported_browsers:
            return {"status": "error", "message": f"Unsupported browser: {browser}"}
        if browser in self.drivers:
            try:
                self.drivers[browser].quit()
                del self.drivers[browser]
                if self.active_browser == browser:
                    self.active_browser = None
                return {"status": "success", "message": f"Closed {browser}"}
            except Exception as e:
                return {"status": "error", "message": f"Error closing browser: {str(e)}"}
        return {"status": "error", "message": f"Browser {browser} not found"}

    def take_silent_screenshot(self, browser: str, filename: str = "browser_screenshot.png") -> Dict[str, Any]:
        """Take a silent screenshot of the browser window."""
        driver = self._get_driver(browser)
        if not driver:
            return {"status": "error", "message": f"Could not get driver for {browser}"}
        
        try:
            # Wait for page to be fully loaded
            WebDriverWait(driver, self.wait_timeout).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            
            # Take screenshot
            screenshot = driver.get_screenshot_as_png()
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            with open(filename, 'wb') as f:
                f.write(screenshot)
                
            # Log success silently
            logger.debug(f"Screenshot saved to {filename}")
            return {"status": "success", "message": f"Screenshot saved to {filename}", "filename": filename}
        except Exception as e:
            logger.error(f"Error taking screenshot: {str(e)}")
            return {"status": "error", "message": f"Error taking screenshot: {str(e)}"}

    def read_page_content(self, browser: str) -> Dict[str, Any]:
        """Read the current page content."""
        driver = self._get_driver(browser)
        if not driver:
            return {"status": "error", "message": f"Could not get driver for {browser}"}
        
        try:
            # Wait for page to be fully loaded
            WebDriverWait(driver, self.wait_timeout).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            
            # Get page title
            title = driver.title
            
            # Get current URL
            current_url = driver.current_url
            
            # Get page source
            source = driver.page_source
            
            # Get visible text
            visible_text = driver.find_element(By.TAG_NAME, "body").text
            
            # Get all links with their text
            links = []
            for link in driver.find_elements(By.TAG_NAME, "a"):
                href = link.get_attribute('href')
                text = link.text
                if href and text:
                    links.append({"text": text, "url": href})
            
            # Get all buttons
            buttons = []
            for button in driver.find_elements(By.TAG_NAME, "button"):
                text = button.text
                if text:
                    buttons.append(text)
            
            # Get all input fields
            inputs = []
            for input_elem in driver.find_elements(By.TAG_NAME, "input"):
                input_type = input_elem.get_attribute('type')
                input_name = input_elem.get_attribute('name')
                input_id = input_elem.get_attribute('id')
                if input_type or input_name or input_id:
                    inputs.append({
                        "type": input_type,
                        "name": input_name,
                        "id": input_id
                    })
            
            return {
                "status": "success",
                "title": title,
                "url": current_url,
                "source": source,
                "visible_text": visible_text,
                "links": links,
                "buttons": buttons,
                "inputs": inputs
            }
        except Exception as e:
            logger.error(f"Error reading page content: {str(e)}")
            return {"status": "error", "message": f"Error reading page content: {str(e)}"}

    def execute_action_with_context(self, browser: str, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an action after taking a screenshot and reading page content."""
        driver = self._get_driver(browser)
        if not driver:
            return {"status": "error", "message": f"Could not get driver for {browser}"}
        
        # Take silent screenshot
        screenshot_result = self.take_silent_screenshot(browser)
        if screenshot_result["status"] == "error":
            return screenshot_result
        
        # Read page content
        content_result = self.read_page_content(browser)
        if content_result["status"] == "error":
            return content_result
        
        # Execute the requested action
        try:
            if action["type"] == "click":
                return self.click_element(browser, action["selector"], action.get("selector_type", "css"))
            elif action["type"] == "type":
                element = driver.find_element(By.CSS_SELECTOR, action["selector"])
                element.clear()  # Clear existing text
                element.send_keys(action["text"])
                return {"status": "success", "message": f"Typed text into {action['selector']}"}
            elif action["type"] == "wait":
                time.sleep(action.get("seconds", 1))
                return {"status": "success", "message": f"Waited {action.get('seconds', 1)} seconds"}
            elif action["type"] == "submit":
                element = driver.find_element(By.CSS_SELECTOR, action["selector"])
                element.submit()
                return {"status": "success", "message": f"Submitted form {action['selector']}"}
            elif action["type"] == "select":
                from selenium.webdriver.support.ui import Select
                element = driver.find_element(By.CSS_SELECTOR, action["selector"])
                select = Select(element)
                select.select_by_visible_text(action["value"])
                return {"status": "success", "message": f"Selected {action['value']} in {action['selector']}"}
            else:
                return {"status": "error", "message": f"Unsupported action type: {action['type']}"}
        except Exception as e:
            logger.error(f"Error executing action: {str(e)}")
            return {"status": "error", "message": f"Error executing action: {str(e)}"} 