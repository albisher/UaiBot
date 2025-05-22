"""
AI Response Cache Module

This module implements a caching mechanism for AI responses
to improve performance by avoiding redundant processing of
similar queries.
"""

import hashlib
import json
import time
import sys
from typing import Dict, Any, Optional, Tuple
import logging
import threading

logger = logging.getLogger(__name__)

class AIResponseCache:
    """
    Caches AI responses to reduce processing time for similar queries.
    Implements time-based invalidation and LRU eviction policy.
    """
    
    def __init__(self, max_size: int = 100, ttl_seconds: int = 3600):
        """
        Initialize the cache with the specified maximum size and time-to-live.
        
        Args:
            max_size: Maximum number of entries in the cache
            ttl_seconds: Time-to-live for cache entries in seconds
        """
        self._cache = {}
        self._access_times = {}
        self._max_size = max_size
        self._ttl_seconds = ttl_seconds
        self._lock = threading.RLock()  # Use RLock for thread safety
        
    def generate_key(self, query: str, context: Dict[str, Any] = None) -> str:
        """
        Generate a cache key from the query and context.
        
        Args:
            query: The user query
            context: Additional context information
            
        Returns:
            A string key for the cache
        """
        # Normalize the query by removing extra whitespace and converting to lowercase
        normalized_query = ' '.join(query.strip().lower().split())
        
        # Extract only the relevant parts of the context to avoid unnecessary cache misses
        relevant_context = {}
        if context:
            # Only include platform-specific information that affects command execution
            if 'os_type' in context:
                relevant_context['os_type'] = context['os_type']
            if 'os_version' in context:
                relevant_context['os_version'] = context['os_version']
            if 'shell_type' in context:
                relevant_context['shell_type'] = context['shell_type']
        
        # Create a combined string for hashing
        combined = f"{normalized_query}|{json.dumps(relevant_context, sort_keys=True)}"
        
        # Use a fast hash function
        return hashlib.md5(combined.encode('utf-8')).hexdigest()
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get a value from the cache if it exists and is not expired.
        
        Args:
            key: The cache key
            
        Returns:
            The cached value or None if not found or expired
        """
        with self._lock:
            if key in self._cache:
                # Check if the entry has expired
                access_time = self._access_times.get(key, 0)
                current_time = time.time()
                
                if current_time - access_time > self._ttl_seconds:
                    # Entry has expired, remove it
                    del self._cache[key]
                    del self._access_times[key]
                    return None
                
                # Update the access time
                self._access_times[key] = current_time
                return self._cache[key]
            
            return None
    
    def put(self, key: str, value: Dict[str, Any]) -> None:
        """
        Put a value in the cache.
        
        Args:
            key: The cache key
            value: The value to cache
        """
        with self._lock:
            # Check if we need to evict an entry
            if len(self._cache) >= self._max_size and key not in self._cache:
                self._evict_lru()
            
            # Add the new entry
            self._cache[key] = value
            self._access_times[key] = time.time()
    
    def _evict_lru(self) -> None:
        """
        Evict the least recently used entry from the cache.
        """
        if not self._access_times:
            return
        
        # Find the least recently used key
        lru_key = min(self._access_times.items(), key=lambda x: x[1])[0]
        
        # Remove it from the cache
        del self._cache[lru_key]
        del self._access_times[lru_key]
    
    def clear(self) -> None:
        """
        Clear all entries from the cache.
        """
        with self._lock:
            self._cache.clear()
            self._access_times.clear()
    
    def invalidate(self, key: str) -> bool:
        """
        Invalidate a specific cache entry.
        
        Args:
            key: The cache key to invalidate
            
        Returns:
            True if the key was found and invalidated, False otherwise
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                del self._access_times[key]
                return True
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the cache.
        
        Returns:
            Dictionary with cache statistics
        """
        with self._lock:
            return {
                "size": len(self._cache),
                "max_size": self._max_size,
                "ttl_seconds": self._ttl_seconds,
                "keys": list(self._cache.keys()),
                "memory_usage_bytes": sys.getsizeof(self._cache) + sys.getsizeof(self._access_times)
            }
