"""
Configuration validation tests for Ideen Channel MCP Server
Tests configuration management, validation, and API reachability checks
"""

import pytest
from ideen_channel.config import validate_config, ConfigError, check_api_reachability, load_config


def test_valid_config():
    """Test validation of valid configuration"""
    config = {
        "api_url": "http://localhost:8002",
        "timeout": 30,
        "cache_ttl": 300
    }
    assert validate_config(config) is True


def test_missing_api_url():
    """Test that missing API URL raises error"""
    config = {
        "timeout": 30
    }
    with pytest.raises(ConfigError, match="api_url is required"):
        validate_config(config)


def test_invalid_timeout():
    """Test that invalid timeout raises error"""
    config = {
        "api_url": "http://localhost:8002",
        "timeout": -1
    }
    with pytest.raises(ConfigError, match="timeout must be positive"):
        validate_config(config)


def test_invalid_cache_ttl():
    """Test that invalid cache TTL raises error"""
    config = {
        "api_url": "http://localhost:8002",
        "cache_ttl": -1
    }
    with pytest.raises(ConfigError, match="cache_ttl must be non-negative"):
        validate_config(config)


def test_invalid_api_url_format():
    """Test that invalid API URL format raises error"""
    config = {
        "api_url": "invalid-url",  # Missing http:// or https://
        "timeout": 30
    }
    with pytest.raises(ConfigError, match="api_url must start with http:// or https://"):
        validate_config(config)


def test_zero_timeout():
    """Test that zero timeout raises error"""
    config = {
        "api_url": "http://localhost:8002",
        "timeout": 0
    }
    with pytest.raises(ConfigError, match="timeout must be positive"):
        validate_config(config)


@pytest.mark.asyncio
async def test_api_reachability_check_with_real_api():
    """Test that API reachability check works with real API"""
    # Test with potentially running API
    is_reachable = await check_api_reachability("http://localhost:8002")
    assert isinstance(is_reachable, bool)


@pytest.mark.asyncio
async def test_api_reachability_check_with_unreachable_api():
    """Test that API reachability check returns false for unreachable API"""
    is_reachable = await check_api_reachability("http://localhost:9999")
    assert is_reachable is False


def test_load_config_from_env():
    """Test that configuration loads from environment variables"""
    config = load_config()
    
    assert "api_url" in config
    assert "timeout" in config
    assert "cache_ttl" in config
    assert "rate_limit" in config
    
    # Check default values
    assert config["api_url"] == "http://localhost:8002"
    assert config["timeout"] == 30
    assert config["cache_ttl"] == 300
    assert config["rate_limit"] == 10


def test_load_config_with_custom_env():
    """Test that configuration respects custom environment variables"""
    import os
    
    # Set custom environment variables
    original_api_url = os.environ.get("IDEEN_API_URL")
    original_timeout = os.environ.get("IDEEN_API_TIMEOUT")
    
    try:
        os.environ["IDEEN_API_URL"] = "http://custom.api:9000"
        os.environ["IDEEN_API_TIMEOUT"] = "60"
        
        config = load_config()
        
        assert config["api_url"] == "http://custom.api:9000"
        assert config["timeout"] == 60
        
    finally:
        # Restore original values
        if original_api_url:
            os.environ["IDEEN_API_URL"] = original_api_url
        else:
            os.environ.pop("IDEEN_API_URL", None)
        
        if original_timeout:
            os.environ["IDEEN_API_TIMEOUT"] = original_timeout
        else:
            os.environ.pop("IDEEN_API_TIMEOUT", None)