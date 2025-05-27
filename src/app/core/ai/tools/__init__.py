"""
Tool Registry Implementation

This module provides the ToolRegistry class for managing all tools,
implementing A2A (Agent-to-Agent), MCP (Model Context Protocol), and SmolAgents patterns.
"""
import logging
from typing import Any, Dict, Optional, Type
from .base_tool import BaseTool
from .datetime_tool import DateTimeTool
from .system_resource_tool import SystemResourceTool
from .file_tool import FileTool
from .network_tool import NetworkTool
from .process_tool import ProcessTool
from .text_tool import TextTool
from .web_tool import WebTool

logger = logging.getLogger(__name__)

class ToolRegistry:
    """Registry for managing all tools."""
    
    _tools: Dict[str, BaseTool] = {}
    
    @classmethod
    def register(cls, tool_class: Type[BaseTool]) -> Type[BaseTool]:
        """
        Register a tool class.
        
        Args:
            tool_class (Type[BaseTool]): The tool class to register
            
        Returns:
            Type[BaseTool]: The registered tool class
        """
        tool = tool_class()
        cls._tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")
        return tool_class
    
    @classmethod
    def get_tool(cls, name: str) -> Optional[BaseTool]:
        """
        Get a tool by name.
        
        Args:
            name (str): The name of the tool
            
        Returns:
            Optional[BaseTool]: The tool if found, None otherwise
        """
        return cls._tools.get(name)
    
    @classmethod
    def get_all_tools(cls) -> Dict[str, BaseTool]:
        """
        Get all registered tools.
        
        Returns:
            Dict[str, BaseTool]: All registered tools
        """
        return cls._tools.copy()
    
    @classmethod
    def get_tool_capabilities(cls) -> Dict[str, Dict[str, Any]]:
        """
        Get capabilities of all tools.
        
        Returns:
            Dict[str, Dict[str, Any]]: Capabilities of all tools
        """
        capabilities = {}
        for name, tool in cls._tools.items():
            capabilities[name] = {
                "description": tool.description,
                "actions": tool.get_available_actions()
            }
        return capabilities

# Register all tools
DateTimeTool = ToolRegistry.register(DateTimeTool)
SystemResourceTool = ToolRegistry.register(SystemResourceTool)
FileTool = ToolRegistry.register(FileTool)
NetworkTool = ToolRegistry.register(NetworkTool)
ProcessTool = ToolRegistry.register(ProcessTool)
TextTool = ToolRegistry.register(TextTool)
WebTool = ToolRegistry.register(WebTool)
