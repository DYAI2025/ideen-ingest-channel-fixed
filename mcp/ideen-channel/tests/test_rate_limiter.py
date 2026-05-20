"""
Rate limiting tests for Ideen Channel MCP Server
Tests the RateLimiter implementation with token bucket algorithm
"""

import pytest
import asyncio
import time
from ideen_channel.rate_limiter import RateLimiter, RateLimitError


@pytest.mark.asyncio
async def test_rate_limiter_allow_within_limit():
    """Test that requests within rate limit are allowed"""
    limiter = RateLimiter(max_requests=5, window_seconds=60)
    
    # First 5 requests should be allowed
    for i in range(5):
        assert await limiter.allow() is True


@pytest.mark.asyncio
async def test_rate_limiter_block_over_limit():
    """Test that requests over rate limit are blocked"""
    limiter = RateLimiter(max_requests=3, window_seconds=60)
    
    # First 3 requests should be allowed
    for i in range(3):
        assert await limiter.allow() is True
    
    # 4th request should be blocked
    assert await limiter.allow() is False


@pytest.mark.asyncio
async def test_rate_limiter_reset_after_window():
    """Test that rate limit resets after window expires"""
    limiter = RateLimiter(max_requests=2, window_seconds=1)  # 1 second window
    
    # First 2 requests should be allowed
    assert await limiter.allow() is True
    assert await limiter.allow() is True
    
    # 3rd request should be blocked
    assert await limiter.allow() is False
    
    # Wait for window to expire
    await asyncio.sleep(1.5)
    
    # New request should be allowed after reset
    assert await limiter.allow() is True


@pytest.mark.asyncio
async def test_rate_limiter_concurrent_requests():
    """Test that rate limiter handles concurrent requests correctly"""
    limiter = RateLimiter(max_requests=5, window_seconds=60)
    
    # Launch 10 concurrent requests
    tasks = [limiter.allow() for _ in range(10)]
    results = await asyncio.gather(*tasks)
    
    # Only first 5 should be allowed
    allowed_count = sum(results)
    assert allowed_count == 5


@pytest.mark.asyncio
async def test_rate_limiter_per_key_isolation():
    """Test that rate limits are isolated per key"""
    limiter = RateLimiter(max_requests=2, window_seconds=60)
    
    # Key 1: 2 requests allowed
    assert await limiter.allow("key1") is True
    assert await limiter.allow("key1") is True
    assert await limiter.allow("key1") is False
    
    # Key 2: Should have its own limit
    assert await limiter.allow("key2") is True
    assert await limiter.allow("key2") is True
    assert await limiter.allow("key2") is False


@pytest.mark.asyncio
async def test_rate_limiter_remaining_requests():
    """Test that remaining requests counter is accurate"""
    limiter = RateLimiter(max_requests=5, window_seconds=60)
    
    # Initially should have 5 remaining
    assert limiter.get_remaining("key1") == 5
    
    # After 1 request
    await limiter.allow("key1")
    assert limiter.get_remaining("key1") == 4
    
    # After 3 more requests
    await limiter.allow("key1")
    await limiter.allow("key1")
    await limiter.allow("key1")
    assert limiter.get_remaining("key1") == 1
    
    # After final request
    await limiter.allow("key1")
    assert limiter.get_remaining("key1") == 0


@pytest.mark.asyncio
async def test_rate_limiter_reset_key():
    """Test manual reset of rate limit for a specific key"""
    limiter = RateLimiter(max_requests=3, window_seconds=60)
    
    # Exhaust limit
    for i in range(3):
        await limiter.allow("key1")
    
    assert await limiter.allow("key1") is False
    
    # Reset key
    limiter.reset("key1")
    
    # Should be allowed again
    assert await limiter.allow("key1") is True


@pytest.mark.asyncio
async def test_rate_limiter_reset_all():
    """Test resetting all rate limits"""
    limiter = RateLimiter(max_requests=2, window_seconds=60)
    
    # Exhaust limits for multiple keys
    await limiter.allow("key1")
    await limiter.allow("key1")
    await limiter.allow("key2")
    await limiter.allow("key2")
    
    assert await limiter.allow("key1") is False
    assert await limiter.allow("key2") is False
    
    # Reset all
    limiter.reset_all()
    
    # All should be allowed again
    assert await limiter.allow("key1") is True
    assert await limiter.allow("key2") is True


@pytest.mark.asyncio
async def test_rate_limiter_zero_limit():
    """Test rate limiter with zero max_requests (always block)"""
    limiter = RateLimiter(max_requests=0, window_seconds=60)
    
    # All requests should be blocked
    assert await limiter.allow() is False
    assert await limiter.allow() is False