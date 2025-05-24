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

class UserRoutineAwarenessManager:
    """Tracks user routines and activity patterns.
    
    This manager monitors:
    - Keyboard activity
    - Mouse activity
    - Screen dimming
    - Window changes
    - Input activity
    
    Attributes:
        activity (UserActivity): Current user activity data
    """
    
    def __init__(self):
        self.activity = UserActivity(last_input_time=time.time())
        self._setup_activity_monitoring()
    
    def _setup_activity_monitoring(self) -> None:
        """Setup activity monitoring based on platform."""
        try:
            if platform.system() == "Darwin":
                self._setup_macos_monitoring()
            elif platform.system() == "Windows":
                self._setup_windows_monitoring()
            else:  # Linux
                self._setup_linux_monitoring()
        except Exception as e:
            logger.error(f"Failed to setup activity monitoring: {str(e)}")
    
    def _setup_macos_monitoring(self) -> None:
        """Setup activity monitoring for macOS."""
        try:
            import Quartz
            def callback(event):
                self.update_input_activity()
            self.monitor = Quartz.CGEventTapCreate(
                Quartz.kCGSessionEventTap,
                Quartz.kCGHeadInsertEventTap,
                Quartz.kCGEventTapOptionDefault,
                Quartz.CGEventMaskBit(Quartz.kCGEventKeyDown) | Quartz.CGEventMaskBit(Quartz.kCGEventMouseMoved),
                callback,
                None
            )
        except Exception as e:
            logger.error(f"Failed to setup macOS monitoring: {str(e)}")
    
    def _setup_windows_monitoring(self) -> None:
        """Setup activity monitoring for Windows."""
        try:
            import win32api
            import win32con
            def callback(event):
                self.update_input_activity()
            self.monitor = win32api.SetWindowsHookEx(
                win32con.WH_KEYBOARD_LL | win32con.WH_MOUSE_LL,
                callback,
                None,
                0
            )
        except Exception as e:
            logger.error(f"Failed to setup Windows monitoring: {str(e)}")
    
    def _setup_linux_monitoring(self) -> None:
        """Setup activity monitoring for Linux."""
        try:
            import Xlib
            from Xlib import X
            display = Xlib.display.Display()
            root = display.screen().root
            root.change_attributes(event_mask=X.KeyPressMask | X.ButtonPressMask | X.ButtonReleaseMask | X.PointerMotionMask)
        except Exception as e:
            logger.error(f"Failed to setup Linux monitoring: {str(e)}")
    
    def update_input_activity(self) -> None:
        """Update the last input activity timestamp."""
        self.activity.last_input_time = time.time()
    
    def update_screen_dim(self) -> None:
        """Update the last screen dim timestamp."""
        self.activity.last_screen_dim_time = time.time()
    
    def update_keyboard_activity(self) -> None:
        """Update the last keyboard activity timestamp."""
        self.activity.last_keyboard_activity = time.time()
        self.update_input_activity()
    
    def update_mouse_activity(self) -> None:
        """Update the last mouse activity timestamp."""
        self.activity.last_mouse_activity = time.time()
        self.update_input_activity()
    
    def update_window_change(self) -> None:
        """Update the last window change timestamp."""
        self.activity.last_window_change = time.time()
    
    def get_user_routine(self) -> Dict[str, Any]:
        """Get current user activity data.
        
        Returns:
            Dict[str, Any]: Dictionary containing user activity information
        """
        now = time.time()
        return {
            "idle_time_seconds": now - self.activity.last_input_time,
            "screen_dim_idle_seconds": (now - self.activity.last_screen_dim_time) if self.activity.last_screen_dim_time else None,
            "keyboard_idle_seconds": (now - self.activity.last_keyboard_activity) if self.activity.last_keyboard_activity else None,
            "mouse_idle_seconds": (now - self.activity.last_mouse_activity) if self.activity.last_mouse_activity else None,
            "window_change_idle_seconds": (now - self.activity.last_window_change) if self.activity.last_window_change else None,
            "last_activity": datetime.fromtimestamp(self.activity.last_input_time).isoformat()
        }
    
    def is_user_active(self, idle_threshold_seconds: float = 300) -> bool:
        """Check if user is currently active.
        
        Args:
            idle_threshold_seconds (float): Time in seconds to consider user inactive
            
        Returns:
            bool: True if user is active, False otherwise
        """
        return (time.time() - self.activity.last_input_time) < idle_threshold_seconds 