"""
Platform core module for Labeeb.

This module provides platform-specific functionality and isolation.
"""
from .platform_manager import platform_manager
from .common.base_handler import BaseHandler

from .common.platform_utils import (
    get_platform_name,
    get_system_info,
    execute_command,
    get_file_path,
    get_environment_variable,
    set_environment_variable,
    get_process_list,
    get_network_info,
    get_display_info,
    get_audio_info,
    get_input_devices,
    get_usb_devices,
    get_bluetooth_devices
)

from .common.platform_factory import PlatformFactory
from .common.platform_interface import PlatformInterface

__all__ = [
    'platform_manager',
    'BaseHandler',
    'get_platform_name',
    'get_system_info',
    'execute_command',
    'get_file_path',
    'get_environment_variable',
    'set_environment_variable',
    'get_process_list',
    'get_network_info',
    'get_display_info',
    'get_audio_info',
    'get_input_devices',
    'get_usb_devices',
    'get_bluetooth_devices',
    'PlatformFactory',
    'PlatformInterface'
]
