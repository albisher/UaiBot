from abc import ABC, abstractmethod
from typing import Dict, List, Optional

class NetworkInterface(ABC):
    """Interface for network-related operations."""
    
    @abstractmethod
    def get_network_interfaces(self) -> List[Dict[str, str]]:
        """Get list of network interfaces."""
        pass
    
    @abstractmethod
    def get_interface_status(self, interface: str) -> Dict[str, str]:
        """Get status of a specific network interface."""
        pass
    
    @abstractmethod
    def get_ip_address(self, interface: str) -> str:
        """Get IP address of a specific interface."""
        pass
    
    @abstractmethod
    def get_mac_address(self, interface: str) -> str:
        """Get MAC address of a specific interface."""
        pass
    
    @abstractmethod
    def get_connection_speed(self, interface: str) -> Dict[str, float]:
        """Get connection speed of a specific interface."""
        pass
    
    @abstractmethod
    def get_connected_devices(self) -> List[Dict[str, str]]:
        """Get list of devices connected to the network."""
        pass
    
    @abstractmethod
    def check_connectivity(self, host: str) -> bool:
        """Check connectivity to a specific host."""
        pass
    
    @abstractmethod
    def get_dns_servers(self) -> List[str]:
        """Get list of DNS servers."""
        pass 