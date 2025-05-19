#!/usr/bin/env python3
"""
Mouse and Keyboard Input Module for UaiBot.

This module allows UaiBot to control input devices (mouse and keyboard) 
programmatically across different platforms.
"""
from .mouse_keyboard_handler import MouseKeyboardHandler

# We don't need to import from input_control.py here
# The function is in an external file

# Export main class
__all__ = ['MouseKeyboardHandler']
