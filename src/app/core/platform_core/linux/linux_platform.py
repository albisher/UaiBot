"""
Linux Platform Implementation

This module provides the Linux-specific implementation of the platform interface.
"""
import os
import sys
import platform
import subprocess
from typing import Dict, Any
from ..common.platform_interface import PlatformInterface

class LinuxPlatform(PlatformInterface):
    """Linux-specific platform implementation."""
    
    def __init__(self):
        """Initialize the Linux platform implementation."""
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
        return sys.platform.startswith('linux')
    
    def get_system_resources(self) -> Dict[str, Any]:
        """Get system resource information."""
        return {
            'cpu_count': os.cpu_count(),
            'memory': self._get_memory_info(),
            'disk': self._get_disk_info()
        }
    
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
    
    def get_system_paths(self) -> Dict[str, str]:
        """Get system-specific paths."""
        return {
            'home': os.path.expanduser('~'),
            'temp': '/tmp',
            'config': os.path.join(os.path.expanduser('~'), '.config'),
            'cache': os.path.join(os.path.expanduser('~'), '.cache')
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
            'dist': self._get_distribution_info()
        }
    
    def _get_memory_info(self) -> Dict[str, Any]:
        """Get memory information."""
        try:
            result = subprocess.run(['free', '-h'], capture_output=True, text=True)
            return {'memory_info': result.stdout}
        except Exception as e:
            return {'error': str(e)}
    
    def _get_disk_info(self) -> Dict[str, Any]:
        """Get disk information."""
        try:
            result = subprocess.run(['df', '-h'], capture_output=True, text=True)
            return {'disk_info': result.stdout}
        except Exception as e:
            return {'error': str(e)}
    
    def _get_distribution_info(self) -> Dict[str, str]:
        """Get Linux distribution information."""
        try:
            result = subprocess.run(['lsb_release', '-a'], capture_output=True, text=True)
            return {'distribution_info': result.stdout}
        except Exception:
            return {'error': 'Could not determine distribution info'} 