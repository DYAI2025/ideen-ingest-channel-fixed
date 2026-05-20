"""
Agent API Endpoints
Provides API access for local agents to research and enrich ideas
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import logging
from datetime import datetime
import json

from src.services.gbrain_service import GBrainService

router = APIRouter()
logger = logging.getLogger(__name__)

gbrain_service = GBrainService()


class ProductIdea(BaseModel):
    """Product idea from agent research"""

    title: str
    description: str
    target_audience: str
    revenue_model: str
    estimated_value: Optional[str] = None
    complexity: Optional[str] = None
    time_to_market: Optional[str] = None


class ResearchData(BaseModel):
    """Research data from agent analysis"""

    market_analysis: Optional[str] = None
    competitors: Optional[List[str]] = None
    opportunities: Optional[List[str]] = None
    risks: Optional[List[str]] = None
    resources_needed: Optional[List[str]] = None


class IdeaEnrichment(BaseModel):
    """Enrichment data for an idea"""

    products: List[ProductIdea] = []
    research: ResearchData = None
    agent_notes: Optional[str] = None
    status: str = "researched"  # researched, validated, rejected
    enriched_at: str = datetime.now().isoformat()


class AgentTask(BaseModel):
    """Task for an agent"""

    id: str
    idea_id: str
    task_type: str  # research, validate, monetize
    priority: str = "medium"  # high, medium, low
    status: str = "pending"  # pending, in_progress, completed, failed
    created_at: str
    assigned_to: Optional[str] = None
    deadline: Optional[str] = None


# In-memory task storage (in production, use a database)
agent_tasks: List[AgentTask] = []


@router.get("/ideas")
async def get_all_ideas_for_agents(phase: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
    """
    Get all ideas for agent processing

    Args:
        phase: Filter by phase (seed, sprout, growth, flower, harvest)
        limit: Maximum number of ideas to return

    Returns:
        List of ideas with metadata
    """
    try:
        ideas_list = await gbrain_service.list_ideas()

        if not ideas_list:
            return {"status": "success", "ideas": [], "message": "No ideas found"}

        # Filter by phase if specified
        if phase:
            ideas_list = [idea for idea in ideas_list if idea.get("phase") == phase]

        # Limit results
        ideas = ideas_list[:limit]

        return {"status": "success", "ideas": ideas, "total": len(ideas), "phase_filter": phase}

    except Exception as e:
        logger.error(f"Error getting ideas for agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ideas/{idea_id}")
async def get_idea_for_agents(idea_id: str) -> Dict[str, Any]:
    """
    Get a specific idea for agent processing

    Args:
        idea_id: ID or slug of the idea

    Returns:
        Detailed idea information
    """
    try:
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

        # Check if idea has enrichment data
        enrichment_file = f"/tmp/agent_enrichment_{idea_id}.json"
        enrichment = None
        try:
            with open(enrichment_file, "r") as f:
                enrichment = json.load(f)
        except FileNotFoundError:
            pass

        return {"status": "success", "idea": idea, "enrichment": enrichment}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting idea {idea_id} for agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/ideas/{idea_id}/enrich")
async def enrich_idea(idea_id: str, enrichment: IdeaEnrichment) -> Dict[str, Any]:
    """
    Enrich an idea with agent research and product ideas

    Args:
        idea_id: ID or slug of the idea to enrich
        enrichment: Enrichment data from agent

    Returns:
        Confirmation of enrichment
    """
    try:
        # Verify idea exists
        ideas_list = await gbrain_service.list_ideas()
        idea_exists = False
        for i in ideas_list:
            if i.get("slug") == idea_id or i.get("id") == idea_id:
                idea_exists = True
                break

        if not idea_exists:
            raise HTTPException(status_code=404, detail=f"Idea {idea_id} not found")

        # Save enrichment data (in production, use a database)
        enrichment_file = f"/tmp/agent_enrichment_{idea_id}.json"
        with open(enrichment_file, "w") as f:
            json.dump(enrichment.dict(), f, indent=2)

        logger.info(
            f"Idea {idea_id} enriched by agent with {len(enrichment.products)} product ideas"
        )

        return {
            "status": "success",
            "message": f"Idea {idea_id} enriched successfully",
            "enrichment_id": f"agent_enrichment_{idea_id}",
            "products_added": len(enrichment.products),
            "enriched_at": enrichment.enriched_at,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error enriching idea {idea_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ideas/{idea_id}/similar")
async def get_similar_ideas_for_agents(idea_id: str, limit: int = 5) -> Dict[str, Any]:
    """
    Get ideas similar to a given idea for agent cross-referencing

    Args:
        idea_id: ID or slug of the reference idea
        limit: Maximum number of similar ideas

    Returns:
        List of similar ideas
    """
    try:
        # Use semantic analysis to find similar ideas
        from src.services.semantic_analysis import semantic_service

        ideas_list = await gbrain_service.list_ideas()

        if not ideas_list:
            return {"status": "success", "similar_ideas": [], "message": "No ideas found"}

        # Find reference idea
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
            similarity_threshold=0.3,
        )

        # Filter for reference idea
        reference_id = reference_idea.get("slug", reference_idea.get("id"))
        similar_ideas = []

        for conn in connections:
            if conn["source"] == reference_id:
                similar_ideas.append({"idea_id": conn["target"], "similarity": conn["weight"]})
            elif conn["target"] == reference_id:
                similar_ideas.append({"idea_id": conn["source"], "similarity": conn["weight"]})

        # Sort and limit
        similar_ideas.sort(key=lambda x: x["similarity"], reverse=True)
        similar_ideas = similar_ideas[:limit]

        # Add details
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
        logger.error(f"Error getting similar ideas for {idea_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks")
async def get_agent_tasks(
    status: Optional[str] = None, task_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get tasks for agents

    Args:
        status: Filter by status (pending, in_progress, completed, failed)
        task_type: Filter by task type (research, validate, monetize)

    Returns:
        List of agent tasks
    """
    try:
        tasks = agent_tasks

        # Filter by status
        if status:
            tasks = [t for t in tasks if t.status == status]

        # Filter by task type
        if task_type:
            tasks = [t for t in tasks if t.task_type == task_type]

        return {"status": "success", "tasks": tasks, "total": len(tasks)}

    except Exception as e:
        logger.error(f"Error getting agent tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tasks")
async def create_agent_task(task: AgentTask) -> Dict[str, Any]:
    """
    Create a new task for agents

    Args:
        task: Task details

    Returns:
        Created task
    """
    try:
        task.id = f"task_{len(agent_tasks)}_{datetime.now().timestamp()}"
        task.created_at = datetime.now().isoformat()

        agent_tasks.append(task)

        logger.info(f"Created agent task {task.id} for idea {task.idea_id}")

        return {"status": "success", "task": task, "message": "Task created successfully"}

    except Exception as e:
        logger.error(f"Error creating agent task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/tasks/{task_id}/complete")
async def complete_agent_task(task_id: str) -> Dict[str, Any]:
    """
    Mark an agent task as completed

    Args:
        task_id: ID of the task to complete

    Returns:
        Updated task
    """
    try:
        task = None
        for t in agent_tasks:
            if t.id == task_id:
                task = t
                break

        if not task:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

        task.status = "completed"

        logger.info(f"Completed agent task {task_id}")

        return {"status": "success", "task": task, "message": "Task marked as completed"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing task {task_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_agent_stats() -> Dict[str, Any]:
    """
    Get statistics about ideas and agent activities

    Returns:
        Statistics about ideas, phases, enrichment status
    """
    try:
        ideas_list = await gbrain_service.list_ideas()

        total_ideas = len(ideas_list) if ideas_list else 0

        # Count ideas by phase
        phase_counts = {}
        for idea in ideas_list:
            phase = idea.get("phase", "unknown")
            phase_counts[phase] = phase_counts.get(phase, 0) + 1

        # Count enriched ideas
        enriched_count = 0
        import os

        for idea in ideas_list:
            idea_id = idea.get("slug", idea.get("id"))
            if os.path.exists(f"/tmp/agent_enrichment_{idea_id}.json"):
                enriched_count += 1

        # Task statistics
        total_tasks = len(agent_tasks)
        completed_tasks = len([t for t in agent_tasks if t.status == "completed"])
        pending_tasks = len([t for t in agent_tasks if t.status == "pending"])

        return {
            "status": "success",
            "stats": {
                "total_ideas": total_ideas,
                "phase_distribution": phase_counts,
                "enriched_ideas": enriched_count,
                "enrichment_rate": (
                    f"{(enriched_count / total_ideas * 100):.1f}%" if total_ideas > 0 else "0%"
                ),
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "pending_tasks": pending_tasks,
                "task_completion_rate": (
                    f"{(completed_tasks / total_tasks * 100):.1f}%" if total_tasks > 0 else "0%"
                ),
            },
        }

    except Exception as e:
        logger.error(f"Error getting agent stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
