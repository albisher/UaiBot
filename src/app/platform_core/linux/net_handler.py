import logging
import socket
import subprocess
from typing import Any, Dict, List, Optional

from ..base_net_handler import BaseNetHandler

logger = logging.getLogger(__name__)

class LinuxNetHandler(BaseNetHandler):
    """Linux-specific networking handler implementation."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the Linux networking handler.
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(config)
    
    def initialize(self) -> bool:
        """Initialize the Linux networking handler.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            # Linux-specific initialization if needed
            self._initialized = True
            return True
        except Exception as e:
            logging.error(f"Failed to initialize Linux networking handler: {e}")
            return False
    
    def cleanup(self) -> None:
        """Clean up networking resources."""
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
                'platform': 'Linux'
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
            
            # Use ip link to get interface list
            result = subprocess.run(
                ['ip', 'link', 'show'],
                capture_output=True,
                text=True
            )
            
            interfaces = []
            for line in result.stdout.splitlines():
                if ':' in line:
                    parts = line.split(':')
                    if len(parts) >= 2:
                        interface = parts[1].strip()
                        if interface != 'lo':  # Skip loopback
                            interfaces.append(self.get_interface_info(interface))
            
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
            
            # Get interface type
            result = subprocess.run(
                ['iwconfig', interface],
                capture_output=True,
                text=True
            )
            
            is_wireless = 'IEEE 802.11' in result.stdout
            
            # Get interface details
            result = subprocess.run(
                ['ip', 'link', 'show', interface],
                capture_output=True,
                text=True
            )
            
            info = {
                'name': interface,
                'type': 'Wi-Fi' if is_wireless else 'Ethernet',
                'enabled': 'state UP' in result.stdout,
                'ip_addresses': self.get_ip_addresses().get(interface, []),
                'mac_address': None,
                'mtu': None,
                'status': 'active' if 'state UP' in result.stdout else 'disabled'
            }
            
            # Parse ip link output
            for line in result.stdout.splitlines():
                if 'link/ether' in line:
                    info['mac_address'] = line.split('link/ether')[1].split()[0]
                elif 'mtu' in line:
                    info['mtu'] = int(line.split('mtu')[1].split()[0])
            
            return info
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
                ['netstat', '-tun'],
                capture_output=True,
                text=True
            )
            
            connections = []
            for line in result.stdout.splitlines():
                if 'tcp' in line or 'udp' in line:
                    parts = line.split()
                    if len(parts) >= 4:
                        connections.append({
                            'protocol': parts[0],
                            'local_address': parts[3],
                            'remote_address': parts[4] if len(parts) > 4 else None,
                            'state': parts[5] if len(parts) > 5 else None
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
                ['netstat', '-tun'],
                capture_output=True,
                text=True
            )
            
            for line in result.stdout.splitlines():
                if protocol in line and local in line and remote in line:
                    parts = line.split()
                    return {
                        'protocol': parts[0],
                        'local_address': parts[3],
                        'remote_address': parts[4],
                        'state': parts[5] if len(parts) > 5 else None,
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
            
            # Use ip route to get routing table
            result = subprocess.run(
                ['ip', 'route', 'show'],
                capture_output=True,
                text=True
            )
            
            routes = []
            for line in result.stdout.splitlines():
                parts = line.split()
                if len(parts) >= 3:
                    route = {
                        'destination': parts[0],
                        'gateway': None,
                        'interface': None,
                        'metric': None
                    }
                    
                    for i, part in enumerate(parts):
                        if part == 'via':
                            route['gateway'] = parts[i + 1]
                        elif part == 'dev':
                            route['interface'] = parts[i + 1]
                        elif part == 'metric':
                            route['metric'] = int(parts[i + 1])
                    
                    routes.append(route)
            
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
            
            # Read from resolv.conf
            with open('/etc/resolv.conf', 'r') as f:
                servers = []
                for line in f:
                    if line.startswith('nameserver'):
                        server = line.split()[1]
                        if server not in servers:
                            servers.append(server)
            
            return servers
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
            
            # Use ip addr to get IP addresses
            result = subprocess.run(
                ['ip', 'addr', 'show'],
                capture_output=True,
                text=True
            )
            
            addresses = {}
            current_interface = None
            
            for line in result.stdout.splitlines():
                if ':' in line and not line.startswith(' '):
                    current_interface = line.split(':')[1].strip()
                    addresses[current_interface] = []
                elif current_interface and 'inet ' in line:
                    ip = line.split('inet ')[1].split('/')[0]
                    addresses[current_interface].append(ip)
            
            return addresses
        except Exception as e:
            logging.error(f"Error getting IP addresses: {e}")
            return {} 