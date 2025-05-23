"""
Command Processor Types module for UaiBot.

This module provides type definitions for the command processor,
including command types, result types, and configuration types.

The module includes:
- Command type definitions
- Result type definitions
- Configuration type definitions
- Type utilities

Example:
    >>> from .command_processor_types import Command, CommandResult
    >>> command = Command(text="What is the weather?", type="query")
    >>> result = CommandResult(success=True, output="The weather is sunny")
"""
import logging
from typing import Optional, Dict, Any, Union, List, TypeVar, Generic, Literal
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto

# Set up logging
logger = logging.getLogger(__name__)

# Type variables for generic types
T = TypeVar('T')
CommandResponse = TypeVar('CommandResponse')

class CommandType(Enum):
    """Type of command."""
    QUERY = auto()
    ACTION = auto()
    SYSTEM = auto()
    UNKNOWN = auto()

@dataclass
class Command:
    """A command to be processed."""
    text: str
    type: CommandType = CommandType.UNKNOWN
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class CommandResult:
    """Result of processing a command."""
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class CommandConfig:
    """Configuration for command processing."""
    max_retries: int = 3
    timeout: float = 30.0
    safety_level: Literal["basic", "moderate", "strict"] = "moderate"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CommandContext:
    """Context for command processing."""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    environment: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CommandStats:
    """Statistics for command processing."""
    total_commands: int = 0
    successful_commands: int = 0
    failed_commands: int = 0
    average_processing_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

def create_command(text: str, type: CommandType = CommandType.UNKNOWN) -> Command:
    """Create a new command.
    
    Args:
        text: The command text
        type: The command type
        
    Returns:
        A new Command instance
    """
    return Command(text=text, type=type)

def create_command_result(
    success: bool,
    output: Optional[str] = None,
    error: Optional[str] = None
) -> CommandResult:
    """Create a new command result.
    
    Args:
        success: Whether the command was successful
        output: The command output
        error: The error message if any
        
    Returns:
        A new CommandResult instance
    """
    return CommandResult(success=success, output=output, error=error)

def create_command_config(
    max_retries: int = 3,
    timeout: float = 30.0,
    safety_level: Literal["basic", "moderate", "strict"] = "moderate"
) -> CommandConfig:
    """Create a new command configuration.
    
    Args:
        max_retries: Maximum number of retries
        timeout: Command timeout in seconds
        safety_level: Safety level for command processing
        
    Returns:
        A new CommandConfig instance
    """
    return CommandConfig(
        max_retries=max_retries,
        timeout=timeout,
        safety_level=safety_level
    )

def create_command_context(
    user_id: Optional[str] = None,
    session_id: Optional[str] = None
) -> CommandContext:
    """Create a new command context.
    
    Args:
        user_id: The user ID
        session_id: The session ID
        
    Returns:
        A new CommandContext instance
    """
    return CommandContext(user_id=user_id, session_id=session_id)

def create_command_stats() -> CommandStats:
    """Create new command statistics.
    
    Returns:
        A new CommandStats instance
    """
    return CommandStats()

if __name__ == "__main__":
    # Example usage
    command = create_command("What is the weather?", CommandType.QUERY)
    print(f"Command: {command}")
    
    result = create_command_result(True, "The weather is sunny")
    print(f"Result: {result}")
    
    config = create_command_config(max_retries=5, safety_level="strict")
    print(f"Config: {config}")
    
    context = create_command_context(user_id="user123", session_id="session456")
    print(f"Context: {context}")
    
    stats = create_command_stats()
    print(f"Stats: {stats}") 