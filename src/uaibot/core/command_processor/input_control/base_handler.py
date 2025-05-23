#!/usr/bin/env python3
"""
Base input handler for cross-platform mouse and keyboard control.

This module provides the abstract base class for platform-specific input handlers.
Platform-specific implementations should inherit from and extend this class.
"""
from .abc import ABC, abstractmethod
from typing import Tuple, Union, Optional, Any, Callable

class BaseInputHandler(ABC):
    """
    Abstract base class for platform-specific input handlers.
    
    This class defines the common interface that all platform-specific
    input handlers must implement.
    """
    
    @abstractmethod
    def get_mouse_position(self) -> Tuple[int, int]:
        """
        Get the current mouse position.
        
        Returns:
            tuple: (x, y) coordinates
        """
        pass
    
    @abstractmethod
    def get_screen_size(self) -> Tuple[int, int]:
        """
        Get the screen size.
        
        Returns:
            tuple: (width, height) in pixels
        """
        pass
    
    @abstractmethod
    def move_mouse(self, x: int, y: int, duration: float = 0.25) -> bool:
        """
        Move the mouse to the specified coordinates.
        
        Args:
            x: X-coordinate
            y: Y-coordinate
            duration: Time to take for the movement in seconds
        
        Returns:
            bool: Success status
        """
        pass
    
    @abstractmethod
    def move_mouse_relative(self, xOffset: int, yOffset: int, duration: float = 0.25) -> bool:
        """
        Move the mouse relative to its current position.
        
        Args:
            xOffset: X offset from current position
            yOffset: Y offset from current position
            duration: Time to take for the movement in seconds
        
        Returns:
            bool: Success status
        """
        pass
    
    @abstractmethod
    def click(self, x: Optional[int] = None, y: Optional[int] = None, 
              button: str = 'left', clicks: int = 1, interval: float = 0.0) -> bool:
        """
        Click the mouse at the specified position or current position.
        
        Args:
            x: X-coordinate. If None, uses current position.
            y: Y-coordinate. If None, uses current position.
            button: 'left', 'middle', or 'right'
            clicks: Number of clicks
            interval: Time between clicks in seconds
        
        Returns:
            bool: Success status
        """
        pass
    
    @abstractmethod
    def type_text(self, text: str, interval: float = 0.0) -> bool:
        """
        Type text with optional delay between characters.
        
        Args:
            text: Text to type
            interval: Delay between characters in seconds
        
        Returns:
            bool: Success status
        """
        pass
    
    @abstractmethod
    def press_key(self, key: str) -> bool:
        """
        Press and release a key.
        
        Args:
            key: Key to press (e.g., 'enter', 'esc', 'space', 'a')
        
        Returns:
            bool: Success status
        """
        pass
    
    @abstractmethod
    def hotkey(self, *keys) -> bool:
        """
        Press multiple keys simultaneously.
        
        Args:
            *keys: Keys to press simultaneously
        
        Returns:
            bool: Success status
        """
        pass
    
    @abstractmethod
    def screenshot(self, filename: Optional[str] = None, 
                  region: Optional[Tuple[int, int, int, int]] = None) -> Union[object, bool]:
        """
        Take a screenshot.
        
        Args:
            filename: Path to save the screenshot
            region: Region to capture (left, top, width, height)
        
        Returns:
            Image or bool: Image object if successful and no filename, otherwise bool success status
        """
        pass
    
    @abstractmethod
    def is_simulation_mode(self) -> bool:
        """
        Check if the handler is in simulation mode.
        
        Returns:
            bool: True if in simulation mode, False otherwise
        """
        pass
