from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

class BaseAgentTool(ABC):
    """Base class for agent tools that defines the common interface."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the agent tool.
        
        Args:
            config: Optional configuration dictionary
        """
        self._config = config or {}
        self._initialized = False
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the tool.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """Clean up resources used by the tool."""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> Dict[str, bool]:
        """Get the capabilities of this tool.
        
        Returns:
            Dict[str, bool]: Dictionary of capability names and their availability
        """
        pass
    
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the tool.
        
        Returns:
            Dict[str, Any]: Dictionary containing status information
        """
        pass
    
    @abstractmethod
    def execute(self, command: str, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a command using this tool.
        
        Args:
            command: Command to execute
            args: Optional arguments for the command
            
        Returns:
            Dict[str, Any]: Result of the command execution
        """
        pass
    
    @abstractmethod
    def get_available_commands(self) -> List[str]:
        """Get list of available commands for this tool.
        
        Returns:
            List[str]: List of available command names
        """
        pass
    
    @abstractmethod
    def get_command_help(self, command: str) -> Dict[str, Any]:
        """Get help information for a specific command.
        
        Args:
            command: Command name to get help for
            
        Returns:
            Dict[str, Any]: Help information for the command
        """
        pass
    
    @abstractmethod
    def validate_command(self, command: str, args: Optional[Dict[str, Any]] = None) -> bool:
        """Validate if a command and its arguments are valid.
        
        Args:
            command: Command to validate
            args: Optional arguments to validate
            
        Returns:
            bool: True if command and arguments are valid, False otherwise
        """
        pass
    
    def is_initialized(self) -> bool:
        """Check if the tool is initialized.
        
        Returns:
            bool: True if initialized, False otherwise
        """
        return self._initialized
    
    def get_config(self) -> Dict[str, Any]:
        """Get the current configuration.
        
        Returns:
            Dict[str, Any]: Current configuration dictionary
        """
        return self._config.copy()
    
    def update_config(self, new_config: Dict[str, Any]) -> None:
        """Update the configuration.
        
        Args:
            new_config: New configuration dictionary
        """
        self._config.update(new_config)
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get information about this tool.
        
        Returns:
            Dict[str, Any]: Dictionary containing tool information
        """
        return {
            'name': self.__class__.__name__,
            'initialized': self._initialized,
            'capabilities': self.get_capabilities(),
            'available_commands': self.get_available_commands(),
            'config': self._config
        } 