"""
DateTime Tool Implementation

This module provides the DateTimeTool for handling date and time operations,
implementing A2A (Agent-to-Agent), MCP (Model Context Protocol), and SmolAgents patterns.
"""
from datetime import datetime, timedelta
from typing import Any, Dict
from .base_tool import BaseTool

class DateTimeTool(BaseTool):
    """Tool for handling date and time operations."""
    
    def __init__(self):
        """Initialize the DateTimeTool."""
        super().__init__(
            name="DateTimeTool",
            description="Handles date and time operations including formatting, parsing, and calculations"
        )
    
    async def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a date/time operation.
        
        Args:
            action (str): The action to execute
            **kwargs: Additional arguments for the action
            
        Returns:
            Dict[str, Any]: The result of the operation
        """
        try:
            if not self.validate_input(action, **kwargs):
                return self.handle_error(ValueError("Invalid input"))
            
            if action == "get_current_time":
                return self._get_current_time(**kwargs)
            elif action == "format_datetime":
                return self._format_datetime(**kwargs)
            elif action == "parse_datetime":
                return self._parse_datetime(**kwargs)
            elif action == "add_time":
                return self._add_time(**kwargs)
            elif action == "subtract_time":
                return self._subtract_time(**kwargs)
            else:
                return self.handle_error(ValueError(f"Unknown action: {action}"))
                
        except Exception as e:
            return self.handle_error(e)
    
    def get_available_actions(self) -> Dict[str, str]:
        """
        Get available date/time operations.
        
        Returns:
            Dict[str, str]: Available operations and their descriptions
        """
        return {
            "get_current_time": "Get the current date and time",
            "format_datetime": "Format a datetime object into a string",
            "parse_datetime": "Parse a datetime string into a datetime object",
            "add_time": "Add time to a datetime object",
            "subtract_time": "Subtract time from a datetime object"
        }
    
    def _get_current_time(self, **kwargs) -> Dict[str, Any]:
        """Get the current date and time."""
        now = datetime.now()
        return {
            "datetime": now.isoformat(),
            "timestamp": now.timestamp(),
            "formatted": now.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def _format_datetime(self, dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S", **kwargs) -> Dict[str, Any]:
        """Format a datetime object."""
        return {
            "formatted": dt.strftime(format_str)
        }
    
    def _parse_datetime(self, dt_str: str, format_str: str = "%Y-%m-%d %H:%M:%S", **kwargs) -> Dict[str, Any]:
        """Parse a datetime string."""
        dt = datetime.strptime(dt_str, format_str)
        return {
            "datetime": dt.isoformat(),
            "timestamp": dt.timestamp()
        }
    
    def _add_time(self, dt: datetime, days: int = 0, hours: int = 0, minutes: int = 0, **kwargs) -> Dict[str, Any]:
        """Add time to a datetime object."""
        delta = timedelta(days=days, hours=hours, minutes=minutes)
        result = dt + delta
        return {
            "datetime": result.isoformat(),
            "timestamp": result.timestamp()
        }
    
    def _subtract_time(self, dt: datetime, days: int = 0, hours: int = 0, minutes: int = 0, **kwargs) -> Dict[str, Any]:
        """Subtract time from a datetime object."""
        delta = timedelta(days=days, hours=hours, minutes=minutes)
        result = dt - delta
        return {
            "datetime": result.isoformat(),
            "timestamp": result.timestamp()
        } 