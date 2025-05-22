#!/usr/bin/env python3
"""
Input control module for UaiBot.

This module provides convenience imports for the input control functionality.
It's the recommended way to import input control components.
"""
import os
import sys
import platform
from typing import Optional

# Add current directory to path to enable relative imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import from platform_uai
try:
    from platform_uai.platform_utils import get_input_handler
    from platform_uai.common.input_control.base_handler import BaseInputHandler
    from platform_uai.common.input_control.mouse_keyboard_handler import MouseKeyboardHandler as CommonMouseKeyboardHandler
    
    # Platform-specific imports
    _system = platform.system().lower()
    
    if _system == 'darwin':
        try:
            from platform_uai.mac.input_control import MacInputHandler
        except ImportError:
            MacInputHandler = None
    elif _system == 'windows':
        try:
            from platform_uai.windows.input_control import WindowsInputHandler
        except ImportError:
            WindowsInputHandler = None
    elif _system == 'linux':
        # Check for Jetson
        is_jetson = False
        try:
            with open('/proc/device-tree/model', 'r') as f:
                if 'jetson' in f.read().lower():
                    is_jetson = True
        except:
            pass
            
        if is_jetson:
            try:
                from platform_uai.jetson.input_control import JetsonInputHandler
            except ImportError:
                JetsonInputHandler = None
        else:
            try:
                from platform_uai.ubuntu.input_control import UbuntuInputHandler
            except ImportError:
                UbuntuInputHandler = None
                
except ImportError as e:
    print(f"Warning: Could not import platform-specific input handlers: {e}")
    # Define empty classes to avoid import errors
    BaseInputHandler = None
    CommonMouseKeyboardHandler = None
    MacInputHandler = None
    WindowsInputHandler = None
    UbuntuInputHandler = None
    JetsonInputHandler = None
    
    def get_input_handler():
        """Fallback function for get_input_handler."""
        from input_control.mouse_keyboard_handler import MouseKeyboardHandler
        return MouseKeyboardHandler()

# For backward compatibility
from input_control.mouse_keyboard_handler import MouseKeyboardHandler

__all__ = [
    'BaseInputHandler',
    'MouseKeyboardHandler',
    'CommonMouseKeyboardHandler',
    'MacInputHandler',
    'WindowsInputHandler', 
    'UbuntuInputHandler',
    'JetsonInputHandler',
    'get_input_handler'
]

def get_platform_handler() -> Optional[BaseInputHandler]:
    """
    Get the appropriate input handler for the current platform.
    
    Returns:
        The platform-specific input handler instance, or None if not available.
    """
    return get_input_handler()
