from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

class PlatformInterface(ABC):
    """Base interface for platform-specific implementations."""
    
    @abstractmethod
    def get_platform_name(self) -> str:
        """Get the name of the current platform."""
        pass
    
    @abstractmethod
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information."""
        pass
    
    @abstractmethod
    def execute_command(self, command: str) -> Dict[str, Any]:
        """Execute a system command."""
        pass
    
    @abstractmethod
    def get_file_path(self, path: str) -> str:
        """Get platform-specific file path."""
        pass
    
    @abstractmethod
    def get_environment_variable(self, name: str) -> Optional[str]:
        """Get environment variable value."""
        pass
    
    @abstractmethod
    def set_environment_variable(self, name: str, value: str) -> bool:
        """Set environment variable value."""
        pass
    
    @abstractmethod
    def get_process_list(self) -> List[Dict[str, Any]]:
        """Get list of running processes."""
        pass
    
    @abstractmethod
    def get_network_info(self) -> Dict[str, Any]:
        """Get network information."""
        pass
    
    @abstractmethod
    def get_display_info(self) -> Dict[str, Any]:
        """Get display information."""
        pass
    
    @abstractmethod
    def get_audio_info(self) -> Dict[str, Any]:
        """Get audio device information."""
        pass
    
    @abstractmethod
    def get_input_devices(self) -> Dict[str, Any]:
        """Get input device information."""
        pass
    
    @abstractmethod
    def get_usb_devices(self) -> List[Dict[str, Any]]:
        """Get USB device information."""
        pass
    
    @abstractmethod
    def get_bluetooth_devices(self) -> List[Dict[str, Any]]:
        """Get Bluetooth device information."""
        pass 