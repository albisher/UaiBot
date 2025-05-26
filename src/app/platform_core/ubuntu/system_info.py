"""
Ubuntu-specific system information gatherer.

This module provides an Ubuntu-specific implementation of the system information gatherer.
It uses various Linux commands to gather detailed system information specific to Ubuntu.
"""
from typing import Dict, Any
import subprocess
from ..common.system_info import BaseSystemInfoGatherer

class UbuntuSystemInfoGatherer(BaseSystemInfoGatherer):
    """Ubuntu-specific implementation of system information gatherer.
    
    This class provides methods to gather Ubuntu-specific system information using
    Linux commands like lsb_release, uname, uptime, and hostname. It inherits common
    system information gathering functionality from BaseSystemInfoGatherer.
    
    Attributes:
        None
        
    Example:
        >>> gatherer = UbuntuSystemInfoGatherer()
        >>> info = gatherer.get_system_info()
        >>> print(info['platform']['ubuntu_version'])
        'Ubuntu 22.04.1 LTS'
    """
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get Ubuntu-specific system information.
        
        This method gathers Ubuntu-specific system information by combining common
        system information with Ubuntu-specific details obtained through various
        Linux commands.
        
        Returns:
            Dict[str, Any]: Dictionary containing system information with the following structure:
                {
                    'platform': {
                        'ubuntu_version': str,  # Ubuntu version (e.g., 'Ubuntu 22.04.1 LTS')
                        'kernel_version': str,  # Kernel version (e.g., '5.15.0-56-generic')
                        'boot_time': str,       # System boot time
                        'hostname': str,        # System hostname
                        ...  # Common platform info
                    },
                    'cpu': {...},      # Common CPU info
                    'memory': {...},   # Common memory info
                    'disk': {...},     # Common disk info
                    'network': {...}   # Common network info
                }
        """
        info = self.get_common_info()
        
        # Add Ubuntu-specific information
        info['platform'].update({
            'ubuntu_version': self._get_ubuntu_version(),
            'kernel_version': self._get_kernel_version(),
            'boot_time': self._get_boot_time(),
            'hostname': self._get_hostname(),
        })
        
        return info
    
    def _get_ubuntu_version(self) -> str:
        """Get Ubuntu version using lsb_release command.
        
        Uses the lsb_release command to retrieve the Ubuntu version information.
        
        Returns:
            str: Ubuntu version (e.g., 'Ubuntu 22.04.1 LTS') or 'Unknown' if command fails
        """
        try:
            result = subprocess.run(['lsb_release', '-d'], 
                                 capture_output=True, text=True, check=True)
            return result.stdout.split(':')[1].strip()
        except subprocess.CalledProcessError:
            return "Unknown"
    
    def _get_kernel_version(self) -> str:
        """Get kernel version using uname command.
        
        Uses the uname command to retrieve the kernel version information.
        
        Returns:
            str: Kernel version (e.g., '5.15.0-56-generic') or 'Unknown' if command fails
        """
        try:
            result = subprocess.run(['uname', '-r'], 
                                 capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return "Unknown"
    
    def _get_boot_time(self) -> str:
        """Get system boot time using uptime command.
        
        Uses the uptime command to retrieve the system boot time information.
        
        Returns:
            str: System boot time in ISO format (e.g., '2023-01-01 00:00:00') or 'Unknown' if command fails
        """
        try:
            result = subprocess.run(['uptime', '-s'], 
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