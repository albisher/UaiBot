import logging
import pyautogui
from typing import Dict, Any, Tuple
from app.platform_core.platform_manager import PlatformManager

logger = logging.getLogger(__name__)

class ScreenControlTool:
    def __init__(self):
        self.platform_manager = PlatformManager()
        self.platform_info = self.platform_manager.get_platform_info()
        self.handlers = self.platform_manager.get_handlers()
        self._configure_platform()

    def _configure_platform(self) -> None:
        """Configure platform-specific screen settings"""
        try:
            if self.platform_info['name'] == 'mac':
                pyautogui.FAILSAFE = True
                pyautogui.PAUSE = 0.1
            elif self.platform_info['name'] == 'windows':
                pyautogui.FAILSAFE = True
                pyautogui.PAUSE = 0.1
            elif self.platform_info['name'] == 'ubuntu':
                pyautogui.FAILSAFE = True
                pyautogui.PAUSE = 0.1
        except Exception as e:
            logger.error(f"Error configuring platform: {str(e)}")

    def get_screen_size(self) -> Dict[str, Any]:
        """Get screen size"""
        try:
            width, height = pyautogui.size()
            return {
                'platform': self.platform_info['name'],
                'action': 'get_size',
                'status': 'success',
                'size': {'width': width, 'height': height}
            }
        except Exception as e:
            logger.error(f"Error getting screen size: {str(e)}")
            return {
                'platform': self.platform_info['name'],
                'action': 'get_size',
                'status': 'error',
                'error': str(e)
            }

    def take_screenshot(self, region: Tuple[int, int, int, int] = None) -> Dict[str, Any]:
        """Take a screenshot"""
        try:
            result = {
                'platform': self.platform_info['name'],
                'action': 'screenshot',
                'status': 'success',
                'image': None
            }

            screenshot = pyautogui.screenshot(region=region)
            result['image'] = screenshot
            return result

        except Exception as e:
            logger.error(f"Error taking screenshot: {str(e)}")
            return {
                'platform': self.platform_info['name'],
                'action': 'screenshot',
                'status': 'error',
                'error': str(e)
            }

    def locate_on_screen(self, image_path: str, confidence: float = 0.9) -> Dict[str, Any]:
        """Locate an image on screen"""
        try:
            result = {
                'platform': self.platform_info['name'],
                'action': 'locate',
                'status': 'success',
                'location': None
            }

            location = pyautogui.locateOnScreen(image_path, confidence=confidence)
            if location:
                result['location'] = {
                    'left': location.left,
                    'top': location.top,
                    'width': location.width,
                    'height': location.height
                }
            return result

        except Exception as e:
            logger.error(f"Error locating on screen: {str(e)}")
            return {
                'platform': self.platform_info['name'],
                'action': 'locate',
                'status': 'error',
                'error': str(e)
            }

    def check_screen_availability(self) -> bool:
        """Check if screen control is available"""
        try:
            # Test screen control
            pyautogui.size()
            return True
        except Exception as e:
            logger.error(f"Error checking screen availability: {str(e)}")
            return False 