"""
Platform core module for Labeeb.

This module provides platform-specific functionality and isolation.
"""
from .platform_manager import platform_manager
from .common.base_handler import BaseHandler

__all__ = ['platform_manager', 'BaseHandler']
