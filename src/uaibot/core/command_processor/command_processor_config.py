"""
Command Processor Configuration module for UaiBot.

This module provides configuration management for command processors,
including loading, validation, and persistence of configuration settings.

The module includes:
- Configuration loading and validation
- Configuration persistence
- Configuration utilities

Example:
    >>> from .command_processor_config import CommandProcessorConfig
    >>> config = CommandProcessorConfig()
    >>> settings = config.load_config()
"""
import logging
import json
import os
from typing import Optional, Dict, Any, Union, List, TypeVar, Generic, Literal
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from .command_processor_types import CommandConfig
from .command_processor_exceptions import CommandValidationError, CommandSafetyError, CommandProcessingError, AIError

# Set up logging
logger = logging.getLogger(__name__)

# Type variables for configuration responses
T = TypeVar('T')
ConfigResponse = TypeVar('ConfigResponse')

@dataclass
class ProcessorConfig:
    """Configuration for the command processor."""
    max_retries: int = 3
    timeout: int = 30
    safety_level: str = "moderate"
    debug_mode: bool = False
    output_dir: str = "results"
    metadata: Dict[str, Any] = field(default_factory=dict)

class CommandProcessorConfig:
    """Configuration manager for command processors."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the command processor configuration.
        
        Args:
            config_path: Optional path to configuration file
        """
        self.config_path = config_path or "config/processor_config.json"
        self.config = ProcessorConfig()
        
    def load_config(self) -> ProcessorConfig:
        """Load configuration from file.
        
        Returns:
            Loaded configuration
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                    self.config = ProcessorConfig(**data)
            return self.config
            
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            raise
            
    def save_config(self, config: Optional[ProcessorConfig] = None) -> None:
        """Save configuration to file.
        
        Args:
            config: Optional configuration to save
        """
        try:
            config = config or self.config
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            # Save configuration
            with open(self.config_path, 'w') as f:
                json.dump(config.__dict__, f, indent=4)
                
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            raise
            
    def validate_config(self, config: Optional[ProcessorConfig] = None) -> bool:
        """Validate configuration.
        
        Args:
            config: Optional configuration to validate
            
        Returns:
            True if configuration is valid
        """
        try:
            config = config or self.config
            
            # Validate max retries
            if config.max_retries < 0:
                raise CommandValidationError("Max retries must be non-negative")
                
            # Validate timeout
            if config.timeout < 0:
                raise CommandValidationError("Timeout must be non-negative")
                
            # Validate safety level
            if config.safety_level not in ["basic", "moderate", "strict"]:
                raise CommandValidationError("Invalid safety level")
                
            return True
            
        except Exception as e:
            logger.error(f"Error validating configuration: {e}")
            raise
            
    def create_command_config(self) -> CommandConfig:
        """Create a command configuration from processor configuration.
        
        Returns:
            A new CommandConfig instance
        """
        try:
            return CommandConfig(
                max_retries=self.config.max_retries,
                timeout=self.config.timeout,
                safety_level=self.config.safety_level
            )
            
        except Exception as e:
            logger.error(f"Error creating command configuration: {e}")
            raise

if __name__ == "__main__":
    # Example usage
    config_manager = CommandProcessorConfig()
    
    # Load configuration
    config = config_manager.load_config()
    print(f"Config: {config}")
    
    # Validate configuration
    is_valid = config_manager.validate_config(config)
    print(f"Config valid: {is_valid}")
    
    # Create command configuration
    command_config = config_manager.create_command_config()
    print(f"Command config: {command_config}")
    
    # Save configuration
    config_manager.save_config(config) 