import platform
import psutil
from typing import Dict, List

from ...common.system.system_interface import SystemInterface

class MacOSSystem(SystemInterface):
    """macOS implementation of system operations."""
    
    def get_system_info(self) -> Dict[str, str]:
        """Get system information."""
        return {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version()
        }
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Get memory usage information."""
        memory = psutil.virtual_memory()
        return {
            'total': memory.total,
            'available': memory.available,
            'used': memory.used,
            'percent': memory.percent
        }
    
    def get_cpu_usage(self) -> float:
        """Get CPU usage percentage."""
        return psutil.cpu_percent(interval=1)
    
    def get_disk_usage(self) -> Dict[str, Dict[str, float]]:
        """Get disk usage information."""
        result = {}
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                result[partition.mountpoint] = {
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': usage.percent
                }
            except (PermissionError, OSError):
                continue
        return result
    
    def get_network_interfaces(self) -> List[Dict[str, str]]:
        """Get network interface information."""
        interfaces = []
        for interface, addrs in psutil.net_if_addrs().items():
            interface_info = {'name': interface}
            for addr in addrs:
                if addr.family == psutil.AF_INET:
                    interface_info['ipv4'] = addr.address
                elif addr.family == psutil.AF_INET6:
                    interface_info['ipv6'] = addr.address
                elif addr.family == psutil.AF_LINK:
                    interface_info['mac'] = addr.address
            interfaces.append(interface_info)
        return interfaces
    
    def get_running_processes(self) -> List[Dict[str, str]]:
        """Get list of running processes."""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'username', 'status']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return processes
    
    def execute_command(self, command: str) -> Dict[str, str]:
        """Execute a system command."""
        import subprocess
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                check=True
            )
            return {
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': str(result.returncode)
            }
        except subprocess.CalledProcessError as e:
            return {
                'stdout': e.stdout,
                'stderr': e.stderr,
                'returncode': str(e.returncode)
            } 