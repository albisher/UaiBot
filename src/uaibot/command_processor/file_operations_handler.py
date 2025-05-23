"""
File operations handler for UaiBot command processor.
Handles file-related commands and operations.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from uaibot.core.file_operations import FileOperations, FileOperation

@dataclass
class FileCommand:
    """Data class representing a file command."""
    command: str
    arguments: Dict[str, Any]
    flags: Optional[Dict[str, bool]] = None

class FileOperationsHandler:
    """Handler for file operations in the command processor."""
    
    def __init__(self):
        self.file_ops = FileOperations()
    
    def handle_command(self, command: FileCommand) -> str:
        """Handle a file command."""
        if not command.command:
            return "Error: No command specified"
        
        # Parse the command into a file operation
        operation = self._parse_command(command)
        
        # Execute the operation
        return self.file_ops.execute(operation)
    
    def _parse_command(self, command: FileCommand) -> FileOperation:
        """Parse a command into a file operation."""
        # Map command to operation type
        operation_map = {
            'create': 'create',
            'read': 'read',
            'write': 'write',
            'append': 'append',
            'delete': 'delete',
            'search': 'search',
            'list': 'list',
            'rename': 'rename',
            'copy': 'copy',
            'info': 'info'
        }
        
        operation_type = operation_map.get(command.command.lower())
        if not operation_type:
            return FileOperation(operation='unknown')
        
        # Extract arguments
        filename = command.arguments.get('filename')
        content = command.arguments.get('content')
        directory = command.arguments.get('directory')
        pattern = command.arguments.get('pattern')
        
        # Handle special cases
        if operation_type == 'rename' and 'new_name' in command.arguments:
            content = command.arguments['new_name']
        elif operation_type == 'copy' and 'destination' in command.arguments:
            content = command.arguments['destination']
        
        return FileOperation(
            operation=operation_type,
            filename=filename,
            content=content,
            directory=directory,
            pattern=pattern
        ) 