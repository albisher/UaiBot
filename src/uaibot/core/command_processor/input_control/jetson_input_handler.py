#!/usr/bin/env python3
"""
Jetson-specific input handler implementation for mouse and keyboard control.
"""
import os
import sys
import time
from typing import Tuple, Optional, Union, Any, List

from ...common.input_control.base_handler import BaseInputHandler

class JetsonInputHandler(BaseInputHandler):
    """
    Jetson-specific implementation of the input handler.
    Uses PyAutoGUI with X11 support, optimized for Jetson devices.
    """
    
    def __init__(self):
        """Initialize the Jetson input handler."""
        self.pyautogui = None
        self.keyboard = None
        self.mouse = None
        self.screen_size = (1920, 1080)  # Default size if detection fails
        self.mouse_position = (0, 0)     # Default position if detection fails
        self._simulate_only = False
        
        self._check_dependencies()
        self._init_libraries()
    
    def _check_dependencies(self):
        """Check for Jetson-specific dependencies."""
        # Check for X11 display (Jetson typically uses X11)
        if not os.environ.get("DISPLAY"):
            print("Warning: No X11 display detected. Using simulation mode.")
            self._simulate_only = True
            return
            
        # Import PyAutoGUI
        try:
            import pyautogui
            self.pyautogui = pyautogui
            # Test if it can actually interact with the display
            try:
                screen_size = pyautogui.size()
                self.screen_size = screen_size
                print(f"Screen size detected: {screen_size[0]}x{screen_size[1]}")
            except Exception as e:
                print(f"PyAutoGUI installed but encountered an error: {e}")
                print("Falling back to simulation mode.")
                self._simulate_only = True
        except ImportError:
            print("PyAutoGUI not available. Input control will be limited.")
            self._simulate_only = True
            
        # Import keyboard library (Linux)
        try:
            import keyboard
            # Test if it has the required permissions
            try:
                keyboard.is_pressed('a')  # Just a test
                self.keyboard = keyboard
            except Exception as e:
                print(f"Keyboard library installed but encountered an error: {e}")
                print("This may require elevated permissions.")
                print("Try running with sudo or add user to input group.")
        except ImportError:
            print("Keyboard library not available. Advanced keyboard features disabled.")
            
        # Import mouse library (Linux)
        try:
            import mouse
            # Test if it has the required permissions
            try:
                mouse.hook(lambda x: None)
                mouse.unhook_all()
                self.mouse = mouse
            except Exception as e:
                print(f"Mouse library installed but encountered an error: {e}")
                print("This may require elevated permissions.")
        except ImportError:
            print("Mouse library not available. Advanced mouse features disabled.")
    
    def _init_libraries(self):
        """Initialize libraries based on availability."""
        if self.pyautogui and not self._simulate_only:
            # Set PyAutoGUI safety features
            self.pyautogui.FAILSAFE = True
            self.pyautogui.PAUSE = 0.1
            # Update actual screen size and position
            self.screen_size = self.pyautogui.size()
            self.mouse_position = self.pyautogui.position()
            # Set a longer default pause for Jetson devices which might be slower
            self.pyautogui.PAUSE = 0.2
    
    def get_mouse_position(self) -> Tuple[int, int]:
        """Get the current mouse position."""
        if self.pyautogui and not self._simulate_only:
            try:
                pos = self.pyautogui.position()
                self.mouse_position = (pos.x, pos.y)
                return (pos.x, pos.y)
            except Exception as e:
                print(f"Error getting mouse position: {e}")
        
        # Return simulated position
        return self.mouse_position
    
    def get_screen_size(self) -> Tuple[int, int]:
        """Get the screen size."""
        if self.pyautogui and not self._simulate_only:
            try:
                size = self.pyautogui.size()
                self.screen_size = (size.width, size.height)
                return (size.width, size.height)
            except Exception as e:
                print(f"Error getting screen size: {e}")
        
        # Return default size
        return self.screen_size
    
    def move_mouse(self, x: int, y: int, duration: float = 0.25) -> bool:
        """Move the mouse to the specified coordinates."""
        # Jetson might need slightly longer durations for reliable operation
        duration = max(0.3, duration)
        
        if self.pyautogui and not self._simulate_only:
            try:
                self.pyautogui.moveTo(x, y, duration=duration)
                self.mouse_position = (x, y)
                return True
            except Exception as e:
                print(f"Error moving mouse: {e}")
        else:
            # Simulate movement
            print(f"Simulating mouse move to ({x}, {y})")
            self.mouse_position = (x, y)
            time.sleep(duration)  # Simulate duration
        
        return False
    
    def click_mouse(self, x: Optional[int] = None, y: Optional[int] = None, 
                   button: str = 'left', clicks: int = 1) -> bool:
        """Click the mouse at the specified coordinates."""
        # If coordinates not provided, use current position
        if x is None or y is None:
            x, y = self.get_mouse_position()
        
        if self.pyautogui and not self._simulate_only:
            try:
                # On Jetson, we add a small delay before clicking for stability
                time.sleep(0.1)
                self.pyautogui.click(x, y, clicks=clicks, button=button)
                return True
            except Exception as e:
                print(f"Error clicking mouse: {e}")
        else:
            # Simulate click
            print(f"Simulating {button} mouse click at ({x}, {y})")
            time.sleep(0.1 * clicks)  # Simulate time for clicks
        
        return False
    
    def press_key(self, key: str) -> bool:
        """Press a single key."""
        if self.pyautogui and not self._simulate_only:
            try:
                self.pyautogui.press(key)
                return True
            except Exception as e:
                print(f"Error pressing key: {e}")
        else:
            # Simulate key press
            print(f"Simulating key press: {key}")
        
        return False
    
    def type_text(self, text: str, interval: float = 0.0) -> bool:
        """Type text with an optional interval between keypresses."""
        # Jetson might need a slightly longer interval for reliability
        interval = max(0.02, interval)
        
        if self.pyautogui and not self._simulate_only:
            try:
                self.pyautogui.write(text, interval=interval)
                return True
            except Exception as e:
                print(f"Error typing text: {e}")
        else:
            # Simulate typing
            print(f"Simulating typing: {text}")
            if interval > 0:
                time.sleep(len(text) * interval)
        
        return False
    
    def hotkey(self, *keys) -> bool:
        """Press multiple keys simultaneously."""
        if self.pyautogui and not self._simulate_only:
            try:
                self.pyautogui.hotkey(*keys)
                return True
            except Exception as e:
                print(f"Error with hotkey: {e}")
        else:
            # Simulate hotkey
            print(f"Simulating hotkey: {' + '.join(keys)}")
        
        return False
    
    def is_key_pressed(self, key: str) -> bool:
        """Check if a key is currently pressed."""
        if self.keyboard:
            try:
                return self.keyboard.is_pressed(key)
            except Exception:
                pass
        # Default when not supported
        return False
    
    def scroll(self, clicks: int, x: Optional[int] = None, y: Optional[int] = None) -> bool:
        """
        Scroll the mouse wheel.
        Positive clicks scroll up, negative clicks scroll down.
        """
        # If coordinates not provided, use current position
        if x is None or y is None:
            x, y = self.get_mouse_position()
            
        if self.pyautogui and not self._simulate_only:
            try:
                # On Jetson, we might need smoother scrolling (smaller individual steps)
                for _ in range(abs(clicks)):
                    step = 1 if clicks > 0 else -1
                    self.pyautogui.scroll(step, x=x, y=y)
                    time.sleep(0.05)  # Small delay between scroll steps
                return True
            except Exception as e:
                print(f"Error scrolling: {e}")
        else:
            # Simulate scrolling
            direction = "up" if clicks > 0 else "down"
            print(f"Simulating {direction} scroll ({clicks}) at ({x}, {y})")
        
        return False

    def click(self, x: Optional[int] = None, y: Optional[int] = None, 
             button: str = 'left', clicks: int = 1) -> bool:
        """Click at the specified position or current mouse position."""
        # If coordinates not provided, use current position
        if x is None or y is None:
            x, y = self.get_mouse_position()
        
        if self.pyautogui and not self._simulate_only:
            try:
                # On Jetson, we add a small delay before clicking for stability
                time.sleep(0.1)
                self.pyautogui.click(x, y, button=button, clicks=clicks)
                return True
            except Exception as e:
                print(f"Error clicking: {e}")
        else:
            # Simulate click
            print(f"Simulating {button} mouse click at ({x}, {y})")
        
        return False
    
    def move_mouse_relative(self, x_offset: int, y_offset: int, duration: float = 0.25) -> bool:
        """Move the mouse by a relative offset from its current position."""
        current_x, current_y = self.get_mouse_position()
        new_x = current_x + x_offset
        new_y = current_y + y_offset
        
        # Jetson might need slightly longer durations for reliable operation
        duration = max(0.3, duration)
        
        return self.move_mouse(new_x, new_y, duration)
    
    def screenshot(self, region: Optional[Tuple[int, int, int, int]] = None) -> Any:
        """Take a screenshot of the screen or specified region."""
        if self.pyautogui and not self._simulate_only:
            try:
                return self.pyautogui.screenshot(region=region)
            except Exception as e:
                print(f"Error taking screenshot: {e}")
        
        print("Screenshot functionality not available in simulation mode")
        return None
    
    def is_simulation_mode(self) -> bool:
        """Check if the handler is operating in simulation mode."""
        return self._simulate_only
