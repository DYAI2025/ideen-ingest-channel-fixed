"""
HTTP Client for Ideen Channel API
Supports mock clients for testing
"""

import httpx
from typing import List, Dict, Any, Optional


class IdeenClient:
    """HTTP client for Ideen Channel API with mock support"""
    
    def __init__(self, api_url: str, timeout: int = 30, mock_client: Optional[httpx.AsyncClient] = None):
        """
        Initialize Ideen client
        
        Args:
            api_url: Base URL of the Ideen API
            timeout: Request timeout in seconds (default: 30)
            mock_client: Optional mock HTTP client for testing
        """
        self.api_url = api_url.rstrip("/")
        self.timeout = timeout
        self.client = mock_client or httpx.AsyncClient(timeout=timeout)
    
    async def list_ideas(self, phase: Optional[str] = None, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """
        List all ideas from GBrain
        
        Args:
            phase: The phase to filter ideas (seed, sprout, growth, flower, harvest)
            limit: Maximum number of ideas to return (default: 50)
            offset: Number of ideas to skip (default: 0)
        
        Returns:
            Dictionary with ideas list and metadata
        
        Raises:
            ConnectionError: If API is unreachable
        """
        try:
            params = {"limit": limit, "offset": offset}
            if phase:
                params["phase"] = phase
            
            response = await self.client.get(f"{self.api_url}/api/ideas/list", params=params)
            response.raise_for_status()
            data = response.json()
            return {"ideas": data.get("results", []), "total": data.get("total", 0)}
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return {"ideas": [], "total": 0}
            raise
        except httpx.ConnectError:
            raise ConnectionError(f"Cannot connect to Ideen API at {self.api_url}")
    
    async def search_ideas(self, query: str, phase: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
        """
        Search ideas by text query
        
        Args:
            query: Search query string
            phase: Filter by phase (optional)
            limit: Maximum number of results to return (default: 50)
        
        Returns:
            Dictionary with search results and metadata
        """
        try:
            params = {"query": query, "limit": limit}
            if phase:
                params["phase"] = phase
            
            response = await self.client.get(f"{self.api_url}/api/ideas/search", params=params)
            response.raise_for_status()
            data = response.json()
            return {"ideas": data.get("results", []), "total": data.get("total", 0)}
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return {"ideas": [], "total": 0}
            raise
        except httpx.ConnectError:
            raise ConnectionError(f"Cannot connect to Ideen API at {self.api_url}")
    
    async def get_idea(self, idea_id: str) -> Dict[str, Any]:
        """
        Get a specific idea by ID
        
        Args:
            idea_id: Unique identifier of the idea
        
        Returns:
            Dictionary with idea details
        
        Raises:
            ConnectionError: If API is unreachable
        """
        try:
            response = await self.client.get(f"{self.api_url}/api/ideas/{idea_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return {"error": "Idea not found"}
            raise
        except httpx.ConnectError:
            raise ConnectionError(f"Cannot connect to Ideen API at {self.api_url}")
    
    async def create_idea(self, title: str, description: str, phase: str = "discovery", tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Create a new idea
        
        Args:
            title: Title of the idea
            description: Detailed description
            phase: Phase for the idea (default: "discovery")
            tags: Optional list of tags
        
        Returns:
            Dictionary with created idea details
        """
        try:
            payload = {
                "title": title,
                "description": description,
                "phase": phase,
                "tags": tags or []
            }
            response = await self.client.post(f"{self.api_url}/api/ideas", json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.ConnectError:
            raise ConnectionError(f"Cannot connect to Ideen API at {self.api_url}")
    
    async def update_idea(self, idea_id: str, title: Optional[str] = None, description: Optional[str] = None, phase: Optional[str] = None, tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Update an existing idea
        
        Args:
            idea_id: Unique identifier of the idea
            title: New title (optional)
            description: New description (optional)
            phase: New phase (optional)
            tags: New list of tags (optional)
        
        Returns:
            Dictionary with updated idea details
        """
        try:
            payload = {}
            if title is not None:
                payload["title"] = title
            if description is not None:
                payload["description"] = description
            if phase is not None:
                payload["phase"] = phase
            if tags is not None:
                payload["tags"] = tags
            
            response = await self.client.put(f"{self.api_url}/api/ideas/{idea_id}", json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return {"error": "Idea not found"}
            raise
        except httpx.ConnectError:
            raise ConnectionError(f"Cannot connect to Ideen API at {self.api_url}")
    
    async def delete_idea(self, idea_id: str) -> Dict[str, Any]:
        """
        Delete an idea
        
        Args:
            idea_id: Unique identifier of the idea
        
        Returns:
            Dictionary with deletion status
        """
        try:
            response = await self.client.delete(f"{self.api_url}/api/ideas/{idea_id}")
            response.raise_for_status()
            return {"success": True, "message": "Idea deleted successfully"}
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return {"error": "Idea not found"}
            raise
        except httpx.ConnectError:
            raise ConnectionError(f"Cannot connect to Ideen API at {self.api_url}")
    
    async def get_kanban_board(self) -> Dict[str, Any]:
        """
        Get the complete Kanban board
        
        Returns:
            Dictionary with Kanban board structure and tasks
        """
        try:
            response = await self.client.get(f"{self.api_url}/api/kanban/board")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return {"columns": []}
            raise
        except httpx.ConnectError:
            raise ConnectionError(f"Cannot connect to Ideen API at {self.api_url}")
    
    async def create_kanban_task(self, title: str, description: str, column: str = "backlog", priority: str = "medium") -> Dict[str, Any]:
        """
        Create a new Kanban task
        
        Args:
            title: Title of the task
            description: Detailed description
            column: Column to place task in (default: "backlog")
            priority: Priority level (default: "medium")
        
        Returns:
            Dictionary with created task details
        """
        try:
            payload = {
                "title": title,
                "description": description,
                "column": column,
                "priority": priority
            }
            response = await self.client.post(f"{self.api_url}/api/kanban/tasks", json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.ConnectError:
            raise ConnectionError(f"Cannot connect to Ideen API at {self.api_url}")