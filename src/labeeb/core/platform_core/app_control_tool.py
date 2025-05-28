"""
AppControlTool: Controls application launching and management for Labeeb agent.

This tool provides application control functionality while following:
- A2A (Agent-to-Agent) protocol for agent collaboration
- MCP (Multi-Channel Protocol) for unified channel support
- SmolAgents pattern for minimal, efficient implementation
"""

import logging
import platform
import subprocess
import time
from typing import Dict, Any, Optional
from labeeb.core.ai.tools.base_tool import BaseTool

logger = logging.getLogger(__name__)

class AppControlTool(BaseTool):
    """Tool for managing application launching and control."""
    
    def __init__(self, config: dict = None):
        """Initialize the app control tool.
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(
            name="app_control",
            description="Manages application launching and control for the Labeeb agent"
        )
        self.config = config or {}
        
        # Arabic translations for actions
        self.arabic_actions = {
            "افتح": "open",
            "اغلق": "close",
            "ركز": "focus",
            "صغر": "minimize",
            "كبر": "maximize"
        }
        
        # Platform-specific application names
        self.app_names = {
            "darwin": {  # macOS
                "calculator": "Calculator",
                "الحاسبة": "Calculator",
                "notes": "Notes",
                "الملاحظات": "Notes",
                "safari": "Safari",
                "سفاري": "Safari",
                "terminal": "Terminal",
                "الطرفية": "Terminal"
            },
            "win32": {  # Windows
                "calculator": "calc.exe",
                "الحاسبة": "calc.exe",
                "notepad": "notepad.exe",
                "المفكرة": "notepad.exe",
                "explorer": "explorer.exe",
                "المستكشف": "explorer.exe",
                "cmd": "cmd.exe",
                "موجه الأوامر": "cmd.exe"
            }
        }
        
        # Get platform-specific app names
        self.platform = platform.system().lower()
        self.platform_apps = self.app_names.get(self.platform, {})

    async def execute(self, action: str, app: str = None, **kwargs) -> Dict[str, Any]:
        """Execute the specified action on the application."""
        try:
            # Map Arabic action to English if needed
            action = self.arabic_actions.get(action, action)
            
            # Map Arabic app name to English if needed
            if app in self.platform_apps:
                app = self.platform_apps[app]
            
            if action == "open":
                return await self.open_app(app)
            elif action == "close":
                return await self.close_app(app)
            elif action == "focus":
                return await self.focus_app(app)
            elif action == "minimize":
                return await self.minimize_app(app)
            elif action == "maximize":
                return await self.maximize_app(app)
            else:
                return {"error": f"Unknown action: {action}"}
        except Exception as e:
            return {"error": str(e)}

    def get_available_actions(self) -> Dict[str, str]:
        """Get available actions for this tool.
        
        Returns:
            Dict[str, str]: Available actions and their descriptions
        """
        return {
            'open': 'Open an application',
            'close': 'Close an application',
            'focus': 'Focus on an application',
            'minimize': 'Minimize an application',
            'maximize': 'Maximize an application'
        }

    async def open_app(self, app_name: str) -> Dict[str, Any]:
        """Open an application."""
        try:
            if self.platform == "darwin":
                subprocess.run(["open", "-a", app_name])
            elif self.platform == "win32":
                subprocess.run(["start", app_name], shell=True)
            else:
                return {"error": f"Unsupported platform: {self.platform}"}
            return {"success": True, "app": app_name}
        except Exception as e:
            return {"error": str(e)}

    async def close_app(self, app_name: str) -> Dict[str, Any]:
        """Close an application."""
        try:
            if self.platform == "darwin":
                subprocess.run(["osascript", "-e", f'quit app "{app_name}"'])
            elif self.platform == "win32":
                subprocess.run(["taskkill", "/F", "/IM", app_name], shell=True)
            else:
                return {"error": f"Unsupported platform: {self.platform}"}
            return {"success": True, "app": app_name}
        except Exception as e:
            return {"error": str(e)}

    async def focus_app(self, app_name: str) -> Dict[str, Any]:
        """Focus an application window."""
        try:
            if self.platform == "darwin":
                subprocess.run(["osascript", "-e", f'tell application "{app_name}" to activate'])
            elif self.platform == "win32":
                subprocess.run(["powershell", "-command", f'(New-Object -ComObject WScript.Shell).AppActivate("{app_name}")'])
            else:
                return {"error": f"Unsupported platform: {self.platform}"}
            return {"success": True, "app": app_name}
        except Exception as e:
            return {"error": str(e)}

    async def minimize_app(self, app_name: str) -> Dict[str, Any]:
        """Minimize an application window."""
        try:
            if self.platform == "darwin":
                subprocess.run(["osascript", "-e", f'tell application "{app_name}" to set visible of window 1 to false'])
            elif self.platform == "win32":
                subprocess.run(["powershell", "-command", f'(New-Object -ComObject WScript.Shell).AppActivate("{app_name}"); (New-Object -ComObject WScript.Shell).SendKeys("% n")'])
            else:
                return {"error": f"Unsupported platform: {self.platform}"}
            return {"success": True, "app": app_name}
        except Exception as e:
            return {"error": str(e)}

    async def maximize_app(self, app_name: str) -> Dict[str, Any]:
        """Maximize an application window."""
        try:
            if self.platform == "darwin":
                subprocess.run(["osascript", "-e", f'tell application "{app_name}" to set visible of window 1 to true'])
            elif self.platform == "win32":
                subprocess.run(["powershell", "-command", f'(New-Object -ComObject WScript.Shell).AppActivate("{app_name}"); (New-Object -ComObject WScript.Shell).SendKeys("% x")'])
            else:
                return {"error": f"Unsupported platform: {self.platform}"}
            return {"success": True, "app": app_name}
        except Exception as e:
            return {"error": str(e)}

    async def forward(self, **kwargs) -> Dict[str, Any]:
        """Forward method to handle tool execution."""
        # Extract action and app from kwargs or params
        action = kwargs.get('action')
        if not action and 'params' in kwargs:
            action = kwargs['params'].get('action')
        
        app = kwargs.get('app')
        if not app and 'params' in kwargs:
            app = kwargs['params'].get('app')
        
        if not action:
            return {"error": "No action specified"}
        if not app:
            return {"error": "No app specified"}
        
        return await self.execute(action, app) 