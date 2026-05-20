"""
Configuration management for Ideen Channel MCP Server
Handles configuration validation, API reachability checks, and environment variable loading
"""

import httpx
from typing import Dict, Any
import os


class ConfigError(Exception):
    """Raised when configuration validation fails"""
    pass


def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validate configuration parameters
    
    Args:
        config: Configuration dictionary to validate
    
    Returns:
        True if configuration is valid
    
    Raises:
        ConfigError: If configuration is invalid
    """
    if "api_url" not in config:
        raise ConfigError("api_url is required")
    
    if not config["api_url"].startswith(("http://", "https://")):
        raise ConfigError("api_url must start with http:// or https://")
    
    if "timeout" in config and config["timeout"] <= 0:
        raise ConfigError("timeout must be positive")
    
    if "cache_ttl" in config and config["cache_ttl"] < 0:
        raise ConfigError("cache_ttl must be non-negative")
    
    if "rate_limit" in config and config["rate_limit"] <= 0:
        raise ConfigError("rate_limit must be positive")
    
    return True


async def check_api_reachability(api_url: str, timeout: int = 5) -> bool:
    """
    Check if the API is reachable
    
    Args:
        api_url: API URL to check
        timeout: Timeout in seconds
    
    Returns:
        True if API is reachable, False otherwise
    """
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(f"{api_url.rstrip('/')}/health")
            return response.status_code == 200
    except Exception:
        return False


def load_config() -> Dict[str, Any]:
    """
    Load configuration from environment variables with defaults
    
    Returns:
        Configuration dictionary
    """
    return {
        "api_url": os.getenv("IDEEN_API_URL", "http://localhost:8002"),
        "timeout": int(os.getenv("IDEEN_API_TIMEOUT", "30")),
        "cache_ttl": int(os.getenv("IDEEN_CACHE_TTL", "300")),
        "rate_limit": int(os.getenv("IDEEN_RATE_LIMIT", "10"))
    }