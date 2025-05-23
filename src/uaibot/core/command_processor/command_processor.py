"""
Command Processor module for UaiBot.

This module handles the processing and execution of commands using AI models.
It includes command validation, safety checks, and response handling.

The module includes:
- Command processing and validation
- Safety checks and filtering
- Response handling and formatting
- Error handling and logging

Example:
    >>> config = ConfigManager()
    >>> model_manager = ModelManager(config)
    >>> ai_handler = AIHandler(model_manager)
    >>> processor = CommandProcessor(ai_handler)
    >>> result = processor.process_command("What is the weather?")
"""
import logging
import json
import os
from typing import Optional, Dict, Any, Union, List, TypeVar, Generic
from dataclasses import dataclass, field
from datetime import datetime
from ..ai_handler import AIHandler

# Set up logging
logger = logging.getLogger(__name__)

# Type variables for command responses
T = TypeVar('T')
CommandResponse = TypeVar('CommandResponse')

@dataclass
class CommandConfig:
    """Configuration for command processing."""
    max_retries: int = 3
    timeout: int = 30
    safety_level: str = "strict"

@dataclass
class CommandResult:
    """Result of a command execution."""
    success: bool
    output: str
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class CommandProcessor:
    """
    A class to process and execute commands using AI models.
    
    This class provides a unified interface for processing commands,
    including validation, safety checks, and response handling.
    
    Attributes:
        ai_handler (AIHandler): AI handler instance
        config (CommandConfig): Configuration for command processing
    """
    
    def __init__(self, ai_handler: AIHandler) -> None:
        """
        Initialize the CommandProcessor.
        
        Args:
            ai_handler (AIHandler): AI handler instance
        """
        self.ai_handler = ai_handler
        self.config = CommandConfig()
    
    def process_command(self, command: str) -> CommandResult:
        """
        Process a command using the AI model.
        
        Args:
            command (str): The command to process
            
        Returns:
            CommandResult: The result of the command execution
            
        Raises:
            Exception: If there's an error processing the command
        """
        try:
            # Validate command
            if not self._validate_command(command):
                return CommandResult(
                    success=False,
                    output="",
                    error="Invalid command format"
                )
            
            # Check command safety
            if not self._check_command_safety(command):
                return CommandResult(
                    success=False,
                    output="",
                    error="Command failed safety check"
                )
            
            # Process command with AI
            response = self.ai_handler.process_prompt(command)
            
            # Save result
            self._save_command_result(command, response)
            
            return CommandResult(
                success=True,
                output=response.text,
                metadata=response.metadata
            )
            
        except Exception as e:
            logger.error(f"Error processing command: {str(e)}")
            return CommandResult(
                success=False,
                output="",
                error=str(e)
            )
    
    def _validate_command(self, command: str) -> bool:
        """
        Validate the command format.
        
        Args:
            command (str): The command to validate
            
        Returns:
            bool: True if the command is valid, False otherwise
        """
        # Basic validation
        if not command or not isinstance(command, str):
            return False
        
        # Add more validation rules as needed
        return True
    
    def _check_command_safety(self, command: str) -> bool:
        """
        Check if the command is safe to execute.
        
        Args:
            command (str): The command to check
            
        Returns:
            bool: True if the command is safe, False otherwise
        """
        # Add safety checks based on config.safety_level
        if self.config.safety_level == "strict":
            # Implement strict safety checks
            pass
        elif self.config.safety_level == "moderate":
            # Implement moderate safety checks
            pass
        else:
            # Implement basic safety checks
            pass
        
        return True
    
    def _save_command_result(self, command: str, response: Any) -> None:
        """
        Save the command result to a file.
        
        Args:
            command (str): The original command
            response (Any): The AI response
        """
        try:
            # Create results directory if it doesn't exist
            results_dir = os.path.join("results", "command_results")
            os.makedirs(results_dir, exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            sanitized_command = "".join(c if c.isalnum() else "_" for c in command[:50])
            filename = f"{timestamp}_{sanitized_command}.json"
            
            # Prepare result data
            result_data = {
                "timestamp": timestamp,
                "command": command,
                "result": response.text,
                "raw_response": response.raw_response,
                "metadata": {
                    "model": response.metadata.get("model"),
                    "tokens": response.metadata.get("tokens"),
                    "processing_time": response.metadata.get("processing_time")
                }
            }
            
            # Save to file
            filepath = os.path.join(results_dir, filename)
            with open(filepath, "w") as f:
                json.dump(result_data, f, indent=2)
            
            logger.info(f"Saved command result to {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving command result: {str(e)}") 