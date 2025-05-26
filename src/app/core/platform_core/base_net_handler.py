from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

class BaseNetHandler(ABC):
    """Base class for platform-specific networking handlers"""
    
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
        
    @abstractmethod
    def get_interfaces(self) -> List[Dict[str, Any]]:
        """Get list of network interfaces
        
        Returns:
            List[Dict[str, Any]]: List of interface information dictionaries
        """
        pass
        
    @abstractmethod
    def get_interface_info(self, interface: str) -> Dict[str, Any]:
        """Get information about a specific interface
        
        Args:
            interface: Interface name to get information for
            
        Returns:
            Dict[str, Any]: Dictionary containing interface information
        """
        pass
        
    @abstractmethod
    def get_connections(self) -> List[Dict[str, Any]]:
        """Get list of active network connections
        
        Returns:
            List[Dict[str, Any]]: List of connection information dictionaries
        """
        pass
        
    @abstractmethod
    def get_connection_info(self, connection_id: str) -> Dict[str, Any]:
        """Get information about a specific connection
        
        Args:
            connection_id: Connection ID to get information for
            
        Returns:
            Dict[str, Any]: Dictionary containing connection information
        """
        pass
        
    @abstractmethod
    def get_routes(self) -> List[Dict[str, Any]]:
        """Get list of network routes
        
        Returns:
            List[Dict[str, Any]]: List of route information dictionaries
        """
        pass
        
    @abstractmethod
    def get_dns_servers(self) -> List[str]:
        """Get list of DNS servers
        
        Returns:
            List[str]: List of DNS server addresses
        """
        pass
        
    @abstractmethod
    def get_hostname(self) -> str:
        """Get system hostname
        
        Returns:
            str: System hostname
        """
        pass
        
    @abstractmethod
    def get_ip_addresses(self) -> Dict[str, List[str]]:
        """Get all IP addresses for all interfaces
        
        Returns:
            Dict[str, List[str]]: Dictionary mapping interface names to lists of IP addresses
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