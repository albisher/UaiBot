"""
Command Processor Factory module for UaiBot.

This module provides a factory for creating command processors,
including configuration, initialization, and dependency injection.

The module includes:
- Command processor factory
- Configuration factory
- Dependency injection
- Factory utilities

Example:
    >>> from .command_processor_factory import CommandProcessorFactory
    >>> factory = CommandProcessorFactory()
    >>> processor = factory.create_processor()
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
from .command_processor_interface import CommandProcessorInterface, InterfaceConfig
from ..config_manager import ConfigManager
from ..model_manager import ModelManager
from ..ai_handler import AIHandler

# Set up logging
logger = logging.getLogger(__name__)

# Type variables for factory responses
T = TypeVar('T')
FactoryResponse = TypeVar('FactoryResponse')

@dataclass
class FactoryConfig:
    """Configuration for the command processor factory."""
    config_dir: str = "config"
    output_dir: str = "results"
    debug_mode: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

class CommandProcessorFactory:
    """Factory for creating command processors."""
    
    def __init__(self, config: Optional[FactoryConfig] = None):
        """Initialize the command processor factory.
        
        Args:
            config: Optional configuration
        """
        self.config = config or FactoryConfig()
        
    def create_processor(self) -> CommandProcessor:
        """Create a command processor.
        
        Returns:
            A new CommandProcessor instance
        """
        try:
            # Create configuration manager
            config_manager = ConfigManager()
            
            # Create model manager
            model_manager = ModelManager(config_manager)
            
            # Create AI handler
            ai_handler = AIHandler(model_manager)
            
            # Create command processor
            processor = CommandProcessor(ai_handler)
            
            return processor
            
        except Exception as e:
            logger.error(f"Error creating command processor: {e}")
            raise
            
    def create_interface(self, processor: Optional[CommandProcessor] = None) -> CommandProcessorInterface:
        """Create a command processor interface.
        
        Args:
            processor: Optional command processor
            
        Returns:
            A new CommandProcessorInterface instance
        """
        try:
            # Create processor if not provided
            if processor is None:
                processor = self.create_processor()
                
            # Create interface configuration
            interface_config = InterfaceConfig(
                debug_mode=self.config.debug_mode,
                output_dir=self.config.output_dir
            )
            
            # Create interface
            interface = CommandProcessorInterface(processor, interface_config)
            
            return interface
            
        except Exception as e:
            logger.error(f"Error creating command processor interface: {e}")
            raise
            
    def create_command_config(self) -> CommandConfig:
        """Create a command configuration.
        
        Returns:
            A new CommandConfig instance
        """
        try:
            return CommandConfig()
            
        except Exception as e:
            logger.error(f"Error creating command configuration: {e}")
            raise
            
    def create_command_context(self) -> CommandContext:
        """Create a command context.
        
        Returns:
            A new CommandContext instance
        """
        try:
            return CommandContext()
            
        except Exception as e:
            logger.error(f"Error creating command context: {e}")
            raise

if __name__ == "__main__":
    # Example usage
    factory = CommandProcessorFactory()
    
    # Create processor
    processor = factory.create_processor()
    print(f"Processor: {processor}")
    
    # Create interface
    interface = factory.create_interface(processor)
    print(f"Interface: {interface}")
    
    # Create configuration
    config = factory.create_command_config()
    print(f"Config: {config}")
    
    # Create context
    context = factory.create_command_context()
    print(f"Context: {context}")
    
    # Process command
    result = interface.handle_command("What is the weather?")
    print(f"Result: {result}") 