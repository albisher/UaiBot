"""
Common input control module for UaiBot.

This module provides base input control functionality that is shared across platforms.
"""

from .base_handler import BaseInputHandler
from .mouse_keyboard_handler import MouseKeyboardHandler

__all__ = ['BaseInputHandler', 'MouseKeyboardHandler']
