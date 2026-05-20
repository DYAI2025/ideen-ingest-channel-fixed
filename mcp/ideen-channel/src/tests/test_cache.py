"""
Caching layer tests for Ideen Channel MCP Server
Tests the IdeaCache implementation with TTL support, invalidation, and cleanup
"""

import pytest
import asyncio
import time
from ideen_channel.cache import IdeaCache


@pytest.mark.asyncio
async def test_cache_hit():
    """Test that cache returns cached data"""
    cache = IdeaCache(ttl=10)
    
    # First call - cache miss
    data = await cache.get("test_key", lambda: {"data": "value"})
    assert data == {"data": "value"}
    
    # Second call - cache hit
    data = await cache.get("test_key", lambda: {"data": "new_value"})
    assert data == {"data": "value"}  # Should return cached value


@pytest.mark.asyncio
async def test_cache_miss_after_ttl():
    """Test that cache expires after TTL"""
    cache = IdeaCache(ttl=1)  # 1 second TTL
    
    # First call
    data = await cache.get("test_key", lambda: {"data": "value"})
    assert data == {"data": "value"}
    
    # Wait for TTL to expire
    await asyncio.sleep(1.5)
    
    # Should fetch new data
    data = await cache.get("test_key", lambda: {"data": "new_value"})
    assert data == {"data": "new_value"}


@pytest.mark.asyncio
async def test_cache_invalidation():
    """Test manual cache invalidation"""
    cache = IdeaCache(ttl=10)
    
    # Populate cache
    await cache.get("test_key", lambda: {"data": "value"})
    
    # Invalidate
    cache.invalidate("test_key")
    
    # Should fetch new data
    data = await cache.get("test_key", lambda: {"data": "new_value"})
    assert data == {"data": "new_value"}


@pytest.mark.asyncio
async def test_cache_clear():
    """Test clearing entire cache"""
    cache = IdeaCache(ttl=10)
    
    # Populate cache with multiple entries
    await cache.get("key1", lambda: {"data": "value1"})
    await cache.get("key2", lambda: {"data": "value2"})
    await cache.get("key3", lambda: {"data": "value3"})
    
    # Clear cache
    cache.clear()
    
    # All entries should be gone
    assert len(cache.cache) == 0


@pytest.mark.asyncio
async def test_cache_cleanup_expired():
    """Test automatic cleanup of expired entries"""
    cache = IdeaCache(ttl=1)  # 1 second TTL
    
    # Populate cache
    await cache.get("key1", lambda: {"data": "value1"})
    await cache.get("key2", lambda: {"data": "value2"})
    
    assert len(cache.cache) == 2
    
    # Wait for expiration
    await asyncio.sleep(1.5)
    
    # Run cleanup
    await cache.cleanup_expired()
    
    # All entries should be cleaned up
    assert len(cache.cache) == 0


@pytest.mark.asyncio
async def test_cache_concurrent_access():
    """Test that cache handles concurrent access safely"""
    cache = IdeaCache(ttl=10)
    
    # Create simple sync fetchers for each key
    fetchers = {i: lambda i=i: {"data": f"value_{i}"} for i in range(10)}
    
    # Simulate concurrent access
    tasks = [
        cache.get(f"key_{i}", fetchers[i])
        for i in range(10)
    ]
    
    results = await asyncio.gather(*tasks)
    
    # All tasks should complete without errors
    assert len(results) == 10
    # Each result should have the expected structure
    assert all(isinstance(r, dict) and "data" in r for r in results)


@pytest.mark.asyncio
async def test_cache_with_different_data_types():
    """Test cache with different data types"""
    cache = IdeaCache(ttl=10)
    
    # Test with dict
    dict_data = await cache.get("dict_key", lambda: {"nested": {"data": "value"}})
    assert dict_data == {"nested": {"data": "value"}}
    
    # Test with list
    list_data = await cache.get("list_key", lambda: [1, 2, 3])
    assert list_data == [1, 2, 3]
    
    # Test with string
    str_data = await cache.get("str_key", lambda: "test_string")
    assert str_data == "test_string"


@pytest.mark.asyncio
async def test_cache_zero_ttl():
    """Test cache with zero TTL (immediate expiration)"""
    cache = IdeaCache(ttl=0)  # Immediate expiration
    
    # First call
    data = await cache.get("test_key", lambda: {"data": "value"})
    assert data == {"data": "value"}
    
    # Second call should fetch new data (cache expired immediately)
    data = await cache.get("test_key", lambda: {"data": "new_value"})
    assert data == {"data": "new_value"}