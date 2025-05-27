from typing import Any, Dict, List, Optional

from .platform_factory import PlatformFactory

def get_platform_name() -> str:
    """Get the name of the current platform."""
    return PlatformFactory.get_platform().get_platform_name()

def get_system_info() -> Dict[str, Any]:
    """Get system information."""
    return PlatformFactory.get_platform().get_system_info()

def execute_command(command: str) -> Dict[str, Any]:
    """Execute a system command."""
    return PlatformFactory.get_platform().execute_command(command)

def get_file_path(path: str) -> str:
    """Get platform-specific file path."""
    return PlatformFactory.get_platform().get_file_path(path)

def get_environment_variable(name: str) -> Optional[str]:
    """Get environment variable value."""
    return PlatformFactory.get_platform().get_environment_variable(name)

def set_environment_variable(name: str, value: str) -> bool:
    """Set environment variable value."""
    return PlatformFactory.get_platform().set_environment_variable(name, value)

def get_process_list() -> List[Dict[str, Any]]:
    """Get list of running processes."""
    return PlatformFactory.get_platform().get_process_list()

def get_network_info() -> Dict[str, Any]:
    """Get network information."""
    return PlatformFactory.get_platform().get_network_info()

def get_display_info() -> Dict[str, Any]:
    """Get display information."""
    return PlatformFactory.get_platform().get_display_info()

def get_audio_info() -> Dict[str, Any]:
    """Get audio device information."""
    return PlatformFactory.get_platform().get_audio_info()

def get_input_devices() -> Dict[str, Any]:
    """Get input device information."""
    return PlatformFactory.get_platform().get_input_devices()

def get_usb_devices() -> List[Dict[str, Any]]:
    """Get USB device information."""
    return PlatformFactory.get_platform().get_usb_devices()

def get_bluetooth_devices() -> List[Dict[str, Any]]:
    """Get Bluetooth device information."""
    return PlatformFactory.get_platform().get_bluetooth_devices() 