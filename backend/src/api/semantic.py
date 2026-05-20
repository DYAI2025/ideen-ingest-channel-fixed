"""
Semantic Analysis API Endpoints
Provides semantic analysis for markdown content and graph connections
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
import logging

from src.services.semantic_analysis import semantic_service
from src.services.gbrain_service import GBrainService

router = APIRouter()
logger = logging.getLogger(__name__)

gbrain_service = GBrainService()


@router.get("/connections")
async def get_semantic_connections(
    similarity_threshold: float = 0.6, limit: int = 50
) -> Dict[str, Any]:
    """
    Get semantic connections between GBrain ideas

    Args:
        similarity_threshold: Minimum similarity score (0.0-1.0)
        limit: Maximum number of connections to return

    Returns:
        Semantic connections between ideas
    """
    try:
        # Get all ideas from GBrain
        ideas_list = await gbrain_service.list_ideas()

        if not ideas_list:
            return {
                "status": "success",
                "connections": [],
                "message": "No ideas found for analysis",
            }

        # Prepare documents for semantic analysis
        documents = []
        for idea in ideas_list:
            content = idea.get("snippet", "") or idea.get("content", "")
            documents.append(
                {
                    "id": idea.get("slug", idea.get("id", "unknown")),
                    "content": content,
                    "metadata": {"phase": idea.get("phase", "seed"), "score": idea.get("score", 0)},
                }
            )

        # Find semantic connections
        connections = semantic_service.find_semantic_connections(documents, similarity_threshold)

        # Limit results
        connections = connections[:limit]

        return {
            "status": "success",
            "connections": connections,
            "total_found": len(connections),
            "threshold": similarity_threshold,
            "documents_analyzed": len(documents),
        }

    except Exception as e:
        logger.error(f"Error getting semantic connections: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/topics")
async def get_main_topics(limit: int = 10) -> Dict[str, Any]:
    """
    Extract main topics from all GBrain ideas

    Args:
        limit: Maximum number of topics to return

    Returns:
        Main topics found in the idea collection
    """
    try:
        # Get all ideas from GBrain
        ideas_list = await gbrain_service.list_ideas()

        if not ideas_list:
            return {
                "status": "success",
                "topics": [],
                "message": "No ideas found for topic extraction",
            }

        # Prepare documents for topic extraction
        documents = []
        for idea in ideas_list:
            content = idea.get("snippet", "") or idea.get("content", "")
            if content:
                documents.append(
                    {"id": idea.get("slug", idea.get("id", "unknown")), "content": content}
                )

        # Extract topics
        topics = semantic_service.extract_topics(documents, limit)

        return {
            "status": "success",
            "topics": topics,
            "total_topics": len(topics),
            "documents_analyzed": len(documents),
        }

    except Exception as e:
        logger.error(f"Error extracting topics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analyze/{idea_id}")
async def analyze_idea(idea_id: str) -> Dict[str, Any]:
    """
    Analyze a single idea for semantic insights

    Args:
        idea_id: ID or slug of the idea to analyze

    Returns:
        Semantic analysis results for the idea
    """
    try:
        # Get specific idea from GBrain
        ideas_list = await gbrain_service.list_ideas()

        if not ideas_list:
            raise HTTPException(status_code=404, detail="No ideas found")

        # Find the specific idea
        idea = None
        for i in ideas_list:
            if i.get("slug") == idea_id or i.get("id") == idea_id:
                idea = i
                break

        if not idea:
            raise HTTPException(status_code=404, detail=f"Idea {idea_id} not found")

        # Analyze the idea
        content = idea.get("snippet", "") or idea.get("content", "")
        analysis = semantic_service.analyze_document({"id": idea_id, "content": content})

        return {
            "status": "success",
            "analysis": analysis,
            "idea_metadata": {
                "slug": idea.get("slug"),
                "phase": idea.get("phase"),
                "score": idea.get("score"),
                "date": idea.get("date"),
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing idea {idea_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/similar/{idea_id}")
async def find_similar_ideas(idea_id: str, limit: int = 5) -> Dict[str, Any]:
    """
    Find ideas semantically similar to a given idea

    Args:
        idea_id: ID or slug of the reference idea
        limit: Maximum number of similar ideas to return

    Returns:
        List of similar ideas with similarity scores
    """
    try:
        # Get all ideas from GBrain
        ideas_list = await gbrain_service.list_ideas()

        if not ideas_list:
            return {"status": "success", "similar_ideas": [], "message": "No ideas found"}

        # Find the reference idea
        reference_idea = None
        for i in ideas_list:
            if i.get("slug") == idea_id or i.get("id") == idea_id:
                reference_idea = i
                break

        if not reference_idea:
            raise HTTPException(status_code=404, detail=f"Idea {idea_id} not found")

        # Get semantic connections
        connections = semantic_service.find_semantic_connections(
            [
                {
                    "id": i.get("slug", i.get("id")),
                    "content": i.get("snippet", "") or i.get("content", ""),
                }
                for i in ideas_list
            ],
            similarity_threshold=0.3,  # Lower threshold for finding similar ideas
        )

        # Filter connections involving the reference idea
        reference_id = reference_idea.get("slug", reference_idea.get("id"))
        similar_ideas = []

        for conn in connections:
            if conn["source"] == reference_id:
                similar_ideas.append({"idea_id": conn["target"], "similarity": conn["weight"]})
            elif conn["target"] == reference_id:
                similar_ideas.append({"idea_id": conn["source"], "similarity": conn["weight"]})

        # Sort by similarity and limit
        similar_ideas.sort(key=lambda x: x["similarity"], reverse=True)
        similar_ideas = similar_ideas[:limit]

        # Add idea details
        for sim_idea in similar_ideas:
            for idea in ideas_list:
                if idea.get("slug") == sim_idea["idea_id"] or idea.get("id") == sim_idea["idea_id"]:
                    sim_idea["details"] = {
                        "slug": idea.get("slug"),
                        "snippet": idea.get("snippet", "")[:200],
                        "phase": idea.get("phase"),
                        "score": idea.get("score"),
                    }
                    break

        return {
            "status": "success",
            "reference_idea": reference_id,
            "similar_ideas": similar_ideas,
            "total_found": len(similar_ideas),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error finding similar ideas for {idea_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
