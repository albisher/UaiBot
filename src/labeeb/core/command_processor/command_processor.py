"""
Command processor for Labeeb.
Handles command registration and processing.
"""
from dataclasses import dataclass
from typing import Dict, Any, Callable, Optional

@dataclass
class CommandResult:
    """Result of a command execution."""
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None

class CommandProcessor:
    """Processes and executes commands."""
    
    def __init__(self, ai_handler=None):
        """Initialize the command processor.
        
        Args:
            ai_handler: Optional AI handler for AI-powered commands
        """
        self.commands: Dict[str, Callable] = {}
        self.handlers: Dict[str, Callable] = {}
        self.ai_handler = ai_handler
    
    def register_command(self, command: str, handler: Callable) -> None:
        """Register a new command.
        
        Args:
            command: Command name
            handler: Command handler function
        """
        self.commands[command] = handler
    
    def process_command(self, command: str) -> CommandResult:
        """Process a command.
        
        Args:
            command: Command to process
            
        Returns:
            CommandResult containing the result of the command execution
        """
        try:
            # Split command into parts
            parts = command.split()
            if not parts:
                return CommandResult(False, error="Empty command")
            
            # Get command name and arguments
            cmd_name = parts[0]
            args = ' '.join(parts[1:])
            
            # Check if command exists
            if cmd_name not in self.commands:
                return CommandResult(False, error=f"Unknown command: {cmd_name}")
            
            # Execute command
            handler = self.commands[cmd_name]
            output = handler(args)
            
            return CommandResult(True, output=output)
            
        except Exception as e:
            return CommandResult(False, error=str(e))
