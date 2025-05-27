"""
Platform Factory Module

This module provides a factory for creating platform-specific implementations.
It ensures proper platform code isolation and handles platform detection.
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
        Optional[PlatformInterface]: Platform-specific implementation or None if platform is not supported.
        
    Raises:
        ImportError: If platform-specific module cannot be imported.
        NotImplementedError: If platform is not supported.
    """
    try:
        if sys.platform == 'darwin':
            from .macos.macos_platform import MacOSPlatform
            return MacOSPlatform()
        elif sys.platform == 'win32':
            from .win32.windows_platform import WindowsPlatform
            return WindowsPlatform()
        elif sys.platform.startswith('linux'):
            from .linux.linux_platform import LinuxPlatform
            return LinuxPlatform()
        else:
            logger.error(f"Unsupported platform: {sys.platform}")
            raise NotImplementedError(f"Platform {sys.platform} is not supported")
    except ImportError as e:
        logger.error(f"Failed to import platform-specific module: {e}")
        raise 