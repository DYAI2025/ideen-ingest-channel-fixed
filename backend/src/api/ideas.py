"""
Ideas API Router
Handles idea querying, graph visualization, and management
"""
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import List, Optional

from ..services.gbrain_service import GBrainService

router = APIRouter()
gbrain_service = GBrainService()

@router.get("/search")
async def search_ideas(
    query: str = Query(..., description="Search query"),
    phase: Optional[str] = Query(None, description="Filter by phase (seed, sprout, growth, flower, harvest)")
):
    """
    Search for ideas in GBrain
    
    Args:
        query: Search query
        phase: Optional phase filter
    """
    try:
        ideas = await gbrain_service.query_ideas(query, phase)
        
        return JSONResponse(content={
            "query": query,
            "phase": phase,
            "results": ideas,
            "count": len(ideas)
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list")
async def list_ideas(
    phase: Optional[str] = Query(None, description="Filter by phase")
):
    """
    List all ideas in the system
    
    Args:
        phase: Optional phase filter
    """
    try:
        ideas = await gbrain_service.list_ideas(phase)
        
        return JSONResponse(content={
            "phase": phase,
            "results": ideas,
            "count": len(ideas)
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{slug}")
async def get_idea(slug: str):
    """
    Get detailed information about an idea
    
    Args:
        slug: Idea slug
    """
    try:
        idea = await gbrain_service.get_idea_details(slug)
        
        return JSONResponse(content=idea)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{slug}/graph")
async def get_idea_graph(
    slug: str,
    depth: int = Query(2, description="Graph traversal depth")
):
    """
    Get the graph structure for an idea
    
    Args:
        slug: Idea slug
        depth: Traversal depth
    """
    try:
        graph = await gbrain_service.get_idea_graph(slug, depth)
        
        return JSONResponse(content=graph)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/link")
async def create_idea_link(
    from_slug: str = Query(..., description="Source idea slug"),
    to_slug: str = Query(..., description="Target idea slug"),
    link_type: str = Query("evolves_into", description="Type of relationship")
):
    """
    Create a link between two ideas
    
    Args:
        from_slug: Source idea slug
        to_slug: Target idea slug
        link_type: Type of relationship
    """
    try:
        result = await gbrain_service.create_link(from_slug, to_slug, link_type)
        
        return JSONResponse(content=result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))