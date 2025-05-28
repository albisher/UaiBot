"""
Platform core module for Labeeb.

This module provides platform-specific functionality and isolation.
"""
from .platform_manager import platform_manager
from .common.base_handler import BaseHandler

from .platform_utils import (
    get_platform_name,
    is_windows,
    is_mac,
    is_linux,
    is_posix,
    get_audio_handler,
    get_usb_handler,
    get_input_handler,
    detect_platform,
    load_platform_handler
)

from .platform_factory import create_platform
from .platform_interface import PlatformInterface

__all__ = [
    'platform_manager',
    'BaseHandler',
    'get_platform_name',
    'is_windows',
    'is_mac',
    'is_linux',
    'is_posix',
    'get_audio_handler',
    'get_usb_handler',
    'get_input_handler',
    'detect_platform',
    'load_platform_handler',
    'create_platform',
    'PlatformInterface'
]
