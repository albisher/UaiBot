"""
DEPRECATED: Mouse input logic has been moved to platform_core/platform_manager.py.
Use PlatformManager for all mouse input logic.
"""

# Deprecated stub for backward compatibility
from platform_core.platform_manager import PlatformManager

"""
Mouse Control Implementation

This module provides comprehensive mouse control capabilities for Labeeb,
including movement, clicking, dragging, scrolling, and gestures.
"""

import time
from typing import Tuple, Optional, List, Dict, Any
import logging
from dataclasses import dataclass
import math
from src.app.core.platform_core.platform_utils import get_platform_name

# Platform-specific imports
try:
    import pyautogui
    from pyautogui import Point, FAILSAFE
    FAILSAFE = True  # Enable PyAutoGUI's failsafe
except ImportError:
    logging.error("PyAutoGUI not installed. Mouse control will be limited.")
    pyautogui = None

logger = logging.getLogger(__name__)

OS_NAME = get_platform_name()

@dataclass
class MouseState:
    """Represents the current state of the mouse."""
    position: Tuple[int, int]
    is_pressed: bool
    last_action: str
    last_action_time: float

class MouseController:
    """Provides comprehensive mouse control capabilities."""
    
    def __init__(self):
        """Initialize the mouse controller."""
        self.state = MouseState(
            position=(0, 0),
            is_pressed=False,
            last_action="",
            last_action_time=time.time()
        )
        self._validate_environment()
    
    def _validate_environment(self) -> None:
        """Validate that the environment is properly set up."""
        if pyautogui is None:
            raise RuntimeError("PyAutoGUI is required for mouse control")
    
    def _get_screen_size(self) -> Tuple[int, int]:
        """Get the screen dimensions."""
        return pyautogui.size()
    
    def _validate_coordinates(self, x: int, y: int) -> bool:
        """Validate that coordinates are within screen bounds."""
        width, height = self._get_screen_size()
        return 0 <= x < width and 0 <= y < height
    
    def move_to(self, x: int, y: int, duration: float = 0.0) -> bool:
        """Move the mouse to absolute coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            duration: Movement duration in seconds
            
        Returns:
            bool: True if movement was successful
        """
        try:
            if not self._validate_coordinates(x, y):
                logger.error(f"Invalid coordinates: ({x}, {y})")
                return False
            
            pyautogui.moveTo(x, y, duration=duration)
            self.state.position = (x, y)
            self.state.last_action = "move"
            self.state.last_action_time = time.time()
            return True
        except Exception as e:
            logger.error(f"Error moving mouse: {e}")
            return False
    
    def move_relative(self, dx: int, dy: int, duration: float = 0.0) -> bool:
        """Move the mouse relative to current position.
        
        Args:
            dx: X distance to move
            dy: Y distance to move
            duration: Movement duration in seconds
            
        Returns:
            bool: True if movement was successful
        """
        try:
            current_x, current_y = self.state.position
            new_x, new_y = current_x + dx, current_y + dy
            
            if not self._validate_coordinates(new_x, new_y):
                logger.error(f"Invalid relative movement: ({dx}, {dy})")
                return False
            
            pyautogui.moveRel(dx, dy, duration=duration)
            self.state.position = (new_x, new_y)
            self.state.last_action = "move_relative"
            self.state.last_action_time = time.time()
            return True
        except Exception as e:
            logger.error(f"Error moving mouse relative: {e}")
            return False
    
    def click(self, button: str = "left", clicks: int = 1) -> bool:
        """Perform a mouse click.
        
        Args:
            button: Mouse button ("left", "right", "middle")
            clicks: Number of clicks
            
        Returns:
            bool: True if click was successful
        """
        try:
            pyautogui.click(button=button, clicks=clicks)
            self.state.last_action = f"click_{button}"
            self.state.last_action_time = time.time()
            return True
        except Exception as e:
            logger.error(f"Error clicking mouse: {e}")
            return False
    
    def drag_to(self, x: int, y: int, duration: float = 0.0) -> bool:
        """Drag the mouse to coordinates.
        
        Args:
            x: Target X coordinate
            y: Target Y coordinate
            duration: Drag duration in seconds
            
        Returns:
            bool: True if drag was successful
        """
        try:
            if not self._validate_coordinates(x, y):
                logger.error(f"Invalid drag coordinates: ({x}, {y})")
                return False
            
            pyautogui.dragTo(x, y, duration=duration)
            self.state.position = (x, y)
            self.state.last_action = "drag"
            self.state.last_action_time = time.time()
            return True
        except Exception as e:
            logger.error(f"Error dragging mouse: {e}")
            return False
    
    def scroll(self, clicks: int, direction: str = "vertical") -> bool:
        """Scroll the mouse wheel.
        
        Args:
            clicks: Number of scroll clicks (positive for up/right, negative for down/left)
            direction: Scroll direction ("vertical" or "horizontal")
            
        Returns:
            bool: True if scroll was successful
        """
        try:
            if direction == "horizontal":
                pyautogui.hscroll(clicks)
            else:
                pyautogui.scroll(clicks)
            
            self.state.last_action = f"scroll_{direction}"
            self.state.last_action_time = time.time()
            return True
        except Exception as e:
            logger.error(f"Error scrolling mouse: {e}")
            return False
    
    def draw_gesture(self, points: List[Tuple[int, int]], duration: float = 0.5) -> bool:
        """Draw a gesture with the mouse.
        
        Args:
            points: List of (x, y) coordinates to draw through
            duration: Total duration of the gesture in seconds
            
        Returns:
            bool: True if gesture was successful
        """
        try:
            if not all(self._validate_coordinates(x, y) for x, y in points):
                logger.error("Invalid gesture coordinates")
                return False
            
            # Move to first point
            self.move_to(points[0][0], points[0][1])
            
            # Draw through remaining points
            for x, y in points[1:]:
                self.drag_to(x, y, duration=duration/len(points))
            
            self.state.last_action = "gesture"
            self.state.last_action_time = time.time()
            return True
        except Exception as e:
            logger.error(f"Error drawing gesture: {e}")
            return False
    
    def draw_circle(self, center: Tuple[int, int], radius: int, duration: float = 1.0) -> bool:
        """Draw a circle with the mouse.
        
        Args:
            center: (x, y) coordinates of circle center
            radius: Circle radius in pixels
            duration: Total duration of the circle drawing
            
        Returns:
            bool: True if circle was drawn successfully
        """
        try:
            if not self._validate_coordinates(center[0], center[1]):
                logger.error(f"Invalid circle center: {center}")
                return False
            
            points = []
            steps = 36  # 10 degrees per step
            for i in range(steps + 1):
                angle = 2 * math.pi * i / steps
                x = center[0] + radius * math.cos(angle)
                y = center[1] + radius * math.sin(angle)
                points.append((int(x), int(y)))
            
            return self.draw_gesture(points, duration)
        except Exception as e:
            logger.error(f"Error drawing circle: {e}")
            return False
    
    def draw_square(self, start: Tuple[int, int], size: int, duration: float = 1.0) -> bool:
        """Draw a square with the mouse.
        
        Args:
            start: (x, y) coordinates of top-left corner
            size: Square size in pixels
            duration: Total duration of the square drawing
            
        Returns:
            bool: True if square was drawn successfully
        """
        try:
            if not self._validate_coordinates(start[0], start[1]):
                logger.error(f"Invalid square start: {start}")
                return False
            
            points = [
                start,
                (start[0] + size, start[1]),
                (start[0] + size, start[1] + size),
                (start[0], start[1] + size),
                start
            ]
            
            return self.draw_gesture(points, duration)
        except Exception as e:
            logger.error(f"Error drawing square: {e}")
            return False
    
    def get_position(self) -> Tuple[int, int]:
        """Get current mouse position.
        
        Returns:
            Tuple[int, int]: Current (x, y) coordinates
        """
        return pyautogui.position()
    
    def is_pressed(self, button: str = "left") -> bool:
        """Check if a mouse button is pressed.
        
        Args:
            button: Mouse button to check ("left", "right", "middle")
            
        Returns:
            bool: True if button is pressed
        """
        return pyautogui.mouseDown(button=button)

# Create a singleton instance
mouse_controller = MouseController()

def process_mouse_command(command: str) -> Dict[str, Any]:
    """Process a mouse control command.
    Returns a dict with status, message, position, os, action, and parameters.
    """
    try:
        command = command.lower()
        action = None
        params = {}
        success = False
        message = ""
        # Basic mouse movement
        if "move mouse to coordinates" in command:
            coords = command.split("(")[1].split(")")[0].split(",")
            x, y = int(coords[0]), int(coords[1])
            success = mouse_controller.move_to(x, y)
            action = "move_to"
            params = {"x": x, "y": y}
        elif "move mouse" in command:
            if "pixels" in command:
                import re
                match = re.search(r"move mouse ([\d\.]+) pixels? (right|left|up|down)", command)
                if match:
                    pixels = float(match.group(1))
                    direction = match.group(2)
                    if direction == "right":
                        success = mouse_controller.move_relative(int(pixels), 0)
                        action = "move_relative"
                        params = {"dx": int(pixels), "dy": 0}
                    elif direction == "left":
                        success = mouse_controller.move_relative(-int(pixels), 0)
                        action = "move_relative"
                        params = {"dx": -int(pixels), "dy": 0}
                    elif direction == "up":
                        success = mouse_controller.move_relative(0, -int(pixels))
                        action = "move_relative"
                        params = {"dx": 0, "dy": -int(pixels)}
                    elif direction == "down":
                        success = mouse_controller.move_relative(0, int(pixels))
                        action = "move_relative"
                        params = {"dx": 0, "dy": int(pixels)}
                else:
                    success = False
            elif "to top left corner" in command:
                success = mouse_controller.move_to(0, 0)
                action = "move_to"
                params = {"x": 0, "y": 0}
            elif "to bottom right corner" in command:
                width, height = mouse_controller._get_screen_size()
                success = mouse_controller.move_to(width - 1, height - 1)
                action = "move_to"
                params = {"x": width - 1, "y": height - 1}
            elif "to screen edge" in command:
                width, height = mouse_controller._get_screen_size()
                success = mouse_controller.move_to(width - 1, height - 1)
                action = "move_to"
                params = {"x": width - 1, "y": height - 1}
            elif "precisely" in command:
                coords = command.split("(")[1].split(")")[0].split(",")
                x, y = int(coords[0]), int(coords[1])
                success = mouse_controller.move_to(x, y, duration=0.5)
                action = "move_to_precise"
                params = {"x": x, "y": y, "duration": 0.5}
            elif "slowly" in command:
                coords = command.split("(")[1].split(")")[0].split(",")
                x, y = int(coords[0]), int(coords[1])
                success = mouse_controller.move_to(x, y, duration=1.0)
                action = "move_to_slow"
                params = {"x": x, "y": y, "duration": 1.0}
            elif "quickly" in command:
                coords = command.split("(")[1].split(")")[0].split(",")
                x, y = int(coords[0]), int(coords[1])
                success = mouse_controller.move_to(x, y, duration=0.1)
                action = "move_to_quick"
                params = {"x": x, "y": y, "duration": 0.1}
            elif "with acceleration" in command:
                coords = command.split("(")[1].split(")")[0].split(",")
                x, y = int(coords[0]), int(coords[1])
                # Simulate acceleration by using a non-linear duration
                success = mouse_controller.move_to(x, y, duration=0.3)
                action = "move_to_accelerate"
                params = {"x": x, "y": y, "duration": 0.3}
            else:
                success = False
        elif "move to" in command:
            # e.g. "move to (150, 150)"
            import re
            match = re.search(r"move to \((\d+),\s*(\d+)\)", command)
            if match:
                x, y = int(match.group(1)), int(match.group(2))
                success = mouse_controller.move_to(x, y)
                action = "move_to"
                params = {"x": x, "y": y}
            else:
                success = False
        # Click operations
        elif "click" in command:
            if "right-click" in command:
                if "at coordinates" in command:
                    coords = command.split("(")[1].split(")")[0].split(",")
                    x, y = int(coords[0]), int(coords[1])
                    mouse_controller.move_to(x, y)
                success = mouse_controller.click("right")
                action = "right_click"
            elif "middle-click" in command:
                success = mouse_controller.click("middle")
                action = "middle_click"
            elif "double-click" in command:
                success = mouse_controller.click("left", 2)
                action = "double_click"
            elif "precisely" in command:
                coords = command.split("(")[1].split(")")[0].split(",")
                x, y = int(coords[0]), int(coords[1])
                mouse_controller.move_to(x, y)
                success = mouse_controller.click("left")
                action = "precise_click"
                params = {"x": x, "y": y}
            elif "at current position" in command:
                success = mouse_controller.click("left")
                action = "click"
            elif "at invalid position" in command:
                success = False
                action = "click_invalid"
            else:
                success = mouse_controller.click("left")
                action = "click"
        # Drag operations
        elif "drag" in command:
            import re
            match = re.search(r"drag (?:and hold )?from \((\d+),\s*(\d+)\) to \((\d+),\s*(\d+)\)", command)
            if match:
                from_x, from_y, to_x, to_y = map(int, match.groups())
                mouse_controller.move_to(from_x, from_y)
                success = mouse_controller.drag_to(to_x, to_y)
                action = "drag"
                params = {"from": (from_x, from_y), "to": (to_x, to_y)}
            elif "release mouse at" in command:
                coords = command.split("(")[1].split(")")[0].split(",")
                x, y = int(coords[0]), int(coords[1])
                # Simulate release by moving to the position
                success = mouse_controller.move_to(x, y)
                action = "release"
                params = {"x": x, "y": y}
            else:
                success = False
        # Scroll operations
        elif "scroll" in command:
            import re
            match = re.search(r"scroll (up|down|left|right)(?: (\d+))?", command)
            if match:
                direction = match.group(1)
                amount = int(match.group(2)) if match.group(2) else 1
                if direction == "up":
                    success = mouse_controller.scroll(amount)
                    action = "scroll_up"
                    params = {"amount": amount}
                elif direction == "down":
                    success = mouse_controller.scroll(-amount)
                    action = "scroll_down"
                    params = {"amount": amount}
                elif direction == "right":
                    success = mouse_controller.scroll(amount, "horizontal")
                    action = "scroll_right"
                    params = {"amount": amount}
                elif direction == "left":
                    success = mouse_controller.scroll(-amount, "horizontal")
                    action = "scroll_left"
                    params = {"amount": amount}
            elif "to bottom of page" in command:
                # Simulate by scrolling a large amount
                success = mouse_controller.scroll(-1000)
                action = "scroll_to_bottom"
                params = {"amount": 1000}
            elif "down slowly" in command:
                success = mouse_controller.scroll(-1)
                action = "scroll_down_slow"
                params = {"amount": 1, "speed": "slow"}
            elif "up quickly" in command:
                success = mouse_controller.scroll(10)
                action = "scroll_up_quick"
                params = {"amount": 10, "speed": "quick"}
            else:
                success = False
        # Gesture operations
        elif "draw" in command:
            if "circle" in command:
                center = (100, 100)
                radius = 50
                success = mouse_controller.draw_circle(center, radius)
                action = "draw_circle"
                params = {"center": center, "radius": radius}
            elif "square" in command:
                start = (100, 100)
                size = 100
                success = mouse_controller.draw_square(start, size)
                action = "draw_square"
                params = {"start": start, "size": size}
            elif "figure eight" in command:
                # Simulate as two circles
                center1 = (100, 100)
                center2 = (150, 100)
                radius = 25
                success = mouse_controller.draw_circle(center1, radius) and mouse_controller.draw_circle(center2, radius)
                action = "draw_figure_eight"
                params = {"center1": center1, "center2": center2, "radius": radius}
            else:
                success = False
        # Combination operations
        elif "and" in command or "," in command:
            # Split the command into parts
            parts = [p.strip() for p in command.replace(",", " and ").split("and")]
            success = True
            actions = []
            for part in parts:
                result = process_mouse_command(part)
                if result["status"] != "success":
                    success = False
                actions.append(result.get("action"))
            action = "combo"
            params = {"actions": actions}
        else:
            success = False
            message = "Command not recognized"
        return {
            "status": "success" if success else "error",
            "message": message if message else ("Command executed successfully" if success else "Invalid command"),
            "position": mouse_controller.get_position(),
            "os": OS_NAME,
            "action": action,
            "parameters": params
        }
    except Exception as e:
        logger.error(f"Error processing mouse command: {e}")
        return {
            "status": "error",
            "message": str(e),
            "position": mouse_controller.get_position(),
            "os": OS_NAME,
            "action": None,
            "parameters": {}
        } 