from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple

class UIInterface(ABC):
    """Interface for UI-related operations."""
    
    @abstractmethod
    def get_screen_size(self) -> Tuple[int, int]:
        """Get screen dimensions."""
        pass
    
    @abstractmethod
    def get_window_list(self) -> List[Dict[str, str]]:
        """Get list of open windows."""
        pass
    
    @abstractmethod
    def get_active_window(self) -> Dict[str, str]:
        """Get information about the active window."""
        pass
    
    @abstractmethod
    def set_window_focus(self, window_id: str) -> bool:
        """Set focus to a specific window."""
        pass
    
    @abstractmethod
    def get_mouse_position(self) -> Tuple[int, int]:
        """Get current mouse position."""
        pass
    
    @abstractmethod
    def set_mouse_position(self, x: int, y: int) -> bool:
        """Set mouse position."""
        pass
    
    @abstractmethod
    def click_mouse(self, button: str = 'left') -> bool:
        """Perform mouse click."""
        pass
    
    @abstractmethod
    def type_text(self, text: str) -> bool:
        """Type text using keyboard."""
        pass
    
    @abstractmethod
    def press_key(self, key: str) -> bool:
        """Press a specific key."""
        pass
    
    @abstractmethod
    def take_screenshot(self, region: Optional[Tuple[int, int, int, int]] = None) -> bytes:
        """Take a screenshot of the screen or a specific region."""
        pass 