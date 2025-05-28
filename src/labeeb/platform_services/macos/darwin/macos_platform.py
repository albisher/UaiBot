"""
macOS Platform Implementation

This module provides the macOS-specific implementation of the platform interface.
"""
import os
import sys
import platform
import subprocess
from typing import Dict, Any, Optional
from ..common.platform_interface import PlatformInterface

class MacOSPlatform(PlatformInterface):
    """macOS-specific platform implementation."""
    
    def __init__(self):
        """Initialize the macOS platform implementation."""
        self._initialized = False
        self._platform_info = None
    
    def initialize(self) -> None:
        """Initialize platform-specific components."""
        if not self._initialized:
            self._platform_info = self._get_platform_info()
            self._initialized = True
    
    def cleanup(self) -> None:
        """Clean up platform-specific resources."""
        self._initialized = False
        self._platform_info = None
    
    def get_platform_info(self) -> Dict[str, Any]:
        """Get platform-specific information."""
        if not self._platform_info:
            self._platform_info = self._get_platform_info()
        return self._platform_info
    
    def is_platform_supported(self) -> bool:
        """Check if the current platform is supported."""
        return sys.platform == 'darwin'
    
    def get_system_resources(self) -> Dict[str, Any]:
        """Get system resource information."""
        return {
            'cpu_count': os.cpu_count(),
            'memory': self._get_memory_info(),
            'disk': self._get_disk_info(),
            'network': self._get_network_info()
        }
    
    def get_audio_devices(self) -> Dict[str, Any]:
        """Get audio device information."""
        try:
            result = subprocess.run(['system_profiler', 'SPAudioDataType'], 
                                 capture_output=True, text=True)
            return {'devices': result.stdout}
        except Exception as e:
            return {'error': str(e)}
    
    def get_display_info(self) -> Dict[str, Any]:
        """Get display information."""
        try:
            result = subprocess.run(['system_profiler', 'SPDisplaysDataType'], 
                                 capture_output=True, text=True)
            return {'displays': result.stdout}
        except Exception as e:
            return {'error': str(e)}
    
    def get_input_devices(self) -> Dict[str, Any]:
        """Get input device information."""
        try:
            result = subprocess.run(['system_profiler', 'SPUSBDataType', 'SPBluetoothDataType'], 
                                 capture_output=True, text=True)
            return {'devices': result.stdout}
        except Exception as e:
            return {'error': str(e)}
    
    def get_system_locale(self) -> Dict[str, Any]:
        """Get system locale information."""
        return {
            'language': os.environ.get('LANG', ''),
            'lc_all': os.environ.get('LC_ALL', ''),
            'lc_messages': os.environ.get('LC_MESSAGES', '')
        }
    
    def get_environment_variables(self) -> Dict[str, str]:
        """Get environment variables."""
        return dict(os.environ)
    
    def get_installed_software(self) -> Dict[str, Any]:
        """Get information about installed software."""
        try:
            result = subprocess.run(['system_profiler', 'SPApplicationsDataType'], 
                                 capture_output=True, text=True)
            return {'applications': result.stdout}
        except Exception as e:
            return {'error': str(e)}
    
    def get_system_permissions(self) -> Dict[str, bool]:
        """Get system permission status."""
        return {
            'camera': self._check_camera_permission(),
            'microphone': self._check_microphone_permission(),
            'location': self._check_location_permission()
        }
    
    def check_required_dependencies(self) -> Dict[str, bool]:
        """Check if required dependencies are installed."""
        return {
            'python': self._check_python_version(),
            'pip': self._check_pip_installed(),
            'git': self._check_git_installed()
        }
    
    def get_system_paths(self) -> Dict[str, str]:
        """Get system-specific paths."""
        return {
            'home': os.path.expanduser('~'),
            'temp': os.path.join(os.path.expanduser('~'), 'Library', 'Caches', 'TemporaryItems'),
            'app_support': os.path.join(os.path.expanduser('~'), 'Library', 'Application Support'),
            'preferences': os.path.join(os.path.expanduser('~'), 'Library', 'Preferences')
        }
    
    def get_system_architecture(self) -> Dict[str, Any]:
        """Get system architecture information."""
        return {
            'machine': platform.machine(),
            'processor': platform.processor(),
            'bits': platform.architecture()[0]
        }
    
    def get_system_version(self) -> Dict[str, Any]:
        """Get system version information."""
        return {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'mac_ver': platform.mac_ver()
        }
    
    def _get_platform_info(self) -> Dict[str, Any]:
        """Get detailed platform information."""
        return {
            'system': platform.system(),
            'node': platform.node(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'mac_ver': platform.mac_ver()
        }
    
    def _get_memory_info(self) -> Dict[str, Any]:
        """Get memory information."""
        try:
            result = subprocess.run(['vm_stat'], capture_output=True, text=True)
            return {'vm_stat': result.stdout}
        except Exception as e:
            return {'error': str(e)}
    
    def _get_disk_info(self) -> Dict[str, Any]:
        """Get disk information."""
        try:
            result = subprocess.run(['df', '-h'], capture_output=True, text=True)
            return {'disk_usage': result.stdout}
        except Exception as e:
            return {'error': str(e)}
    
    def _get_network_info(self) -> Dict[str, Any]:
        """Get network information."""
        try:
            result = subprocess.run(['ifconfig'], capture_output=True, text=True)
            return {'network_interfaces': result.stdout}
        except Exception as e:
            return {'error': str(e)}
    
    def _check_camera_permission(self) -> bool:
        """Check camera permission status."""
        try:
            result = subprocess.run(['tccutil', 'list'], capture_output=True, text=True)
            return 'Camera' in result.stdout
        except Exception:
            return False
    
    def _check_microphone_permission(self) -> bool:
        """Check microphone permission status."""
        try:
            result = subprocess.run(['tccutil', 'list'], capture_output=True, text=True)
            return 'Microphone' in result.stdout
        except Exception:
            return False
    
    def _check_location_permission(self) -> bool:
        """Check location permission status."""
        try:
            result = subprocess.run(['tccutil', 'list'], capture_output=True, text=True)
            return 'Location' in result.stdout
        except Exception:
            return False
    
    def _check_python_version(self) -> bool:
        """Check Python version."""
        return sys.version_info >= (3, 8)
    
    def _check_pip_installed(self) -> bool:
        """Check if pip is installed."""
        try:
            subprocess.run(['pip', '--version'], capture_output=True)
            return True
        except Exception:
            return False
    
    def _check_git_installed(self) -> bool:
        """Check if git is installed."""
        try:
            subprocess.run(['git', '--version'], capture_output=True)
            return True
        except Exception:
            return False 