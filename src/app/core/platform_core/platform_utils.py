"""
Platform utilities for Labeeb.
Provides platform-specific handlers and utilities.
"""
import os
import sys
import platform
from typing import Optional, Dict, Any, List, Union
import logging
from pathlib import Path

# Add src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
sys.path.append(project_root)

from src.app.core.platform_core.mac.audio_handler import MacAudioHandler
# from labeeb.core.platform_core.linux.audio_handler import LinuxAudioHandler
# from labeeb.core.platform_core.windows.audio_handler import WindowsAudioHandler

from src.app.core.platform_core.mac.usb_handler import MacUSBHandler
# from labeeb.core.platform_core.linux.usb_handler import LinuxUSBHandler
# from labeeb.core.platform_core.windows.usb_handler import WindowsUSBHandler

from src.app.core.platform_core.mac.input_handler import MacInputHandler
# from labeeb.core.platform_core.linux.input_handler import LinuxInputHandler
# from labeeb.core.platform_core.windows.input_handler import WindowsInputHandler

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
    module_path = f"platform_core.{platform_dir}.{module_name}"
    
    try:
        # Try to import the platform-specific module
        module = importlib.import_module(module_path)
        return module
    except ImportError as e:
        print(f"Failed to load platform module {module_path}: {e}")
        
        # Fall back to common implementation if available
        try:
            common_module_path = f"platform_core.common.{module_name}"
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
            return MacAudioHandler()
        # elif system == 'Linux':
        #     from labeeb.platform_core.linux.audio_handler import LinuxAudioHandler
        #     return LinuxAudioHandler()
        elif system == 'Windows':
            # from labeeb.platform_core.windows.audio_handler import WindowsAudioHandler
            pass
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
            return MacUSBHandler()
        # elif system == 'Linux':
        #     from labeeb.platform_core.linux.usb_handler import LinuxUSBHandler
        #     return LinuxUSBHandler()
        elif system == 'Windows':
            # from labeeb.platform_core.windows.usb_handler import WindowsUSBHandler
            pass
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
            return MacInputHandler()
        # elif system == 'Linux':
        #     from labeeb.platform_core.linux.input_handler import LinuxInputHandler
        #     return LinuxInputHandler()
        elif system == 'Windows':
            # from labeeb.platform_core.windows.input_handler import WindowsInputHandler
            pass
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
