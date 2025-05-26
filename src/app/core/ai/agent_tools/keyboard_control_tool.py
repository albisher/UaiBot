import logging
import keyboard
from typing import Dict, Any, List
from app.platform_core.platform_manager import PlatformManager

logger = logging.getLogger(__name__)

class KeyboardControlTool:
    def __init__(self):
        self.platform_manager = PlatformManager()
        self.platform_info = self.platform_manager.get_platform_info()
        self.handlers = self.platform_manager.get_handlers()
        self._configure_platform()

    def _configure_platform(self) -> None:
        """Configure platform-specific keyboard settings"""
        try:
            if self.platform_info['name'] == 'mac':
                self.modifier_key = 'command'
            elif self.platform_info['name'] == 'windows':
                self.modifier_key = 'ctrl'
            elif self.platform_info['name'] == 'ubuntu':
                self.modifier_key = 'ctrl'
            else:
                self.modifier_key = 'ctrl'
        except Exception as e:
            logger.error(f"Error configuring platform: {str(e)}")

    def press_key(self, key: str) -> Dict[str, Any]:
        """Press a key"""
        try:
            result = {
                'platform': self.platform_info['name'],
                'action': 'press',
                'status': 'success',
                'key': key
            }

            keyboard.press(key)
            return result

        except Exception as e:
            logger.error(f"Error pressing key: {str(e)}")
            return {
                'platform': self.platform_info['name'],
                'action': 'press',
                'status': 'error',
                'error': str(e)
            }

    def release_key(self, key: str) -> Dict[str, Any]:
        """Release a key"""
        try:
            result = {
                'platform': self.platform_info['name'],
                'action': 'release',
                'status': 'success',
                'key': key
            }

            keyboard.release(key)
            return result

        except Exception as e:
            logger.error(f"Error releasing key: {str(e)}")
            return {
                'platform': self.platform_info['name'],
                'action': 'release',
                'status': 'error',
                'error': str(e)
            }

    def type_text(self, text: str) -> Dict[str, Any]:
        """Type text"""
        try:
            result = {
                'platform': self.platform_info['name'],
                'action': 'type',
                'status': 'success',
                'text': text
            }

            keyboard.write(text)
            return result

        except Exception as e:
            logger.error(f"Error typing text: {str(e)}")
            return {
                'platform': self.platform_info['name'],
                'action': 'type',
                'status': 'error',
                'error': str(e)
            }

    def get_pressed_keys(self) -> Dict[str, Any]:
        """Get currently pressed keys"""
        try:
            keys = keyboard.get_pressed_keys()
            return {
                'platform': self.platform_info['name'],
                'action': 'get_pressed',
                'status': 'success',
                'keys': keys
            }
        except Exception as e:
            logger.error(f"Error getting pressed keys: {str(e)}")
            return {
                'platform': self.platform_info['name'],
                'action': 'get_pressed',
                'status': 'error',
                'error': str(e)
            }

    def check_keyboard_availability(self) -> bool:
        """Check if keyboard control is available"""
        try:
            # Test keyboard control
            keyboard.get_pressed_keys()
            return True
        except Exception as e:
            logger.error(f"Error checking keyboard availability: {str(e)}")
            return False 