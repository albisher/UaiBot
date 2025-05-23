"""
Command Processor Worker module for UaiBot.

This module provides worker functionality for command processors,
including task execution, result handling, and worker management.

The module includes:
- Task execution
- Result handling
- Worker management
- Worker utilities

Example:
    >>> from .command_processor_worker import CommandProcessorWorker
    >>> worker = CommandProcessorWorker()
    >>> worker.execute_task("task1", "What is the weather?")
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

# Type variables for worker responses
T = TypeVar('T')
WorkerResponse = TypeVar('WorkerResponse')

@dataclass
class WorkerConfig:
    """Configuration for the command processor worker."""
    max_tasks: int = 10
    timeout: float = 300.0  # seconds
    retry_delay: float = 60.0  # seconds
    cleanup_interval: float = 3600.0  # seconds
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TaskResult:
    """Result of task execution."""
    task_id: str = ""
    command: Command = field(default_factory=Command)
    result: Optional[CommandResult] = None
    success: bool = True
    error: Optional[str] = None
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WorkerStats:
    """Statistics for worker performance."""
    total_tasks: int = 0
    successful_tasks: int = 0
    failed_tasks: int = 0
    total_time: float = 0.0
    average_time: float = 0.0
    last_update: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

class CommandProcessorWorker:
    """Worker for command processors."""
    
    def __init__(self, config: Optional[WorkerConfig] = None):
        """Initialize the command processor worker.
        
        Args:
            config: Optional worker configuration
        """
        self.config = config or WorkerConfig()
        self.tasks: Dict[str, TaskResult] = {}
        self.stats = WorkerStats()
        self.last_cleanup = datetime.now()
        
    def execute_task(self, task_id: str, command: Command) -> TaskResult:
        """Execute a task.
        
        Args:
            task_id: Task ID
            command: Command to execute
            
        Returns:
            Task result
        """
        try:
            if len(self.tasks) >= self.config.max_tasks:
                raise ValueError("Maximum number of tasks reached")
                
            start_time = datetime.now()
            
            # Execute command
            try:
                result = self._execute_command(command)
                success = True
                error = None
            except Exception as e:
                result = None
                success = False
                error = str(e)
                
            end_time = datetime.now()
            
            # Create task result
            task_result = TaskResult(
                task_id=task_id,
                command=command,
                result=result,
                success=success,
                error=error,
                start_time=start_time,
                end_time=end_time
            )
            
            self.tasks[task_id] = task_result
            
            # Update statistics
            self._update_stats(task_result)
            
            return task_result
            
        except Exception as e:
            logger.error(f"Error executing task: {e}")
            raise
            
    def get_task_result(self, task_id: str) -> Optional[TaskResult]:
        """Get task result.
        
        Args:
            task_id: Task ID
            
        Returns:
            Task result if available
        """
        try:
            return self.tasks.get(task_id)
            
        except Exception as e:
            logger.error(f"Error getting task result: {e}")
            raise
            
    def get_all_task_results(self) -> List[TaskResult]:
        """Get all task results.
        
        Returns:
            List of task results
        """
        try:
            return list(self.tasks.values())
            
        except Exception as e:
            logger.error(f"Error getting all task results: {e}")
            raise
            
    def get_worker_stats(self) -> WorkerStats:
        """Get worker statistics.
        
        Returns:
            Worker statistics
        """
        try:
            return self.stats
            
        except Exception as e:
            logger.error(f"Error getting worker stats: {e}")
            raise
            
    def _execute_command(self, command: Command) -> CommandResult:
        """Execute a command.
        
        Args:
            command: Command to execute
            
        Returns:
            Command result
        """
        # TODO: Implement command execution
        return CommandResult(text="Command executed successfully")
        
    def _update_stats(self, task_result: TaskResult) -> None:
        """Update worker statistics.
        
        Args:
            task_result: Task result
        """
        try:
            self.stats.total_tasks += 1
            
            if task_result.success:
                self.stats.successful_tasks += 1
            else:
                self.stats.failed_tasks += 1
                
            if task_result.end_time:
                duration = (task_result.end_time - task_result.start_time).total_seconds()
                self.stats.total_time += duration
                self.stats.average_time = self.stats.total_time / self.stats.total_tasks
                
            self.stats.last_update = datetime.now()
            
        except Exception as e:
            logger.error(f"Error updating stats: {e}")
            raise
            
    def _cleanup_old_tasks(self) -> None:
        """Clean up old task results."""
        try:
            now = datetime.now()
            
            if (now - self.last_cleanup).total_seconds() < self.config.cleanup_interval:
                return
                
            cutoff = now - timedelta(days=7)
            
            self.tasks = {
                task_id: task
                for task_id, task in self.tasks.items()
                if task.end_time and task.end_time > cutoff
            }
            
            self.last_cleanup = now
            
        except Exception as e:
            logger.error(f"Error cleaning up tasks: {e}")
            raise

if __name__ == "__main__":
    # Example usage
    worker = CommandProcessorWorker()
    
    # Execute tasks
    command1 = Command(text="What is the weather?")
    command2 = Command(text="Check system status")
    
    result1 = worker.execute_task("task1", command1)
    result2 = worker.execute_task("task2", command2)
    
    # Get task results
    task_result = worker.get_task_result("task1")
    print(f"Task result: {task_result}")
    
    # Get all task results
    all_results = worker.get_all_task_results()
    print(f"All task results: {all_results}")
    
    # Get worker stats
    stats = worker.get_worker_stats()
    print(f"Worker stats: {stats}") 