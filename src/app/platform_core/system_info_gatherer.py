"""System information gathering and monitoring module for the Labeeb platform.

This module provides functionality for:
- Collecting system hardware information
- Monitoring system resources (CPU, memory, disk)
- Gathering OS-specific information
- Tracking system performance metrics
- Providing system health status

The module implements platform-specific system information gathering while
maintaining a consistent interface across different operating systems.
"""

import platform
import psutil
from typing import Dict, Any
from labeeb.typing import SystemInfo

class SystemInfoGatherer:
    """Base class for gathering system information in a platform-agnostic way."""
    
    def get_system_info(self) -> SystemInfo:
        """Get system information.
        
        Returns:
            A dictionary containing system information
        """
        return {
            'platform': self._get_platform_info(),
            'cpu': self._get_cpu_info(),
            'memory': self._get_memory_info(),
            'disk': self._get_disk_info(),
            'network': self._get_network_info(),
        }
    
    def _get_platform_info(self) -> Dict[str, str]:
        """Get platform-specific information."""
        return {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
        }
    
    def _get_cpu_info(self) -> Dict[str, Any]:
        """Get CPU information."""
        return {
            'physical_cores': psutil.cpu_count(logical=False),
            'total_cores': psutil.cpu_count(logical=True),
            'max_frequency': psutil.cpu_freq().max if psutil.cpu_freq() else None,
            'min_frequency': psutil.cpu_freq().min if psutil.cpu_freq() else None,
            'current_frequency': psutil.cpu_freq().current if psutil.cpu_freq() else None,
            'cpu_usage_per_core': [x for x in psutil.cpu_percent(percpu=True, interval=1)],
            'total_cpu_usage': psutil.cpu_percent(interval=1),
        }
    
    def _get_memory_info(self) -> Dict[str, int]:
        """Get memory information."""
        memory = psutil.virtual_memory()
        return {
            'total': memory.total,
            'available': memory.available,
            'used': memory.used,
            'percentage': memory.percent,
        }
    
    def _get_disk_info(self) -> Dict[str, int]:
        """Get disk information."""
        disk = psutil.disk_usage('/')
        return {
            'total': disk.total,
            'used': disk.used,
            'free': disk.free,
            'percentage': disk.percent,
        }
    
    def _get_network_info(self) -> Dict[str, int]:
        """Get network information."""
        network = psutil.net_io_counters()
        return {
            'bytes_sent': network.bytes_sent,
            'bytes_received': network.bytes_recv,
            'packets_sent': network.packets_sent,
            'packets_received': network.packets_recv,
        } 