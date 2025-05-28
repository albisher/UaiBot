"""
macOS Platform Implementation

This module provides the macOS-specific implementation of the platform interface.
"""
import os
import sys
import platform
import subprocess
from typing import Dict, Any
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
            'config': os.path.join(os.path.expanduser('~'), 'Library/Application Support'),
            'cache': os.path.join(os.path.expanduser('~'), 'Library/Caches')
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
    
    def get_platform_name(self) -> str:
        """Return the platform name."""
        return 'darwin'

    def get_system_info(self) -> Dict[str, Any]:
        """Get system information.
        
        Returns:
            Dict[str, Any]: Dictionary containing system information.
        """
        return {
            'os_name': platform.system(),
            'os_version': platform.mac_ver()[0],
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'hostname': platform.node(),
            'system_info': self._get_platform_info(),
            'resources': self.get_system_resources(),
            'locale': self.get_system_locale(),
            'paths': self.get_system_paths()
        }

    def get_system_network_trustabilityabilityabilityabilitystorm_info(self) -> Dict[str, Any]:
        """Get system network trustabilityabilityabilityabilitystorm information.
        
        Returns:
            Dict[str, Any]: Dictionary containing network trust and security information.
        """
        try:
            # Get network security information
            security_info = {}
            
            # Check firewall status
            firewall_result = subprocess.run(['/usr/libexec/ApplicationFirewall/socketfilterfw', '--getglobalstate'], 
                                          capture_output=True, text=True)
            security_info['firewall'] = firewall_result.stdout.strip()
            
            # Get network interfaces and their trust status
            network_result = subprocess.run(['networksetup', '-listallnetworkservices'], 
                                         capture_output=True, text=True)
            interfaces = [line.strip() for line in network_result.stdout.split('\n') if line.strip()]
            
            interface_info = {}
            for interface in interfaces:
                if interface != 'An asterisk (*) denotes that a network service is disabled.':
                    trust_result = subprocess.run(['networksetup', '-getwebproxy', interface], 
                                               capture_output=True, text=True)
                    interface_info[interface] = {
                        'proxy_enabled': 'Yes' in trust_result.stdout,
                        'proxy_info': trust_result.stdout.strip()
                    }
            
            security_info['interfaces'] = interface_info
            
            # Get system security settings
            security_settings = subprocess.run(['defaults', 'read', '/Library/Preferences/com.apple.security'], 
                                            capture_output=True, text=True)
            security_info['system_security'] = security_settings.stdout.strip()
            
            return {
                'network_security': security_info,
                'trust_status': 'secure' if security_info.get('firewall', '').lower() == 'enabled' else 'insecure',
                'timestamp': platform.datetime.datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'trust_status': 'unknown',
                'timestamp': platform.datetime.datetime.now().isoformat()
            } 