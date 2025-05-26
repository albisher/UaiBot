import logging
import subprocess
import json
import re
from typing import Any, Dict, List, Optional, Tuple

import Xlib
import Xlib.display
from ..base_ui_handler import BaseUIHandler

logger = logging.getLogger(__name__)

class LinuxUIHandler(BaseUIHandler):
    """Linux-specific UI handler implementation."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the Linux UI handler.
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(config)
        self._display = None
    
    def initialize(self) -> bool:
        """Initialize the Linux UI handler.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            self._display = Xlib.display.Display()
            self._initialized = True
            return True
        except Exception as e:
            logging.error(f"Failed to initialize Linux UI handler: {e}")
            return False
    
    def cleanup(self) -> None:
        """Clean up UI resources."""
        if self._display:
            self._display.close()
        self._display = None
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
                'platform': 'Linux'
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
            
            # Use xrandr to get screen information
            result = subprocess.run(['xrandr', '--query'], capture_output=True, text=True)
            current_screen = None
            
            for line in result.stdout.splitlines():
                if ' connected ' in line:
                    # New screen
                    parts = line.split()
                    current_screen = parts[0]
                    screens[current_screen] = {
                        'id': current_screen,
                        'name': current_screen,
                        'bounds': {
                            'x': 0,
                            'y': 0,
                            'width': 0,
                            'height': 0
                        },
                        'is_main': len(screens) == 0
                    }
                elif current_screen and 'x' in line:
                    # Resolution information
                    match = re.search(r'(\d+)x(\d+)', line)
                    if match:
                        screens[current_screen]['bounds']['width'] = int(match.group(1))
                        screens[current_screen]['bounds']['height'] = int(match.group(2))
            
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
            root = self._display.screen().root
            
            # Get all window IDs
            window_ids = root.get_full_property(
                self._display.intern_atom('_NET_CLIENT_LIST'),
                Xlib.X.AnyPropertyType
            ).value
            
            for window_id in window_ids:
                windows.append(self.get_window_info(str(window_id)))
            
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
            
            window = self._display.create_resource_object('window', int(window_id))
            
            # Get window attributes
            attrs = window.get_attributes()
            geometry = window.get_geometry()
            
            # Get window name
            name = window.get_wm_name() or ''
            
            # Get window class
            wm_class = window.get_wm_class()
            app_name = wm_class[0] if wm_class else ''
            
            return {
                'id': window_id,
                'title': name,
                'app': app_name,
                'bounds': {
                    'x': geometry.x,
                    'y': geometry.y,
                    'width': geometry.width,
                    'height': geometry.height
                },
                'is_visible': attrs.map_state == Xlib.X.IsViewable,
                'is_minimized': False,  # X11 doesn't have a direct way to check this
                'is_fullscreen': False  # Would need to check _NET_WM_STATE
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
            
            root = self._display.screen().root
            active_window = root.get_full_property(
                self._display.intern_atom('_NET_ACTIVE_WINDOW'),
                Xlib.X.AnyPropertyType
            ).value[0]
            
            if not active_window:
                return {'error': 'No active window'}
            
            return self.get_window_info(str(active_window))
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
            
            root = self._display.screen().root
            pointer = root.query_pointer()
            return (pointer.root_x, pointer.root_y)
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
            
            # Use setxkbmap to get current layout
            result = subprocess.run(
                ['setxkbmap', '-query'],
                capture_output=True,
                text=True
            )
            
            for line in result.stdout.splitlines():
                if line.startswith('layout:'):
                    return line.split(':')[1].strip()
            
            return ''
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
            
            # Use xclip to get clipboard content
            result = subprocess.run(
                ['xclip', '-o', '-selection', 'clipboard'],
                capture_output=True,
                text=True
            )
            
            return result.stdout
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
            
            # Use xclip to set clipboard content
            subprocess.run(
                ['xclip', '-i', '-selection', 'clipboard'],
                input=content.encode(),
                check=True
            )
            return True
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
            
            # Try to get theme from gsettings
            try:
                result = subprocess.run(
                    ['gsettings', 'get', 'org.gnome.desktop.interface', 'gtk-theme'],
                    capture_output=True,
                    text=True
                )
                theme_name = result.stdout.strip().strip("'")
                is_dark = 'dark' in theme_name.lower()
            except Exception:
                theme_name = 'Unknown'
                is_dark = False
            
            return {
                'name': theme_name,
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
            
            # Try to get scale from gsettings
            try:
                result = subprocess.run(
                    ['gsettings', 'get', 'org.gnome.desktop.interface', 'scaling-factor'],
                    capture_output=True,
                    text=True
                )
                return float(result.stdout.strip())
            except Exception:
                return 1.0
        except Exception as e:
            logging.error(f"Error getting UI scale: {e}")
            return 1.0
    
    def _get_accent_color(self) -> str:
        """Get current accent color.
        
        Returns:
            str: Current accent color name
        """
        try:
            # Try to get accent color from gsettings
            result = subprocess.run(
                ['gsettings', 'get', 'org.gnome.desktop.interface', 'color-scheme'],
                capture_output=True,
                text=True
            )
            
            color_scheme = result.stdout.strip().strip("'")
            if 'prefer-dark' in color_scheme:
                return 'Blue'  # Default dark theme accent
            return 'Blue'  # Default light theme accent
        except Exception as e:
            logging.error(f"Error getting accent color: {e}")
            return 'Blue' 