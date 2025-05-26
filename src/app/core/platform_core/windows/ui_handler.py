import logging
import win32gui
import win32api
import win32con
import win32process
import win32clipboard
import ctypes
from typing import Any, Dict, List, Optional, Tuple

from ..base_ui_handler import BaseUIHandler

logger = logging.getLogger(__name__)

class WindowsUIHandler(BaseUIHandler):
    """Windows-specific UI handler implementation."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the Windows UI handler.
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(config)
    
    def initialize(self) -> bool:
        """Initialize the Windows UI handler.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            # Windows-specific initialization if needed
            self._initialized = True
            return True
        except Exception as e:
            logging.error(f"Failed to initialize Windows UI handler: {e}")
            return False
    
    def cleanup(self) -> None:
        """Clean up UI resources."""
        self._initialized = False
    
    def get_capabilities(self) -> Dict[str, bool]:
        """Get UI capabilities.
        
        Returns:
            Dict[str, bool]: Dictionary of available UI capabilities
        """
        return {
            'window_management': True,
            'screen_management': True,
            'clipboard_access': True,
            'theme_access': True,
            'scale_access': True,
            'keyboard_layout_access': True,
            'mouse_position_access': True
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current UI status.
        
        Returns:
            Dict[str, Any]: Dictionary containing UI status information
        """
        try:
            if not self._initialized:
                return {'error': 'Handler not initialized'}
            
            return {
                'initialized': self._initialized,
                'screens': self.get_screen_info(),
                'active_window': self.get_active_window(),
                'theme': self.get_ui_theme(),
                'scale': self.get_ui_scale(),
                'platform': 'Windows'
            }
        except Exception as e:
            logging.error(f"Error getting UI status: {e}")
            return {'error': str(e)}
    
    def get_screen_info(self) -> Dict[str, Any]:
        """Get information about all screens/displays.
        
        Returns:
            Dict[str, Any]: Dictionary containing screen information
        """
        try:
            if not self._initialized:
                return {'error': 'Handler not initialized'}
            
            screens = {}
            for i in range(win32api.GetSystemMetrics(win32con.SM_CMONITORS)):
                monitor_info = win32api.GetMonitorInfo(win32api.EnumDisplayMonitors()[i][0])
                device_info = win32api.EnumDisplayDevices(None, i)
                
                screens[str(i)] = {
                    'id': str(i),
                    'name': device_info.DeviceName,
                    'bounds': {
                        'x': monitor_info['Monitor'][0],
                        'y': monitor_info['Monitor'][1],
                        'width': monitor_info['Monitor'][2] - monitor_info['Monitor'][0],
                        'height': monitor_info['Monitor'][3] - monitor_info['Monitor'][1]
                    },
                    'work_area': {
                        'x': monitor_info['Work'][0],
                        'y': monitor_info['Work'][1],
                        'width': monitor_info['Work'][2] - monitor_info['Work'][0],
                        'height': monitor_info['Work'][3] - monitor_info['Work'][1]
                    },
                    'is_main': i == 0
                }
            
            return screens
        except Exception as e:
            logging.error(f"Error getting screen info: {e}")
            return {'error': str(e)}
    
    def get_window_list(self) -> List[Dict[str, Any]]:
        """Get list of all windows.
        
        Returns:
            List[Dict[str, Any]]: List of window information dictionaries
        """
        try:
            if not self._initialized:
                return []
            
            windows = []
            
            def enum_windows_callback(hwnd, _):
                if win32gui.IsWindowVisible(hwnd):
                    windows.append(self.get_window_info(str(hwnd)))
                return True
            
            win32gui.EnumWindows(enum_windows_callback, None)
            return windows
        except Exception as e:
            logging.error(f"Error getting window list: {e}")
            return []
    
    def get_window_info(self, window_id: str) -> Dict[str, Any]:
        """Get information about a specific window.
        
        Args:
            window_id: Window identifier
            
        Returns:
            Dict[str, Any]: Dictionary containing window information
        """
        try:
            if not self._initialized:
                return {'error': 'Handler not initialized'}
            
            hwnd = int(window_id)
            if not win32gui.IsWindow(hwnd):
                return {'error': 'Window not found'}
            
            rect = win32gui.GetWindowRect(hwnd)
            placement = win32gui.GetWindowPlacement(hwnd)
            
            # Get process name
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False, pid)
            process_name = win32process.GetModuleFileNameEx(process, 0)
            
            return {
                'id': window_id,
                'title': win32gui.GetWindowText(hwnd),
                'app': process_name,
                'bounds': {
                    'x': rect[0],
                    'y': rect[1],
                    'width': rect[2] - rect[0],
                    'height': rect[3] - rect[1]
                },
                'is_visible': win32gui.IsWindowVisible(hwnd),
                'is_minimized': placement[1] == win32con.SW_SHOWMINIMIZED,
                'is_maximized': placement[1] == win32con.SW_SHOWMAXIMIZED
            }
        except Exception as e:
            logging.error(f"Error getting window info for {window_id}: {e}")
            return {'error': str(e)}
    
    def get_active_window(self) -> Dict[str, Any]:
        """Get information about the currently active window.
        
        Returns:
            Dict[str, Any]: Dictionary containing active window information
        """
        try:
            if not self._initialized:
                return {'error': 'Handler not initialized'}
            
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                return {'error': 'No active window'}
            
            return self.get_window_info(str(hwnd))
        except Exception as e:
            logging.error(f"Error getting active window: {e}")
            return {'error': str(e)}
    
    def get_mouse_position(self) -> Tuple[int, int]:
        """Get current mouse cursor position.
        
        Returns:
            Tuple[int, int]: (x, y) coordinates of mouse cursor
        """
        try:
            if not self._initialized:
                return (0, 0)
            
            cursor_pos = win32gui.GetCursorPos()
            return cursor_pos
        except Exception as e:
            logging.error(f"Error getting mouse position: {e}")
            return (0, 0)
    
    def get_keyboard_layout(self) -> str:
        """Get current keyboard layout.
        
        Returns:
            str: Current keyboard layout identifier
        """
        try:
            if not self._initialized:
                return ''
            
            # Get keyboard layout ID
            layout_id = win32api.GetKeyboardLayout(0) & 0xFFFF
            return hex(layout_id)
        except Exception as e:
            logging.error(f"Error getting keyboard layout: {e}")
            return ''
    
    def get_clipboard_content(self) -> str:
        """Get current clipboard content.
        
        Returns:
            str: Current clipboard content
        """
        try:
            if not self._initialized:
                return ''
            
            win32clipboard.OpenClipboard()
            try:
                if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
                    return win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
                return ''
            finally:
                win32clipboard.CloseClipboard()
        except Exception as e:
            logging.error(f"Error getting clipboard content: {e}")
            return ''
    
    def set_clipboard_content(self, content: str) -> bool:
        """Set clipboard content.
        
        Args:
            content: Content to set in clipboard
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self._initialized:
                return False
            
            win32clipboard.OpenClipboard()
            try:
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardText(content, win32con.CF_UNICODETEXT)
                return True
            finally:
                win32clipboard.CloseClipboard()
        except Exception as e:
            logging.error(f"Error setting clipboard content: {e}")
            return False
    
    def get_ui_theme(self) -> Dict[str, Any]:
        """Get current UI theme information.
        
        Returns:
            Dict[str, Any]: Dictionary containing theme information
        """
        try:
            if not self._initialized:
                return {'error': 'Handler not initialized'}
            
            # Check if dark mode is enabled
            is_dark = False
            try:
                import winreg
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Themes\Personalize') as key:
                    is_dark = winreg.QueryValueEx(key, 'AppsUseLightTheme')[0] == 0
            except Exception:
                pass
            
            return {
                'name': 'Dark' if is_dark else 'Light',
                'is_dark': is_dark,
                'accent_color': self._get_accent_color()
            }
        except Exception as e:
            logging.error(f"Error getting UI theme: {e}")
            return {'error': str(e)}
    
    def get_ui_scale(self) -> float:
        """Get current UI scaling factor.
        
        Returns:
            float: Current UI scaling factor
        """
        try:
            if not self._initialized:
                return 1.0
            
            # Get DPI for primary monitor
            user32 = ctypes.windll.user32
            user32.SetProcessDPIAware()
            return user32.GetDpiForSystem() / 96.0
        except Exception as e:
            logging.error(f"Error getting UI scale: {e}")
            return 1.0
    
    def _get_accent_color(self) -> str:
        """Get current accent color.
        
        Returns:
            str: Current accent color name
        """
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\DWM') as key:
                color = winreg.QueryValueEx(key, 'ColorizationColor')[0]
                
                # Convert BGR to RGB and get color name
                r = color & 0xFF
                g = (color >> 8) & 0xFF
                b = (color >> 16) & 0xFF
                
                # Simple color mapping
                if r > g and r > b:
                    return 'Red'
                elif g > r and g > b:
                    return 'Green'
                elif b > r and b > g:
                    return 'Blue'
                elif r == g and g > b:
                    return 'Yellow'
                elif r == b and b > g:
                    return 'Purple'
                elif g == b and b > r:
                    return 'Cyan'
                else:
                    return 'Blue'
        except Exception as e:
            logging.error(f"Error getting accent color: {e}")
            return 'Blue' 