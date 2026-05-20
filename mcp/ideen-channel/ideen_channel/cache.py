"""
Caching layer for Ideen Channel MCP Server
Implements TTL-based caching with automatic cleanup and thread safety
"""

import asyncio
import time
from typing import Callable, Any, Dict


class IdeaCache:
    """Thread-safe cache with TTL (time-to-live) support"""
    
    def __init__(self, ttl: int = 300):
        """
        Initialize cache
        
        Args:
            ttl: Time to live for cache entries in seconds
        """
        self.ttl = ttl  # Time to live in seconds
        self.cache: Dict[str, tuple] = {}  # key: (value, timestamp)
        self.lock = asyncio.Lock()
    
    async def get(self, key: str, fetch_func: Callable) -> Any:
        """
        Get value from cache or fetch using function
        
        Args:
            key: Cache key
            fetch_func: Async or sync function to fetch data if cache miss
        
        Returns:
            Cached or freshly fetched value
        """
        async with self.lock:
            if key in self.cache:
                value, timestamp = self.cache[key]
                if time.time() - timestamp < self.ttl:
                    return value
            
            # Cache miss or expired
            value = fetch_func()
            if asyncio.iscoroutine(value):
                value = await value
            self.cache[key] = (value, time.time())
            return value
    
    def invalidate(self, key: str):
        """
        Invalidate specific cache entry
        
        Args:
            key: Cache key to invalidate
        """
        if key in self.cache:
            del self.cache[key]
    
    def clear(self):
        """Clear entire cache"""
        self.cache.clear()
    
    async def cleanup_expired(self):
        """
        Remove expired entries from cache
        
        This should be called periodically to prevent memory leaks
        """
        async with self.lock:
            current_time = time.time()
            expired_keys = [
                key for key, (_, timestamp) in self.cache.items()
                if current_time - timestamp >= self.ttl
            ]
            for key in expired_keys:
                del self.cache[key]
    
    def is_cached(self, key: str) -> bool:
        """
        Check if a key is currently cached (not expired)
        
        Args:
            key: Cache key to check
        
        Returns:
            True if key exists and is not expired
        """
        if key not in self.cache:
            return False
        
        _, timestamp = self.cache[key]
        return time.time() - timestamp < self.ttl