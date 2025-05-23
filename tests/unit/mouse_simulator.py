#!/usr/bin/env python3
"""
Mouse simulation utilities for UaiBot tests.
Provides cross-platform mouse event simulation for automated testing.
"""

import os
import sys
import time
import random
import platform
from src.typing import Tuple, Dict, Optional, List

class MouseSimulator:
    """Cross-platform mouse event simulator for testing."""
    
    def __init__(self, movement_params: Dict = None):
        """
        Initialize the mouse simulator with movement parameters.
        
        Args:
            movement_params: Dictionary with movement parameters
                - min_speed: Minimum movement duration (seconds)
                - max_speed: Maximum movement duration (seconds)
                - precision_error: Maximum pixels of error in targeting
                - curve_factor: Factor for curve simulation (0-1)
        """
        self.system = platform.system()
        
        # Default movement characteristics if not specified
        self.movement_params = movement_params or {
            "min_speed": 0.5,  # seconds
            "max_speed": 1.5,  # seconds
            "precision_error": 5,  # pixels
            "curve_factor": 0.7  # curve simulation factor (0-1)
        }
        
        # Try to load platform-specific mouse libraries
        self.backend = self._initialize_backend()
        
    def _initialize_backend(self) -> Dict:
        """Initialize appropriate mouse control backend based on platform."""
        backend = {"type": None, "module": None}
        
        try:
            # Try pyautogui first (cross-platform)
            import pyautogui
            backend["type"] = "pyautogui"
            backend["module"] = pyautogui
            return backend
        except ImportError:
            pass
            
        # Platform-specific fallbacks
        if self.system == "Windows":
            try:
                # Windows-specific mouse control via ctypes/win32api
                import win32api
                import win32con
                backend["type"] = "win32api"
                backend["module"] = {
                    "api": win32api,
                    "constants": win32con
                }
                return backend
            except ImportError:
                pass
                
        elif self.system == "Darwin":  # macOS
            # AppleScript fallback for macOS
            backend["type"] = "applescript"
            return backend
            
        else:  # Linux
            try:
                # Try pynput for Linux
                from pynput.mouse import Controller, Button
                mouse = {"controller": Controller(), "button": Button}
                backend["type"] = "pynput"
                backend["module"] = mouse
                return backend
            except ImportError:
                # xdotool fallback for Linux
                if os.system("which xdotool > /dev/null 2>&1") == 0:
                    backend["type"] = "xdotool"
                    return backend
                    
        # Last resort: no mouse control
        backend["type"] = "none"
        return backend
    
    def get_position(self) -> Tuple[int, int]:
        """Get current mouse position."""
        if self.backend["type"] == "pyautogui":
            return self.backend["module"].position()
            
        elif self.backend["type"] == "win32api":
            return self.backend["module"]["api"].GetCursorPos()
            
        elif self.backend["type"] == "pynput":
            pos = self.backend["module"]["controller"].position
            return (pos[0], pos[1])
            
        elif self.backend["type"] == "xdotool":
            try:
                # Use xdotool to get position
                import subprocess
                output = subprocess.check_output(["xdotool", "getmouselocation"]).decode()
                # Parse output like "x:100 y:200 screen:0 window:12345"
                parts = output.split()
                x = int(parts[0].split(':')[1])
                y = int(parts[1].split(':')[1])
                return (x, y)
            except:
                return (0, 0)
                
        # Default if no backend available
        return (0, 0)
        
    def move_to(self, x: int, y: int, duration: Optional[float] = None) -> bool:
        """
        Move mouse to position with human-like movement.
        
        Args:
            x: Target x-coordinate
            y: Target y-coordinate
            duration: Movement duration override (None for automatic)
            
        Returns:
            True if successful, False otherwise
        """
        # Add human-like imprecision
        target_x = x + random.randint(
            -self.movement_params["precision_error"],
            self.movement_params["precision_error"]
        )
        target_y = y + random.randint(
            -self.movement_params["precision_error"],
            self.movement_params["precision_error"]
        )
        
        # Determine movement duration if not specified
        if duration is None:
            duration = random.uniform(
                self.movement_params["min_speed"],
                self.movement_params["max_speed"]
            )
        
        # Execute movement with appropriate backend
        if self.backend["type"] == "pyautogui":
            # PyAutoGUI has built-in human-like movement
            try:
                self.backend["module"].moveTo(
                    target_x, target_y, 
                    duration=duration, 
                    tween=self.backend["module"].easeOutQuad  # Human-like easing
                )
                return True
            except:
                return False
                
        elif self.backend["type"] == "win32api":
            try:
                # For win32api, we need to implement our own easing
                start_x, start_y = self.get_position()
                steps = max(int(duration * 60), 10)  # 60 steps per second, min 10 steps
                
                for i in range(1, steps + 1):
                    progress = i / steps
                    # Ease out quadratic interpolation: t * (2-t)
                    ease_factor = progress * (2 - progress)
                    
                    current_x = int(start_x + (target_x - start_x) * ease_factor)
                    current_y = int(start_y + (target_y - start_y) * ease_factor)
                    
                    # Apply slight curve to movement path using sin wave
                    if self.movement_params["curve_factor"] > 0:
                        curve_amount = self.movement_params["curve_factor"] * 10
                        curve_x = int(math.sin(progress * math.pi) * curve_amount)
                        curve_y = int(math.cos(progress * math.pi * 0.5) * curve_amount)
                        current_x += curve_x
                        current_y += curve_y
                    
                    self.backend["module"]["api"].SetCursorPos((current_x, current_y))
                    time.sleep(duration / steps)
                    
                return True
            except:
                return False
                
        elif self.backend["type"] == "pynput":
            try:
                # For pynput, implement easing
                start_x, start_y = self.get_position()
                steps = max(int(duration * 60), 10)  # 60 steps per second
                
                for i in range(1, steps + 1):
                    progress = i / steps
                    # Ease out quadratic
                    ease_factor = progress * (2 - progress)
                    
                    current_x = int(start_x + (target_x - start_x) * ease_factor)
                    current_y = int(start_y + (target_y - start_y) * ease_factor)
                    
                    self.backend["module"]["controller"].position = (current_x, current_y)
                    time.sleep(duration / steps)
                    
                return True
            except:
                return False
                
        elif self.backend["type"] == "xdotool":
            try:
                # For xdotool, we can use mousemove with options
                os.system(f"xdotool mousemove --sync {target_x} {target_y}")
                return True
            except:
                return False
                
        # If we get here, no backend was available
        return False
        
    def click(self, x: Optional[int] = None, y: Optional[int] = None, 
              button: str = "left", clicks: int = 1, interval: float = 0.1) -> bool:
        """
        Perform mouse click at the specified position.
        
        Args:
            x: X-coordinate, or None for current position
            y: Y-coordinate, or None for current position
            button: Mouse button ('left', 'right', 'middle')
            clicks: Number of clicks
            interval: Interval between clicks
        
        Returns:
            True if successful, False otherwise
        """
        # Move to position first if provided
        if x is not None and y is not None:
            if not self.move_to(x, y):
                return False
                
        # Perform the click(s)
        try:
            if self.backend["type"] == "pyautogui":
                for i in range(clicks):
                    self.backend["module"].click(button=button)
                    if i < clicks - 1:
                        time.sleep(interval)
                        
            elif self.backend["type"] == "win32api":
                button_down = None
                button_up = None
                
                if button == "left":
                    button_down = self.backend["module"]["constants"].MOUSEEVENTF_LEFTDOWN
                    button_up = self.backend["module"]["constants"].MOUSEEVENTF_LEFTUP
                elif button == "right":
                    button_down = self.backend["module"]["constants"].MOUSEEVENTF_RIGHTDOWN
                    button_up = self.backend["module"]["constants"].MOUSEEVENTF_RIGHTUP
                elif button == "middle":
                    button_down = self.backend["module"]["constants"].MOUSEEVENTF_MIDDLEDOWN
                    button_up = self.backend["module"]["constants"].MOUSEEVENTF_MIDDLEUP
                
                if button_down and button_up:
                    for i in range(clicks):
                        self.backend["module"]["api"].mouse_event(button_down, 0, 0, 0, 0)
                        self.backend["module"]["api"].mouse_event(button_up, 0, 0, 0, 0)
                        if i < clicks - 1:
                            time.sleep(interval)
                            
            elif self.backend["type"] == "pynput":
                button_map = {
                    "left": self.backend["module"]["button"].left,
                    "right": self.backend["module"]["button"].right,
                    "middle": self.backend["module"]["button"].middle
                }
                
                button_obj = button_map.get(button, button_map["left"])
                
                for i in range(clicks):
                    self.backend["module"]["controller"].click(button_obj)
                    if i < clicks - 1:
                        time.sleep(interval)
                        
            elif self.backend["type"] == "xdotool":
                button_map = {
                    "left": 1,
                    "right": 3,
                    "middle": 2
                }
                
                button_num = button_map.get(button, 1)
                
                for i in range(clicks):
                    os.system(f"xdotool click {button_num}")
                    if i < clicks - 1:
                        time.sleep(interval)
            else:
                return False
                
            return True
            
        except Exception as e:
            print(f"Mouse click error: {e}")
            return False
            
    def drag(self, start_x: int, start_y: int, end_x: int, end_y: int, 
             button: str = "left", duration: float = 1.0) -> bool:
        """
        Perform drag operation from start to end position.
        
        Args:
            start_x: Starting X-coordinate
            start_y: Starting Y-coordinate
            end_x: Ending X-coordinate
            end_y: Ending Y-coordinate
            button: Mouse button to use for dragging
            duration: Duration of drag operation
            
        Returns:
            True if successful, False otherwise
        """
        # First move to the start position
        if not self.move_to(start_x, start_y):
            return False
            
        try:
            if self.backend["type"] == "pyautogui":
                self.backend["module"].mouseDown(button=button)
                self.backend["module"].moveTo(
                    end_x, end_y, 
                    duration=duration, 
                    tween=self.backend["module"].easeOutQuad
                )
                self.backend["module"].mouseUp(button=button)
                return True
                
            elif self.backend["type"] == "win32api":
                button_down = None
                button_up = None
                
                if button == "left":
                    button_down = self.backend["module"]["constants"].MOUSEEVENTF_LEFTDOWN
                    button_up = self.backend["module"]["constants"].MOUSEEVENTF_LEFTUP
                elif button == "right":
                    button_down = self.backend["module"]["constants"].MOUSEEVENTF_RIGHTDOWN
                    button_up = self.backend["module"]["constants"].MOUSEEVENTF_RIGHTUP
                elif button == "middle":
                    button_down = self.backend["module"]["constants"].MOUSEEVENTF_MIDDLEDOWN
                    button_up = self.backend["module"]["constants"].MOUSEEVENTF_MIDDLEUP
                
                if button_down and button_up:
                    self.backend["module"]["api"].mouse_event(button_down, 0, 0, 0, 0)
                    self.move_to(end_x, end_y, duration)
                    self.backend["module"]["api"].mouse_event(button_up, 0, 0, 0, 0)
                    return True
                return False
                
            elif self.backend["type"] == "pynput":
                button_map = {
                    "left": self.backend["module"]["button"].left,
                    "right": self.backend["module"]["button"].right,
                    "middle": self.backend["module"]["button"].middle
                }
                
                button_obj = button_map.get(button, button_map["left"])
                
                self.backend["module"]["controller"].press(button_obj)
                self.move_to(end_x, end_y, duration)
                self.backend["module"]["controller"].release(button_obj)
                return True
                
            elif self.backend["type"] == "xdotool":
                button_map = {
                    "left": 1,
                    "right": 3,
                    "middle": 2
                }
                
                button_num = button_map.get(button, 1)
                
                os.system(f"xdotool mousedown {button_num}")
                time.sleep(0.1)
                os.system(f"xdotool mousemove --sync {end_x} {end_y}")
                time.sleep(0.1)
                os.system(f"xdotool mouseup {button_num}")
                return True
                
            return False
            
        except Exception as e:
            print(f"Mouse drag error: {e}")
            return False


# Example usage when run directly
if __name__ == "__main__":
    import time
    
    print("Mouse Simulator Test")
    print("-------------------")
    
    simulator = MouseSimulator()
    
    print("Getting current mouse position...")
    current_x, current_y = simulator.get_position()
    print(f"Current position: ({current_x}, {current_y})")
    
    print("Moving mouse in 3 seconds...")
    time.sleep(3)
    
    # Move to a position 100 pixels right and 100 pixels down
    target_x = current_x + 100
    target_y = current_y + 100
    print(f"Moving to ({target_x}, {target_y})...")
    
    if simulator.move_to(target_x, target_y):
        print("Move successful!")
    else:
        print("Move failed.")
    
    time.sleep(1)
    
    # Perform a click
    print("Performing click...")
    if simulator.click():
        print("Click successful!")
    else:
        print("Click failed.")
    
    print("Test completed!")
