import logging
import socket
import subprocess
from typing import Any, Dict, List, Optional

import wmi
import win32com.client
from ..base_net_handler import BaseNetHandler

logger = logging.getLogger(__name__)

class WindowsNetHandler(BaseNetHandler):
    """Windows-specific networking handler implementation."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the Windows networking handler.
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(config)
        self._wmi = None
        self._shell = None
    
    def initialize(self) -> bool:
        """Initialize the Windows networking handler.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            self._wmi = wmi.WMI()
            self._shell = win32com.client.Dispatch("WScript.Shell")
            self._initialized = True
            return True
        except Exception as e:
            logging.error(f"Failed to initialize Windows networking handler: {e}")
            return False
    
    def cleanup(self) -> None:
        """Clean up networking resources."""
        self._wmi = None
        self._shell = None
        self._initialized = False
    
    def get_capabilities(self) -> Dict[str, bool]:
        """Get networking capabilities.
        
        Returns:
            Dict[str, bool]: Dictionary of available networking capabilities
        """
        return {
            'interface_control': True,
            'connection_control': True,
            'route_control': True,
            'dns_control': True,
            'firewall_control': True
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current networking status.
        
        Returns:
            Dict[str, Any]: Dictionary containing networking status information
        """
        try:
            if not self._initialized:
                return {'error': 'Handler not initialized'}
            
            return {
                'initialized': self._initialized,
                'hostname': self.get_hostname(),
                'interfaces': self.get_interfaces(),
                'connections': self.get_connections(),
                'routes': self.get_routes(),
                'dns_servers': self.get_dns_servers(),
                'platform': 'Windows'
            }
        except Exception as e:
            logging.error(f"Error getting networking status: {e}")
            return {'error': str(e)}
    
    def get_interfaces(self) -> List[Dict[str, Any]]:
        """Get list of network interfaces.
        
        Returns:
            List[Dict[str, Any]]: List of interface information dictionaries
        """
        try:
            if not self._initialized:
                return []
            
            interfaces = []
            for nic in self._wmi.Win32_NetworkAdapter(PhysicalAdapter=True):
                interface = {
                    'name': nic.Name,
                    'type': 'Wi-Fi' if 'Wireless' in nic.Name else 'Ethernet',
                    'enabled': nic.NetEnabled,
                    'ip_addresses': [],
                    'mac_address': nic.MACAddress,
                    'mtu': None,
                    'status': 'active' if nic.NetEnabled else 'disabled'
                }
                
                # Get IP addresses for this interface
                for nic_config in self._wmi.Win32_NetworkAdapterConfiguration(MACAddress=nic.MACAddress):
                    if nic_config.IPEnabled:
                        interface['ip_addresses'] = nic_config.IPAddress
                        interface['mtu'] = nic_config.MTUSize
                
                interfaces.append(interface)
            
            return interfaces
        except Exception as e:
            logging.error(f"Error getting network interfaces: {e}")
            return []
    
    def get_interface_info(self, interface: str) -> Dict[str, Any]:
        """Get information about a specific interface.
        
        Args:
            interface: Interface name to get information for
            
        Returns:
            Dict[str, Any]: Dictionary containing interface information
        """
        try:
            if not self._initialized:
                return {'error': 'Handler not initialized'}
            
            for nic in self._wmi.Win32_NetworkAdapter(PhysicalAdapter=True):
                if nic.Name == interface:
                    info = {
                        'name': nic.Name,
                        'type': 'Wi-Fi' if 'Wireless' in nic.Name else 'Ethernet',
                        'enabled': nic.NetEnabled,
                        'ip_addresses': [],
                        'mac_address': nic.MACAddress,
                        'mtu': None,
                        'status': 'active' if nic.NetEnabled else 'disabled'
                    }
                    
                    # Get IP configuration
                    for nic_config in self._wmi.Win32_NetworkAdapterConfiguration(MACAddress=nic.MACAddress):
                        if nic_config.IPEnabled:
                            info['ip_addresses'] = nic_config.IPAddress
                            info['mtu'] = nic_config.MTUSize
                    
                    return info
            
            return {'error': 'Interface not found'}
        except Exception as e:
            logging.error(f"Error getting interface info for {interface}: {e}")
            return {'error': str(e)}
    
    def get_connections(self) -> List[Dict[str, Any]]:
        """Get list of active network connections.
        
        Returns:
            List[Dict[str, Any]]: List of connection information dictionaries
        """
        try:
            if not self._initialized:
                return []
            
            # Use netstat to get active connections
            result = subprocess.run(
                ['netstat', '-an'],
                capture_output=True,
                text=True
            )
            
            connections = []
            for line in result.stdout.splitlines():
                if 'TCP' in line or 'UDP' in line:
                    parts = line.split()
                    if len(parts) >= 4:
                        connections.append({
                            'protocol': parts[0],
                            'local_address': parts[1],
                            'remote_address': parts[2],
                            'state': parts[3] if len(parts) > 3 else None
                        })
            
            return connections
        except Exception as e:
            logging.error(f"Error getting network connections: {e}")
            return []
    
    def get_connection_info(self, connection_id: str) -> Dict[str, Any]:
        """Get information about a specific connection.
        
        Args:
            connection_id: Connection ID to get information for
            
        Returns:
            Dict[str, Any]: Dictionary containing connection information
        """
        try:
            if not self._initialized:
                return {'error': 'Handler not initialized'}
            
            # Parse connection ID (format: protocol:local:remote)
            protocol, local, remote = connection_id.split(':')
            
            # Use netstat to get specific connection info
            result = subprocess.run(
                ['netstat', '-an'],
                capture_output=True,
                text=True
            )
            
            for line in result.stdout.splitlines():
                if protocol in line and local in line and remote in line:
                    parts = line.split()
                    return {
                        'protocol': parts[0],
                        'local_address': parts[1],
                        'remote_address': parts[2],
                        'state': parts[3] if len(parts) > 3 else None,
                        'pid': None  # Would need additional tools to get process ID
                    }
            
            return {'error': 'Connection not found'}
        except Exception as e:
            logging.error(f"Error getting connection info for {connection_id}: {e}")
            return {'error': str(e)}
    
    def get_routes(self) -> List[Dict[str, Any]]:
        """Get list of network routes.
        
        Returns:
            List[Dict[str, Any]]: List of route information dictionaries
        """
        try:
            if not self._initialized:
                return []
            
            # Use route print to get routing table
            result = subprocess.run(
                ['route', 'print'],
                capture_output=True,
                text=True
            )
            
            routes = []
            in_table = False
            
            for line in result.stdout.splitlines():
                if 'Network Destination' in line:
                    in_table = True
                    continue
                elif in_table and not line.strip():
                    in_table = False
                    continue
                
                if in_table:
                    parts = line.split()
                    if len(parts) >= 4:
                        routes.append({
                            'destination': parts[0],
                            'gateway': parts[2],
                            'interface': parts[3],
                            'metric': int(parts[4]) if len(parts) > 4 else None
                        })
            
            return routes
        except Exception as e:
            logging.error(f"Error getting network routes: {e}")
            return []
    
    def get_dns_servers(self) -> List[str]:
        """Get list of DNS servers.
        
        Returns:
            List[str]: List of DNS server addresses
        """
        try:
            if not self._initialized:
                return []
            
            servers = []
            for nic_config in self._wmi.Win32_NetworkAdapterConfiguration(IPEnabled=True):
                if nic_config.DNSServerSearchOrder:
                    servers.extend(nic_config.DNSServerSearchOrder)
            
            return list(set(servers))  # Remove duplicates
        except Exception as e:
            logging.error(f"Error getting DNS servers: {e}")
            return []
    
    def get_hostname(self) -> str:
        """Get system hostname.
        
        Returns:
            str: System hostname
        """
        try:
            if not self._initialized:
                return ''
            
            return socket.gethostname()
        except Exception as e:
            logging.error(f"Error getting hostname: {e}")
            return ''
    
    def get_ip_addresses(self) -> Dict[str, List[str]]:
        """Get all IP addresses for all interfaces.
        
        Returns:
            Dict[str, List[str]]: Dictionary mapping interface names to lists of IP addresses
        """
        try:
            if not self._initialized:
                return {}
            
            addresses = {}
            for nic in self._wmi.Win32_NetworkAdapter(PhysicalAdapter=True):
                for nic_config in self._wmi.Win32_NetworkAdapterConfiguration(MACAddress=nic.MACAddress):
                    if nic_config.IPEnabled:
                        addresses[nic.Name] = nic_config.IPAddress
            
            return addresses
        except Exception as e:
            logging.error(f"Error getting IP addresses: {e}")
            return {} 