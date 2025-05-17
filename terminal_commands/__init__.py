"""
Terminal commands package for UaiBot.
Contains command templates and executors for various platforms.
"""

from .command_registry import CommandRegistry
from .command_executor import CommandExecutor
from .output_processor import OutputProcessor

__all__ = ['CommandRegistry', 'CommandExecutor', 'OutputProcessor']
