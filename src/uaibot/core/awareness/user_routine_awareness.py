import time
from typing import Dict, Any

class UserRoutineAwarenessManager:
    """Tracks user routines: keyboard/mouse activity, screen dimming, etc."""
    def __init__(self):
        self.last_input_time = time.time()
        self.last_screen_dim_time = None

    def update_input_activity(self):
        self.last_input_time = time.time()

    def update_screen_dim(self):
        self.last_screen_dim_time = time.time()

    def get_user_routine(self) -> Dict[str, Any]:
        now = time.time()
        idle_time = now - self.last_input_time
        screen_dim_idle = (now - self.last_screen_dim_time) if self.last_screen_dim_time else None
        return {
            "idle_time_seconds": idle_time,
            "screen_dim_idle_seconds": screen_dim_idle
        } 