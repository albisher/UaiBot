"""
Base Tool Implementation

This module provides the BaseTool class that serves as the foundation for all tools,
implementing A2A (Agent-to-Agent), MCP (Model Context Protocol), and SmolAgents patterns.
"""
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class BaseTool(ABC):
    """Base class for all tools."""
    
    def __init__(self, name: str, description: str):
        """
        Initialize the base tool.
        
        Args:
            name (str): The name of the tool
            description (str): A description of the tool's functionality
        """
        self.name = name
        self.description = description
        self._operation_history = []
        self._max_history = 100
    
    @abstractmethod
    async def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a tool action.
        
        Args:
            action (str): The action to execute
            **kwargs: Additional arguments for the action
            
        Returns:
            Dict[str, Any]: The result of the operation
        """
        pass
    
    @abstractmethod
    def get_available_actions(self) -> Dict[str, str]:
        """
        Get available actions for this tool.
        
        Returns:
            Dict[str, str]: Available actions and their descriptions
        """
        pass
    
    def validate_input(self, action: str, **kwargs) -> bool:
        """
        Validate input parameters for an action.
        
        Args:
            action (str): The action to validate
            **kwargs: The parameters to validate
            
        Returns:
            bool: True if input is valid, False otherwise
        """
        try:
            # Check if action exists
            if action not in self.get_available_actions():
                logger.warning(f"Invalid action: {action}")
                return False
            
            # Add custom validation logic in subclasses
            return True
        except Exception as e:
            logger.error(f"Error validating input: {e}")
            return False
    
    def handle_error(self, error: Exception) -> Dict[str, Any]:
        """
        Handle errors in a consistent way.
        
        Args:
            error (Exception): The error to handle
            
        Returns:
            Dict[str, Any]: Error information
        """
        error_info = {
            "error": str(error),
            "type": type(error).__name__,
            "tool": self.name
        }
        
        logger.error(f"Tool error: {error_info}")
        return error_info
    
    def log_execution(self, action: str, result: Dict[str, Any]) -> None:
        """
        Log tool execution details.
        
        Args:
            action (str): The action that was executed
            result (Dict[str, Any]): The result of the execution
        """
        log_entry = {
            "action": action,
            "result": result,
            "timestamp": self._get_timestamp()
        }
        
        self._operation_history.append(log_entry)
        if len(self._operation_history) > self._max_history:
            self._operation_history.pop(0)
    
    def get_execution_history(self) -> Dict[str, Any]:
        """
        Get the execution history of the tool.
        
        Returns:
            Dict[str, Any]: The execution history
        """
        return {
            "tool": self.name,
            "history": self._operation_history,
            "count": len(self._operation_history)
        }
    
    def clear_history(self) -> None:
        """Clear the execution history."""
        self._operation_history = []
    
    def _get_timestamp(self) -> str:
        """
        Get current timestamp in ISO format.
        
        Returns:
            str: Current timestamp
        """
        from datetime import datetime
        return datetime.utcnow().isoformat() 