"""
Command Processor Queue module for UaiBot.

This module provides queue functionality for command processors,
including task queuing, priority management, and queue monitoring.

The module includes:
- Task queuing
- Priority management
- Queue monitoring
- Queue utilities

Example:
    >>> from .command_processor_queue import CommandProcessorQueue
    >>> queue = CommandProcessorQueue()
    >>> queue.enqueue("What is the weather?", priority=1)
"""
import logging
import json
import os
import time
from typing import Optional, Dict, Any, Union, List, TypeVar, Generic, Literal
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from .command_processor_types import Command, CommandResult
from .command_processor_exceptions import CommandValidationError, CommandSafetyError, CommandProcessingError, AIError

# Set up logging
logger = logging.getLogger(__name__)

# Type variables for queue responses
T = TypeVar('T')
QueueResponse = TypeVar('QueueResponse')

@dataclass
class QueueConfig:
    """Configuration for the command processor queue."""
    max_size: int = 1000
    max_priority: int = 10
    timeout: float = 300.0  # seconds
    cleanup_interval: float = 3600.0  # seconds
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class QueueItem:
    """Item in the command processor queue."""
    id: str = ""
    command: Command = field(default_factory=Command)
    priority: int = 0
    timestamp: datetime = field(default_factory=datetime.now)
    status: str = "pending"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class QueueStats:
    """Statistics for queue performance."""
    total_items: int = 0
    processed_items: int = 0
    failed_items: int = 0
    average_wait_time: float = 0.0
    average_processing_time: float = 0.0
    last_update: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

class CommandProcessorQueue:
    """Queue for command processors."""
    
    def __init__(self, config: Optional[QueueConfig] = None):
        """Initialize the command processor queue.
        
        Args:
            config: Optional queue configuration
        """
        self.config = config or QueueConfig()
        self.items: List[QueueItem] = []
        self.stats = QueueStats()
        self.last_cleanup = datetime.now()
        
    def enqueue(self, command: Command, priority: int = 0) -> str:
        """Add a command to the queue.
        
        Args:
            command: Command to queue
            priority: Priority level (higher is more important)
            
        Returns:
            Queue item ID
        """
        try:
            if len(self.items) >= self.config.max_size:
                raise ValueError("Queue is full")
                
            if priority < 0 or priority > self.config.max_priority:
                raise ValueError(f"Priority must be between 0 and {self.config.max_priority}")
                
            item_id = f"item_{int(time.time())}"
            
            item = QueueItem(
                id=item_id,
                command=command,
                priority=priority
            )
            
            # Insert item based on priority
            for i, existing_item in enumerate(self.items):
                if priority > existing_item.priority:
                    self.items.insert(i, item)
                    break
            else:
                self.items.append(item)
                
            self.stats.total_items += 1
            self.stats.last_update = datetime.now()
            
            return item_id
            
        except Exception as e:
            logger.error(f"Error enqueueing command: {e}")
            raise
            
    def dequeue(self) -> Optional[QueueItem]:
        """Remove and return the next item from the queue.
        
        Returns:
            Next queue item if available
        """
        try:
            if not self.items:
                return None
                
            item = self.items.pop(0)
            item.status = "processing"
            
            return item
            
        except Exception as e:
            logger.error(f"Error dequeueing item: {e}")
            raise
            
    def peek(self) -> Optional[QueueItem]:
        """Get the next item from the queue without removing it.
        
        Returns:
            Next queue item if available
        """
        try:
            return self.items[0] if self.items else None
            
        except Exception as e:
            logger.error(f"Error peeking at queue: {e}")
            raise
            
    def get_item(self, item_id: str) -> Optional[QueueItem]:
        """Get a queue item by ID.
        
        Args:
            item_id: Queue item ID
            
        Returns:
            Queue item if found
        """
        try:
            for item in self.items:
                if item.id == item_id:
                    return item
            return None
            
        except Exception as e:
            logger.error(f"Error getting queue item: {e}")
            raise
            
    def remove_item(self, item_id: str) -> None:
        """Remove a queue item by ID.
        
        Args:
            item_id: Queue item ID
        """
        try:
            self.items = [item for item in self.items if item.id != item_id]
            
        except Exception as e:
            logger.error(f"Error removing queue item: {e}")
            raise
            
    def update_item_status(self, item_id: str, status: str) -> None:
        """Update queue item status.
        
        Args:
            item_id: Queue item ID
            status: New status
        """
        try:
            for item in self.items:
                if item.id == item_id:
                    item.status = status
                    
                    if status == "completed":
                        self.stats.processed_items += 1
                    elif status == "failed":
                        self.stats.failed_items += 1
                        
                    self.stats.last_update = datetime.now()
                    break
                    
        except Exception as e:
            logger.error(f"Error updating item status: {e}")
            raise
            
    def get_queue_stats(self) -> QueueStats:
        """Get queue statistics.
        
        Returns:
            Queue statistics
        """
        try:
            return self.stats
            
        except Exception as e:
            logger.error(f"Error getting queue stats: {e}")
            raise
            
    def _cleanup_old_items(self) -> None:
        """Clean up old queue items."""
        try:
            now = datetime.now()
            
            if (now - self.last_cleanup).total_seconds() < self.config.cleanup_interval:
                return
                
            cutoff = now - timedelta(seconds=self.config.timeout)
            
            self.items = [
                item for item in self.items
                if item.timestamp > cutoff
            ]
            
            self.last_cleanup = now
            
        except Exception as e:
            logger.error(f"Error cleaning up queue: {e}")
            raise

if __name__ == "__main__":
    # Example usage
    queue = CommandProcessorQueue()
    
    # Enqueue commands
    command1 = Command(text="What is the weather?")
    command2 = Command(text="Check system status")
    
    item_id1 = queue.enqueue(command1, priority=1)
    item_id2 = queue.enqueue(command2, priority=2)
    
    # Dequeue items
    item1 = queue.dequeue()
    print(f"Dequeued item: {item1}")
    
    # Peek at next item
    next_item = queue.peek()
    print(f"Next item: {next_item}")
    
    # Get item by ID
    item = queue.get_item(item_id1)
    print(f"Item by ID: {item}")
    
    # Update item status
    queue.update_item_status(item_id1, "completed")
    
    # Get queue stats
    stats = queue.get_queue_stats()
    print(f"Queue stats: {stats}") 