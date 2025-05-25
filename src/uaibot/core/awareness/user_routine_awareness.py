import time
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import platform

logger = logging.getLogger(__name__)

@dataclass
class UserActivity:
    """Represents user activity data."""
    last_input_time: float
    last_screen_dim_time: Optional[float] = None
    last_keyboard_activity: Optional[float] = None
    last_mouse_activity: Optional[float] = None
    last_window_change: Optional[float] = None

class UserRoutineAwarenessTool:
    """
    Tool for tracking user routines and activity patterns.
    """
    def __init__(self):
        self.activity = self._init_activity()
        self.logger = logging.getLogger("UserRoutineAwarenessTool")

    def _init_activity(self):
        return {
            'last_input_time': time.time(),
            'last_screen_dim_time': time.time(),
            'last_keyboard_activity': time.time(),
            'last_mouse_activity': time.time(),
            'last_window_change': time.time(),
        }

    def execute(self, action: str, **kwargs) -> Any:
        if action == "update_input_activity":
            return self.update_input_activity()
        elif action == "update_screen_dim":
            return self.update_screen_dim()
        elif action == "update_keyboard_activity":
            return self.update_keyboard_activity()
        elif action == "update_mouse_activity":
            return self.update_mouse_activity()
        elif action == "update_window_change":
            return self.update_window_change()
        elif action == "get_activity":
            return self.activity.copy()
        else:
            return {"error": f"Unknown action: {action}"}

    def update_input_activity(self) -> Dict[str, float]:
        self.activity['last_input_time'] = time.time()
        return self.activity.copy()

    def update_screen_dim(self) -> Dict[str, float]:
        self.activity['last_screen_dim_time'] = time.time()
        return self.activity.copy()

    def update_keyboard_activity(self) -> Dict[str, float]:
        self.activity['last_keyboard_activity'] = time.time()
        self.update_input_activity()
        return self.activity.copy()

    def update_mouse_activity(self) -> Dict[str, float]:
        self.activity['last_mouse_activity'] = time.time()
        self.update_input_activity()
        return self.activity.copy()

    def update_window_change(self) -> Dict[str, float]:
        self.activity['last_window_change'] = time.time()
        return self.activity.copy()

    def get_user_routine(self) -> Dict[str, Any]:
        """Get current user activity data.
        
        Returns:
            Dict[str, Any]: Dictionary containing user activity information
        """
        now = time.time()
        return {
            "idle_time_seconds": now - self.activity['last_input_time'],
            "screen_dim_idle_seconds": (now - self.activity['last_screen_dim_time']) if self.activity['last_screen_dim_time'] else None,
            "keyboard_idle_seconds": (now - self.activity['last_keyboard_activity']) if self.activity['last_keyboard_activity'] else None,
            "mouse_idle_seconds": (now - self.activity['last_mouse_activity']) if self.activity['last_mouse_activity'] else None,
            "window_change_idle_seconds": (now - self.activity['last_window_change']) if self.activity['last_window_change'] else None,
            "last_activity": datetime.fromtimestamp(self.activity['last_input_time']).isoformat()
        }
    
    def is_user_active(self, idle_threshold_seconds: float = 300) -> bool:
        """Check if user is currently active.
        
        Args:
            idle_threshold_seconds (float): Time in seconds to consider user inactive
            
        Returns:
            bool: True if user is active, False otherwise
        """
        return (time.time() - self.activity['last_input_time']) < idle_threshold_seconds 