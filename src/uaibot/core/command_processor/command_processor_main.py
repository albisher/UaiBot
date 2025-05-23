# Copyright (c) 2025 UaiBot Team
# License: Custom license - free for personal and educational use.
# Commercial use requires a paid license. See LICENSE file for details.

import re
import os
import platform
import sys
import json
import shlex
import base64
import logging
from typing import Dict, Any, Union, Optional, List, TypeVar, Generic, Literal
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from uaibot.utils import get_project_root, run_command
from uaibot.core.platform_commands import PlatformCommands
from uaibot.core.command_processor.command_registry import CommandRegistry
from uaibot.core.command_processor.command_executor import CommandExecutor
from uaibot.core.parallel_utils import ParallelTaskManager, run_in_parallel
from uaibot.core.command_processor.ai_command_extractor import AICommandExtractor
from uaibot.utils.ai_json_tools import build_ai_prompt
from uaibot.core.controller import ExecutionController
from ..ai_handler import AIHandler
from .command_processor_types import Command, CommandResult, CommandConfig, CommandContext
from .command_processor_utils import validate_command, check_command_safety, format_command_result
from .command_processor_exceptions import CommandValidationError, CommandSafetyError, CommandProcessingError, AIError

# Set up logging
logger = logging.getLogger(__name__)

# Type variables for command responses
T = TypeVar('T')
CommandResponse = TypeVar('CommandResponse')

@dataclass
class ProcessingStats:
    """Statistics for command processing."""
    total_commands: int = 0
    successful_commands: int = 0
    failed_commands: int = 0
    average_processing_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

class CommandProcessor:
    """Main command processor class."""
    
    def __init__(
        self,
        ai_handler: AIHandler,
        config: Optional[CommandConfig] = None,
        context: Optional[CommandContext] = None
    ):
        """Initialize the command processor.
        
        Args:
            ai_handler: The AI handler to use
            config: Optional configuration
            context: Optional context
        """
        self.ai_handler = ai_handler
        self.config = config or CommandConfig()
        self.context = context or CommandContext()
        self.stats = ProcessingStats()
        
    def process_command(self, command: str) -> CommandResult:
        """Process a command.
        
        Args:
            command: The command to process
            
        Returns:
            CommandResult containing the processing result
        """
        try:
            # Update stats
            self.stats.total_commands += 1
            start_time = datetime.now()
            
            # Validate command
            validation = validate_command(command)
            if not validation.is_valid:
                raise CommandValidationError(validation.error)
                
            # Check safety
            safety = check_command_safety(command, self.config.safety_level)
            if not safety.is_safe:
                raise CommandSafetyError(safety.error)
                
            # Process command with AI
            try:
                response = self.ai_handler.process_prompt(command)
                result = CommandResult(
                    success=True,
                    output=response.output,
                    metadata={
                        "model": response.metadata.get("model"),
                        "tokens": response.metadata.get("tokens"),
                        "processing_time": (datetime.now() - start_time).total_seconds()
                    }
                )
                
            except Exception as e:
                raise AIError(f"AI processing error: {str(e)}")
                
            # Update stats
            self.stats.successful_commands += 1
            self._update_stats(start_time)
            
            return result
            
        except (CommandValidationError, CommandSafetyError, CommandProcessingError, AIError) as e:
            # Update stats
            self.stats.failed_commands += 1
            self._update_stats(start_time)
            
            # Return error result
            return CommandResult(
                success=False,
                error=str(e),
                metadata={
                    "error_type": e.__class__.__name__,
                    "processing_time": (datetime.now() - start_time).total_seconds()
                }
            )
            
        except Exception as e:
            # Update stats
            self.stats.failed_commands += 1
            self._update_stats(start_time)
            
            # Log unexpected error
            logger.error(f"Unexpected error processing command: {e}")
            
            # Return error result
            return CommandResult(
                success=False,
                error=f"Unexpected error: {str(e)}",
                metadata={
                    "error_type": "UnexpectedError",
                    "processing_time": (datetime.now() - start_time).total_seconds()
                }
            )
            
    def _update_stats(self, start_time: datetime) -> None:
        """Update processing statistics.
        
        Args:
            start_time: Start time of command processing
        """
        try:
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Update average processing time
            if self.stats.total_commands > 0:
                self.stats.average_processing_time = (
                    (self.stats.average_processing_time * (self.stats.total_commands - 1) +
                     processing_time) / self.stats.total_commands
                )
                
            # Update metadata
            self.stats.metadata.update({
                "last_processing_time": processing_time,
                "last_update": datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error updating stats: {e}")
            
    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics.
        
        Returns:
            Dict containing processing statistics
        """
        return {
            "total_commands": self.stats.total_commands,
            "successful_commands": self.stats.successful_commands,
            "failed_commands": self.stats.failed_commands,
            "average_processing_time": self.stats.average_processing_time,
            "metadata": self.stats.metadata
        }
        
    def reset_stats(self) -> None:
        """Reset processing statistics."""
        self.stats = ProcessingStats()

if __name__ == "__main__":
    # Example usage
    from ..config_manager import ConfigManager
    from ..model_manager import ModelManager
    
    # Initialize components
    config_manager = ConfigManager()
    model_manager = ModelManager(config_manager)
    ai_handler = AIHandler(model_manager)
    
    # Create command processor
    processor = CommandProcessor(ai_handler)
    
    # Process command
    result = processor.process_command("What is the weather?")
    print(f"Result: {format_command_result(result)}")
    
    # Get stats
    stats = processor.get_stats()
    print(f"Stats: {stats}")
