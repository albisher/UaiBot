"""
Windows-specific system information gatherer.

This module provides a Windows-specific implementation of the system information gatherer.
It uses Windows Registry queries and system commands to gather detailed system information.
"""
from typing import Dict, Any
import subprocess
import winreg
from ..common.system_info import BaseSystemInfoGatherer

class WindowsSystemInfoGatherer(BaseSystemInfoGatherer):
    """Windows-specific implementation of system information gatherer.
    
    This class provides methods to gather Windows-specific system information using
    Windows Registry queries and system commands. It inherits common system information
    gathering functionality from BaseSystemInfoGatherer.
    
    Attributes:
        None
        
    Example:
        >>> gatherer = WindowsSystemInfoGatherer()
        >>> info = gatherer.get_system_info()
        >>> print(info['platform']['windows_version'])
        'Windows 10 Pro'
    """
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get Windows-specific system information.
        
        This method gathers Windows-specific system information by combining common
        system information with Windows-specific details obtained through Registry
        queries and system commands.
        
        Returns:
            Dict[str, Any]: Dictionary containing system information with the following structure:
                {
                    'platform': {
                        'windows_version': str,  # Windows version (e.g., 'Windows 10 Pro')
                        'edition': str,          # Windows edition (e.g., 'Professional')
                        'build_number': str,     # Windows build number (e.g., '19045')
                        'hostname': str,         # System hostname
                        ...  # Common platform info
                    },
                    'cpu': {...},      # Common CPU info
                    'memory': {...},   # Common memory info
                    'disk': {...},     # Common disk info
                    'network': {...}   # Common network info
                }
        """
        info = self.get_common_info()
        
        # Add Windows-specific information
        info['platform'].update({
            'windows_version': self._get_windows_version(),
            'edition': self._get_windows_edition(),
            'build_number': self._get_windows_build(),
            'hostname': self._get_hostname(),
        })
        
        return info
    
    def _get_windows_version(self) -> str:
        """Get Windows version using Registry query.
        
        Uses the Windows Registry to retrieve the Windows version information from
        HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\ProductName.
        
        Returns:
            str: Windows version (e.g., 'Windows 10 Pro') or 'Unknown' if query fails
        """
        try:
            result = subprocess.run(
                ['reg', 'query', 'HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion', '/v', 'ProductName'],
                capture_output=True, text=True, check=True
            )
            return result.stdout.split('REG_SZ')[1].strip()
        except subprocess.CalledProcessError:
            return "Unknown"
    
    def _get_windows_edition(self) -> str:
        """Get Windows edition using Registry query.
        
        Uses the Windows Registry to retrieve the Windows edition information from
        HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\EditionID.
        
        Returns:
            str: Windows edition (e.g., 'Professional') or 'Unknown' if query fails
        """
        try:
            result = subprocess.run(
                ['reg', 'query', 'HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion', '/v', 'EditionID'],
                capture_output=True, text=True, check=True
            )
            return result.stdout.split('REG_SZ')[1].strip()
        except subprocess.CalledProcessError:
            return "Unknown"
    
    def _get_windows_build(self) -> str:
        """Get Windows build number using Registry query.
        
        Uses the Windows Registry to retrieve the Windows build number from
        HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\CurrentBuildNumber.
        
        Returns:
            str: Windows build number (e.g., '19045') or 'Unknown' if query fails
        """
        try:
            result = subprocess.run(
                ['reg', 'query', 'HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion', '/v', 'CurrentBuildNumber'],
                capture_output=True, text=True, check=True
            )
            return result.stdout.split('REG_SZ')[1].strip()
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