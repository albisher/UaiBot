"""
Input control module for UaiBot.

This module provides platform-specific input control functionality.
It automatically selects the appropriate handler based on the operating system.
"""
import platform
from typing import Type
from ...common.input_control.base_handler import BaseInputHandler

# Import platform-specific handlers
if platform.system() == "Darwin":
    from .macos_input_handler import MacOSInputHandler
    InputHandler: Type[BaseInputHandler] = MacOSInputHandler
elif platform.system() == "Windows":
    from .windows_input_handler import WindowsInputHandler
    InputHandler: Type[BaseInputHandler] = WindowsInputHandler
else:
    raise NotImplementedError(f"Input control not implemented for {platform.system()}")

__all__ = ["InputHandler", "BaseInputHandler"]
