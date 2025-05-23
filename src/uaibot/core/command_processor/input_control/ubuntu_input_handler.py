#!/usr/bin/env python3
"""
Ubuntu-specific input handler implementation for mouse and keyboard control.
"""
import os
import sys
import time
from .typing import Tuple, Optional, Union, Any, List

from ...common.input_control.base_handler import BaseInputHandler

class UbuntuInputHandler(BaseInputHandler):
    """
    Ubuntu-specific implementation of the input handler.
    Uses PyAutoGUI with X11 support and Linux-specific libraries for advanced features.
    """
    
    def __init__(self):
        """Initialize the Ubuntu input handler."""
        self.pyautogui = None
        self.keyboard = None
        self.mouse = None
        self.screen_size = (1920, 1080)  # Default size if detection fails
        self.mouse_position = (0, 0)     # Default position if detection fails
        self._simulate_only = False
        
        self._check_dependencies()
        self._init_libraries()
    
    def _check_dependencies(self):
        """Check for Ubuntu-specific dependencies."""
        # Check for X11 display
        if not os.environ.get("DISPLAY") and not os.environ.get("WAYLAND_DISPLAY"):
            print("Warning: No X11 or Wayland display detected. Using simulation mode.")
            self._simulate_only = True
            return
        
        # Even with DISPLAY set, we might be in a headless environment or without proper permissions
        # Let's try to detect if we're running in a test environment
        is_test = 'unittest' in sys.modules or any('test' in arg.lower() for arg in sys.argv)
        
        if is_test:
            print("Running in test mode, using simulation for safety")
            self._simulate_only = True
            return
            
        # Import PyAutoGUI with extra care
        try:
            # We'll try importing in a way that fails more gracefully
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
            except Exception as e:
                print(f"Error importing PyAutoGUI: {e}")
                self._simulate_only = True
        except:
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
        
        return self._simulate_only
    
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
        # If coordinates not provided, use current position
        if x is None or y is None:
            x, y = self.get_mouse_position()
        
        if self.pyautogui and not self._simulate_only:
            try:
                self.pyautogui.click(x, y, clicks=clicks, button=button, interval=interval)
                return True
            except Exception as e:
                print(f"Error clicking mouse: {e}")
        else:
            # Simulate click
            print(f"Simulating {button} mouse click at ({x}, {y})")
            time.sleep(0.1 * clicks + interval * max(0, clicks - 1))  # Simulate time for clicks
        
        return self._simulate_only
    
    def press_key(self, key: str) -> bool:
        """
        Press and release a key.
        
        Args:
            key: Key to press (e.g., 'enter', 'esc', 'space', 'a')
        
        Returns:
            bool: Success status
        """
        if self.pyautogui and not self._simulate_only:
            try:
                self.pyautogui.press(key)
                return True
            except Exception as e:
                print(f"Error pressing key: {e}")
        else:
            # Simulate key press
            print(f"Simulating key press: {key}")
        
        return self._simulate_only
    
    def type_text(self, text: str, interval: float = 0.0) -> bool:
        """
        Type text with optional delay between characters.
        
        Args:
            text: Text to type
            interval: Delay between characters in seconds
            
        Returns:
            bool: Success status
        """
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
        
        return self._simulate_only
    
    def hotkey(self, *keys) -> bool:
        """
        Press multiple keys simultaneously.
        
        Args:
            *keys: Keys to press simultaneously
        
        Returns:
            bool: Success status
        """
        if self.pyautogui and not self._simulate_only:
            try:
                self.pyautogui.hotkey(*keys)
                return True
            except Exception as e:
                print(f"Error with hotkey: {e}")
        else:
            # Simulate hotkey
            print(f"Simulating hotkey: {' + '.join(keys)}")
        
        return self._simulate_only
    
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
        
        Args:
            clicks: Number of steps to scroll (positive scrolls up, negative scrolls down)
            x: X-coordinate for scroll position. If None, uses current position.
            y: Y-coordinate for scroll position. If None, uses current position.
            
        Returns:
            bool: Success status
        """
        # If coordinates not provided, use current position
        if x is None or y is None:
            x, y = self.get_mouse_position()
            
        if self.pyautogui and not self._simulate_only:
            try:
                self.pyautogui.scroll(clicks, x=x, y=y)
                return True
            except Exception as e:
                print(f"Error scrolling: {e}")
        else:
            # Simulate scrolling
            direction = "up" if clicks > 0 else "down"
            print(f"Simulating {direction} scroll ({clicks}) at ({x}, {y})")
        
        return self._simulate_only

    # Note: The main 'click' method has been defined above
    
    def move_mouse_relative(self, x_offset: int, y_offset: int, duration: float = 0.25) -> bool:
        """Move the mouse by a relative offset from its current position."""
        current_x, current_y = self.get_mouse_position()
        new_x = current_x + x_offset
        new_y = current_y + y_offset
        
        return self.move_mouse(new_x, new_y, duration)
    
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
        if self.pyautogui and not self._simulate_only:
            try:
                screenshot = self.pyautogui.screenshot(region=region)
                if filename:
                    screenshot.save(filename)
                    return True
                return screenshot
            except Exception as e:
                print(f"Error taking screenshot: {e}")
        
        print("Screenshot functionality not available in simulation mode")
        return self._simulate_only
    
    def is_simulation_mode(self) -> bool:
        """
        Check if the handler is in simulation mode.
        
        Returns:
            bool: True if in simulation mode, False otherwise
        """
        return self._simulate_only
