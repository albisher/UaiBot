"""
Command Processor Router module for UaiBot.

This module provides routing functionality for command processors,
including command routing, load balancing, and request distribution.

The module includes:
- Command routing
- Load balancing
- Request distribution
- Routing utilities

Example:
    >>> from .command_processor_router import CommandProcessorRouter
    >>> router = CommandProcessorRouter()
    >>> router.route_command("What is the weather?")
"""
import logging
import json
import os
import time
from typing import Optional, Dict, Any, Union, List, TypeVar, Generic, Literal
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from .command_processor_types import Command, CommandResult
from .command_processor_exceptions import CommandValidationError, CommandSafetyError, CommandProcessingError, AIError

# Set up logging
logger = logging.getLogger(__name__)

# Type variables for router responses
T = TypeVar('T')
RouterResponse = TypeVar('RouterResponse')

@dataclass
class RouterConfig:
    """Configuration for the command processor router."""
    max_retries: int = 3
    timeout: float = 30.0  # seconds
    load_balance: bool = True
    round_robin: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ProcessorInfo:
    """Information about a command processor."""
    id: str = ""
    host: str = "localhost"
    port: int = 8000
    status: str = "active"
    load: float = 0.0
    last_used: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RoutingResult:
    """Result of command routing."""
    processor_id: str = ""
    success: bool = True
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class CommandProcessorRouter:
    """Router for command processors."""
    
    def __init__(self, config: Optional[RouterConfig] = None):
        """Initialize the command processor router.
        
        Args:
            config: Optional router configuration
        """
        self.config = config or RouterConfig()
        self.processors: Dict[str, ProcessorInfo] = {}
        self.current_index = 0
        
    def register_processor(self, processor_id: str, host: str = "localhost", port: int = 8000) -> None:
        """Register a command processor.
        
        Args:
            processor_id: Processor ID
            host: Processor host
            port: Processor port
        """
        try:
            self.processors[processor_id] = ProcessorInfo(
                id=processor_id,
                host=host,
                port=port
            )
            
        except Exception as e:
            logger.error(f"Error registering processor: {e}")
            raise
            
    def unregister_processor(self, processor_id: str) -> None:
        """Unregister a command processor.
        
        Args:
            processor_id: Processor ID
        """
        try:
            if processor_id in self.processors:
                del self.processors[processor_id]
                
        except Exception as e:
            logger.error(f"Error unregistering processor: {e}")
            raise
            
    def update_processor_status(self, processor_id: str, status: str, load: float = 0.0) -> None:
        """Update processor status.
        
        Args:
            processor_id: Processor ID
            status: New status
            load: Current load
        """
        try:
            if processor_id in self.processors:
                processor = self.processors[processor_id]
                processor.status = status
                processor.load = load
                processor.last_used = datetime.now()
                
        except Exception as e:
            logger.error(f"Error updating processor status: {e}")
            raise
            
    def route_command(self, command: Command) -> RoutingResult:
        """Route a command to a processor.
        
        Args:
            command: Command to route
            
        Returns:
            Routing result
        """
        try:
            # Check if any processors are available
            if not self.processors:
                return RoutingResult(
                    success=False,
                    error="No processors available"
                )
                
            # Get available processors
            available_processors = [
                p for p in self.processors.values()
                if p.status == "active"
            ]
            
            if not available_processors:
                return RoutingResult(
                    success=False,
                    error="No active processors available"
                )
                
            # Select processor
            if self.config.load_balance:
                # Load balancing
                selected_processor = min(
                    available_processors,
                    key=lambda p: p.load
                )
            elif self.config.round_robin:
                # Round-robin
                self.current_index = (self.current_index + 1) % len(available_processors)
                selected_processor = available_processors[self.current_index]
            else:
                # Random selection
                selected_processor = available_processors[0]
                
            # Update processor info
            self.update_processor_status(
                selected_processor.id,
                selected_processor.status,
                selected_processor.load + 1.0
            )
            
            return RoutingResult(
                processor_id=selected_processor.id,
                success=True,
                metadata={
                    "host": selected_processor.host,
                    "port": selected_processor.port,
                    "load": selected_processor.load
                }
            )
            
        except Exception as e:
            logger.error(f"Error routing command: {e}")
            raise
            
    def get_processor_info(self, processor_id: str) -> Optional[ProcessorInfo]:
        """Get processor information.
        
        Args:
            processor_id: Processor ID
            
        Returns:
            Processor information if available
        """
        try:
            return self.processors.get(processor_id)
            
        except Exception as e:
            logger.error(f"Error getting processor info: {e}")
            raise
            
    def get_all_processors(self) -> List[ProcessorInfo]:
        """Get all processor information.
        
        Returns:
            List of processor information
        """
        try:
            return list(self.processors.values())
            
        except Exception as e:
            logger.error(f"Error getting all processors: {e}")
            raise

if __name__ == "__main__":
    # Example usage
    router = CommandProcessorRouter()
    
    # Register processors
    router.register_processor("processor1", "localhost", 8001)
    router.register_processor("processor2", "localhost", 8002)
    
    # Update processor status
    router.update_processor_status("processor1", "active", 0.5)
    router.update_processor_status("processor2", "active", 0.3)
    
    # Route command
    command = Command(text="What is the weather?")
    routing = router.route_command(command)
    print(f"Routing: {routing}")
    
    # Get processor info
    processor_info = router.get_processor_info(routing.processor_id)
    print(f"Processor info: {processor_info}")
    
    # Get all processors
    all_processors = router.get_all_processors()
    print(f"All processors: {all_processors}") 