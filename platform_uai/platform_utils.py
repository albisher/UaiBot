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
        # Try to import the module
        return importlib.import_module(module_path)
    except ImportError as e:
        print(f"Failed to load platform handler {module_path}: {e}")
        return None

def get_audio_handler():
    """Get the platform-specific audio handler"""
    audio_module = load_platform_handler('audio_handler')
    if not audio_module:
        return None
    
    # Find the handler class in the module
    handler_class = None
    for name in dir(audio_module):
        if name.endswith('AudioHandler'):
            handler_class = getattr(audio_module, name)
            break
    
    if not handler_class:
        print("ERROR: Could not find AudioHandler class in module")
        return None
        
    # Create and return an instance of the handler
    return handler_class()

def get_usb_handler():
    """Get the platform-specific USB handler"""
    usb_module = load_platform_handler('usb_handler')
    if not usb_module:
        return None
    
    # Find the handler class in the module
    handler_class = None
    for name in dir(usb_module):
        if name.endswith('USBHandler'):
            handler_class = getattr(usb_module, name)
            break
    
    if not handler_class:
        print("ERROR: Could not find USBHandler class in module")
        return None
        
    # Create and return an instance of the handler
    return handler_class()
