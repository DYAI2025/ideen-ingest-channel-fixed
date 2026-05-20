"""
Mock tests for Ideen Channel HTTP Client
Tests mock API implementation without requiring real server
"""

import pytest
from ideen_channel.client import IdeenClient
from ideen_channel.mocks import MockIdeenAPI


@pytest.mark.asyncio
async def test_list_ideas_with_mock():
    """Test client with mock API - no real server needed"""
    mock_api = MockIdeenAPI()
    client = IdeenClient(api_url="http://mock.local", mock_client=mock_api)
    
    result = await client.list_ideas(phase="seed")
    ideas = result["ideas"]
    assert len(ideas) == 2  # Mock returns 2 sample ideas for seed
    assert ideas[0]["phase"] == "seed"


@pytest.mark.asyncio
async def test_search_ideas_with_mock():
    """Test search with mock API"""
    mock_api = MockIdeenAPI()
    client = IdeenClient(api_url="http://mock.local", mock_client=mock_api)
    
    result = await client.search_ideas("innovation")
    results = result["ideas"]
    assert len(results) == 1  # Mock returns 1 result for "innovation"
    assert "innovation" in results[0]["title"].lower()


@pytest.mark.asyncio
async def test_error_handling_with_mock():
    """Test error handling with mock API"""
    mock_api = MockIdeenAPI(simulate_error=True)
    client = IdeenClient(api_url="http://mock.local", mock_client=mock_api)
    
    with pytest.raises(ConnectionError):
        await client.list_ideas()


@pytest.mark.asyncio
async def test_list_ideas_different_phases():
    """Test listing ideas from different phases"""
    mock_api = MockIdeenAPI()
    client = IdeenClient(api_url="http://mock.local", mock_client=mock_api)
    
    # Test seed phase
    seed_result = await client.list_ideas(phase="seed")
    seed_ideas = seed_result["ideas"]
    assert len(seed_ideas) == 2  # 2 seed ideas in mock
    assert all(idea["phase"] == "seed" for idea in seed_ideas)
    
    # Test sprout phase
    sprout_result = await client.list_ideas(phase="sprout")
    sprout_ideas = sprout_result["ideas"]
    assert len(sprout_ideas) == 1  # 1 sprout idea in mock
    assert sprout_ideas[0]["phase"] == "sprout"


@pytest.mark.asyncio
async def test_search_empty_results():
    """Test search with no matching results"""
    mock_api = MockIdeenAPI()
    client = IdeenClient(api_url="http://mock.local", mock_client=mock_api)
    
    result = await client.search_ideas("nonexistent_term_xyz")
    results = result["ideas"]
    assert len(results) == 0