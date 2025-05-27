"""
Platform Factory

This module provides a factory for creating platform-specific implementations.
"""
import sys
import logging
from typing import Optional
from .common.platform_interface import PlatformInterface

logger = logging.getLogger(__name__)

def create_platform() -> Optional[PlatformInterface]:
    """
    Create a platform-specific implementation based on the current system.
    
    Returns:
        Optional[PlatformInterface]: A platform-specific implementation or None if the platform is not supported.
    """
    try:
        platform = sys.platform.lower()
        
        if platform == 'darwin':
            from .macos.macos_platform import MacOSPlatform
            return MacOSPlatform()
        elif platform == 'win32':
            from .win32.windows_platform import WindowsPlatform
            return WindowsPlatform()
        elif platform == 'linux':
            from .linux.linux_platform import LinuxPlatform
            return LinuxPlatform()
        else:
            logger.error(f"Unsupported platform: {platform}")
            return None
            
    except ImportError as e:
        logger.error(f"Failed to import platform implementation: {e}")
        return None
    except Exception as e:
        logger.error(f"Error creating platform implementation: {e}")
        return None 