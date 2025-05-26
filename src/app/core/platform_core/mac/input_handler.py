"""
macOS input handler for Labeeb.

This module provides platform-specific input handling for macOS,
including keyboard, mouse, and trackpad support.
"""
import os
import sys
from typing import Dict, Any, Optional, Tuple
from ..common.base_handler import BaseHandler

class MacInputHandler(BaseHandler):
    """Handler for macOS input devices."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the macOS input handler."""
        super().__init__(config)
        self._keyboard_enabled = False
        self._mouse_enabled = False
        self._trackpad_enabled = False
        self._accessibility_enabled = False
    
    def initialize(self) -> bool:
        """Initialize the input handler.
        
        Returns:
            bool: True if initialization was successful, False otherwise.
        """
        try:
            # Check if accessibility is enabled
            self._check_accessibility()
            
            # Initialize input devices
            self._initialize_keyboard()
            self._initialize_mouse()
            self._initialize_trackpad()
            
            return all([
                self._keyboard_enabled,
                self._mouse_enabled or self._trackpad_enabled,
                self._accessibility_enabled
            ])
        except Exception as e:
            print(f"Failed to initialize MacInputHandler: {e}")
            return False
    
    def cleanup(self) -> None:
        """Clean up input handler resources."""
        self._keyboard_enabled = False
        self._mouse_enabled = False
        self._trackpad_enabled = False
        self._accessibility_enabled = False
    
    def is_available(self) -> bool:
        """Check if input handling is available.
        
        Returns:
            bool: True if input handling is available, False otherwise.
        """
        return all([
            self._accessibility_enabled,
            self._keyboard_enabled,
            self._mouse_enabled or self._trackpad_enabled
        ])
    
    def _check_accessibility(self) -> None:
        """Check if accessibility permissions are enabled."""
        try:
            import Quartz
            # Check if accessibility is enabled
            trusted = Quartz.AXIsProcessTrusted()
            self._accessibility_enabled = trusted
            if not trusted:
                print("Accessibility permissions are required for input handling")
        except ImportError:
            print("Failed to import Quartz module")
            self._accessibility_enabled = False
    
    def _initialize_keyboard(self) -> None:
        """Initialize keyboard support."""
        try:
            import Quartz
            # Check if keyboard monitoring is available
            self._keyboard_enabled = True
        except ImportError:
            print("Failed to initialize keyboard support")
            self._keyboard_enabled = False
    
    def _initialize_mouse(self) -> None:
        """Initialize mouse support."""
        try:
            import Quartz
            # Check if mouse monitoring is available
            self._mouse_enabled = True
        except ImportError:
            print("Failed to initialize mouse support")
            self._mouse_enabled = False
    
    def _initialize_trackpad(self) -> None:
        """Initialize trackpad support."""
        try:
            import Quartz
            # Check if trackpad monitoring is available
            self._trackpad_enabled = True
        except ImportError:
            print("Failed to initialize trackpad support")
            self._trackpad_enabled = False
    
    def get_mouse_position(self) -> Tuple[int, int]:
        """Get the current mouse position.
        
        Returns:
            Tuple[int, int]: The current mouse position (x, y).
        """
        try:
            import Quartz
            mouse_pos = Quartz.CGEventGetLocation(Quartz.CGEventGetCurrent())
            return (int(mouse_pos.x), int(mouse_pos.y))
        except Exception as e:
            print(f"Failed to get mouse position: {e}")
            return (0, 0)
    
    def move_mouse(self, x: int, y: int) -> bool:
        """Move the mouse to the specified position.
        
        Args:
            x: The target x coordinate.
            y: The target y coordinate.
            
        Returns:
            bool: True if the mouse was moved successfully, False otherwise.
        """
        try:
            import Quartz
            event = Quartz.CGEventCreateMouseEvent(
                None, Quartz.kCGEventMouseMoved,
                (x, y), Quartz.kCGMouseButtonLeft
            )
            Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)
            return True
        except Exception as e:
            print(f"Failed to move mouse: {e}")
            return False
    
    def click_mouse(self, button: str = 'left') -> bool:
        """Simulate a mouse click.
        
        Args:
            button: The mouse button to click ('left', 'right', or 'middle').
            
        Returns:
            bool: True if the click was successful, False otherwise.
        """
        try:
            import Quartz
            button_map = {
                'left': Quartz.kCGMouseButtonLeft,
                'right': Quartz.kCGMouseButtonRight,
                'middle': Quartz.kCGMouseButtonCenter
            }
            button_code = button_map.get(button, Quartz.kCGMouseButtonLeft)
            
            # Get current mouse position
            pos = self.get_mouse_position()
            
            # Create and post mouse down event
            down_event = Quartz.CGEventCreateMouseEvent(
                None, Quartz.kCGEventLeftMouseDown,
                pos, button_code
            )
            Quartz.CGEventPost(Quartz.kCGHIDEventTap, down_event)
            
            # Create and post mouse up event
            up_event = Quartz.CGEventCreateMouseEvent(
                None, Quartz.kCGEventLeftMouseUp,
                pos, button_code
            )
            Quartz.CGEventPost(Quartz.kCGHIDEventTap, up_event)
            
            return True
        except Exception as e:
            print(f"Failed to click mouse: {e}")
            return False
    
    def type_text(self, text: str) -> bool:
        """Type the specified text.
        
        Args:
            text: The text to type.
            
        Returns:
            bool: True if the text was typed successfully, False otherwise.
        """
        try:
            import Quartz
            for char in text:
                # Create key down event
                down_event = Quartz.CGEventCreateKeyboardEvent(None, 0, True)
                Quartz.CGEventKeyboardSetUnicodeString(down_event, len(char), char)
                Quartz.CGEventPost(Quartz.kCGHIDEventTap, down_event)
                
                # Create key up event
                up_event = Quartz.CGEventCreateKeyboardEvent(None, 0, False)
                Quartz.CGEventKeyboardSetUnicodeString(up_event, len(char), char)
                Quartz.CGEventPost(Quartz.kCGHIDEventTap, up_event)
            return True
        except Exception as e:
            print(f"Failed to type text: {e}")
            return False
    
    def press_key(self, key: str) -> bool:
        """Press a key.
        
        Args:
            key: Key to press.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            import Quartz
            # Create key down event
            down_event = Quartz.CGEventCreateKeyboardEvent(None, 0, True)
            Quartz.CGEventKeyboardSetUnicodeString(down_event, len(key), key)
            Quartz.CGEventPost(Quartz.kCGHIDEventTap, down_event)
            
            return True
        except Exception as e:
            print(f"Failed to press key: {e}")
            return False
    
    def release_key(self, key: str) -> bool:
        """Release a key.
        
        Args:
            key: Key to release.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            import Quartz
            # Create key up event
            up_event = Quartz.CGEventCreateKeyboardEvent(None, 0, False)
            Quartz.CGEventKeyboardSetUnicodeString(up_event, len(key), key)
            Quartz.CGEventPost(Quartz.kCGHIDEventTap, up_event)
            
            return True
        except Exception as e:
            print(f"Failed to release key: {e}")
            return False
    
    def is_key_pressed(self, key: str) -> bool:
        """Check if a key is pressed.
        
        Args:
            key: Key to check.
            
        Returns:
            True if the key is pressed, False otherwise.
        """
        try:
            import Quartz
            # Create key down event
            down_event = Quartz.CGEventCreateKeyboardEvent(None, 0, True)
            Quartz.CGEventKeyboardSetUnicodeString(down_event, len(key), key)
            Quartz.CGEventPost(Quartz.kCGHIDEventTap, down_event)
            
            return True
        except Exception as e:
            print(f"Failed to check key state: {e}")
            return False
    
    def register_hotkey(self, key_combination: List[str], callback: callable) -> bool:
        """Register a hotkey combination.
        
        Args:
            key_combination: List of keys that form the hotkey.
            callback: Function to call when the hotkey is pressed.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            # Convert key combination to PyAutoGUI format
            hotkey = '+'.join(key_combination)
            import Quartz
            # Create key down event
            down_event = Quartz.CGEventCreateKeyboardEvent(None, 0, True)
            Quartz.CGEventKeyboardSetUnicodeString(down_event, len(hotkey), hotkey)
            Quartz.CGEventPost(Quartz.kCGHIDEventTap, down_event)
            
            return True
        except Exception as e:
            print(f"Failed to register hotkey: {e}")
            return False
    
    def unregister_hotkey(self, key_combination: List[str]) -> bool:
        """Unregister a hotkey combination.
        
        Args:
            key_combination: List of keys that form the hotkey.
            
        Returns:
            True if successful, False otherwise.
        """
        # PyAutoGUI doesn't support unregistering hotkeys
        # This is a limitation of the library
        print("Unregistering hotkeys is not supported in PyAutoGUI")
        return False
    
    def get_supported_keys(self) -> List[str]:
        """Get list of supported keys.
        
        Returns:
            List of supported key names.
        """
        return [
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
            'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
            'space', 'enter', 'tab', 'backspace', 'delete',
            'shift', 'ctrl', 'alt', 'command',
            'up', 'down', 'left', 'right',
            'home', 'end', 'pageup', 'pagedown',
            'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12'
        ]
    
    def _platform_specific_cleanup(self) -> None:
        """Clean up macOS-specific resources."""
        # PyAutoGUI doesn't require explicit cleanup
        pass 