import os
import json
import time
from pathlib import Path
from typing import Any, Dict, Optional, Union
from dataclasses import dataclass
import hashlib
import threading
from datetime import datetime

@dataclass
class CacheEntry:
    """Represents a single cache entry with metadata."""
    value: Any
    created_at: float
    expires_at: Optional[float]
    metadata: Dict[str, Any]

class Cache:
    """Caching system supporting both memory and disk caching with TTL."""
    
    def __init__(self, cache_dir: Optional[str] = None):
        self.memory_cache: Dict[str, CacheEntry] = {}
        self.cache_dir = cache_dir or os.path.expanduser("~/Documents/uaibot/cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        self.lock = threading.Lock()
        
    def _get_cache_key(self, key: Union[str, Dict[str, Any]]) -> str:
        """Generate a cache key from a string or dictionary."""
        if isinstance(key, dict):
            # Sort keys to ensure consistent hashing
            key_str = json.dumps(key, sort_keys=True)
        else:
            key_str = str(key)
        return hashlib.sha256(key_str.encode()).hexdigest()
    
    def _is_expired(self, entry: CacheEntry) -> bool:
        """Check if a cache entry has expired."""
        if entry.expires_at is None:
            return False
        return time.time() > entry.expires_at
    
    def get(self, key: Union[str, Dict[str, Any]], default: Any = None) -> Any:
        """Get a value from the cache."""
        cache_key = self._get_cache_key(key)
        
        # Try memory cache first
        with self.lock:
            if cache_key in self.memory_cache:
                entry = self.memory_cache[cache_key]
                if not self._is_expired(entry):
                    return entry.value
                else:
                    del self.memory_cache[cache_key]
        
        # Try disk cache
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    entry = CacheEntry(
                        value=data['value'],
                        created_at=data['created_at'],
                        expires_at=data.get('expires_at'),
                        metadata=data.get('metadata', {})
                    )
                    if not self._is_expired(entry):
                        # Update memory cache
                        with self.lock:
                            self.memory_cache[cache_key] = entry
                        return entry.value
                    else:
                        os.remove(cache_file)
            except Exception:
                pass
        
        return default
    
    def set(self, key: Union[str, Dict[str, Any]], value: Any, 
            ttl: Optional[int] = None, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Set a value in the cache with optional TTL and metadata."""
        cache_key = self._get_cache_key(key)
        now = time.time()
        
        entry = CacheEntry(
            value=value,
            created_at=now,
            expires_at=now + ttl if ttl is not None else None,
            metadata=metadata or {}
        )
        
        # Update memory cache
        with self.lock:
            self.memory_cache[cache_key] = entry
        
        # Update disk cache
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        try:
            with open(cache_file, 'w') as f:
                json.dump({
                    'value': value,
                    'created_at': now,
                    'expires_at': entry.expires_at,
                    'metadata': metadata or {}
                }, f)
        except Exception as e:
            print(f"Warning: Failed to write to disk cache: {e}")
    
    def delete(self, key: Union[str, Dict[str, Any]]) -> None:
        """Delete a value from the cache."""
        cache_key = self._get_cache_key(key)
        
        # Remove from memory cache
        with self.lock:
            self.memory_cache.pop(cache_key, None)
        
        # Remove from disk cache
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        if os.path.exists(cache_file):
            try:
                os.remove(cache_file)
            except Exception as e:
                print(f"Warning: Failed to delete from disk cache: {e}")
    
    def clear(self) -> None:
        """Clear all cache entries."""
        # Clear memory cache
        with self.lock:
            self.memory_cache.clear()
        
        # Clear disk cache
        try:
            for file in os.listdir(self.cache_dir):
                if file.endswith('.json'):
                    os.remove(os.path.join(self.cache_dir, file))
        except Exception as e:
            print(f"Warning: Failed to clear disk cache: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self.lock:
            memory_entries = len(self.memory_cache)
            memory_size = sum(len(str(v.value)) for v in self.memory_cache.values())
            
        disk_entries = 0
        disk_size = 0
        try:
            for file in os.listdir(self.cache_dir):
                if file.endswith('.json'):
                    disk_entries += 1
                    disk_size += os.path.getsize(os.path.join(self.cache_dir, file))
        except Exception:
            pass
        
        return {
            'memory_entries': memory_entries,
            'memory_size_bytes': memory_size,
            'disk_entries': disk_entries,
            'disk_size_bytes': disk_size,
            'total_entries': memory_entries + disk_entries,
            'total_size_bytes': memory_size + disk_size
        } 