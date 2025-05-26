"""macOS-specific input handler implementation."""

import pyautogui
from typing import Tuple, List, Optional
import logging
from uaibot.platform_uai.common.input_handler import InputHandler

logger = logging.getLogger(__name__)

class MacInputHandler(InputHandler):
    """macOS-specific input handler implementation."""
    
    def _platform_specific_init(self) -> None:
        """Initialize macOS-specific input handling."""
        # Configure PyAutoGUI for macOS
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
    
    def click_mouse(self, x: int, y: int, button: str = 'left') -> bool:
        """Click the mouse at the specified coordinates.
        
        Args:
            x: X coordinate.
            y: Y coordinate.
            button: Mouse button ('left', 'right', 'middle').
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            pyautogui.click(x=x, y=y, button=button)
            return True
        except Exception as e:
            logger.error(f"Failed to click mouse: {e}")
            return False
    
    def move_mouse(self, x: int, y: int) -> bool:
        """Move the mouse to the specified coordinates.
        
        Args:
            x: X coordinate.
            y: Y coordinate.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            pyautogui.moveTo(x, y)
            return True
        except Exception as e:
            logger.error(f"Failed to move mouse: {e}")
            return False
    
    def get_mouse_position(self) -> Tuple[int, int]:
        """Get the current mouse position.
        
        Returns:
            Tuple of (x, y) coordinates.
        """
        try:
            return pyautogui.position()
        except Exception as e:
            logger.error(f"Failed to get mouse position: {e}")
            return (0, 0)
    
    def press_key(self, key: str) -> bool:
        """Press a key.
        
        Args:
            key: Key to press.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            pyautogui.keyDown(key)
            return True
        except Exception as e:
            logger.error(f"Failed to press key: {e}")
            return False
    
    def release_key(self, key: str) -> bool:
        """Release a key.
        
        Args:
            key: Key to release.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            pyautogui.keyUp(key)
            return True
        except Exception as e:
            logger.error(f"Failed to release key: {e}")
            return False
    
    def is_key_pressed(self, key: str) -> bool:
        """Check if a key is pressed.
        
        Args:
            key: Key to check.
            
        Returns:
            True if the key is pressed, False otherwise.
        """
        try:
            return pyautogui.isKeyDown(key)
        except Exception as e:
            logger.error(f"Failed to check key state: {e}")
            return False
    
    def type_text(self, text: str) -> bool:
        """Type the specified text.
        
        Args:
            text: Text to type.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            pyautogui.write(text)
            return True
        except Exception as e:
            logger.error(f"Failed to type text: {e}")
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
            pyautogui.hotkey(hotkey, callback)
            return True
        except Exception as e:
            logger.error(f"Failed to register hotkey: {e}")
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
        logger.warning("Unregistering hotkeys is not supported in PyAutoGUI")
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