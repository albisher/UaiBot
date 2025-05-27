"""
Base input control handler for Labeeb.

This module provides the base class for platform-specific input control handlers.
It defines the interface that all input handlers must implement.
"""
from abc import ABC, abstractmethod
from typing import Tuple, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class InputEvent:
    """Data class for storing input events."""
    event_type: str
    x: Optional[int] = None
    y: Optional[int] = None
    button: Optional[str] = None
    key: Optional[str] = None
    modifiers: Optional[Dict[str, bool]] = None
    timestamp: datetime = datetime.now()

class BaseInputHandler(ABC):
    """
    Base class for platform-specific input handlers.
    
    This class defines the interface that all input handlers must implement.
    It provides abstract methods for mouse and keyboard control that must be
    implemented by platform-specific handlers.
    """
    
    @abstractmethod
    def move_mouse(self, x: int, y: int) -> None:
        """
        Move the mouse cursor to the specified coordinates.
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate
        """
        pass
    
    @abstractmethod
    def click_mouse(self, button: str = "left") -> None:
        """
        Click the specified mouse button.
        
        Args:
            button (str): Mouse button to click ("left", "right", "middle")
        """
        pass
    
    @abstractmethod
    def press_key(self, key: str) -> None:
        """
        Press a keyboard key.
        
        Args:
            key (str): Key to press
        """
        pass
    
    @abstractmethod
    def release_key(self, key: str) -> None:
        """
        Release a keyboard key.
        
        Args:
            key (str): Key to release
        """
        pass
    
    @abstractmethod
    def get_mouse_position(self) -> Tuple[int, int]:
        """
        Get the current mouse position.
        
        Returns:
            Tuple[int, int]: Current (x, y) coordinates of the mouse cursor
        """
        pass
    
    @abstractmethod
    def is_key_pressed(self, key: str) -> bool:
        """
        Check if a key is currently pressed.
        
        Args:
            key (str): Key to check
            
        Returns:
            bool: True if the key is pressed, False otherwise
        """
        pass
    
    @abstractmethod
    def simulate_input(self, event: InputEvent) -> None:
        """
        Simulate an input event.
        
        Args:
            event (InputEvent): The input event to simulate
        """
        pass 