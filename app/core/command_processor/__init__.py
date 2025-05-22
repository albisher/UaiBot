"""
Command processor module for UaiBot.
Handles command processing and execution.
"""
from app.core.command_processor.command_processor_main import CommandProcessor
from app.core.command_processor.command_registry import CommandRegistry
from app.core.command_processor.command_executor import CommandExecutor
from app.core.shell_handler import ShellHandler

__all__ = ['CommandProcessor', 'CommandRegistry', 'CommandExecutor']
