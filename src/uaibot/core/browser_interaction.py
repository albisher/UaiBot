import logging
from .typing import Dict, Any, Optional, List
import webbrowser
from .selenium import webdriver
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
        """Read the current page content with comprehensive element analysis."""
        driver = self._get_driver(browser)
        if not driver:
            return {"status": "error", "message": f"Could not get driver for {browser}"}
        
        try:
            # Wait for page to be fully loaded
            WebDriverWait(driver, self.wait_timeout).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            
            # Get page title and URL
            title = driver.title
            current_url = driver.current_url
            
            # Get page source
            source = driver.page_source
            
            # Get visible text
            visible_text = driver.find_element(By.TAG_NAME, "body").text
            
            # Get all interactive elements
            elements = {
                "links": [],
                "buttons": [],
                "inputs": [],
                "videos": [],
                "images": [],
                "iframes": [],
                "dropdowns": [],
                "checkboxes": [],
                "radio_buttons": [],
                "text_areas": [],
                "media_players": []
            }
            
            # Links with text, href, and position
            for link in driver.find_elements(By.TAG_NAME, "a"):
                try:
                    href = link.get_attribute('href')
                    text = link.text
                    location = link.location
                    size = link.size
                    if href:
                        elements["links"].append({
                            "text": text,
                            "url": href,
                            "position": location,
                            "size": size,
                            "is_visible": link.is_displayed()
                        })
                except:
                    continue
            
            # Buttons with text, type, and position
            for button in driver.find_elements(By.TAG_NAME, "button"):
                try:
                    text = button.text
                    button_type = button.get_attribute('type')
                    location = button.location
                    size = button.size
                    if text or button_type:
                        elements["buttons"].append({
                            "text": text,
                            "type": button_type,
                            "position": location,
                            "size": size,
                            "is_visible": button.is_displayed()
                        })
                except:
                    continue
            
            # Input fields with type, name, and position
            for input_elem in driver.find_elements(By.TAG_NAME, "input"):
                try:
                    input_type = input_elem.get_attribute('type')
                    input_name = input_elem.get_attribute('name')
                    input_id = input_elem.get_attribute('id')
                    location = input_elem.location
                    size = input_elem.size
                    if input_type:
                        elements["inputs"].append({
                            "type": input_type,
                            "name": input_name,
                            "id": input_id,
                            "position": location,
                            "size": size,
                            "is_visible": input_elem.is_displayed()
                        })
                except:
                    continue
            
            # Video elements
            for video in driver.find_elements(By.TAG_NAME, "video"):
                try:
                    src = video.get_attribute('src')
                    poster = video.get_attribute('poster')
                    location = video.location
                    size = video.size
                    elements["videos"].append({
                        "src": src,
                        "poster": poster,
                        "position": location,
                        "size": size,
                        "is_visible": video.is_displayed()
                    })
                except:
                    continue
            
            # Images with src and alt text
            for img in driver.find_elements(By.TAG_NAME, "img"):
                try:
                    src = img.get_attribute('src')
                    alt = img.get_attribute('alt')
                    location = img.location
                    size = img.size
                    if src:
                        elements["images"].append({
                            "src": src,
                            "alt": alt,
                            "position": location,
                            "size": size,
                            "is_visible": img.is_displayed()
                        })
                except:
                    continue
            
            # Iframes
            for iframe in driver.find_elements(By.TAG_NAME, "iframe"):
                try:
                    src = iframe.get_attribute('src')
                    location = iframe.location
                    size = iframe.size
                    if src:
                        elements["iframes"].append({
                            "src": src,
                            "position": location,
                            "size": size,
                            "is_visible": iframe.is_displayed()
                        })
                except:
                    continue
            
            # Dropdowns (select elements)
            for select in driver.find_elements(By.TAG_NAME, "select"):
                try:
                    options = [option.text for option in select.find_elements(By.TAG_NAME, "option")]
                    location = select.location
                    size = select.size
                    elements["dropdowns"].append({
                        "options": options,
                        "position": location,
                        "size": size,
                        "is_visible": select.is_displayed()
                    })
                except:
                    continue
            
            # Checkboxes
            for checkbox in driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']"):
                try:
                    name = checkbox.get_attribute('name')
                    checked = checkbox.is_selected()
                    location = checkbox.location
                    size = checkbox.size
                    elements["checkboxes"].append({
                        "name": name,
                        "checked": checked,
                        "position": location,
                        "size": size,
                        "is_visible": checkbox.is_displayed()
                    })
                except:
                    continue
            
            # Radio buttons
            for radio in driver.find_elements(By.CSS_SELECTOR, "input[type='radio']"):
                try:
                    name = radio.get_attribute('name')
                    checked = radio.is_selected()
                    location = radio.location
                    size = radio.size
                    elements["radio_buttons"].append({
                        "name": name,
                        "checked": checked,
                        "position": location,
                        "size": size,
                        "is_visible": radio.is_displayed()
                    })
                except:
                    continue
            
            # Text areas
            for textarea in driver.find_elements(By.TAG_NAME, "textarea"):
                try:
                    name = textarea.get_attribute('name')
                    placeholder = textarea.get_attribute('placeholder')
                    location = textarea.location
                    size = textarea.size
                    elements["text_areas"].append({
                        "name": name,
                        "placeholder": placeholder,
                        "position": location,
                        "size": size,
                        "is_visible": textarea.is_displayed()
                    })
                except:
                    continue
            
            # Media players (audio, video, iframe-based players)
            for media in driver.find_elements(By.CSS_SELECTOR, "audio, video, iframe[src*='player'], iframe[src*='video']"):
                try:
                    src = media.get_attribute('src')
                    media_type = media.tag_name
                    location = media.location
                    size = media.size
                    elements["media_players"].append({
                        "src": src,
                        "type": media_type,
                        "position": location,
                        "size": size,
                        "is_visible": media.is_displayed()
                    })
                except:
                    continue
            
            # Get page styles and layout information
            styles = {
                "colors": self._extract_colors(driver),
                "fonts": self._extract_fonts(driver),
                "layout": self._analyze_layout(driver)
            }
            
            return {
                "status": "success",
                "title": title,
                "url": current_url,
                "source": source,
                "visible_text": visible_text,
                "elements": elements,
                "styles": styles
            }
        except Exception as e:
            logger.error(f"Error reading page content: {str(e)}")
            return {"status": "error", "message": f"Error reading page content: {str(e)}"}
    
    def _extract_colors(self, driver) -> Dict[str, List[str]]:
        """Extract color information from the page."""
        try:
            colors = {
                "background": [],
                "text": [],
                "links": [],
                "buttons": []
            }
            
            # Get background colors
            for elem in driver.find_elements(By.CSS_SELECTOR, "*"):
                try:
                    bg_color = elem.value_of_css_property("background-color")
                    if bg_color and bg_color != "rgba(0, 0, 0, 0)":
                        colors["background"].append(bg_color)
                except:
                    continue
            
            # Get text colors
            for elem in driver.find_elements(By.CSS_SELECTOR, "p, h1, h2, h3, h4, h5, h6, span, div"):
                try:
                    text_color = elem.value_of_css_property("color")
                    if text_color:
                        colors["text"].append(text_color)
                except:
                    continue
            
            # Get link colors
            for link in driver.find_elements(By.TAG_NAME, "a"):
                try:
                    link_color = link.value_of_css_property("color")
                    if link_color:
                        colors["links"].append(link_color)
                except:
                    continue
            
            # Get button colors
            for button in driver.find_elements(By.TAG_NAME, "button"):
                try:
                    button_color = button.value_of_css_property("background-color")
                    if button_color:
                        colors["buttons"].append(button_color)
                except:
                    continue
            
            return colors
        except:
            return {}
    
    def _extract_fonts(self, driver) -> Dict[str, List[str]]:
        """Extract font information from the page."""
        try:
            fonts = {
                "families": [],
                "sizes": []
            }
            
            for elem in driver.find_elements(By.CSS_SELECTOR, "*"):
                try:
                    font_family = elem.value_of_css_property("font-family")
                    font_size = elem.value_of_css_property("font-size")
                    if font_family:
                        fonts["families"].append(font_family)
                    if font_size:
                        fonts["sizes"].append(font_size)
                except:
                    continue
            
            return fonts
        except:
            return {}
    
    def _analyze_layout(self, driver) -> Dict[str, Any]:
        """Analyze the page layout and structure."""
        try:
            layout = {
                "sections": [],
                "navigation": [],
                "content_areas": [],
                "sidebars": []
            }
            
            # Analyze page sections
            for section in driver.find_elements(By.CSS_SELECTOR, "section, main, article, aside, nav, header, footer"):
                try:
                    section_type = section.tag_name
                    location = section.location
                    size = section.size
                    layout["sections"].append({
                        "type": section_type,
                        "position": location,
                        "size": size
                    })
                except:
                    continue
            
            # Analyze navigation elements
            for nav in driver.find_elements(By.CSS_SELECTOR, "nav, [role='navigation']"):
                try:
                    location = nav.location
                    size = nav.size
                    layout["navigation"].append({
                        "position": location,
                        "size": size
                    })
                except:
                    continue
            
            # Analyze content areas
            for content in driver.find_elements(By.CSS_SELECTOR, "main, article, [role='main']"):
                try:
                    location = content.location
                    size = content.size
                    layout["content_areas"].append({
                        "position": location,
                        "size": size
                    })
                except:
                    continue
            
            # Analyze sidebars
            for sidebar in driver.find_elements(By.CSS_SELECTOR, "aside, [role='complementary']"):
                try:
                    location = sidebar.location
                    size = sidebar.size
                    layout["sidebars"].append({
                        "position": location,
                        "size": size
                    })
                except:
                    continue
            
            return layout
        except:
            return {}

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