"""
AI Response Cache Module

This module implements a caching mechanism for AI responses
to improve performance by avoiding redundant processing of
similar queries.
"""

import hashlib
import json
import time
from typing import Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class AIResponseCache:
    """
    Caches AI responses to reduce processing time for similar queries.
    Implements time-based invalidation and LRU eviction policy.
    """
    
    def __init__(self, max_size=100, ttl=3600):
        """
        Initialize the AI response cache.
        
        Args:
            max_size (int): Maximum number of items in the cache
            ttl (int): Time-to-live for cache entries in seconds
        """
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.access_times: Dict[str, float] = {}
        self.max_size = max_size
        self.ttl = ttl
        logger.info(f"Initialized AI response cache with max_size={max_size}, ttl={ttl}")
    
    def _generate_key(self, query: str) -> str:
        """
        Generate a unique key for a query by normalizing and hashing it.
        
        Args:
            query (str): The query to generate a key for
            
        Returns:
            str: A hash representing the query
        """
        # Normalize query by stripping whitespace, lowercasing
        normalized = query.strip().lower()
        # Hash the normalized query
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def get(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a cached response for a query if it exists and is valid.
        
        Args:
            query (str): The query to look up
            
        Returns:
            Optional[Dict[str, Any]]: The cached response or None if not found/invalid
        """
        key = self._generate_key(query)
        current_time = time.time()
        
        if key in self.cache:
            # Check if the cache entry is still valid
            entry_time = self.access_times.get(key, 0)
            if current_time - entry_time <= self.ttl:
                # Update access time for LRU tracking
                self.access_times[key] = current_time
                logger.debug(f"Cache hit for query: {query[:30]}...")
                return self.cache[key]
            else:
                # Entry has expired
                logger.debug(f"Cache entry expired for query: {query[:30]}...")
                self._remove_entry(key)
        
        logger.debug(f"Cache miss for query: {query[:30]}...")
        return None
    
    def put(self, query: str, response: Dict[str, Any]) -> None:
        """
        Store a response in the cache.
        
        Args:
            query (str): The query the response is for
            response (Dict[str, Any]): The response to cache
        """
        key = self._generate_key(query)
        current_time = time.time()
        
        # Check if cache is full and needs eviction
        if len(self.cache) >= self.max_size and key not in self.cache:
            self._evict_lru()
        
        # Store the response and update access time
        self.cache[key] = response
        self.access_times[key] = current_time
        logger.debug(f"Cached response for query: {query[:30]}...")
    
    def _evict_lru(self) -> None:
        """Remove the least recently used item from the cache."""
        if not self.access_times:
            return
        
        # Find the least recently accessed key
        lru_key = min(self.access_times, key=self.access_times.get)
        self._remove_entry(lru_key)
        logger.debug(f"Evicted LRU cache entry: {lru_key}")
    
    def _remove_entry(self, key: str) -> None:
        """Remove a specific entry from the cache."""
        self.cache.pop(key, None)
        self.access_times.pop(key, None)
    
    def clear(self) -> None:
        """Clear all entries from the cache."""
        self.cache.clear()
        self.access_times.clear()
        logger.info("Cleared AI response cache")
    
    def invalidate(self, query: str) -> bool:
        """
        Invalidate a specific cache entry.
        
        Args:
            query (str): The query whose response should be invalidated
            
        Returns:
            bool: True if an entry was invalidated, False otherwise
        """
        key = self._generate_key(query)
        if key in self.cache:
            self._remove_entry(key)
            logger.debug(f"Invalidated cache entry for query: {query[:30]}...")
            return True
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the current cache state.
        
        Returns:
            Dict[str, Any]: Dictionary containing cache statistics
        """
        current_time = time.time()
        stats = {
            "size": len(self.cache),
            "max_size": self.max_size,
            "ttl": self.ttl,
            "oldest_entry_age": 0,
            "newest_entry_age": 0,
            "average_entry_age": 0,
        }
        
        if self.access_times:
            ages = [current_time - t for t in self.access_times.values()]
            stats["oldest_entry_age"] = max(ages)
            stats["newest_entry_age"] = min(ages)
            stats["average_entry_age"] = sum(ages) / len(ages)
        
        return stats
