import os
import sys
from pathlib import Path
from typing import Dict, Callable, Any, Optional
from dataclasses import dataclass, field
from src.app.logging_config import get_logger

# Add src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))))
sys.path.append(project_root)

logger = get_logger(__name__)

@dataclass
class CommandResult:
    success: bool
    output: Any
    error: Optional[str] = None

class CommandProcessor:
    """
    Handles command registration and execution for Labeeb.
    Provides a unified interface for processing and executing commands.
    """
    def __init__(self):
        self.commands: Dict[str, Callable] = {}
        self.handlers: Dict[str, Callable] = {}

    def register_command(self, command: str, handler: Callable) -> None:
        """Register a new command and its handler."""
        if command in self.commands:
            logger.warning(f"Command {command} already registered, overwriting")
        self.commands[command] = handler
        logger.debug(f"Registered command: {command}")

    def register_handler(self, handler_type: str, handler: Callable) -> None:
        """Register a new handler type."""
        if handler_type in self.handlers:
            logger.warning(f"Handler {handler_type} already registered, overwriting")
        self.handlers[handler_type] = handler
        logger.debug(f"Registered handler: {handler_type}")

    def process_command(self, command_str: str) -> CommandResult:
        """Process and execute a command string."""
        try:
            # Split command and arguments
            parts = command_str.strip().split(maxsplit=1)
            command = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""

            # Check if command exists
            if command not in self.commands:
                return CommandResult(
                    success=False,
                    output=None,
                    error=f"Unknown command: {command}"
                )

            # Execute command
            handler = self.commands[command]
            result = handler(args)
            return CommandResult(success=True, output=result)

        except Exception as e:
            logger.error(f"Error processing command: {str(e)}")
            return CommandResult(
                success=False,
                output=None,
                error=str(e)
            ) 