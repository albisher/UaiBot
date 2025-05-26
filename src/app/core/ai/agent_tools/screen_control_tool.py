import logging
import pyautogui
import gettext
import locale
from typing import Dict, Any, Tuple
from app.platform_core.platform_manager import PlatformManager

"""
Screen Control Tool for Labeeb

This module provides screen control and automation capabilities for the Labeeb AI agent.
It handles screen-related operations like taking screenshots, locating images on screen,
and managing screen dimensions across different platforms.

Key features:
- Cross-platform screen control (macOS, Windows, Ubuntu)
- Screenshot capture with optional region selection
- Image recognition and location detection
- Screen dimension management
- Platform-specific configuration
- Internationalization (i18n) support with RTL layout handling

See also:
- docs/features/screen_control.md for detailed usage examples
- app/platform_core/platform_manager.py for platform-specific implementations
- docs/architecture/agent_tools.md for tool architecture overview
"""

logger = logging.getLogger(__name__)

class ScreenControlTool:
    def __init__(self, language_code: str = 'en'):
        self.platform_manager = PlatformManager()
        self.platform_info = self.platform_manager.get_platform_info()
        self.handlers = self.platform_manager.get_handlers()
        self._configure_platform()
        self._setup_translations(language_code)

    def _setup_translations(self, language_code: str) -> None:
        """Setup translations and RTL support for the specified language"""
        try:
            # Set locale for the current thread
            locale.setlocale(locale.LC_ALL, f'{language_code}.UTF-8')
            
            # Setup gettext translations
            self.translations = gettext.translation(
                'labeeb',
                localedir='locales',
                languages=[language_code],
                fallback=True
            )
            self._ = self.translations.gettext
            
            # Check if language is RTL
            self.is_rtl = language_code.startswith('ar')
            
            logger.info(f"Translations setup for language: {language_code} (RTL: {self.is_rtl})")
        except Exception as e:
            logger.error(f"Error setting up translations: {str(e)}")
            # Fallback to English
            self._ = lambda x: x
            self.is_rtl = False

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
                'size': {'width': width, 'height': height},
                'is_rtl': self.is_rtl  # Include RTL status in response
            }
        except Exception as e:
            logger.error(f"Error getting screen size: {str(e)}")
            return {
                'platform': self.platform_info['name'],
                'action': 'get_size',
                'status': 'error',
                'error': self._("Error getting screen size: {}").format(str(e)),
                'is_rtl': self.is_rtl
            }

    def take_screenshot(self, region: Tuple[int, int, int, int] = None) -> Dict[str, Any]:
        """Take a screenshot"""
        try:
            result = {
                'platform': self.platform_info['name'],
                'action': 'screenshot',
                'status': 'success',
                'image': None,
                'is_rtl': self.is_rtl
            }

            screenshot = pyautogui.screenshot(region=region)
            result['image'] = screenshot
            result['message'] = self._("Screen capture successful")
            return result

        except Exception as e:
            logger.error(f"Error taking screenshot: {str(e)}")
            return {
                'platform': self.platform_info['name'],
                'action': 'screenshot',
                'status': 'error',
                'error': self._("Screen capture failed: {}").format(str(e)),
                'is_rtl': self.is_rtl
            }

    def locate_on_screen(self, image_path: str, confidence: float = 0.9) -> Dict[str, Any]:
        """Locate an image on screen"""
        try:
            result = {
                'platform': self.platform_info['name'],
                'action': 'locate',
                'status': 'success',
                'location': None,
                'is_rtl': self.is_rtl
            }

            location = pyautogui.locateOnScreen(image_path, confidence=confidence)
            if location:
                result['location'] = {
                    'left': location.left,
                    'top': location.top,
                    'width': location.width,
                    'height': location.height
                }
                result['message'] = self._("Image found on screen")
            else:
                result['message'] = self._("Image not found on screen")
            return result

        except Exception as e:
            logger.error(f"Error locating on screen: {str(e)}")
            return {
                'platform': self.platform_info['name'],
                'action': 'locate',
                'status': 'error',
                'error': self._("Error locating image: {}").format(str(e)),
                'is_rtl': self.is_rtl
            }

    def check_screen_availability(self) -> bool:
        """Check if screen control is available"""
        try:
            # Test screen control
            pyautogui.size()
            return True
        except Exception as e:
            logger.error(self._("Error checking screen availability: {}").format(str(e)))
            return False 