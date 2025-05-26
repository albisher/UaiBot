"""Base input handler for UaiBot."""

from abc import ABC, abstractmethod
from typing import Tuple, List, Optional, Callable
import logging

logger = logging.getLogger(__name__)

class InputHandler(ABC):
    """Base class for platform-specific input handlers."""
    
    def __init__(self):
        """Initialize the input handler."""
        self._platform_specific_init()
    
    @abstractmethod
    def _platform_specific_init(self) -> None:
        """Initialize platform-specific input handling."""
        pass
    
    @abstractmethod
    def click_mouse(self, x: int, y: int, button: str = 'left') -> bool:
        """Click the mouse at the specified coordinates.
        
        Args:
            x: X coordinate.
            y: Y coordinate.
            button: Mouse button ('left', 'right', 'middle').
            
        Returns:
            True if successful, False otherwise.
        """
        pass
    
    @abstractmethod
    def move_mouse(self, x: int, y: int) -> bool:
        """Move the mouse to the specified coordinates.
        
        Args:
            x: X coordinate.
            y: Y coordinate.
            
        Returns:
            True if successful, False otherwise.
        """
        pass
    
    @abstractmethod
    def get_mouse_position(self) -> Tuple[int, int]:
        """Get the current mouse position.
        
        Returns:
            Tuple of (x, y) coordinates.
        """
        pass
    
    @abstractmethod
    def press_key(self, key: str) -> bool:
        """Press a key.
        
        Args:
            key: Key to press.
            
        Returns:
            True if successful, False otherwise.
        """
        pass
    
    @abstractmethod
    def release_key(self, key: str) -> bool:
        """Release a key.
        
        Args:
            key: Key to release.
            
        Returns:
            True if successful, False otherwise.
        """
        pass
    
    @abstractmethod
    def is_key_pressed(self, key: str) -> bool:
        """Check if a key is pressed.
        
        Args:
            key: Key to check.
            
        Returns:
            True if the key is pressed, False otherwise.
        """
        pass
    
    @abstractmethod
    def type_text(self, text: str) -> bool:
        """Type the specified text.
        
        Args:
            text: Text to type.
            
        Returns:
            True if successful, False otherwise.
        """
        pass
    
    @abstractmethod
    def register_hotkey(self, key_combination: List[str], callback: Callable) -> bool:
        """Register a hotkey combination.
        
        Args:
            key_combination: List of keys that form the hotkey.
            callback: Function to call when the hotkey is pressed.
            
        Returns:
            True if successful, False otherwise.
        """
        pass
    
    @abstractmethod
    def unregister_hotkey(self, key_combination: List[str]) -> bool:
        """Unregister a hotkey combination.
        
        Args:
            key_combination: List of keys that form the hotkey.
            
        Returns:
            True if successful, False otherwise.
        """
        pass
    
    @abstractmethod
    def get_supported_keys(self) -> List[str]:
        """Get list of supported keys.
        
        Returns:
            List of supported key names.
        """
        pass
    
    def cleanup(self) -> None:
        """Clean up resources."""
        try:
            self._platform_specific_cleanup()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    @abstractmethod
    def _platform_specific_cleanup(self) -> None:
        """Clean up platform-specific resources."""
        pass 