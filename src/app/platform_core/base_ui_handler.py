from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

class BaseUIHandler(ABC):
    """Base class for platform-specific UI handlers"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the handler with optional configuration
        
        Args:
            config: Optional configuration dictionary
        """
        self._config = config or {}
        self._initialized = False
        
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the handler
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        pass
        
    @abstractmethod
    def cleanup(self) -> None:
        """Clean up resources used by the handler"""
        pass
        
    @abstractmethod
    def get_capabilities(self) -> Dict[str, bool]:
        """Get the capabilities of this handler
        
        Returns:
            Dict[str, bool]: Dictionary of capability names and their availability
        """
        pass
        
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the handler
        
        Returns:
            Dict[str, Any]: Dictionary containing status information
        """
        pass
        
    @abstractmethod
    def get_screen_info(self) -> Dict[str, Any]:
        """Get information about all screens/displays
        
        Returns:
            Dict[str, Any]: Dictionary containing screen information
        """
        pass
        
    @abstractmethod
    def get_window_list(self) -> List[Dict[str, Any]]:
        """Get list of all windows
        
        Returns:
            List[Dict[str, Any]]: List of window information dictionaries
        """
        pass
        
    @abstractmethod
    def get_window_info(self, window_id: str) -> Dict[str, Any]:
        """Get information about a specific window
        
        Args:
            window_id: Window identifier
            
        Returns:
            Dict[str, Any]: Dictionary containing window information
        """
        pass
        
    @abstractmethod
    def get_active_window(self) -> Dict[str, Any]:
        """Get information about the currently active window
        
        Returns:
            Dict[str, Any]: Dictionary containing active window information
        """
        pass
        
    @abstractmethod
    def get_mouse_position(self) -> Tuple[int, int]:
        """Get current mouse cursor position
        
        Returns:
            Tuple[int, int]: (x, y) coordinates of mouse cursor
        """
        pass
        
    @abstractmethod
    def get_keyboard_layout(self) -> str:
        """Get current keyboard layout
        
        Returns:
            str: Current keyboard layout identifier
        """
        pass
        
    @abstractmethod
    def get_clipboard_content(self) -> str:
        """Get current clipboard content
        
        Returns:
            str: Current clipboard content
        """
        pass
        
    @abstractmethod
    def set_clipboard_content(self, content: str) -> bool:
        """Set clipboard content
        
        Args:
            content: Content to set in clipboard
            
        Returns:
            bool: True if successful, False otherwise
        """
        pass
        
    @abstractmethod
    def get_ui_theme(self) -> Dict[str, Any]:
        """Get current UI theme information
        
        Returns:
            Dict[str, Any]: Dictionary containing theme information
        """
        pass
        
    @abstractmethod
    def get_ui_scale(self) -> float:
        """Get current UI scaling factor
        
        Returns:
            float: Current UI scaling factor
        """
        pass
        
    def is_initialized(self) -> bool:
        """Check if the handler is initialized
        
        Returns:
            bool: True if initialized, False otherwise
        """
        return self._initialized
        
    def get_config(self) -> Dict[str, Any]:
        """Get the current configuration
        
        Returns:
            Dict[str, Any]: Current configuration dictionary
        """
        return self._config.copy()
        
    def update_config(self, new_config: Dict[str, Any]) -> None:
        """Update the configuration
        
        Args:
            new_config: New configuration dictionary
        """
        self._config.update(new_config) 