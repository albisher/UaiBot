"""
AI Response Cache Module

This module implements caching for AI responses to improve performance
and reduce API calls.
"""

import time
import logging
from typing import Dict, Any, Optional
from collections import OrderedDict

logger = logging.getLogger(__name__)

class AIResponseCache:
    """
    Cache for AI responses with TTL (Time To Live) support.
    """
    
    def __init__(self, max_size: int = 100, ttl_seconds: int = 3600):
        """
        Initialize the cache.
        
        Args:
            max_size: Maximum number of items to store in the cache
            ttl_seconds: Time to live for cache entries in seconds
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache = OrderedDict()
        self.timestamps = {}
        
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get a value from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found or expired
        """
        if key not in self.cache:
            return None
            
        # Check if entry has expired
        if time.time() - self.timestamps[key] > self.ttl_seconds:
            logger.debug(f"Cache entry expired for key: {key}")
            self._remove(key)
            return None
            
        # Move to end (most recently used)
        value = self.cache.pop(key)
        self.cache[key] = value
        return value
        
    def put(self, key: str, value: Dict[str, Any]) -> None:
        """
        Add a value to the cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        # Remove if exists
        if key in self.cache:
            self._remove(key)
            
        # Check if cache is full
        if len(self.cache) >= self.max_size:
            # Remove oldest entry
            oldest_key = next(iter(self.cache))
            self._remove(oldest_key)
            
        # Add new entry
        self.cache[key] = value
        self.timestamps[key] = time.time()
        
    def _remove(self, key: str) -> None:
        """
        Remove an entry from the cache.
        
        Args:
            key: Cache key to remove
        """
        if key in self.cache:
            del self.cache[key]
            del self.timestamps[key]
            
    def clear(self) -> None:
        """Clear all entries from the cache."""
        self.cache.clear()
        self.timestamps.clear()
        
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary containing cache statistics
        """
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "ttl_seconds": self.ttl_seconds,
            "hits": getattr(self, "_hits", 0),
            "misses": getattr(self, "_misses", 0)
        }
