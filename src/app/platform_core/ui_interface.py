import logging
import sys
from typing import Any, Dict, List, Optional, Tuple

from .base_ui_handler import BaseUIHandler
from .macos.ui_handler import MacOSUIHandler
from .windows.ui_handler import WindowsUIHandler
from .linux.ui_handler import LinuxUIHandler

logger = logging.getLogger(__name__)

class UIInterface:
    """Platform-agnostic UI interface that manages platform-specific handlers."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the UI interface.
        
        Args:
            config: Optional configuration dictionary
        """
        self._handler: Optional[BaseUIHandler] = None
        self._config = config or {}
        self._initialize_handler()
    
    def _initialize_handler(self) -> None:
        """Initialize the appropriate platform-specific handler."""
        try:
            if sys.platform == 'darwin':
                self._handler = MacOSUIHandler(self._config)
            elif sys.platform == 'win32':
                self._handler = WindowsUIHandler(self._config)
            elif sys.platform.startswith('linux'):
                self._handler = LinuxUIHandler(self._config)
            else:
                raise RuntimeError(f"Unsupported platform: {sys.platform}")
            
            if not self._handler.initialize():
                raise RuntimeError("Failed to initialize UI handler")
        except Exception as e:
            logger.error(f"Error initializing UI handler: {e}")
            raise
    
    def get_screen_info(self) -> Dict[str, Any]:
        """Get information about all screens/displays.
        
        Returns:
            Dict[str, Any]: Dictionary containing screen information
        """
        if not self._handler:
            return {'error': 'Handler not initialized'}
        return self._handler.get_screen_info()
    
    def get_window_list(self) -> List[Dict[str, Any]]:
        """Get list of all windows.
        
        Returns:
            List[Dict[str, Any]]: List of window information dictionaries
        """
        if not self._handler:
            return []
        return self._handler.get_window_list()
    
    def get_window_info(self, window_id: str) -> Dict[str, Any]:
        """Get information about a specific window.
        
        Args:
            window_id: Window identifier
            
        Returns:
            Dict[str, Any]: Dictionary containing window information
        """
        if not self._handler:
            return {'error': 'Handler not initialized'}
        return self._handler.get_window_info(window_id)
    
    def get_active_window(self) -> Dict[str, Any]:
        """Get information about the currently active window.
        
        Returns:
            Dict[str, Any]: Dictionary containing active window information
        """
        if not self._handler:
            return {'error': 'Handler not initialized'}
        return self._handler.get_active_window()
    
    def get_mouse_position(self) -> Tuple[int, int]:
        """Get current mouse cursor position.
        
        Returns:
            Tuple[int, int]: (x, y) coordinates of mouse cursor
        """
        if not self._handler:
            return (0, 0)
        return self._handler.get_mouse_position()
    
    def get_keyboard_layout(self) -> str:
        """Get current keyboard layout.
        
        Returns:
            str: Current keyboard layout identifier
        """
        if not self._handler:
            return ''
        return self._handler.get_keyboard_layout()
    
    def get_clipboard_content(self) -> str:
        """Get current clipboard content.
        
        Returns:
            str: Current clipboard content
        """
        if not self._handler:
            return ''
        return self._handler.get_clipboard_content()
    
    def set_clipboard_content(self, content: str) -> bool:
        """Set clipboard content.
        
        Args:
            content: Content to set in clipboard
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self._handler:
            return False
        return self._handler.set_clipboard_content(content)
    
    def get_ui_theme(self) -> Dict[str, Any]:
        """Get current UI theme information.
        
        Returns:
            Dict[str, Any]: Dictionary containing theme information
        """
        if not self._handler:
            return {'error': 'Handler not initialized'}
        return self._handler.get_ui_theme()
    
    def get_ui_scale(self) -> float:
        """Get current UI scaling factor.
        
        Returns:
            float: Current UI scaling factor
        """
        if not self._handler:
            return 1.0
        return self._handler.get_ui_scale()
    
    def get_status(self) -> Dict[str, Any]:
        """Get current UI status.
        
        Returns:
            Dict[str, Any]: Dictionary containing UI status information
        """
        if not self._handler:
            return {'error': 'Handler not initialized'}
        return self._handler.get_status()
    
    def get_capabilities(self) -> Dict[str, bool]:
        """Get UI capabilities.
        
        Returns:
            Dict[str, bool]: Dictionary of available UI capabilities
        """
        if not self._handler:
            return {}
        return self._handler.get_capabilities()
    
    def cleanup(self) -> None:
        """Clean up UI resources."""
        if self._handler:
            self._handler.cleanup()
            self._handler = None 