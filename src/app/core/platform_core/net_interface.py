import logging
import sys
from typing import Any, Dict, List, Optional

from .base_net_handler import BaseNetHandler
from .macos.net_handler import MacOSNetHandler
from .windows.net_handler import WindowsNetHandler
from .linux.net_handler import LinuxNetHandler

logger = logging.getLogger(__name__)

class NetInterface:
    """Platform-agnostic networking interface that manages platform-specific handlers."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the networking interface.
        
        Args:
            config: Optional configuration dictionary
        """
        self._handler = self._initialize_handler(config)
    
    def _initialize_handler(self, config: Optional[Dict[str, Any]] = None) -> BaseNetHandler:
        """Initialize the appropriate platform-specific handler.
        
        Args:
            config: Optional configuration dictionary
            
        Returns:
            BaseNetHandler: Platform-specific networking handler
            
        Raises:
            RuntimeError: If the platform is not supported
        """
        platform = sys.platform
        
        if platform == 'darwin':
            handler = MacOSNetHandler(config)
        elif platform == 'win32':
            handler = WindowsNetHandler(config)
        elif platform.startswith('linux'):
            handler = LinuxNetHandler(config)
        else:
            raise RuntimeError(f"Unsupported platform: {platform}")
        
        if not handler.initialize():
            raise RuntimeError(f"Failed to initialize networking handler for {platform}")
        
        return handler
    
    def get_interfaces(self) -> List[Dict[str, Any]]:
        """Get list of network interfaces.
        
        Returns:
            List[Dict[str, Any]]: List of interface information dictionaries
        """
        return self._handler.get_interfaces()
    
    def get_interface_info(self, interface: str) -> Dict[str, Any]:
        """Get information about a specific interface.
        
        Args:
            interface: Interface name to get information for
            
        Returns:
            Dict[str, Any]: Dictionary containing interface information
        """
        return self._handler.get_interface_info(interface)
    
    def get_connections(self) -> List[Dict[str, Any]]:
        """Get list of active network connections.
        
        Returns:
            List[Dict[str, Any]]: List of connection information dictionaries
        """
        return self._handler.get_connections()
    
    def get_connection_info(self, connection_id: str) -> Dict[str, Any]:
        """Get information about a specific connection.
        
        Args:
            connection_id: Connection ID to get information for
            
        Returns:
            Dict[str, Any]: Dictionary containing connection information
        """
        return self._handler.get_connection_info(connection_id)
    
    def get_routes(self) -> List[Dict[str, Any]]:
        """Get list of network routes.
        
        Returns:
            List[Dict[str, Any]]: List of route information dictionaries
        """
        return self._handler.get_routes()
    
    def get_dns_servers(self) -> List[str]:
        """Get list of DNS servers.
        
        Returns:
            List[str]: List of DNS server addresses
        """
        return self._handler.get_dns_servers()
    
    def get_hostname(self) -> str:
        """Get system hostname.
        
        Returns:
            str: System hostname
        """
        return self._handler.get_hostname()
    
    def get_ip_addresses(self) -> Dict[str, List[str]]:
        """Get all IP addresses for all interfaces.
        
        Returns:
            Dict[str, List[str]]: Dictionary mapping interface names to lists of IP addresses
        """
        return self._handler.get_ip_addresses()
    
    def get_status(self) -> Dict[str, Any]:
        """Get current networking status.
        
        Returns:
            Dict[str, Any]: Dictionary containing networking status information
        """
        return self._handler.get_status()
    
    def get_capabilities(self) -> Dict[str, bool]:
        """Get networking capabilities.
        
        Returns:
            Dict[str, bool]: Dictionary of available networking capabilities
        """
        return self._handler.get_capabilities()
    
    def cleanup(self) -> None:
        """Clean up networking resources."""
        self._handler.cleanup() 