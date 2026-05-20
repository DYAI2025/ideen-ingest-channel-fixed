"""
Rate limiting for Ideen Channel MCP Server
Implements token bucket algorithm with per-key isolation
"""

import asyncio
import time
from typing import Dict
from collections import defaultdict


class RateLimitError(Exception):
    """Raised when rate limit is exceeded"""
    pass


class RateLimiter:
    """Token bucket rate limiter with per-key isolation"""
    
    def __init__(self, max_requests: int, window_seconds: int):
        """
        Initialize rate limiter
        
        Args:
            max_requests: Maximum number of requests allowed in window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = defaultdict(list)
        self.lock = asyncio.Lock()
    
    async def allow(self, key: str = "default") -> bool:
        """
        Check if request is allowed under rate limit
        
        Args:
            key: Identifier for rate limit bucket (default: "default")
        
        Returns:
            True if request is allowed, False otherwise
        """
        async with self.lock:
            now = time.time()
            requests = self.requests[key]
            
            # Remove requests outside the time window
            cutoff = now - self.window_seconds
            self.requests[key] = [req_time for req_time in requests if req_time > cutoff]
            
            # Check if under limit
            if len(self.requests[key]) < self.max_requests:
                self.requests[key].append(now)
                return True
            
            return False
    
    async def acquire(self, key: str = "default") -> None:
        """
        Acquire a rate limit slot, raise exception if not available
        
        Args:
            key: Identifier for rate limit bucket (default: "default")
        
        Raises:
            RateLimitError: If rate limit is exceeded
        """
        if not await self.allow(key):
            raise RateLimitError(f"Rate limit exceeded for key: {key}")
    
    def get_remaining(self, key: str = "default") -> int:
        """
        Get remaining requests for a key
        
        Args:
            key: Identifier for rate limit bucket (default: "default")
        
        Returns:
            Number of remaining requests
        """
        now = time.time()
        requests = self.requests[key]
        
        # Remove requests outside the time window
        cutoff = now - self.window_seconds
        valid_requests = [req_time for req_time in requests if req_time > cutoff]
        self.requests[key] = valid_requests
        
        return max(0, self.max_requests - len(valid_requests))
    
    def reset(self, key: str = "default") -> None:
        """
        Reset rate limit for a specific key
        
        Args:
            key: Identifier for rate limit bucket (default: "default")
        """
        if key in self.requests:
            del self.requests[key]
    
    def reset_all(self) -> None:
        """Reset all rate limits"""
        self.requests.clear()