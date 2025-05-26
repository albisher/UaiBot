import json
import os
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class MemoryHandler:
    """Handles UaiBot's memory and state management."""
    
    def __init__(self):
        self.memory_file = "uaibot/data/uaibot_memory.json"
        self.memory = self._load_memory()
    
    def _load_memory(self) -> Dict[str, Any]:
        """Load memory from file if it exists, otherwise create a default structure."""
        default_memory = {
            "last_browser": None,
            "last_search": None,
            "last_url": None,
            "last_action": None,
            "browser_state": {
                "focused": False,
                "volume": 50,
                "window_position": None,
                "window_size": None
            },
            "command_history": [],
            "session_start": datetime.now().isoformat(),
            "active_browsers": {},
            "last_media": None,
            "cast_targets": [],
            "app_indicator": None
        }
        
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r') as f:
                    return json.load(f)
            else:
                # Create the directory if it doesn't exist
                os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
                # Save the default memory structure
                with open(self.memory_file, 'w') as f:
                    json.dump(default_memory, f, indent=2)
                return default_memory
        except Exception as e:
            logger.error(f"Error loading memory: {str(e)}")
            return default_memory
    
    def _save_memory(self) -> None:
        """Save memory to file."""
        try:
            with open(self.memory_file, 'w') as f:
                json.dump(self.memory, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving memory: {str(e)}")
    
    def update_browser_state(self, browser: str, state: Dict[str, Any]) -> None:
        """Update browser state."""
        self.memory["last_browser"] = browser
        self.memory["browser_state"].update(state)
        self._save_memory()
    
    def update_search(self, query: str, url: str) -> None:
        """Update last search information."""
        self.memory["last_search"] = query
        self.memory["last_url"] = url
        self._save_memory()
    
    def add_command(self, command: str, result: Dict[str, Any]) -> None:
        """Add command to history."""
        self.memory["command_history"].append({
            "timestamp": datetime.now().isoformat(),
            "command": command,
            "result": result
        })
        self._save_memory()
    
    def get_last_browser(self) -> Optional[str]:
        """Get last used browser."""
        return self.memory["last_browser"]
    
    def get_last_search(self) -> Optional[str]:
        """Get last search query."""
        return self.memory["last_search"]
    
    def get_last_url(self) -> Optional[str]:
        """Get last accessed URL."""
        return self.memory["last_url"]
    
    def get_browser_state(self) -> Dict[str, Any]:
        """Get current browser state."""
        return self.memory["browser_state"]
    
    def update_media_state(self, media_info: Dict[str, Any]) -> None:
        """Update media playback state."""
        self.memory["last_media"] = media_info
        self._save_memory()
    
    def add_cast_target(self, target: str) -> None:
        """Add a cast target."""
        if target not in self.memory["cast_targets"]:
            self.memory["cast_targets"].append(target)
            self._save_memory()
    
    def get_cast_targets(self) -> List[str]:
        """Get available cast targets."""
        return self.memory["cast_targets"]
    
    def clear_memory(self) -> None:
        """Clear all memory."""
        self.memory = {
            "last_browser": None,
            "last_search": None,
            "last_url": None,
            "last_action": None,
            "browser_state": {
                "focused": False,
                "volume": 50,
                "window_position": None,
                "window_size": None
            },
            "command_history": [],
            "session_start": datetime.now().isoformat(),
            "active_browsers": {},
            "last_media": None,
            "cast_targets": []
        }
        self._save_memory() 