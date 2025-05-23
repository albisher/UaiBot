"""
Command Processor Optimizer module for UaiBot.

This module provides optimization functionality for command processors,
including performance optimization, resource management, and caching.

The module includes:
- Performance optimization
- Resource management
- Caching
- Optimization utilities

Example:
    >>> from .command_processor_optimizer import CommandProcessorOptimizer
    >>> optimizer = CommandProcessorOptimizer()
    >>> optimizer.optimize_command("What is the weather?")
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

# Type variables for optimizer responses
T = TypeVar('T')
OptimizerResponse = TypeVar('OptimizerResponse')

@dataclass
class OptimizerConfig:
    """Configuration for the command processor optimizer."""
    cache_size: int = 1000
    cache_ttl: float = 3600.0  # seconds
    max_workers: int = 4
    batch_size: int = 10
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CacheEntry:
    """Cache entry for command results."""
    result: CommandResult
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class OptimizationResult:
    """Result of command optimization."""
    optimized: bool = False
    cache_hit: bool = False
    performance_gain: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

class CommandProcessorOptimizer:
    """Optimizer for command processors."""
    
    def __init__(self, config: Optional[OptimizerConfig] = None):
        """Initialize the command processor optimizer.
        
        Args:
            config: Optional optimizer configuration
        """
        self.config = config or OptimizerConfig()
        self.cache: Dict[str, CacheEntry] = {}
        self.last_cleanup = time.time()
        
    def optimize_command(self, command: Command) -> OptimizationResult:
        """Optimize a command.
        
        Args:
            command: Command to optimize
            
        Returns:
            Optimization result
        """
        try:
            # Check cache
            cache_key = self._generate_cache_key(command)
            cache_entry = self.cache.get(cache_key)
            
            if cache_entry:
                # Check if cache entry is still valid
                if self._is_cache_valid(cache_entry):
                    return OptimizationResult(
                        optimized=True,
                        cache_hit=True,
                        performance_gain=1.0,
                        metadata={"cache_key": cache_key}
                    )
                else:
                    # Remove invalid cache entry
                    del self.cache[cache_key]
                    
            # Clean up cache if needed
            self._cleanup_cache()
            
            return OptimizationResult(
                optimized=False,
                cache_hit=False,
                performance_gain=0.0,
                metadata={"cache_key": cache_key}
            )
            
        except Exception as e:
            logger.error(f"Error optimizing command: {e}")
            raise
            
    def cache_result(self, command: Command, result: CommandResult) -> None:
        """Cache a command result.
        
        Args:
            command: Command
            result: Result to cache
        """
        try:
            # Generate cache key
            cache_key = self._generate_cache_key(command)
            
            # Create cache entry
            entry = CacheEntry(
                result=result,
                metadata={"command_text": command.text}
            )
            
            # Add to cache
            self.cache[cache_key] = entry
            
            # Clean up cache if needed
            self._cleanup_cache()
            
        except Exception as e:
            logger.error(f"Error caching result: {e}")
            raise
            
    def get_cached_result(self, command: Command) -> Optional[CommandResult]:
        """Get cached result for command.
        
        Args:
            command: Command
            
        Returns:
            Cached result if available and valid
        """
        try:
            # Generate cache key
            cache_key = self._generate_cache_key(command)
            
            # Get cache entry
            entry = self.cache.get(cache_key)
            
            if entry and self._is_cache_valid(entry):
                return entry.result
                
            return None
            
        except Exception as e:
            logger.error(f"Error getting cached result: {e}")
            raise
            
    def _generate_cache_key(self, command: Command) -> str:
        """Generate cache key for command.
        
        Args:
            command: Command
            
        Returns:
            Cache key
        """
        try:
            # Use command text as key
            return command.text.lower().strip()
            
        except Exception as e:
            logger.error(f"Error generating cache key: {e}")
            raise
            
    def _is_cache_valid(self, entry: CacheEntry) -> bool:
        """Check if cache entry is valid.
        
        Args:
            entry: Cache entry
            
        Returns:
            True if entry is valid
        """
        try:
            # Check TTL
            age = (datetime.now() - entry.timestamp).total_seconds()
            return age < self.config.cache_ttl
            
        except Exception as e:
            logger.error(f"Error checking cache validity: {e}")
            raise
            
    def _cleanup_cache(self) -> None:
        """Clean up cache."""
        try:
            current_time = time.time()
            
            # Check if cleanup is needed
            if current_time - self.last_cleanup < 60.0:  # Clean up every minute
                return
                
            # Remove expired entries
            expired_keys = [
                key for key, entry in self.cache.items()
                if not self._is_cache_valid(entry)
            ]
            for key in expired_keys:
                del self.cache[key]
                
            # Remove oldest entries if cache is too large
            if len(self.cache) > self.config.cache_size:
                sorted_entries = sorted(
                    self.cache.items(),
                    key=lambda x: x[1].timestamp
                )
                for key, _ in sorted_entries[:len(self.cache) - self.config.cache_size]:
                    del self.cache[key]
                    
            # Update last cleanup time
            self.last_cleanup = current_time
            
        except Exception as e:
            logger.error(f"Error cleaning up cache: {e}")
            raise

if __name__ == "__main__":
    # Example usage
    optimizer = CommandProcessorOptimizer()
    
    # Optimize command
    command = Command(text="What is the weather?")
    optimization = optimizer.optimize_command(command)
    print(f"Optimization: {optimization}")
    
    # Cache result
    result = CommandResult(
        success=True,
        output="The weather is sunny",
        error=None,
        metadata={"response_time": 0.5}
    )
    optimizer.cache_result(command, result)
    
    # Get cached result
    cached_result = optimizer.get_cached_result(command)
    print(f"Cached result: {cached_result}") 