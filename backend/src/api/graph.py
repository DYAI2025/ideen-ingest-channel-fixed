"""
Graph API Router
Specialized endpoints for graph visualization and SSH access
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from ..services.gbrain_service import GBrainService

router = APIRouter()
gbrain_service = GBrainService()


@router.get("/nodes")
async def get_gbrain_nodes():
    """
    Get all ideas from GBrain as graph nodes
    """
    try:
        ideas = await gbrain_service.list_ideas()

        # Transform ideas into graph nodes
        nodes = []
        for idea in ideas:
            if isinstance(idea, dict) and "slug" in idea:
                nodes.append(
                    {
                        "id": idea["slug"],
                        "label": idea.get("title", idea["slug"]),
                        "type": idea.get("type", "concept"),
                        "date": idea.get("date", ""),
                        "phase": idea.get("phase", "seed"),  # Default to seed if not specified
                        "data": idea,
                    }
                )

        return JSONResponse(content={"nodes": nodes, "count": len(nodes)})

    except Exception as e:
        return JSONResponse(
            content={"status": "error", "error": str(e), "nodes": [], "count": 0}, status_code=500
        )


@router.get("/edges")
async def get_gbrain_edges():
    """
    Get relationships between ideas as graph edges
    """
    try:
        # For now, create simple sequential edges
        # In a real implementation, this would query GBrain's relationship data
        ideas = await gbrain_service.list_ideas()

        edges = []
        idea_list = [idea for idea in ideas if isinstance(idea, dict) and "slug" in idea]

        # Create edges between sequential ideas
        for i in range(len(idea_list) - 1):
            edges.append(
                {
                    "id": f"e_{idea_list[i]['slug']}_{idea_list[i+1]['slug']}",
                    "source": idea_list[i]["slug"],
                    "target": idea_list[i + 1]["slug"],
                    "type": "evolves_into",
                    "animated": True,
                }
            )

        return JSONResponse(content={"edges": edges, "count": len(edges)})

    except Exception as e:
        return JSONResponse(
            content={"status": "error", "error": str(e), "edges": [], "count": 0}, status_code=500
        )


@router.get("/full-graph")
async def get_full_gbrain_graph():
    """
    Get complete graph data (nodes + edges) for GBrain
    Optimized for SSH access and remote visualization
    """
    try:
        # Get nodes
        ideas = await gbrain_service.list_ideas()

        nodes = []
        for idea in ideas:
            if isinstance(idea, dict) and "slug" in idea:
                nodes.append(
                    {
                        "id": idea["slug"],
                        "label": idea.get("title", idea["slug"]),
                        "type": idea.get("type", "concept"),
                        "date": idea.get("date", ""),
                        "phase": idea.get("phase", "seed"),
                        "data": idea,
                    }
                )

        # Create simple edges
        idea_list = [idea for idea in ideas if isinstance(idea, dict) and "slug" in idea]
        edges = []

        for i in range(len(idea_list) - 1):
            edges.append(
                {
                    "id": f"e_{idea_list[i]['slug']}_{idea_list[i+1]['slug']}",
                    "source": idea_list[i]["slug"],
                    "target": idea_list[i + 1]["slug"],
                    "type": "evolves_into",
                    "animated": True,
                }
            )

        return JSONResponse(
            content={
                "status": "success",
                "graph": {"nodes": nodes, "edges": edges},
                "metadata": {
                    "node_count": len(nodes),
                    "edge_count": len(edges),
                    "last_updated": ideas[0].get("date", "") if ideas else "",
                },
            }
        )

    except Exception as e:
        return JSONResponse(
            content={
                "status": "error",
                "error": str(e),
                "graph": {"nodes": [], "edges": []},
                "metadata": {"node_count": 0, "edge_count": 0, "last_updated": ""},
            },
            status_code=500,
        )
