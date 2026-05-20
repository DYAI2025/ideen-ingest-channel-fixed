"""
MCP Server for Ideen Channel integration
Exposes Ideen Ingest Channel API as MCP tools
"""

import asyncio
import logging
from typing import Optional, List
from mcp.server.fastmcp import FastMCP
from ideen_channel.client import IdeenClient
from ideen_channel.cache import IdeaCache
from ideen_channel.rate_limiter import RateLimiter
from ideen_channel.config import load_config, ConfigError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create MCP server
mcp = FastMCP("ideen-channel")

# Initialize components
config = load_config()
client = IdeenClient(
    api_url=config["api_url"],
    timeout=config["timeout"],
    mock_client=config.get("mock_client", False)
)
cache = IdeaCache(ttl=config["cache_ttl"])
rate_limiter = RateLimiter(
    max_requests=config.get("rate_limit_max_requests", 60),
    window_seconds=config.get("rate_limit_window_seconds", 60)
)


@mcp.tool()
async def list_ideas(
    phase: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> dict:
    """
    List ideas from the Ideen Ingest Channel
    
    Args:
        phase: Filter by phase (e.g., "discovery", "validation", "implementation")
        limit: Maximum number of ideas to return (default: 50)
        offset: Number of ideas to skip (default: 0)
    
    Returns:
        Dictionary with list of ideas and metadata
    """
    try:
        # Apply rate limiting
        await rate_limiter.acquire("list_ideas")
        
        # Build cache key
        cache_key = f"list_ideas:{phase}:{limit}:{offset}"
        
        # Fetch from cache or API
        async def fetch():
            return await client.list_ideas(phase=phase, limit=limit, offset=offset)
        
        result = await cache.get(cache_key, fetch)
        logger.info(f"Listed {len(result.get('ideas', []))} ideas")
        return result
        
    except Exception as e:
        logger.error(f"Error listing ideas: {e}")
        return {"error": str(e), "ideas": []}


@mcp.tool()
async def search_ideas(
    query: str,
    phase: Optional[str] = None,
    limit: int = 50
) -> dict:
    """
    Search ideas by query text
    
    Args:
        query: Search query string
        phase: Filter by phase (e.g., "discovery", "validation", "implementation")
        limit: Maximum number of results to return (default: 50)
    
    Returns:
        Dictionary with search results and metadata
    """
    try:
        # Apply rate limiting
        await rate_limiter.acquire("search_ideas")
        
        # Build cache key
        cache_key = f"search_ideas:{query}:{phase}:{limit}"
        
        # Fetch from cache or API
        async def fetch():
            return await client.search_ideas(query=query, phase=phase, limit=limit)
        
        result = await cache.get(cache_key, fetch)
        logger.info(f"Found {len(result.get('ideas', []))} ideas for query: {query}")
        return result
        
    except Exception as e:
        logger.error(f"Error searching ideas: {e}")
        return {"error": str(e), "ideas": []}


@mcp.tool()
async def get_idea(idea_id: str) -> dict:
    """
    Get a specific idea by ID
    
    Args:
        idea_id: Unique identifier of the idea
    
    Returns:
        Dictionary with idea details
    """
    try:
        # Apply rate limiting
        await rate_limiter.acquire("get_idea")
        
        # Build cache key
        cache_key = f"get_idea:{idea_id}"
        
        # Fetch from cache or API
        async def fetch():
            return await client.get_idea(idea_id=idea_id)
        
        result = await cache.get(cache_key, fetch)
        logger.info(f"Retrieved idea {idea_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error getting idea {idea_id}: {e}")
        return {"error": str(e)}


@mcp.tool()
async def create_idea(
    title: str,
    description: str,
    phase: str = "discovery",
    tags: Optional[List[str]] = None
) -> dict:
    """
    Create a new idea
    
    Args:
        title: Title of the idea
        description: Detailed description of the idea
        phase: Phase for the idea (default: "discovery")
        tags: Optional list of tags
    
    Returns:
        Dictionary with created idea details
    """
    try:
        # Apply rate limiting
        await rate_limiter.acquire("create_idea")
        
        # Invalidate cache for list operations
        cache.invalidate("list_ideas:")
        cache.invalidate("search_ideas:")
        
        # Create idea
        result = await client.create_idea(
            title=title,
            description=description,
            phase=phase,
            tags=tags or []
        )
        
        logger.info(f"Created idea: {title}")
        return result
        
    except Exception as e:
        logger.error(f"Error creating idea: {e}")
        return {"error": str(e)}


@mcp.tool()
async def update_idea(
    idea_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    phase: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> dict:
    """
    Update an existing idea
    
    Args:
        idea_id: Unique identifier of the idea to update
        title: New title (optional)
        description: New description (optional)
        phase: New phase (optional)
        tags: New list of tags (optional)
    
    Returns:
        Dictionary with updated idea details
    """
    try:
        # Apply rate limiting
        await rate_limiter.acquire("update_idea")
        
        # Invalidate cache for this idea and list operations
        cache.invalidate(f"get_idea:{idea_id}")
        cache.invalidate("list_ideas:")
        cache.invalidate("search_ideas:")
        
        # Update idea
        result = await client.update_idea(
            idea_id=idea_id,
            title=title,
            description=description,
            phase=phase,
            tags=tags
        )
        
        logger.info(f"Updated idea {idea_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error updating idea {idea_id}: {e}")
        return {"error": str(e)}


@mcp.tool()
async def delete_idea(idea_id: str) -> dict:
    """
    Delete an idea
    
    Args:
        idea_id: Unique identifier of the idea to delete
    
    Returns:
        Dictionary with deletion status
    """
    try:
        # Apply rate limiting
        await rate_limiter.acquire("delete_idea")
        
        # Invalidate cache for this idea and list operations
        cache.invalidate(f"get_idea:{idea_id}")
        cache.invalidate("list_ideas:")
        cache.invalidate("search_ideas:")
        
        # Delete idea
        result = await client.delete_idea(idea_id=idea_id)
        
        logger.info(f"Deleted idea {idea_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error deleting idea {idea_id}: {e}")
        return {"error": str(e)}


@mcp.tool()
async def get_kanban_board() -> dict:
    """
    Get the complete Kanban board with all tasks
    
    Returns:
        Dictionary with Kanban board structure and tasks
    """
    try:
        # Apply rate limiting
        await rate_limiter.acquire("get_kanban_board")
        
        # Build cache key
        cache_key = "get_kanban_board"
        
        # Fetch from cache or API
        async def fetch():
            return await client.get_kanban_board()
        
        result = await cache.get(cache_key, fetch)
        logger.info("Retrieved Kanban board")
        return result
        
    except Exception as e:
        logger.error(f"Error getting Kanban board: {e}")
        return {"error": str(e), "columns": []}


@mcp.tool()
async def create_kanban_task(
    title: str,
    description: str,
    column: str = "backlog",
    priority: str = "medium"
) -> dict:
    """
    Create a new Kanban task
    
    Args:
        title: Title of the task
        description: Detailed description of the task
        column: Column to place task in (default: "backlog")
        priority: Priority level (default: "medium")
    
    Returns:
        Dictionary with created task details
    """
    try:
        # Apply rate limiting
        await rate_limiter.acquire("create_kanban_task")
        
        # Invalidate cache
        cache.invalidate("get_kanban_board")
        
        # Create task
        result = await client.create_kanban_task(
            title=title,
            description=description,
            column=column,
            priority=priority
        )
        
        logger.info(f"Created Kanban task: {title}")
        return result
        
    except Exception as e:
        logger.error(f"Error creating Kanban task: {e}")
        return {"error": str(e)}


def main():
    """Entry point for the MCP server"""
    mcp.run()


if __name__ == "__main__":
    main()