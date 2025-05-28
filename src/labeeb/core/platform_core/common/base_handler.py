from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class BaseHandler(ABC):
    """Base class for platform-specific handlers"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the handler with optional configuration
        
        Args:
            config: Optional configuration dictionary
        """
        self._config = config or {}
        self._initialized = False
        
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the handler
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        pass
        
    @abstractmethod
    def cleanup(self) -> None:
        """Clean up resources used by the handler"""
        pass
        
    @abstractmethod
    def get_capabilities(self) -> Dict[str, bool]:
        """Get the capabilities of this handler
        
        Returns:
            Dict[str, bool]: Dictionary of capability names and their availability
        """
        pass
        
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the handler
        
        Returns:
            Dict[str, Any]: Dictionary containing status information
        """
        pass
        
    def is_initialized(self) -> bool:
        """Check if the handler is initialized
        
        Returns:
            bool: True if initialized, False otherwise
        """
        return self._initialized
        
    def get_config(self) -> Dict[str, Any]:
        """Get the current configuration
        
        Returns:
            Dict[str, Any]: Current configuration dictionary
        """
        return self._config.copy()
        
    def update_config(self, new_config: Dict[str, Any]) -> None:
        """Update the configuration
        
        Args:
            new_config: New configuration dictionary
        """
        self._config.update(new_config) 