"""
Command Processor Logger module for UaiBot.

This module provides logging functionality for command processors,
including log configuration, formatting, and persistence.

The module includes:
- Log configuration
- Log formatting
- Log persistence
- Log utilities

Example:
    >>> from .command_processor_logger import CommandProcessorLogger
    >>> logger = CommandProcessorLogger()
    >>> logger.info("Processing command")
"""
import logging
import json
import os
from typing import Optional, Dict, Any, Union, List, TypeVar, Generic, Literal
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from .command_processor_types import Command, CommandResult
from .command_processor_exceptions import CommandValidationError, CommandSafetyError, CommandProcessingError, AIError

# Type variables for logger responses
T = TypeVar('T')
LoggerResponse = TypeVar('LoggerResponse')

@dataclass
class LoggerConfig:
    """Configuration for the command processor logger."""
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file: str = "logs/processor.log"
    max_bytes: int = 10485760  # 10MB
    backup_count: int = 5
    metadata: Dict[str, Any] = field(default_factory=dict)

class CommandProcessorLogger:
    """Logger for command processors."""
    
    def __init__(self, config: Optional[LoggerConfig] = None):
        """Initialize the command processor logger.
        
        Args:
            config: Optional logger configuration
        """
        self.config = config or LoggerConfig()
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """Set up the logger.
        
        Returns:
            Configured logger
        """
        try:
            # Create logger
            logger = logging.getLogger("command_processor")
            logger.setLevel(getattr(logging, self.config.log_level))
            
            # Create formatter
            formatter = logging.Formatter(self.config.log_format)
            
            # Create file handler
            os.makedirs(os.path.dirname(self.config.log_file), exist_ok=True)
            file_handler = logging.handlers.RotatingFileHandler(
                self.config.log_file,
                maxBytes=self.config.max_bytes,
                backupCount=self.config.backup_count
            )
            file_handler.setFormatter(formatter)
            
            # Create console handler
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            
            # Add handlers
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
            
            return logger
            
        except Exception as e:
            print(f"Error setting up logger: {e}")
            raise
            
    def log_command(self, command: Command) -> None:
        """Log a command.
        
        Args:
            command: Command to log
        """
        try:
            self.logger.info(f"Processing command: {command.text}")
            self.logger.debug(f"Command metadata: {command.metadata}")
            
        except Exception as e:
            self.logger.error(f"Error logging command: {e}")
            raise
            
    def log_result(self, result: CommandResult) -> None:
        """Log a command result.
        
        Args:
            result: Result to log
        """
        try:
            if result.success:
                self.logger.info(f"Command succeeded: {result.output}")
            else:
                self.logger.error(f"Command failed: {result.error}")
                
            self.logger.debug(f"Result metadata: {result.metadata}")
            
        except Exception as e:
            self.logger.error(f"Error logging result: {e}")
            raise
            
    def log_error(self, error: Exception) -> None:
        """Log an error.
        
        Args:
            error: Error to log
        """
        try:
            self.logger.error(f"Error: {str(error)}")
            
        except Exception as e:
            print(f"Error logging error: {e}")
            raise

if __name__ == "__main__":
    # Example usage
    logger = CommandProcessorLogger()
    
    # Log command
    command = Command(text="What is the weather?")
    logger.log_command(command)
    
    # Log result
    result = CommandResult(
        success=True,
        output="The weather is sunny",
        error=None,
        metadata={"temperature": 25}
    )
    logger.log_result(result)
    
    # Log error
    error = CommandValidationError("Invalid command")
    logger.log_error(error) 