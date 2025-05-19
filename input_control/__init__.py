#!/usr/bin/env python3
"""
Mouse and Keyboard Input Module for UaiBot.

This module allows UaiBot to control input devices (mouse and keyboard) 
programmatically across different platforms.
"""
from .mouse_keyboard_handler import MouseKeyboardHandler
from platform_uai.platform_utils import get_input_handler as get_platform_handler

# Export main class and convenience function
__all__ = ['MouseKeyboardHandler', 'get_platform_handler']
