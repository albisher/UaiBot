"""
macOS-specific system information gatherer.

This module provides a macOS-specific implementation of the system information gatherer.
It uses various macOS-specific commands to gather detailed system information.
"""
from typing import Dict, Any
import subprocess
from labeeb.platform_services.common.system_info import BaseSystemInfoGatherer

class MacSystemInfoGatherer(BaseSystemInfoGatherer):
    """macOS-specific implementation of system information gatherer.
    
    This class provides methods to gather macOS-specific system information using
    native commands like sw_vers, uname, sysctl, and hostname. It inherits common
    system information gathering functionality from BaseSystemInfoGatherer.
    
    Attributes:
        None
        
    Example:
        >>> gatherer = MacSystemInfoGatherer()
        >>> info = gatherer.get_system_info()
        >>> print(info['platform']['macos_version'])
        '10.15.7'
    """
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get macOS-specific system information.
        
        This method gathers macOS-specific system information by combining common
        system information with macOS-specific details obtained through various
        system commands.
        
        Returns:
            Dict[str, Any]: Dictionary containing system information with the following structure:
                {
                    'platform': {
                        'macos_version': str,  # macOS version (e.g., '10.15.7')
                        'kernel_version': str,  # Kernel version (e.g., '19.6.0')
                        'boot_time': str,      # System boot time
                        'hostname': str,       # System hostname
                        ...  # Common platform info
                    },
                    'cpu': {...},      # Common CPU info
                    'memory': {...},   # Common memory info
                    'disk': {...},     # Common disk info
                    'network': {...}   # Common network info
                }
        """
        info = self.get_common_info()
        
        # Add macOS-specific information
        info['platform'].update({
            'macos_version': self._get_macos_version(),
            'kernel_version': self._get_kernel_version(),
            'boot_time': self._get_boot_time(),
            'hostname': self._get_hostname(),
        })
        
        return info
    
    def _get_macos_version(self) -> str:
        """Get macOS version using sw_vers command.
        
        Uses the sw_vers command to retrieve the macOS version information.
        
        Returns:
            str: macOS version (e.g., '10.15.7') or 'Unknown' if command fails
        """
        try:
            result = subprocess.run(['sw_vers', '-productVersion'], 
                                 capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return "Unknown"
    
    def _get_kernel_version(self) -> str:
        """Get kernel version using uname command.
        
        Uses the uname command to retrieve the kernel version information.
        
        Returns:
            str: Kernel version (e.g., '19.6.0') or 'Unknown' if command fails
        """
        try:
            result = subprocess.run(['uname', '-r'], 
                                 capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return "Unknown"
    
    def _get_boot_time(self) -> str:
        """Get system boot time using sysctl command.
        
        Uses the sysctl command to retrieve the system boot time information.
        
        Returns:
            str: System boot time or 'Unknown' if command fails
        """
        try:
            result = subprocess.run(['sysctl', '-n', 'kern.boottime'], 
                                 capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return "Unknown"
    
    def _get_hostname(self) -> str:
        """Get system hostname.
        
        Uses the hostname command to retrieve the system hostname.
        
        Returns:
            str: System hostname or 'Unknown' if command fails
        """
        try:
            result = subprocess.run(['hostname'], 
                                 capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return "Unknown" 