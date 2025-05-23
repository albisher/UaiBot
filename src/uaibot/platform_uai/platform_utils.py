"""
Platform detection and handler loading utility
"""
import platform
import os
import sys
import importlib.util

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

def get_audio_handler():
    """
    Get the appropriate audio handler for the current platform
    
    Returns:
        An instance of the platform-specific AudioHandler
    """
    audio_module = load_platform_handler('audio_handler')
    if not audio_module:
        return None
        
    try:
        # Check if the module has an AudioHandler class
        if hasattr(audio_module, 'AudioHandler'):
            return audio_module.AudioHandler()
        else:
            print(f"ERROR: AudioHandler class not found in module")
            return None
    except Exception as e:
        print(f"Failed to instantiate AudioHandler: {e}")
        return None

def get_usb_handler():
    """
    Get the appropriate USB handler for the current platform
    
    Returns:
        An instance of the platform-specific USBHandler
    """
    usb_module = load_platform_handler('usb_handler')
    if not usb_module:
        return None
        
    try:
        # Check if the module has a USBHandler class
        if hasattr(usb_module, 'USBHandler'):
            return usb_module.USBHandler()
        else:
            print(f"ERROR: USBHandler class not found in module")
            return None
    except Exception as e:
        print(f"Failed to instantiate USBHandler: {e}")
        return None

def get_input_handler():
    """
    Get the appropriate input handler for the current platform
    
    Returns:
        An instance of the platform-specific InputHandler
    """
    platform_name, platform_dir = detect_platform()
    
    if platform_name == 'ubuntu':
        # For Ubuntu, use the specific input handler
        try:
            from uaibot.platform_uai.ubuntu.input_control.ubuntu_input_handler import UbuntuInputHandler
            print("Using Ubuntu-specific input handler")
            return UbuntuInputHandler()
        except ImportError as e:
            print(f"Failed to load Ubuntu input handler: {e}")
            return None
    
    # For other platforms, try the common implementation
    try:
        from uaibot.platform_uai.common.input_control import MouseKeyboardHandler
        print("Using common MouseKeyboardHandler as fallback")
        return MouseKeyboardHandler()
    except ImportError as e:
        print(f"Failed to load common MouseKeyboardHandler: {e}")
        return None
