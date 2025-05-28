from abc import ABC, abstractmethod
from typing import Dict, List, Optional

class SystemInterface(ABC):
    """Interface for system-related operations."""
    
    @abstractmethod
    def get_system_info(self) -> Dict[str, str]:
        """Get system information."""
        pass
    
    @abstractmethod
    def get_memory_usage(self) -> Dict[str, float]:
        """Get memory usage information."""
        pass
    
    @abstractmethod
    def get_cpu_usage(self) -> float:
        """Get CPU usage percentage."""
        pass
    
    @abstractmethod
    def get_disk_usage(self) -> Dict[str, Dict[str, float]]:
        """Get disk usage information."""
        pass
    
    @abstractmethod
    def get_network_interfaces(self) -> List[Dict[str, str]]:
        """Get network interface information."""
        pass
    
    @abstractmethod
    def get_running_processes(self) -> List[Dict[str, str]]:
        """Get list of running processes."""
        pass
    
    @abstractmethod
    def execute_command(self, command: str) -> Dict[str, str]:
        """Execute a system command."""
        pass 