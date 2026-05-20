"""
Mock implementation for Ideen API
Used for testing without requiring real server
"""

import httpx
from typing import List, Dict, Any


class MockIdeenAPI:
    """Mock HTTP client for Ideen API testing"""
    
    def __init__(self, simulate_error: bool = False):
        self.simulate_error = simulate_error
        self.sample_ideas = [
            {
                "slug": "test-idea-1",
                "title": "Test Idea 1",
                "phase": "seed",
                "content": "Sample content for testing"
            },
            {
                "slug": "test-idea-2", 
                "title": "Innovation Test Idea",
                "phase": "seed",
                "content": "Innovation related content"
            },
            {
                "slug": "test-idea-3",
                "title": "Test Idea 3",
                "phase": "sprout",
                "content": "Another sample idea"
            }
        ]
    
    async def get(self, url: str, params: dict = None) -> httpx.Response:
        """Mock GET request handler"""
        if self.simulate_error:
            raise httpx.ConnectError("Mock connection error")
        
        # Mock response based on URL path
        if "list" in url:
            phase = params.get("phase", "seed") if params else "seed"
            filtered_ideas = [i for i in self.sample_ideas if i["phase"] == phase]
            return self._mock_response({"results": filtered_ideas})
        
        elif "search" in url:
            query = params.get("query", "").lower() if params else ""
            filtered = [i for i in self.sample_ideas if query in i["title"].lower()]
            return self._mock_response({"results": filtered})
        
        # Default empty response
        return self._mock_response({"results": []})
    
    def _mock_response(self, data: dict) -> httpx.Response:
        """Create mock HTTP response"""
        return httpx.Response(
            200,
            json=data,
            request=httpx.Request("GET", "http://mock.local")
        )