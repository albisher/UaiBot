"""
DEPRECATED: System information gathering has been moved to platform_core/platform_manager.py.
Use PlatformManager for all system info logic.
"""

# Deprecated stub for backward compatibility
from platform_core.platform_manager import PlatformManager

"""
System information gathering module for Labeeb.

This module handles the collection and formatting of system information for use in AI prompts.
It provides detailed information about the operating system, hardware, and environment,
with support for multiple platforms including macOS, Windows, Linux, and BSD systems.

The module includes:
- Basic system information collection
- Platform-specific information gathering
- Error handling and logging
- Formatted output generation

Example:
    >>> system_info = SystemInfoGatherer.get_system_info()
    >>> print(system_info)
    Operating System: Linux
    OS Version: 6.11.0-25-generic
    Architecture: x86_64
    Processor: Intel(R) Core(TM) i7-9750H CPU @ 2.60GHz
    Python Version: 3.9.7
    Distribution: Ubuntu 22.04.3 LTS
    Kernel: 6.11.0-25-generic
"""
import os
import platform
import subprocess
import re
import logging
from typing import Dict, Any, Optional, List, Tuple, Union

# Set up logging
logger = logging.getLogger(__name__)

class SystemInfoGatherer:
    """
    A class to gather and format system information.
    
    This class provides static methods for collecting detailed information about
    the system, including operating system details, hardware information, and
    platform-specific data. It supports multiple operating systems and handles
    errors gracefully.
    
    The class uses a combination of platform module functions and system-specific
    commands to gather comprehensive information about the system environment.
    """
    
    @staticmethod
    def get_system_info() -> str:
        """
        Get detailed system information.
        
        This method:
        1. Collects basic system information using the platform module
        2. Gathers OS-specific information based on the detected platform
        3. Formats all information into a readable string
        
        Returns:
            str: Formatted string containing system information
            
        Note:
            The method handles errors gracefully and will return partial information
            if some details cannot be gathered.
        """
        system_info: Dict[str, Any] = {
            'os': platform.system(),
            'os_version': platform.version(),
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version()
        }
        
        # Get OS-specific information
        if system_info['os'] == 'Darwin':  # macOS
            system_info.update(SystemInfoGatherer._get_macos_info())
        elif system_info['os'] == 'Windows':
            system_info.update(SystemInfoGatherer._get_windows_info())
        elif system_info['os'] == 'Linux':
            system_info.update(SystemInfoGatherer._get_linux_info())
        elif system_info['os'] == 'FreeBSD':
            system_info.update(SystemInfoGatherer._get_bsd_info())
        
        return SystemInfoGatherer._format_system_info(system_info)
    
    @staticmethod
    def _get_macos_info() -> Dict[str, str]:
        """
        Get macOS specific information.
        
        This method:
        1. Retrieves the Mac model name using sysctl
        2. Gets the macOS version using sw_vers
        3. Handles any errors that occur during information gathering
        
        Returns:
            Dict[str, str]: Dictionary containing macOS specific information
            
        Note:
            The method uses subprocess to run system commands and handles
            any errors that might occur during command execution.
        """
        info: Dict[str, str] = {}
        try:
            # Get model name
            model_info: str = subprocess.check_output(['sysctl', '-n', 'hw.model']).decode().strip()
            info['model'] = model_info
            
            # Get macOS version
            version_info: str = subprocess.check_output(['sw_vers', '-productVersion']).decode().strip()
            info['os_version'] = version_info
        except subprocess.SubprocessError as e:
            logging.error(f"Error getting macOS info: {e}")
        
        return info
    
    @staticmethod
    def _get_windows_info() -> Dict[str, str]:
        """
        Get Windows specific information.
        
        This method:
        1. Retrieves the Windows version using the ver command
        2. Gets detailed system information using systeminfo
        3. Handles any errors that occur during information gathering
        
        Returns:
            Dict[str, str]: Dictionary containing Windows specific information
            
        Note:
            The method uses subprocess to run system commands and handles
            any errors that might occur during command execution.
        """
        info: Dict[str, str] = {}
        try:
            # Get Windows version
            version_info: str = subprocess.check_output(['ver']).decode().strip()
            info['os_version'] = version_info
            
            # Get system info
            system_info: str = subprocess.check_output(['systeminfo']).decode()
            info['system_info'] = system_info
        except subprocess.SubprocessError as e:
            logging.error(f"Error getting Windows info: {e}")
        
        return info
    
    @staticmethod
    def _get_linux_info() -> Dict[str, str]:
        """
        Get Linux specific information.
        
        This method:
        1. Reads distribution information from /etc/os-release
        2. Gets the kernel version using uname
        3. Handles any errors that occur during information gathering
        
        Returns:
            Dict[str, str]: Dictionary containing Linux specific information
            
        Note:
            The method handles both file reading and command execution errors,
            and will return partial information if some details cannot be gathered.
        """
        info: Dict[str, str] = {}
        try:
            # Get distribution info
            if os.path.exists('/etc/os-release'):
                with open('/etc/os-release', 'r') as f:
                    content: str = f.read()
                    name_match: Optional[re.Match] = re.search(r'PRETTY_NAME="(.+)"', content)
                    if name_match:
                        info['distribution'] = name_match.group(1)
            
            # Get kernel version
            kernel_info: str = subprocess.check_output(['uname', '-r']).decode().strip()
            info['kernel'] = kernel_info
        except (subprocess.SubprocessError, IOError) as e:
            logging.error(f"Error getting Linux info: {e}")
        
        return info
    
    @staticmethod
    def _get_bsd_info() -> Dict[str, str]:
        """
        Get BSD specific information.
        
        This method:
        1. Retrieves the BSD version using uname
        2. Gets detailed system information using sysctl
        3. Handles any errors that occur during information gathering
        
        Returns:
            Dict[str, str]: Dictionary containing BSD specific information
            
        Note:
            The method uses subprocess to run system commands and handles
            any errors that might occur during command execution.
        """
        info: Dict[str, str] = {}
        try:
            # Get BSD version
            version_info: str = subprocess.check_output(['uname', '-r']).decode().strip()
            info['os_version'] = version_info
            
            # Get system info
            system_info: str = subprocess.check_output(['sysctl', '-a']).decode()
            info['system_info'] = system_info
        except subprocess.SubprocessError as e:
            logging.error(f"Error getting BSD info: {e}")
        
        return info
    
    @staticmethod
    def _format_system_info(info: Dict[str, Any]) -> str:
        """
        Format system information into a readable string.
        
        This method:
        1. Creates a list of formatted information strings
        2. Adds basic system information
        3. Adds OS-specific information if available
        4. Joins all information with newlines
        
        Args:
            info (Dict[str, Any]): Dictionary containing system information
            
        Returns:
            str: Formatted string containing system information
            
        Note:
            The method handles missing information gracefully and will
            only include fields that are present in the info dictionary.
        """
        formatted_info: List[str] = []
        
        # Add basic system information
        formatted_info.append(f"Operating System: {info['os']}")
        formatted_info.append(f"OS Version: {info['os_version']}")
        formatted_info.append(f"Architecture: {info['architecture']}")
        formatted_info.append(f"Processor: {info['processor']}")
        formatted_info.append(f"Python Version: {info['python_version']}")
        
        # Add OS-specific information
        if 'model' in info:
            formatted_info.append(f"Model: {info['model']}")
        if 'distribution' in info:
            formatted_info.append(f"Distribution: {info['distribution']}")
        if 'kernel' in info:
            formatted_info.append(f"Kernel: {info['kernel']}")
        
        return "\n".join(formatted_info) 