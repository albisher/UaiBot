"""
Platform detection and handler loading utility
"""
import platform
import os
import sys
import importlib.util
from typing import Optional, Any
import logging

logger = logging.getLogger(__name__)

def detect_platform():
    """
    Detect the current platform and return a tuple containing:
    (platform_name, platform_handler_directory)
    """
    system = platform.system().lower()
    
    if system == 'darwin':
        # macOS
        return 'mac', 'mac'
    elif system == 'linux':
        # Check for Jetson-specific indicators
        try:
            with open('/proc/device-tree/model', 'r') as f:
                model = f.read().lower()
                if 'jetson' in model:
                    return 'jetson', 'jetson'
        except:
            pass
        # Default to Ubuntu for Linux
        return 'ubuntu', 'ubuntu'
    elif system == 'windows':
        # Windows support
        return 'windows', 'windows'
    else:
        # Unsupported platform
        return None, None

def load_platform_handler(module_name):
    """
    Dynamically load a platform-specific handler module
    
    Args:
        module_name: The name of the module to load (e.g., 'audio_handler', 'usb_handler')
        
    Returns:
        The loaded module or None if not found/supported
    """
    platform_name, platform_dir = detect_platform()
    
    if not platform_name:
        print(f"ERROR: Unsupported platform: {platform.system()}")
        return None
    
    # Build the path to the platform-specific module
    module_path = f"platform_uai.{platform_dir}.{module_name}"
    
    try:
        # Try to import the platform-specific module
        module = importlib.import_module(module_path)
        return module
    except ImportError as e:
        print(f"Failed to load platform module {module_path}: {e}")
        
        # Fall back to common implementation if available
        try:
            common_module_path = f"platform_uai.common.{module_name}"
            module = importlib.import_module(common_module_path)
            print(f"Loaded common module {common_module_path} as fallback")
            return module
        except ImportError as e2:
            print(f"Failed to load common module {common_module_path}: {e2}")
            return None

def get_audio_handler() -> Optional[Any]:
    """Get the appropriate audio handler for the current platform.
    
    Returns:
        Audio handler instance or None if not available.
    """
    system = platform.system()
    try:
        if system == 'Darwin':
            from uaibot.platform_uai.mac.audio_handler import MacAudioHandler
            return MacAudioHandler()
        elif system == 'Linux':
            from uaibot.platform_uai.linux.audio_handler import LinuxAudioHandler
            return LinuxAudioHandler()
        elif system == 'Windows':
            from uaibot.platform_uai.windows.audio_handler import WindowsAudioHandler
            return WindowsAudioHandler()
    except ImportError as e:
        logger.warning(f"Failed to import audio handler for {system}: {e}")
    return None

def get_usb_handler() -> Optional[Any]:
    """Get the appropriate USB handler for the current platform.
    
    Returns:
        USB handler instance or None if not available.
    """
    system = platform.system()
    try:
        if system == 'Darwin':
            from uaibot.platform_uai.mac.usb_handler import MacUSBHandler
            return MacUSBHandler()
        elif system == 'Linux':
            from uaibot.platform_uai.linux.usb_handler import LinuxUSBHandler
            return LinuxUSBHandler()
        elif system == 'Windows':
            from uaibot.platform_uai.windows.usb_handler import WindowsUSBHandler
            return WindowsUSBHandler()
    except ImportError as e:
        logger.warning(f"Failed to import USB handler for {system}: {e}")
    return None

def get_input_handler() -> Optional[Any]:
    """Get the appropriate input handler for the current platform.
    
    Returns:
        Input handler instance or None if not available.
    """
    system = platform.system()
    try:
        if system == 'Darwin':
            from uaibot.platform_uai.mac.input_handler import MacInputHandler
            return MacInputHandler()
        elif system == 'Linux':
            from uaibot.platform_uai.linux.input_handler import LinuxInputHandler
            return LinuxInputHandler()
        elif system == 'Windows':
            from uaibot.platform_uai.windows.input_handler import WindowsInputHandler
            return WindowsInputHandler()
    except ImportError as e:
        logger.warning(f"Failed to import input handler for {system}: {e}")
    return None

def get_platform_name() -> Optional[str]:
    """Get the platform name in a standardized format.
    
    Returns:
        Platform name ('mac', 'linux', 'windows') or None if unsupported.
    """
    system = platform.system()
    if system == 'Darwin':
        return 'mac'
    elif system == 'Linux':
        return 'linux'
    elif system == 'Windows':
        return 'windows'
    return None
