"""
Command Processor Exceptions module for UaiBot.

This module provides custom exceptions for the command processor,
including validation errors, safety errors, and processing errors.

The module includes:
- Command validation exceptions
- Command safety exceptions
- Command processing exceptions
- Error handling utilities

Example:
    >>> try:
    ...     raise CommandValidationError("Invalid command format")
    ... except CommandValidationError as e:
    ...     print(f"Validation error: {e}")
"""
import logging
from typing import Optional, Dict, Any, Union, List, TypeVar, Generic
from dataclasses import dataclass, field
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)

# Type variables for error responses
T = TypeVar('T')
ErrorResponse = TypeVar('ErrorResponse')

@dataclass
class ErrorInfo:
    """Information about an error."""
    code: str
    message: str
    details: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)

class CommandProcessorError(Exception):
    """Base exception for command processor errors."""
    def __init__(self, message: str, error_info: Optional[ErrorInfo] = None):
        self.message = message
        self.error_info = error_info or ErrorInfo(
            code="UNKNOWN_ERROR",
            message=message
        )
        super().__init__(self.message)
        
    def __str__(self) -> str:
        return f"{self.error_info.code}: {self.message}"

class CommandValidationError(CommandProcessorError):
    """Exception raised for command validation errors."""
    def __init__(self, message: str, error_info: Optional[ErrorInfo] = None):
        super().__init__(
            message,
            error_info or ErrorInfo(
                code="VALIDATION_ERROR",
                message=message
            )
        )

class CommandSafetyError(CommandProcessorError):
    """Exception raised for command safety errors."""
    def __init__(self, message: str, error_info: Optional[ErrorInfo] = None):
        super().__init__(
            message,
            error_info or ErrorInfo(
                code="SAFETY_ERROR",
                message=message
            )
        )

class CommandProcessingError(CommandProcessorError):
    """Exception raised for command processing errors."""
    def __init__(self, message: str, error_info: Optional[ErrorInfo] = None):
        super().__init__(
            message,
            error_info or ErrorInfo(
                code="PROCESSING_ERROR",
                message=message
            )
        )

class AIError(CommandProcessorError):
    """Exception raised for AI-related errors."""
    def __init__(self, message: str, error_info: Optional[ErrorInfo] = None):
        super().__init__(
            message,
            error_info or ErrorInfo(
                code="AI_ERROR",
                message=message
            )
        )

def handle_command_error(error: CommandProcessorError) -> Dict[str, Any]:
    """Handle a command processor error.
    
    Args:
        error: The error to handle
        
    Returns:
        Dict containing error information
    """
    logger.error(f"Command error: {error}")
    
    return {
        "success": False,
        "error": str(error),
        "error_info": {
            "code": error.error_info.code,
            "message": error.error_info.message,
            "details": error.error_info.details,
            "timestamp": error.error_info.timestamp.isoformat(),
            "context": error.error_info.context
        }
    }

if __name__ == "__main__":
    # Example usage
    try:
        raise CommandValidationError("Invalid command format")
    except CommandValidationError as e:
        print(f"Validation error: {e}")
        print(f"Error info: {e.error_info}")
        
    try:
        raise CommandSafetyError("Dangerous command detected")
    except CommandSafetyError as e:
        print(f"Safety error: {e}")
        print(f"Error info: {e.error_info}")
        
    try:
        raise CommandProcessingError("Failed to process command")
    except CommandProcessingError as e:
        print(f"Processing error: {e}")
        print(f"Error info: {e.error_info}")
        
    try:
        raise AIError("AI model error")
    except AIError as e:
        print(f"AI error: {e}")
        print(f"Error info: {e.error_info}") 