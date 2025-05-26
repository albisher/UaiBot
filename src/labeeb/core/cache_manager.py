import json
import time
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime, timedelta
import hashlib
from labeeb.logging_config import get_logger

logger = get_logger(__name__)

class CacheManager:
    """Manages caching of AI responses with TTL support."""
    
    def __init__(
        self,
        cache_dir: str = ".cache",
        ttl_seconds: int = 3600,  # 1 hour default TTL
        max_size_mb: int = 100  # 100MB default max size
    ):
        """
        Initialize the cache manager.
        
        Args:
            cache_dir: Directory to store cache files
            ttl_seconds: Time-to-live for cache entries in seconds
            max_size_mb: Maximum cache size in megabytes
        """
        self.cache_dir = Path(cache_dir)
        self.ttl_seconds = ttl_seconds
        self.max_size_bytes = max_size_mb * 1024 * 1024
        
        # Create cache directory if it doesn't exist
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize cache metadata
        self.metadata_file = self.cache_dir / "cache_metadata.json"
        self.metadata = self._load_metadata()
        
        # Clean up expired entries
        self._cleanup_expired()
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load cache metadata from file."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.warning("Cache metadata file corrupted, creating new one")
                return {"entries": {}, "total_size": 0}
        return {"entries": {}, "total_size": 0}
    
    def _save_metadata(self) -> None:
        """Save cache metadata to file."""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f)
    
    def _get_cache_key(self, data: str) -> str:
        """Generate a cache key from input data."""
        return hashlib.sha256(data.encode()).hexdigest()
    
    def _get_cache_path(self, key: str) -> Path:
        """Get the full path for a cache entry."""
        return self.cache_dir / f"{key}.json"
    
    def _cleanup_expired(self) -> None:
        """Remove expired cache entries."""
        current_time = time.time()
        expired_keys = []
        
        for key, entry in self.metadata["entries"].items():
            if current_time > entry["expires_at"]:
                expired_keys.append(key)
                try:
                    self._get_cache_path(key).unlink()
                except FileNotFoundError:
                    pass
        
        for key in expired_keys:
            self.metadata["total_size"] -= self.metadata["entries"][key]["size"]
            del self.metadata["entries"][key]
        
        if expired_keys:
            self._save_metadata()
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def _enforce_size_limit(self) -> None:
        """Enforce cache size limit by removing oldest entries."""
        while self.metadata["total_size"] > self.max_size_bytes:
            if not self.metadata["entries"]:
                break
                
            # Find oldest entry
            oldest_key = min(
                self.metadata["entries"].keys(),
                key=lambda k: self.metadata["entries"][k]["created_at"]
            )
            
            # Remove oldest entry
            try:
                self._get_cache_path(oldest_key).unlink()
            except FileNotFoundError:
                pass
            
            self.metadata["total_size"] -= self.metadata["entries"][oldest_key]["size"]
            del self.metadata["entries"][oldest_key]
            
            logger.info(f"Removed oldest cache entry to enforce size limit")
    
    def get(self, data: str) -> Optional[Any]:
        """
        Get a cached response for the given data.
        
        Args:
            data: The input data to look up
            
        Returns:
            The cached response if found and not expired, None otherwise
        """
        key = self._get_cache_key(data)
        
        if key not in self.metadata["entries"]:
            return None
        
        entry = self.metadata["entries"][key]
        if time.time() > entry["expires_at"]:
            self._cleanup_expired()
            return None
        
        try:
            with open(self._get_cache_path(key), 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            logger.warning(f"Cache entry {key} corrupted or missing")
            return None
    
    def set(self, data: str, response: Any) -> None:
        """
        Cache a response for the given data.
        
        Args:
            data: The input data
            response: The response to cache
        """
        key = self._get_cache_key(data)
        cache_path = self._get_cache_path(key)
        
        # Serialize response to get size
        serialized = json.dumps(response)
        size = len(serialized.encode())
        
        # Update metadata
        self.metadata["entries"][key] = {
            "created_at": time.time(),
            "expires_at": time.time() + self.ttl_seconds,
            "size": size
        }
        self.metadata["total_size"] += size
        
        # Write cache file
        with open(cache_path, 'w') as f:
            f.write(serialized)
        
        # Enforce size limit
        self._enforce_size_limit()
        
        # Save metadata
        self._save_metadata()
    
    def clear(self) -> None:
        """Clear all cache entries."""
        for key in list(self.metadata["entries"].keys()):
            try:
                self._get_cache_path(key).unlink()
            except FileNotFoundError:
                pass
        
        self.metadata = {"entries": {}, "total_size": 0}
        self._save_metadata()
        logger.info("Cache cleared") 