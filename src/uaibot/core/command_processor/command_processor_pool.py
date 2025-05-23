"""
Command Processor Pool module for UaiBot.

This module provides pool functionality for command processors,
including worker management, load balancing, and resource allocation.

The module includes:
- Worker management
- Load balancing
- Resource allocation
- Pool utilities

Example:
    >>> from .command_processor_pool import CommandProcessorPool
    >>> pool = CommandProcessorPool()
    >>> pool.execute_command("What is the weather?")
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
from .command_processor_worker import CommandProcessorWorker, WorkerConfig, TaskResult

# Set up logging
logger = logging.getLogger(__name__)

# Type variables for pool responses
T = TypeVar('T')
PoolResponse = TypeVar('PoolResponse')

@dataclass
class PoolConfig:
    """Configuration for the command processor pool."""
    min_workers: int = 1
    max_workers: int = 10
    worker_timeout: float = 300.0  # seconds
    load_threshold: float = 0.8
    cleanup_interval: float = 3600.0  # seconds
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WorkerInfo:
    """Information about a worker in the pool."""
    id: str = ""
    worker: CommandProcessorWorker = field(default_factory=lambda: CommandProcessorWorker())
    status: str = "idle"
    last_used: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PoolStats:
    """Statistics for pool performance."""
    total_workers: int = 0
    active_workers: int = 0
    total_tasks: int = 0
    successful_tasks: int = 0
    failed_tasks: int = 0
    average_load: float = 0.0
    last_update: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

class CommandProcessorPool:
    """Pool for command processors."""
    
    def __init__(self, config: Optional[PoolConfig] = None):
        """Initialize the command processor pool.
        
        Args:
            config: Optional pool configuration
        """
        self.config = config or PoolConfig()
        self.workers: Dict[str, WorkerInfo] = {}
        self.stats = PoolStats()
        self.last_cleanup = datetime.now()
        
        # Initialize minimum number of workers
        for i in range(self.config.min_workers):
            self._add_worker()
            
    def execute_command(self, command: Command) -> TaskResult:
        """Execute a command using a worker from the pool.
        
        Args:
            command: Command to execute
            
        Returns:
            Task result
        """
        try:
            # Get available worker
            worker_info = self._get_available_worker()
            
            if not worker_info:
                raise ValueError("No available workers")
                
            # Execute command
            task_id = f"task_{int(time.time())}"
            result = worker_info.worker.execute_task(task_id, command)
            
            # Update worker info
            worker_info.status = "busy"
            worker_info.last_used = datetime.now()
            
            # Update statistics
            self._update_stats(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            raise
            
    def get_worker_info(self, worker_id: str) -> Optional[WorkerInfo]:
        """Get worker information.
        
        Args:
            worker_id: Worker ID
            
        Returns:
            Worker information if available
        """
        try:
            return self.workers.get(worker_id)
            
        except Exception as e:
            logger.error(f"Error getting worker info: {e}")
            raise
            
    def get_all_workers(self) -> List[WorkerInfo]:
        """Get all worker information.
        
        Returns:
            List of worker information
        """
        try:
            return list(self.workers.values())
            
        except Exception as e:
            logger.error(f"Error getting all workers: {e}")
            raise
            
    def get_pool_stats(self) -> PoolStats:
        """Get pool statistics.
        
        Returns:
            Pool statistics
        """
        try:
            return self.stats
            
        except Exception as e:
            logger.error(f"Error getting pool stats: {e}")
            raise
            
    def _add_worker(self) -> None:
        """Add a new worker to the pool."""
        try:
            if len(self.workers) >= self.config.max_workers:
                raise ValueError("Maximum number of workers reached")
                
            worker_id = f"worker_{len(self.workers) + 1}"
            
            self.workers[worker_id] = WorkerInfo(
                id=worker_id,
                worker=CommandProcessorWorker(
                    WorkerConfig(timeout=self.config.worker_timeout)
                )
            )
            
            self.stats.total_workers += 1
            self.stats.active_workers += 1
            
        except Exception as e:
            logger.error(f"Error adding worker: {e}")
            raise
            
    def _remove_worker(self, worker_id: str) -> None:
        """Remove a worker from the pool.
        
        Args:
            worker_id: Worker ID
        """
        try:
            if worker_id in self.workers:
                del self.workers[worker_id]
                self.stats.total_workers -= 1
                self.stats.active_workers -= 1
                
        except Exception as e:
            logger.error(f"Error removing worker: {e}")
            raise
            
    def _get_available_worker(self) -> Optional[WorkerInfo]:
        """Get an available worker from the pool.
        
        Returns:
            Available worker if any
        """
        try:
            # Check if we need more workers
            if len(self.workers) < self.config.max_workers:
                self._add_worker()
                
            # Get idle workers
            idle_workers = [
                w for w in self.workers.values()
                if w.status == "idle"
            ]
            
            if idle_workers:
                return idle_workers[0]
                
            # Get least busy worker
            return min(
                self.workers.values(),
                key=lambda w: w.worker.get_worker_stats().total_tasks
            )
            
        except Exception as e:
            logger.error(f"Error getting available worker: {e}")
            raise
            
    def _update_stats(self, task_result: TaskResult) -> None:
        """Update pool statistics.
        
        Args:
            task_result: Task result
        """
        try:
            self.stats.total_tasks += 1
            
            if task_result.success:
                self.stats.successful_tasks += 1
            else:
                self.stats.failed_tasks += 1
                
            # Calculate average load
            total_load = sum(
                w.worker.get_worker_stats().total_tasks
                for w in self.workers.values()
            )
            self.stats.average_load = total_load / len(self.workers)
            
            self.stats.last_update = datetime.now()
            
        except Exception as e:
            logger.error(f"Error updating stats: {e}")
            raise
            
    def _cleanup_idle_workers(self) -> None:
        """Clean up idle workers."""
        try:
            now = datetime.now()
            
            if (now - self.last_cleanup).total_seconds() < self.config.cleanup_interval:
                return
                
            # Remove idle workers if we have more than minimum
            idle_workers = [
                w for w in self.workers.values()
                if w.status == "idle" and
                (now - w.last_used).total_seconds() > self.config.worker_timeout
            ]
            
            for worker in idle_workers:
                if len(self.workers) > self.config.min_workers:
                    self._remove_worker(worker.id)
                    
            self.last_cleanup = now
            
        except Exception as e:
            logger.error(f"Error cleaning up workers: {e}")
            raise

if __name__ == "__main__":
    # Example usage
    pool = CommandProcessorPool()
    
    # Execute commands
    command1 = Command(text="What is the weather?")
    command2 = Command(text="Check system status")
    
    result1 = pool.execute_command(command1)
    result2 = pool.execute_command(command2)
    
    # Get worker info
    worker_info = pool.get_worker_info("worker_1")
    print(f"Worker info: {worker_info}")
    
    # Get all workers
    all_workers = pool.get_all_workers()
    print(f"All workers: {all_workers}")
    
    # Get pool stats
    stats = pool.get_pool_stats()
    print(f"Pool stats: {stats}") 