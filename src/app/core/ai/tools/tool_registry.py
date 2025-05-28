"""
Tool Registry for Labeeb AI system.

This module provides the ToolRegistry class for managing all available tools.
"""
from typing import Dict, Type, Optional
from .base_tool import BaseTool

class ToolRegistry:
    """Registry for all available tools."""
    
    _tools: Dict[str, Type[BaseTool]] = {}
    
    @classmethod
    def register(cls, tool_class: Type[BaseTool]) -> None:
        """Register a tool class.
        
        Args:
            tool_class: Tool class to register
        """
        # Instantiate the tool to get its name
        tool_instance = tool_class()
        cls._tools[tool_instance.name] = tool_class
    
    @classmethod
    def get_tool(cls, tool_name: str) -> Optional[Type[BaseTool]]:
        """Get a tool class by name.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Optional[Type[BaseTool]]: Tool class if found, None otherwise
        """
        return cls._tools.get(tool_name)
    
    @classmethod
    def get_all_tools(cls) -> Dict[str, Type[BaseTool]]:
        """Get all registered tools.
        
        Returns:
            Dict[str, Type[BaseTool]]: Dictionary of tool names to tool classes
        """
        return cls._tools.copy() 