"""
Command Processor Statistics module for UaiBot.

This module provides statistics tracking for command processors,
including performance metrics, usage statistics, and error rates.

The module includes:
- Statistics tracking
- Performance metrics
- Usage statistics
- Error rates

Example:
    >>> from .command_processor_stats import CommandProcessorStats
    >>> stats = CommandProcessorStats()
    >>> stats.track_command("What is the weather?")
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

# Set up logging
logger = logging.getLogger(__name__)

# Type variables for statistics responses
T = TypeVar('T')
StatsResponse = TypeVar('StatsResponse')

@dataclass
class StatsConfig:
    """Configuration for the command processor statistics."""
    stats_file: str = "stats/processor_stats.json"
    track_performance: bool = True
    track_usage: bool = True
    track_errors: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PerformanceStats:
    """Performance statistics for command processing."""
    total_commands: int = 0
    successful_commands: int = 0
    failed_commands: int = 0
    average_response_time: float = 0.0
    total_response_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class UsageStats:
    """Usage statistics for command processing."""
    command_types: Dict[str, int] = field(default_factory=dict)
    user_ids: Dict[str, int] = field(default_factory=dict)
    time_periods: Dict[str, int] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ErrorStats:
    """Error statistics for command processing."""
    error_types: Dict[str, int] = field(default_factory=dict)
    error_messages: Dict[str, int] = field(default_factory=dict)
    error_timestamps: List[datetime] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class CommandProcessorStats:
    """Statistics tracker for command processors."""
    
    def __init__(self, config: Optional[StatsConfig] = None):
        """Initialize the command processor statistics.
        
        Args:
            config: Optional statistics configuration
        """
        self.config = config or StatsConfig()
        self.performance = PerformanceStats()
        self.usage = UsageStats()
        self.errors = ErrorStats()
        
    def track_command(self, command: Command) -> None:
        """Track a command.
        
        Args:
            command: Command to track
        """
        try:
            if self.config.track_usage:
                # Track command type
                command_type = command.metadata.get("type", "unknown")
                self.usage.command_types[command_type] = self.usage.command_types.get(command_type, 0) + 1
                
                # Track user
                user_id = command.metadata.get("user_id", "unknown")
                self.usage.user_ids[user_id] = self.usage.user_ids.get(user_id, 0) + 1
                
                # Track time period
                time_period = datetime.now().strftime("%Y-%m-%d")
                self.usage.time_periods[time_period] = self.usage.time_periods.get(time_period, 0) + 1
                
            # Update performance stats
            if self.config.track_performance:
                self.performance.total_commands += 1
                
        except Exception as e:
            logger.error(f"Error tracking command: {e}")
            raise
            
    def track_result(self, result: CommandResult) -> None:
        """Track a command result.
        
        Args:
            result: Result to track
        """
        try:
            if self.config.track_performance:
                # Update performance stats
                if result.success:
                    self.performance.successful_commands += 1
                else:
                    self.performance.failed_commands += 1
                    
                # Update response time
                response_time = result.metadata.get("response_time", 0.0)
                self.performance.total_response_time += response_time
                self.performance.average_response_time = (
                    self.performance.total_response_time / self.performance.total_commands
                )
                
        except Exception as e:
            logger.error(f"Error tracking result: {e}")
            raise
            
    def track_error(self, error: Exception) -> None:
        """Track an error.
        
        Args:
            error: Error to track
        """
        try:
            if self.config.track_errors:
                # Track error type
                error_type = type(error).__name__
                self.errors.error_types[error_type] = self.errors.error_types.get(error_type, 0) + 1
                
                # Track error message
                error_message = str(error)
                self.errors.error_messages[error_message] = self.errors.error_messages.get(error_message, 0) + 1
                
                # Track error timestamp
                self.errors.error_timestamps.append(datetime.now())
                
        except Exception as e:
            logger.error(f"Error tracking error: {e}")
            raise
            
    def save_stats(self) -> None:
        """Save statistics to file."""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.config.stats_file), exist_ok=True)
            
            # Prepare statistics data
            stats_data = {
                "performance": self.performance.__dict__,
                "usage": self.usage.__dict__,
                "errors": {
                    "error_types": self.errors.error_types,
                    "error_messages": self.errors.error_messages,
                    "error_timestamps": [ts.isoformat() for ts in self.errors.error_timestamps]
                }
            }
            
            # Save statistics
            with open(self.config.stats_file, 'w') as f:
                json.dump(stats_data, f, indent=4)
                
        except Exception as e:
            logger.error(f"Error saving statistics: {e}")
            raise
            
    def load_stats(self) -> None:
        """Load statistics from file."""
        try:
            if os.path.exists(self.config.stats_file):
                with open(self.config.stats_file, 'r') as f:
                    stats_data = json.load(f)
                    
                    # Load performance stats
                    self.performance = PerformanceStats(**stats_data["performance"])
                    
                    # Load usage stats
                    self.usage = UsageStats(**stats_data["usage"])
                    
                    # Load error stats
                    error_data = stats_data["errors"]
                    self.errors = ErrorStats(
                        error_types=error_data["error_types"],
                        error_messages=error_data["error_messages"],
                        error_timestamps=[datetime.fromisoformat(ts) for ts in error_data["error_timestamps"]]
                    )
                    
        except Exception as e:
            logger.error(f"Error loading statistics: {e}")
            raise

if __name__ == "__main__":
    # Example usage
    stats = CommandProcessorStats()
    
    # Track command
    command = Command(text="What is the weather?")
    stats.track_command(command)
    
    # Track result
    result = CommandResult(
        success=True,
        output="The weather is sunny",
        error=None,
        metadata={"response_time": 0.5}
    )
    stats.track_result(result)
    
    # Track error
    error = CommandValidationError("Invalid command")
    stats.track_error(error)
    
    # Save statistics
    stats.save_stats()
    
    # Load statistics
    stats.load_stats() 