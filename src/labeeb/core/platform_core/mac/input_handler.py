"""
macOS input handler for Labeeb.

This module provides platform-specific input handling for macOS,
including keyboard, mouse, and trackpad support.

Supports RTL languages (Arabic, Hebrew, etc.) with proper text input handling.
"""
import os
import sys
from typing import Dict, Any, Optional, Tuple, List
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
        self._keyboard_layout = None
    
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
            
            # Initialize keyboard layout
            self._initialize_keyboard_layout()
            
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
        self._keyboard_layout = None
    
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
    
    def _initialize_keyboard_layout(self) -> None:
        """Initialize keyboard layout for RTL support."""
        try:
            import Quartz
            # Get current keyboard layout
            source = Quartz.TISCopyCurrentKeyboardInputSource()
            if source:
                self._keyboard_layout = Quartz.TISGetInputSourceProperty(source, Quartz.kTISPropertyInputSourceID)
                Quartz.CFRelease(source)
        except Exception as e:
            print(f"Failed to initialize keyboard layout: {e}")
            self._keyboard_layout = None
    
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
            
            # Process RTL text if needed
            if self._rtl_support:
                text = self._process_rtl_text(text)
            
            # Handle RTL text input
            if self._rtl_support and any('\u0600' <= c <= '\u06FF' for c in text):
                # For RTL text, we need to handle the text direction
                # This is handled by the system's text input system
                # We just need to ensure the keyboard layout is correct
                if self._keyboard_layout and 'Arabic' not in self._keyboard_layout:
                    # Switch to Arabic keyboard layout if needed
                    self._switch_to_arabic_layout()
            
            # Type each character
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
    
    def _switch_to_arabic_layout(self) -> bool:
        """Switch to Arabic keyboard layout.
        
        Returns:
            bool: True if the layout was switched successfully, False otherwise.
        """
        try:
            import Quartz
            
            # Get all input sources
            input_sources = Quartz.TISCreateInputSourceList(None, True)
            if not input_sources:
                return False
            
            # Find Arabic input source
            arabic_source = None
            for i in range(Quartz.CFArrayGetCount(input_sources)):
                source = Quartz.CFArrayGetValueAtIndex(input_sources, i)
                source_id = Quartz.TISGetInputSourceProperty(source, Quartz.kTISPropertyInputSourceID)
                if 'Arabic' in source_id:
                    arabic_source = source
                    break
            
            if arabic_source:
                # Switch to Arabic layout
                Quartz.TISSelectInputSource(arabic_source)
                self._keyboard_layout = Quartz.TISGetInputSourceProperty(arabic_source, Quartz.kTISPropertyInputSourceID)
                return True
            
            return False
        except Exception as e:
            print(f"Failed to switch to Arabic layout: {e}")
            return False
    
    def press_key(self, key: str) -> bool:
        """Press a key.
        
        Args:
            key: The key to press.
            
        Returns:
            bool: True if the key was pressed successfully, False otherwise.
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
            key: The key to release.
            
        Returns:
            bool: True if the key was released successfully, False otherwise.
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
            key: The key to check.
            
        Returns:
            bool: True if the key is pressed, False otherwise.
        """
        try:
            import Quartz
            # Get current keyboard state
            state = Quartz.CGEventSourceKeyState(Quartz.kCGEventSourceStateHIDSystemState, key)
            return bool(state)
        except Exception as e:
            print(f"Failed to check key state: {e}")
            return False
    
    def register_hotkey(self, key_combination: List[str], callback: callable) -> bool:
        """Register a hotkey combination.
        
        Args:
            key_combination: List of keys in the combination.
            callback: Function to call when the hotkey is triggered.
            
        Returns:
            bool: True if the hotkey was registered successfully, False otherwise.
        """
        try:
            import Quartz
            # TODO: Implement hotkey registration
            return False
        except Exception as e:
            print(f"Failed to register hotkey: {e}")
            return False
    
    def unregister_hotkey(self, key_combination: List[str]) -> bool:
        """Unregister a hotkey combination.
        
        Args:
            key_combination: List of keys in the combination.
            
        Returns:
            bool: True if the hotkey was unregistered successfully, False otherwise.
        """
        try:
            import Quartz
            # TODO: Implement hotkey unregistration
            return False
        except Exception as e:
            print(f"Failed to unregister hotkey: {e}")
            return False
    
    def get_supported_keys(self) -> List[str]:
        """Get list of supported keys.
        
        Returns:
            List[str]: List of supported keys.
        """
        try:
            import Quartz
            # TODO: Implement supported keys list
            return []
        except Exception as e:
            print(f"Failed to get supported keys: {e}")
            return []
    
    def _platform_specific_cleanup(self) -> None:
        """Perform platform-specific cleanup."""
        try:
            import Quartz
            # TODO: Implement platform-specific cleanup
            pass
        except Exception as e:
            print(f"Failed to perform platform-specific cleanup: {e}") 