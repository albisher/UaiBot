import logging
from typing import Any, Dict, List, Optional, Type

from .base_tool import BaseAgentTool

logger = logging.getLogger(__name__)

class ToolManager:
    """Manager class for agent tools that handles registration and management."""
    
    def __init__(self):
        """Initialize the tool manager."""
        self._tools: Dict[str, BaseAgentTool] = {}
        self._tool_classes: Dict[str, Type[BaseAgentTool]] = {}
    
    def register_tool(self, tool_class: Type[BaseAgentTool], config: Optional[Dict[str, Any]] = None) -> bool:
        """Register a new tool class.
        
        Args:
            tool_class: Tool class to register
            config: Optional configuration for the tool
            
        Returns:
            bool: True if registration was successful, False otherwise
        """
        try:
            tool_name = tool_class.__name__
            if tool_name in self._tool_classes:
                logger.warning(f"Tool {tool_name} is already registered")
                return False
            
            self._tool_classes[tool_name] = tool_class
            return True
        except Exception as e:
            logger.error(f"Error registering tool {tool_class.__name__}: {e}")
            return False
    
    def unregister_tool(self, tool_name: str) -> bool:
        """Unregister a tool class.
        
        Args:
            tool_name: Name of the tool to unregister
            
        Returns:
            bool: True if unregistration was successful, False otherwise
        """
        try:
            if tool_name not in self._tool_classes:
                logger.warning(f"Tool {tool_name} is not registered")
                return False
            
            # Clean up any existing instances
            if tool_name in self._tools:
                self._tools[tool_name].cleanup()
                del self._tools[tool_name]
            
            del self._tool_classes[tool_name]
            return True
        except Exception as e:
            logger.error(f"Error unregistering tool {tool_name}: {e}")
            return False
    
    def get_tool(self, tool_name: str, config: Optional[Dict[str, Any]] = None) -> Optional[BaseAgentTool]:
        """Get an instance of a tool.
        
        Args:
            tool_name: Name of the tool to get
            config: Optional configuration for the tool
            
        Returns:
            Optional[BaseAgentTool]: Tool instance if successful, None otherwise
        """
        try:
            if tool_name not in self._tool_classes:
                logger.warning(f"Tool {tool_name} is not registered")
                return None
            
            # Return existing instance if available
            if tool_name in self._tools:
                return self._tools[tool_name]
            
            # Create new instance
            tool = self._tool_classes[tool_name](config)
            if not tool.initialize():
                logger.error(f"Failed to initialize tool {tool_name}")
                return None
            
            self._tools[tool_name] = tool
            return tool
        except Exception as e:
            logger.error(f"Error getting tool {tool_name}: {e}")
            return None
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tool names.
        
        Returns:
            List[str]: List of available tool names
        """
        return list(self._tool_classes.keys())
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific tool.
        
        Args:
            tool_name: Name of the tool to get info for
            
        Returns:
            Optional[Dict[str, Any]]: Tool information if successful, None otherwise
        """
        tool = self.get_tool(tool_name)
        if not tool:
            return None
        return tool.get_tool_info()
    
    def execute_tool_command(self, tool_name: str, command: str, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a command using a specific tool.
        
        Args:
            tool_name: Name of the tool to use
            command: Command to execute
            args: Optional arguments for the command
            
        Returns:
            Dict[str, Any]: Result of the command execution
        """
        try:
            tool = self.get_tool(tool_name)
            if not tool:
                return {'error': f'Tool {tool_name} not available'}
            
            if not tool.validate_command(command, args):
                return {'error': f'Invalid command or arguments for tool {tool_name}'}
            
            return tool.execute(command, args)
        except Exception as e:
            logger.error(f"Error executing command {command} on tool {tool_name}: {e}")
            return {'error': str(e)}
    
    def cleanup(self) -> None:
        """Clean up all tool instances."""
        for tool_name, tool in self._tools.items():
            try:
                tool.cleanup()
            except Exception as e:
                logger.error(f"Error cleaning up tool {tool_name}: {e}")
        
        self._tools.clear() 