import subprocess
import socket
import psutil
from typing import Dict, List, Optional

from ...common.network.network_interface import NetworkInterface

class MacOSNetwork(NetworkInterface):
    """macOS implementation of network operations."""
    
    def get_network_interfaces(self) -> List[Dict[str, str]]:
        """Get list of network interfaces."""
        interfaces = []
        for interface, addrs in psutil.net_if_addrs().items():
            interface_info = {'name': interface}
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    interface_info['ipv4'] = addr.address
                elif addr.family == socket.AF_INET6:
                    interface_info['ipv6'] = addr.address
                elif addr.family == psutil.AF_LINK:
                    interface_info['mac'] = addr.address
            interfaces.append(interface_info)
        return interfaces
    
    def get_interface_status(self, interface: str) -> Dict[str, str]:
        """Get status of a specific network interface."""
        try:
            result = subprocess.run(
                ['ifconfig', interface],
                capture_output=True,
                text=True,
                check=True
            )
            
            status = {
                'name': interface,
                'status': 'up' if 'status: active' in result.stdout else 'down',
                'ipv4': '',
                'ipv6': '',
                'mac': ''
            }
            
            for line in result.stdout.splitlines():
                if 'inet ' in line:
                    status['ipv4'] = line.split()[1]
                elif 'inet6 ' in line:
                    status['ipv6'] = line.split()[1]
                elif 'ether' in line:
                    status['mac'] = line.split()[1]
            
            return status
        except subprocess.CalledProcessError:
            return {'name': interface, 'status': 'unknown'}
    
    def get_ip_address(self, interface: str) -> str:
        """Get IP address of a specific interface."""
        try:
            result = subprocess.run(
                ['ipconfig', 'getifaddr', interface],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return ''
    
    def get_mac_address(self, interface: str) -> str:
        """Get MAC address of a specific interface."""
        try:
            result = subprocess.run(
                ['ifconfig', interface],
                capture_output=True,
                text=True,
                check=True
            )
            for line in result.stdout.splitlines():
                if 'ether' in line:
                    return line.split()[1]
            return ''
        except subprocess.CalledProcessError:
            return ''
    
    def get_connection_speed(self, interface: str) -> Dict[str, float]:
        """Get connection speed of a specific interface."""
        try:
            result = subprocess.run(
                ['networksetup', '-getinfo', interface],
                capture_output=True,
                text=True,
                check=True
            )
            
            speed_info = {'up': 0.0, 'down': 0.0}
            for line in result.stdout.splitlines():
                if 'Link Speed:' in line:
                    speed = line.split(':')[1].strip().split()[0]
                    speed_info['up'] = float(speed)
                    speed_info['down'] = float(speed)
            
            return speed_info
        except (subprocess.CalledProcessError, ValueError):
            return {'up': 0.0, 'down': 0.0}
    
    def get_connected_devices(self) -> List[Dict[str, str]]:
        """Get list of devices connected to the network."""
        try:
            result = subprocess.run(
                ['arp', '-a'],
                capture_output=True,
                text=True,
                check=True
            )
            
            devices = []
            for line in result.stdout.splitlines():
                if 'incomplete' not in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        devices.append({
                            'ip': parts[1].strip('()'),
                            'mac': parts[3] if len(parts) > 3 else '',
                            'interface': parts[5] if len(parts) > 5 else ''
                        })
            return devices
        except subprocess.CalledProcessError:
            return []
    
    def check_connectivity(self, host: str) -> bool:
        """Check connectivity to a specific host."""
        try:
            subprocess.run(
                ['ping', '-c', '1', host],
                capture_output=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError:
            return False
    
    def get_dns_servers(self) -> List[str]:
        """Get list of DNS servers."""
        try:
            result = subprocess.run(
                ['scutil', '--dns'],
                capture_output=True,
                text=True,
                check=True
            )
            
            dns_servers = []
            for line in result.stdout.splitlines():
                if 'nameserver[' in line:
                    server = line.split('[')[1].split(']')[0]
                    if server not in dns_servers:
                        dns_servers.append(server)
            return dns_servers
        except subprocess.CalledProcessError:
            return [] 