import pyautogui
from typing import Dict, List, Optional, Tuple
from Quartz import (
    CGWindowListCopyWindowInfo,
    kCGWindowListOptionOnScreenOnly,
    kCGNullWindowID,
    CGMainDisplayID,
    CGDisplayBounds,
    CGDisplayPixelsWide,
    CGDisplayPixelsHigh
)

from ...common.ui.ui_interface import UIInterface

class MacOSUI(UIInterface):
    """macOS implementation of UI operations."""
    
    def get_screen_size(self) -> Tuple[int, int]:
        """Get screen dimensions."""
        display_id = CGMainDisplayID()
        width = CGDisplayPixelsWide(display_id)
        height = CGDisplayPixelsHigh(display_id)
        return (width, height)
    
    def get_window_list(self) -> List[Dict[str, str]]:
        """Get list of open windows."""
        window_list = []
        windows = CGWindowListCopyWindowInfo(kCGWindowListOptionOnScreenOnly, kCGNullWindowID)
        for window in windows:
            window_info = {
                'id': str(window.get('kCGWindowNumber', '')),
                'name': window.get('kCGWindowName', ''),
                'owner': window.get('kCGWindowOwnerName', ''),
                'bounds': window.get('kCGWindowBounds', {}),
                'layer': str(window.get('kCGWindowLayer', 0))
            }
            window_list.append(window_info)
        return window_list
    
    def get_active_window(self) -> Dict[str, str]:
        """Get information about the active window."""
        windows = CGWindowListCopyWindowInfo(kCGWindowListOptionOnScreenOnly, kCGNullWindowID)
        for window in windows:
            if window.get('kCGWindowLayer', 0) == 0:  # Active window is usually layer 0
                return {
                    'id': str(window.get('kCGWindowNumber', '')),
                    'name': window.get('kCGWindowName', ''),
                    'owner': window.get('kCGWindowOwnerName', ''),
                    'bounds': window.get('kCGWindowBounds', {})
                }
        return {}
    
    def set_window_focus(self, window_id: str) -> bool:
        """Set focus to a specific window."""
        # macOS requires AppleScript for window focus
        import subprocess
        script = f'''
        tell application "System Events"
            set frontmost of process "{window_id}" to true
        end tell
        '''
        try:
            subprocess.run(['osascript', '-e', script], check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def get_mouse_position(self) -> Tuple[int, int]:
        """Get current mouse position."""
        return pyautogui.position()
    
    def set_mouse_position(self, x: int, y: int) -> bool:
        """Set mouse position."""
        try:
            pyautogui.moveTo(x, y)
            return True
        except Exception:
            return False
    
    def click_mouse(self, button: str = 'left') -> bool:
        """Perform mouse click."""
        try:
            pyautogui.click(button=button)
            return True
        except Exception:
            return False
    
    def type_text(self, text: str) -> bool:
        """Type text using keyboard."""
        try:
            pyautogui.write(text)
            return True
        except Exception:
            return False
    
    def press_key(self, key: str) -> bool:
        """Press a specific key."""
        try:
            pyautogui.press(key)
            return True
        except Exception:
            return False
    
    def take_screenshot(self, region: Optional[Tuple[int, int, int, int]] = None) -> bytes:
        """Take a screenshot of the screen or a specific region."""
        try:
            if region:
                screenshot = pyautogui.screenshot(region=region)
            else:
                screenshot = pyautogui.screenshot()
            return screenshot.tobytes()
        except Exception:
            return b'' 