"""
Command Processor Cache module for UaiBot.

This module provides caching functionality for command processors,
including result caching, cache management, and cache monitoring.

The module includes:
- Result caching
- Cache management
- Cache monitoring
- Cache utilities

Example:
    >>> from .command_processor_cache import CommandProcessorCache
    >>> cache = CommandProcessorCache()
    >>> cache.set("weather", "Sunny")
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

# Type variables for cache responses
T = TypeVar('T')
CacheResponse = TypeVar('CacheResponse')

@dataclass
class CacheConfig:
    """Configuration for the command processor cache."""
    max_size: int = 1000
    ttl: float = 3600.0  # seconds
    cleanup_interval: float = 300.0  # seconds
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CacheEntry:
    """Entry in the command processor cache."""
    key: str = ""
    value: Any = None
    timestamp: datetime = field(default_factory=datetime.now)
    ttl: float = 3600.0  # seconds
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CacheStats:
    """Statistics for cache performance."""
    total_entries: int = 0
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    average_ttl: float = 0.0
    last_update: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

class CommandProcessorCache:
    """Cache for command processors."""
    
    def __init__(self, config: Optional[CacheConfig] = None):
        """Initialize the command processor cache.
        
        Args:
            config: Optional cache configuration
        """
        self.config = config or CacheConfig()
        self.entries: Dict[str, CacheEntry] = {}
        self.stats = CacheStats()
        self.last_cleanup = datetime.now()
        
    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """Set a value in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
        """
        try:
            if len(self.entries) >= self.config.max_size:
                self._evict_oldest()
                
            self.entries[key] = CacheEntry(
                key=key,
                value=value,
                ttl=ttl or self.config.ttl
            )
            
            self.stats.total_entries += 1
            self.stats.last_update = datetime.now()
            
        except Exception as e:
            logger.error(f"Error setting cache entry: {e}")
            raise
            
    def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value if available and not expired
        """
        try:
            entry = self.entries.get(key)
            
            if not entry:
                self.stats.misses += 1
                return None
                
            if self._is_expired(entry):
                del self.entries[key]
                self.stats.misses += 1
                return None
                
            self.stats.hits += 1
            return entry.value
            
        except Exception as e:
            logger.error(f"Error getting cache entry: {e}")
            raise
            
    def delete(self, key: str) -> None:
        """Delete a value from the cache.
        
        Args:
            key: Cache key
        """
        try:
            if key in self.entries:
                del self.entries[key]
                
        except Exception as e:
            logger.error(f"Error deleting cache entry: {e}")
            raise
            
    def clear(self) -> None:
        """Clear all entries from the cache."""
        try:
            self.entries.clear()
            self.stats.total_entries = 0
            self.stats.last_update = datetime.now()
            
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            raise
            
    def get_cache_stats(self) -> CacheStats:
        """Get cache statistics.
        
        Returns:
            Cache statistics
        """
        try:
            return self.stats
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            raise
            
    def _is_expired(self, entry: CacheEntry) -> bool:
        """Check if a cache entry is expired.
        
        Args:
            entry: Cache entry
            
        Returns:
            Whether the entry is expired
        """
        try:
            age = (datetime.now() - entry.timestamp).total_seconds()
            return age > entry.ttl
            
        except Exception as e:
            logger.error(f"Error checking cache entry expiration: {e}")
            raise
            
    def _evict_oldest(self) -> None:
        """Evict the oldest cache entry."""
        try:
            if not self.entries:
                return
                
            oldest_key = min(
                self.entries.keys(),
                key=lambda k: self.entries[k].timestamp
            )
            
            del self.entries[oldest_key]
            self.stats.evictions += 1
            self.stats.total_entries -= 1
            
        except Exception as e:
            logger.error(f"Error evicting cache entry: {e}")
            raise
            
    def _cleanup_expired(self) -> None:
        """Clean up expired cache entries."""
        try:
            now = datetime.now()
            
            if (now - self.last_cleanup).total_seconds() < self.config.cleanup_interval:
                return
                
            expired_keys = [
                key for key, entry in self.entries.items()
                if self._is_expired(entry)
            ]
            
            for key in expired_keys:
                del self.entries[key]
                self.stats.evictions += 1
                self.stats.total_entries -= 1
                
            self.last_cleanup = now
            
        except Exception as e:
            logger.error(f"Error cleaning up cache: {e}")
            raise

if __name__ == "__main__":
    # Example usage
    cache = CommandProcessorCache()
    
    # Set cache entries
    cache.set("weather", "Sunny")
    cache.set("temperature", 25)
    
    # Get cache entries
    weather = cache.get("weather")
    print(f"Weather: {weather}")
    
    temperature = cache.get("temperature")
    print(f"Temperature: {temperature}")
    
    # Delete cache entry
    cache.delete("weather")
    
    # Get cache stats
    stats = cache.get_cache_stats()
    print(f"Cache stats: {stats}") 