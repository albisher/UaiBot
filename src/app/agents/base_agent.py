import logging
from typing import Any, Dict, List, Optional

from ..tools.tool_manager import ToolManager

logger = logging.getLogger(__name__)

class BaseAgent:
    """Base class for agents that use tools to execute commands."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the agent.
        
        Args:
            config: Optional configuration dictionary
        """
        self._config = config or {}
        self._tool_manager = ToolManager()
        self._initialized = False
    
    def initialize(self) -> bool:
        """Initialize the agent.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            # Register default tools
            self._register_default_tools()
            self._initialized = True
            return True
        except Exception as e:
            logger.error(f"Failed to initialize agent: {e}")
            return False
    
    def cleanup(self) -> None:
        """Clean up agent resources."""
        try:
            self._tool_manager.cleanup()
            self._initialized = False
        except Exception as e:
            logger.error(f"Error cleaning up agent: {e}")
    
    def _register_default_tools(self) -> None:
        """Register default tools for this agent."""
        # To be implemented by subclasses
        pass
    
    def register_tool(self, tool_class: type, config: Optional[Dict[str, Any]] = None) -> bool:
        """Register a new tool.
        
        Args:
            tool_class: Tool class to register
            config: Optional configuration for the tool
            
        Returns:
            bool: True if registration was successful, False otherwise
        """
        try:
            if not self._initialized:
                logger.error("Agent not initialized")
                return False
            
            return self._tool_manager.register_tool(tool_class, config)
        except Exception as e:
            logger.error(f"Error registering tool: {e}")
            return False
    
    def unregister_tool(self, tool_name: str) -> bool:
        """Unregister a tool.
        
        Args:
            tool_name: Name of the tool to unregister
            
        Returns:
            bool: True if unregistration was successful, False otherwise
        """
        try:
            if not self._initialized:
                logger.error("Agent not initialized")
                return False
            
            return self._tool_manager.unregister_tool(tool_name)
        except Exception as e:
            logger.error(f"Error unregistering tool: {e}")
            return False
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tools.
        
        Returns:
            List[str]: List of available tool names
        """
        try:
            if not self._initialized:
                logger.error("Agent not initialized")
                return []
            
            return self._tool_manager.get_available_tools()
        except Exception as e:
            logger.error(f"Error getting available tools: {e}")
            return []
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific tool.
        
        Args:
            tool_name: Name of the tool to get info for
            
        Returns:
            Optional[Dict[str, Any]]: Tool information if successful, None otherwise
        """
        try:
            if not self._initialized:
                logger.error("Agent not initialized")
                return None
            
            return self._tool_manager.get_tool_info(tool_name)
        except Exception as e:
            logger.error(f"Error getting tool info: {e}")
            return None
    
    def execute_command(self, tool_name: str, command: str, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a command using a specific tool.
        
        Args:
            tool_name: Name of the tool to use
            command: Command to execute
            args: Optional arguments for the command
            
        Returns:
            Dict[str, Any]: Result of the command execution
        """
        try:
            if not self._initialized:
                return {'error': 'Agent not initialized'}
            
            return self._tool_manager.execute_tool_command(tool_name, command, args)
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            return {'error': str(e)}
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about this agent.
        
        Returns:
            Dict[str, Any]: Dictionary containing agent information
        """
        return {
            'name': self.__class__.__name__,
            'initialized': self._initialized,
            'available_tools': self.get_available_tools(),
            'config': self._config
        } 