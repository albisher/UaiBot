import logging
import pyautogui
from typing import Dict, Any, Tuple
from app.platform_core.platform_manager import PlatformManager

logger = logging.getLogger(__name__)

class MouseControlTool:
    def __init__(self):
        self.platform_manager = PlatformManager()
        self.platform_info = self.platform_manager.get_platform_info()
        self.handlers = self.platform_manager.get_handlers()
        self._configure_platform()

    def _configure_platform(self) -> None:
        """Configure platform-specific mouse settings"""
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

    def move_mouse(self, x: int, y: int) -> Dict[str, Any]:
        """Move mouse to specified coordinates"""
        try:
            result = {
                'platform': self.platform_info['name'],
                'action': 'move',
                'status': 'success',
                'position': {'x': x, 'y': y}
            }

            pyautogui.moveTo(x, y)
            return result

        except Exception as e:
            logger.error(f"Error moving mouse: {str(e)}")
            return {
                'platform': self.platform_info['name'],
                'action': 'move',
                'status': 'error',
                'error': str(e)
            }

    def click(self, button: str = 'left') -> Dict[str, Any]:
        """Click mouse button"""
        try:
            result = {
                'platform': self.platform_info['name'],
                'action': 'click',
                'status': 'success',
                'button': button
            }

            pyautogui.click(button=button)
            return result

        except Exception as e:
            logger.error(f"Error clicking mouse: {str(e)}")
            return {
                'platform': self.platform_info['name'],
                'action': 'click',
                'status': 'error',
                'error': str(e)
            }

    def get_mouse_position(self) -> Dict[str, Any]:
        """Get current mouse position"""
        try:
            x, y = pyautogui.position()
            return {
                'platform': self.platform_info['name'],
                'action': 'get_position',
                'status': 'success',
                'position': {'x': x, 'y': y}
            }
        except Exception as e:
            logger.error(f"Error getting mouse position: {str(e)}")
            return {
                'platform': self.platform_info['name'],
                'action': 'get_position',
                'status': 'error',
                'error': str(e)
            }

    def check_mouse_availability(self) -> bool:
        """Check if mouse control is available"""
        try:
            # Test mouse control
            pyautogui.position()
            return True
        except Exception as e:
            logger.error(f"Error checking mouse availability: {str(e)}")
            return False 