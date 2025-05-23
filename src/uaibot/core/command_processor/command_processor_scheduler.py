"""
Command Processor Scheduler module for UaiBot.

This module provides scheduling functionality for command processors,
including task scheduling, job management, and execution tracking.

The module includes:
- Task scheduling
- Job management
- Execution tracking
- Scheduling utilities

Example:
    >>> from .command_processor_scheduler import CommandProcessorScheduler
    >>> scheduler = CommandProcessorScheduler()
    >>> scheduler.schedule_task("task1", "What is the weather?", "*/5 * * * *")
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

# Type variables for scheduler responses
T = TypeVar('T')
SchedulerResponse = TypeVar('SchedulerResponse')

@dataclass
class SchedulerConfig:
    """Configuration for the command processor scheduler."""
    max_tasks: int = 100
    max_retries: int = 3
    retry_delay: float = 60.0  # seconds
    cleanup_interval: float = 3600.0  # seconds
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TaskInfo:
    """Information about a scheduled task."""
    id: str = ""
    command: Command = field(default_factory=Command)
    schedule: str = ""  # Cron expression
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    status: str = "pending"
    retries: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ExecutionResult:
    """Result of task execution."""
    task_id: str = ""
    success: bool = True
    error: Optional[str] = None
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class CommandProcessorScheduler:
    """Scheduler for command processors."""
    
    def __init__(self, config: Optional[SchedulerConfig] = None):
        """Initialize the command processor scheduler.
        
        Args:
            config: Optional scheduler configuration
        """
        self.config = config or SchedulerConfig()
        self.tasks: Dict[str, TaskInfo] = {}
        self.executions: Dict[str, List[ExecutionResult]] = {}
        self.last_cleanup = datetime.now()
        
    def schedule_task(self, task_id: str, command: Command, schedule: str) -> None:
        """Schedule a task.
        
        Args:
            task_id: Task ID
            command: Command to execute
            schedule: Cron expression
        """
        try:
            if len(self.tasks) >= self.config.max_tasks:
                raise ValueError("Maximum number of tasks reached")
                
            self.tasks[task_id] = TaskInfo(
                id=task_id,
                command=command,
                schedule=schedule,
                next_run=self._calculate_next_run(schedule)
            )
            
        except Exception as e:
            logger.error(f"Error scheduling task: {e}")
            raise
            
    def unschedule_task(self, task_id: str) -> None:
        """Unschedule a task.
        
        Args:
            task_id: Task ID
        """
        try:
            if task_id in self.tasks:
                del self.tasks[task_id]
                
        except Exception as e:
            logger.error(f"Error unscheduling task: {e}")
            raise
            
    def update_task_status(self, task_id: str, status: str) -> None:
        """Update task status.
        
        Args:
            task_id: Task ID
            status: New status
        """
        try:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                task.status = status
                
                if status == "completed":
                    task.last_run = datetime.now()
                    task.next_run = self._calculate_next_run(task.schedule)
                    
        except Exception as e:
            logger.error(f"Error updating task status: {e}")
            raise
            
    def get_task_info(self, task_id: str) -> Optional[TaskInfo]:
        """Get task information.
        
        Args:
            task_id: Task ID
            
        Returns:
            Task information if available
        """
        try:
            return self.tasks.get(task_id)
            
        except Exception as e:
            logger.error(f"Error getting task info: {e}")
            raise
            
    def get_all_tasks(self) -> List[TaskInfo]:
        """Get all task information.
        
        Returns:
            List of task information
        """
        try:
            return list(self.tasks.values())
            
        except Exception as e:
            logger.error(f"Error getting all tasks: {e}")
            raise
            
    def record_execution(self, task_id: str, success: bool, error: Optional[str] = None) -> None:
        """Record task execution.
        
        Args:
            task_id: Task ID
            success: Whether execution was successful
            error: Error message if any
        """
        try:
            if task_id not in self.executions:
                self.executions[task_id] = []
                
            result = ExecutionResult(
                task_id=task_id,
                success=success,
                error=error,
                end_time=datetime.now()
            )
            
            self.executions[task_id].append(result)
            
            # Update task status
            if success:
                self.update_task_status(task_id, "completed")
            else:
                task = self.tasks[task_id]
                task.retries += 1
                
                if task.retries >= self.config.max_retries:
                    self.update_task_status(task_id, "failed")
                else:
                    self.update_task_status(task_id, "retrying")
                    task.next_run = datetime.now() + timedelta(seconds=self.config.retry_delay)
                    
        except Exception as e:
            logger.error(f"Error recording execution: {e}")
            raise
            
    def get_execution_history(self, task_id: str) -> List[ExecutionResult]:
        """Get task execution history.
        
        Args:
            task_id: Task ID
            
        Returns:
            List of execution results
        """
        try:
            return self.executions.get(task_id, [])
            
        except Exception as e:
            logger.error(f"Error getting execution history: {e}")
            raise
            
    def _calculate_next_run(self, schedule: str) -> datetime:
        """Calculate next run time from cron expression.
        
        Args:
            schedule: Cron expression
            
        Returns:
            Next run time
        """
        # TODO: Implement cron expression parsing
        return datetime.now() + timedelta(minutes=5)
        
    def _cleanup_old_executions(self) -> None:
        """Clean up old execution records."""
        try:
            now = datetime.now()
            
            if (now - self.last_cleanup).total_seconds() < self.config.cleanup_interval:
                return
                
            cutoff = now - timedelta(days=7)
            
            for task_id in self.executions:
                self.executions[task_id] = [
                    e for e in self.executions[task_id]
                    if e.end_time and e.end_time > cutoff
                ]
                
            self.last_cleanup = now
            
        except Exception as e:
            logger.error(f"Error cleaning up executions: {e}")
            raise

if __name__ == "__main__":
    # Example usage
    scheduler = CommandProcessorScheduler()
    
    # Schedule tasks
    command1 = Command(text="What is the weather?")
    command2 = Command(text="Check system status")
    
    scheduler.schedule_task("task1", command1, "*/5 * * * *")
    scheduler.schedule_task("task2", command2, "0 * * * *")
    
    # Update task status
    scheduler.update_task_status("task1", "running")
    
    # Record execution
    scheduler.record_execution("task1", True)
    scheduler.record_execution("task2", False, "Connection error")
    
    # Get task info
    task_info = scheduler.get_task_info("task1")
    print(f"Task info: {task_info}")
    
    # Get execution history
    history = scheduler.get_execution_history("task1")
    print(f"Execution history: {history}")
    
    # Get all tasks
    all_tasks = scheduler.get_all_tasks()
    print(f"All tasks: {all_tasks}") 