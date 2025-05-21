"""
Command processor module for UaiBot.
Handles command processing and execution.
"""
from uaibot.core.command_processor.command_processor_main import CommandProcessor
from uaibot.core.command_processor.command_registry import CommandRegistry
from uaibot.core.command_processor.command_executor import CommandExecutor
from uaibot.core.shell_handler import ShellHandler

__all__ = ['CommandProcessor', 'CommandRegistry', 'CommandExecutor']
