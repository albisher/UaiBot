import logging
import subprocess
from typing import Any, Dict, List, Optional, Tuple

import Quartz
import AppKit
from ..base_ui_handler import BaseUIHandler

logger = logging.getLogger(__name__)

class MacOSUIHandler(BaseUIHandler):
    """macOS-specific UI handler implementation."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the macOS UI handler.
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(config)
    
    def initialize(self) -> bool:
        """Initialize the macOS UI handler.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            # macOS-specific initialization if needed
            self._initialized = True
            return True
        except Exception as e:
            logging.error(f"Failed to initialize macOS UI handler: {e}")
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
                'platform': 'macOS'
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
            for screen in Quartz.CGGetActiveDisplayList(10)[0]:
                bounds = Quartz.CGDisplayBounds(screen)
                mode = Quartz.CGDisplayCopyDisplayMode(screen)
                
                screens[str(screen)] = {
                    'id': str(screen),
                    'name': Quartz.CGDisplayGetDisplayIDFromUUID(screen),
                    'bounds': {
                        'x': bounds.origin.x,
                        'y': bounds.origin.y,
                        'width': bounds.size.width,
                        'height': bounds.size.height
                    },
                    'resolution': {
                        'width': Quartz.CGDisplayModeGetWidth(mode),
                        'height': Quartz.CGDisplayModeGetHeight(mode)
                    },
                    'scale': Quartz.CGDisplayModeGetPixelWidth(mode) / bounds.size.width,
                    'is_main': screen == Quartz.CGMainDisplayID()
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
            for app in AppKit.NSWorkspace.sharedWorkspace().runningApplications():
                if app.activationPolicy() == AppKit.NSApplicationActivationPolicyRegular:
                    for window in app.windows():
                        windows.append(self.get_window_info(str(window.windowNumber())))
            
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
            
            window = AppKit.NSApp.windowWithWindowNumber_(int(window_id))
            if not window:
                return {'error': 'Window not found'}
            
            frame = window.frame()
            return {
                'id': window_id,
                'title': window.title(),
                'app': window.app().localizedName(),
                'bounds': {
                    'x': frame.origin.x,
                    'y': frame.origin.y,
                    'width': frame.size.width,
                    'height': frame.size.height
                },
                'is_visible': window.isVisible(),
                'is_minimized': window.isMiniaturized(),
                'is_fullscreen': window.styleMask() & AppKit.NSFullScreenWindowMask != 0
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
            
            active_app = AppKit.NSWorkspace.sharedWorkspace().activeApplication()
            if not active_app:
                return {'error': 'No active application'}
            
            active_window = active_app.activeWindow()
            if not active_window:
                return {'error': 'No active window'}
            
            return self.get_window_info(str(active_window.windowNumber()))
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
            
            event = Quartz.CGEventGetCurrentLocation(Quartz.CGEventGetCurrent())
            return (int(event.x), int(event.y))
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
            
            # Use defaults to get keyboard layout
            result = subprocess.run(
                ['defaults', 'read', '~/Library/Preferences/com.apple.HIToolbox.plist', 'AppleCurrentKeyboardLayoutInputSourceID'],
                capture_output=True,
                text=True
            )
            
            return result.stdout.strip()
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
            
            return AppKit.NSPasteboard.generalPasteboard().stringForType_(AppKit.NSStringPboardType)
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
            
            pasteboard = AppKit.NSPasteboard.generalPasteboard()
            pasteboard.clearContents()
            return pasteboard.setString_forType_(content, AppKit.NSStringPboardType)
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
            
            # Use defaults to get theme
            result = subprocess.run(
                ['defaults', 'read', '-g', 'AppleInterfaceStyle'],
                capture_output=True,
                text=True
            )
            
            is_dark = result.stdout.strip() == 'Dark'
            
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
            
            main_screen = Quartz.CGMainDisplayID()
            mode = Quartz.CGDisplayCopyDisplayMode(main_screen)
            bounds = Quartz.CGDisplayBounds(main_screen)
            
            return Quartz.CGDisplayModeGetPixelWidth(mode) / bounds.size.width
        except Exception as e:
            logging.error(f"Error getting UI scale: {e}")
            return 1.0
    
    def _get_accent_color(self) -> str:
        """Get current accent color.
        
        Returns:
            str: Current accent color name
        """
        try:
            result = subprocess.run(
                ['defaults', 'read', '-g', 'AppleAccentColor'],
                capture_output=True,
                text=True
            )
            
            color_map = {
                '-1': 'Blue',
                '0': 'Red',
                '1': 'Orange',
                '2': 'Yellow',
                '3': 'Green',
                '4': 'Purple',
                '5': 'Pink'
            }
            
            return color_map.get(result.stdout.strip(), 'Blue')
        except Exception as e:
            logging.error(f"Error getting accent color: {e}")
            return 'Blue' 