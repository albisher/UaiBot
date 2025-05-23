"""
Command Processor Interface module for UaiBot.

This module provides the interface for the command processor,
including command handling, result handling, and error handling.

The module includes:
- Command handling interface
- Result handling interface
- Error handling interface
- Logging interface

Example:
    >>> from .command_processor_interface import CommandProcessorInterface
    >>> interface = CommandProcessorInterface(processor)
    >>> result = interface.handle_command("What is the weather?")
"""
import logging
import json
import os
from typing import Optional, Dict, Any, Union, List, TypeVar, Generic, Literal
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from .command_processor_types import Command, CommandResult, CommandConfig, CommandContext
from .command_processor_exceptions import CommandValidationError, CommandSafetyError, CommandProcessingError, AIError
from .command_processor_main import CommandProcessor

# Set up logging
logger = logging.getLogger(__name__)

# Type variables for interface responses
T = TypeVar('T')
InterfaceResponse = TypeVar('InterfaceResponse')

@dataclass
class InterfaceConfig:
    """Configuration for the command processor interface."""
    quiet_mode: bool = False
    debug_mode: bool = False
    output_dir: str = "results"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class InterfaceStats:
    """Statistics for the command processor interface."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

class CommandProcessorInterface:
    """Interface for the command processor."""
    
    def __init__(
        self,
        processor: CommandProcessor,
        config: Optional[InterfaceConfig] = None
    ):
        """Initialize the command processor interface.
        
        Args:
            processor: The command processor to use
            config: Optional configuration
        """
        self.processor = processor
        self.config = config or InterfaceConfig()
        self.stats = InterfaceStats()
        
    def handle_command(self, command: str) -> CommandResult:
        """Handle a command.
        
        Args:
            command: The command to handle
            
        Returns:
            CommandResult containing the processing result
        """
        try:
            # Update stats
            self.stats.total_requests += 1
            start_time = datetime.now()
            
            # Process command
            result = self.processor.process_command(command)
            
            # Update stats
            if result.success:
                self.stats.successful_requests += 1
            else:
                self.stats.failed_requests += 1
            self._update_stats(start_time)
            
            return result
            
        except Exception as e:
            # Update stats
            self.stats.failed_requests += 1
            self._update_stats(start_time)
            
            # Log error
            logger.error(f"Error handling command: {e}")
            
            # Return error result
            return CommandResult(
                success=False,
                error=f"Interface error: {str(e)}",
                metadata={
                    "error_type": "InterfaceError",
                    "processing_time": (datetime.now() - start_time).total_seconds()
                }
            )
            
    def _update_stats(self, start_time: datetime) -> None:
        """Update interface statistics.
        
        Args:
            start_time: Start time of command handling
        """
        try:
            # Calculate response time
            response_time = (datetime.now() - start_time).total_seconds()
            
            # Update average response time
            if self.stats.total_requests > 0:
                self.stats.average_response_time = (
                    (self.stats.average_response_time * (self.stats.total_requests - 1) +
                     response_time) / self.stats.total_requests
                )
                
            # Update metadata
            self.stats.metadata.update({
                "last_response_time": response_time,
                "last_update": datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error updating stats: {e}")
            
    def get_stats(self) -> Dict[str, Any]:
        """Get interface statistics.
        
        Returns:
            Dict containing interface statistics
        """
        return {
            "total_requests": self.stats.total_requests,
            "successful_requests": self.stats.successful_requests,
            "failed_requests": self.stats.failed_requests,
            "average_response_time": self.stats.average_response_time,
            "metadata": self.stats.metadata
        }
        
    def reset_stats(self) -> None:
        """Reset interface statistics."""
        self.stats = InterfaceStats()

if __name__ == "__main__":
    # Example usage
    from ..config_manager import ConfigManager
    from ..model_manager import ModelManager
    from ..ai_handler import AIHandler
    
    # Initialize components
    config_manager = ConfigManager()
    model_manager = ModelManager(config_manager)
    ai_handler = AIHandler(model_manager)
    
    # Create command processor and interface
    processor = CommandProcessor(ai_handler)
    interface = CommandProcessorInterface(processor)
    
    # Handle command
    result = interface.handle_command("What is the weather?")
    print(f"Result: {result}")
    
    # Get stats
    stats = interface.get_stats()
    print(f"Stats: {stats}") 