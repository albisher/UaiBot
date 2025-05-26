"""
Labeeb User Routine Awareness

This module provides user routine awareness functionality for Labeeb.
It tracks and analyzes user patterns and behaviors to provide context-aware assistance.
"""

import time
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
import platform
from labeeb.platform_core.platform_manager import PlatformManager

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
    """Tool for tracking and analyzing user routines and patterns.
    
    This tool provides functionality for:
    - Monitoring user activity patterns
    - Identifying common routines and workflows
    - Suggesting optimizations based on usage patterns
    - Adapting to user preferences over time
    
    Attributes:
        routines (Dict[str, Any]): Dictionary of tracked user routines
        patterns (Dict[str, Any]): Dictionary of identified usage patterns
    """

    name = 'user_routine_awareness'
    description = "Track user routines and activity patterns"

    def __init__(self):
        """Initialize the user routine awareness tool."""
        self.activity = self._init_activity()
        self.logger = logging.getLogger("UserRoutineAwarenessTool")
        self.platform_manager = PlatformManager()
        self.platform_info = self.platform_manager.get_platform_info()
        self.handlers = self.platform_manager.get_handlers()
        self.routines = {}
        self.patterns = {}

    def _init_activity(self):
        return {
            'last_input_time': time.time(),
            'last_screen_dim_time': time.time(),
            'last_keyboard_activity': time.time(),
            'last_mouse_activity': time.time(),
            'last_window_change': time.time(),
        }

    async def execute(self, action: str, **kwargs) -> Any:
        if action == "update_input_activity":
            return await self.update_input_activity()
        elif action == "update_screen_dim":
            return await self.update_screen_dim()
        elif action == "update_keyboard_activity":
            return await self.update_keyboard_activity()
        elif action == "update_mouse_activity":
            return await self.update_mouse_activity()
        elif action == "update_window_change":
            return await self.update_window_change()
        elif action == "get_activity":
            return self.activity.copy()
        elif action == "get_user_routines":
            return self.get_user_routines()
        else:
            return {"error": f"Unknown action: {action}"}

    async def update_input_activity(self) -> Dict[str, float]:
        self.activity['last_input_time'] = time.time()
        return self.activity.copy()

    async def update_screen_dim(self) -> Dict[str, float]:
        self.activity['last_screen_dim_time'] = time.time()
        return self.activity.copy()

    async def update_keyboard_activity(self) -> Dict[str, float]:
        self.activity['last_keyboard_activity'] = time.time()
        await self.update_input_activity()
        return self.activity.copy()

    async def update_mouse_activity(self) -> Dict[str, float]:
        self.activity['last_mouse_activity'] = time.time()
        await self.update_input_activity()
        return self.activity.copy()

    async def update_window_change(self) -> Dict[str, float]:
        self.activity['last_window_change'] = time.time()
        return self.activity.copy()

    async def get_user_routine(self) -> Dict[str, Any]:
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
    
    async def is_user_active(self, idle_threshold_seconds: float = 300) -> bool:
        """Check if user is currently active.
        
        Args:
            idle_threshold_seconds (float): Time in seconds to consider user inactive
            
        Returns:
            bool: True if user is active, False otherwise
        """
        return (time.time() - self.activity['last_input_time']) < idle_threshold_seconds 

    def get_user_routines(self) -> Dict[str, Any]:
        """Get user routines based on platform"""
        try:
            routines = {
                'platform': self.platform_info['name'],
                'routines': {}
            }

            # Get platform-specific routines
            if self.platform_info['name'] == 'mac':
                routines['routines'] = self._get_mac_routines()
            elif self.platform_info['name'] == 'windows':
                routines['routines'] = self._get_windows_routines()
            elif self.platform_info['name'] == 'ubuntu':
                routines['routines'] = self._get_ubuntu_routines()
            else:
                routines['routines'] = self._get_default_routines()

            return routines

        except Exception as e:
            logger.error(f"Error getting user routines: {str(e)}")
            return {
                'platform': self.platform_info['name'],
                'error': str(e)
            }

    def _get_mac_routines(self) -> Dict[str, Any]:
        """Get macOS-specific routines"""
        return {
            'system': {
                'startup': ['Login', 'Dock', 'Menu Bar', 'Finder'],
                'shutdown': ['Save Work', 'Close Apps', 'Logout']
            },
            'apps': {
                'browser': ['Safari', 'Chrome', 'Firefox'],
                'productivity': ['Notes', 'Calendar', 'Mail', 'Messages'],
                'development': ['Terminal', 'Xcode', 'VS Code']
            },
            'shortcuts': {
                'system': ['Command+Space', 'Command+Tab', 'Command+Q'],
                'apps': ['Command+N', 'Command+S', 'Command+W']
            }
        }

    def _get_windows_routines(self) -> Dict[str, Any]:
        """Get Windows-specific routines"""
        return {
            'system': {
                'startup': ['Login', 'Start Menu', 'Taskbar', 'File Explorer'],
                'shutdown': ['Save Work', 'Close Apps', 'Logout']
            },
            'apps': {
                'browser': ['Edge', 'Chrome', 'Firefox'],
                'productivity': ['Notepad', 'Calendar', 'Mail', 'Teams'],
                'development': ['Command Prompt', 'PowerShell', 'VS Code']
            },
            'shortcuts': {
                'system': ['Windows+Space', 'Alt+Tab', 'Alt+F4'],
                'apps': ['Ctrl+N', 'Ctrl+S', 'Ctrl+W']
            }
        }

    def _get_ubuntu_routines(self) -> Dict[str, Any]:
        """Get Ubuntu-specific routines"""
        return {
            'system': {
                'startup': ['Login', 'GNOME Shell', 'Nautilus'],
                'shutdown': ['Save Work', 'Close Apps', 'Logout']
            },
            'apps': {
                'browser': ['Firefox', 'Chrome', 'Brave'],
                'productivity': ['Gedit', 'Calendar', 'Thunderbird'],
                'development': ['Terminal', 'VS Code', 'Sublime Text']
            },
            'shortcuts': {
                'system': ['Super+Space', 'Alt+Tab', 'Alt+F4'],
                'apps': ['Ctrl+N', 'Ctrl+S', 'Ctrl+W']
            }
        }

    def _get_default_routines(self) -> Dict[str, Any]:
        """Get default routines for unknown platforms.
        
        Returns:
            Dict[str, Any]: Dictionary containing default routines organized by category:
                - system: System-level routines (startup, shutdown)
                - apps: Application-specific routines
                - shortcuts: Common keyboard shortcuts
        """
        return {
            'system': {
                'startup': ['Login', 'Desktop', 'File Manager'],
                'shutdown': ['Save Work', 'Close Apps', 'Logout']
            },
            'apps': {
                'browser': ['Default Browser'],
                'productivity': ['Text Editor', 'Calendar', 'Mail'],
                'development': ['Terminal', 'Code Editor']
            },
            'shortcuts': {
                'system': ['Alt+Tab', 'Alt+F4'],
                'apps': ['Ctrl+N', 'Ctrl+S', 'Ctrl+W']
            }
        } 