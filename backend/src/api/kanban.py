"""
Kanban Board API Endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json
import os

router = APIRouter()

# Data storage path
KANBAN_FILE = "kanban_data.json"

class Task(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    phase: str
    tags: List[str] = []
    status: str = "backlog"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class Column(BaseModel):
    id: str
    title: str
    tasks: List[Task] = []

class KanbanBoard(BaseModel):
    columns: List[Column]

def load_kanban_data() -> KanbanBoard:
    """Load kanban data from file"""
    if os.path.exists(KANBAN_FILE):
        with open(KANBAN_FILE, 'r') as f:
            data = json.load(f)
            return KanbanBoard(**data)
    
    # Default board structure
    return KanbanBoard(
        columns=[
            Column(id="backlog", title="📋 Backlog", tasks=[]),
            Column(id="todo", title="📝 To Do", tasks=[]),
            Column(id="in-progress", title="🚀 In Progress", tasks=[]),
            Column(id="review", title="👀 Review", tasks=[]),
            Column(id="done", title="✅ Done", tasks=[]),
        ]
    )

def save_kanban_data(board: KanbanBoard):
    """Save kanban data to file"""
    with open(KANBAN_FILE, 'w') as f:
        json.dump(board.dict(), f, indent=2)

@router.get("/board")
async def get_kanban_board():
    """Get the kanban board"""
    board = load_kanban_data()
    return {"status": "success", "board": board}

@router.post("/board")
async def update_kanban_board(board: KanbanBoard):
    """Update the kanban board"""
    save_kanban_data(board)
    return {"status": "success", "board": board}

@router.get("/")
async def get_kanban_root():
    """Root endpoint for compatibility"""
    board = load_kanban_data()
    return {"status": "success", "board": board}

@router.post("/task")
async def add_task(task: Task):
    """Add a new task to the backlog"""
    board = load_kanban_data()
    
    # Set timestamps
    now = datetime.now().isoformat()
    task.created_at = now
    task.updated_at = now
    
    # Add to backlog
    backlog_column = next(col for col in board.columns if col.id == "backlog")
    backlog_column.tasks.append(task)
    
    save_kanban_data(board)
    return {"status": "success", "task": task}

@router.put("/task/{task_id}")
async def update_task(task_id: str, task: Task):
    """Update an existing task"""
    board = load_kanban_data()
    
    for column in board.columns:
        for i, existing_task in enumerate(column.tasks):
            if existing_task.id == task_id:
                task.updated_at = datetime.now().isoformat()
                column.tasks[i] = task
                save_kanban_data(board)
                return {"status": "success", "task": task}
    
    raise HTTPException(status_code=404, detail="Task not found")

@router.delete("/task/{task_id}")
async def delete_task(task_id: str):
    """Delete a task"""
    board = load_kanban_data()
    
    for column in board.columns:
        column.tasks = [task for task in column.tasks if task.id != task_id]
    
    save_kanban_data(board)
    return {"status": "success"}

@router.post("/move/{task_id}/{column_id}")
async def move_task(task_id: str, column_id: str):
    """Move a task to a different column"""
    board = load_kanban_data()
    
    # Find and remove task from current column
    task_to_move = None
    for column in board.columns:
        for i, task in enumerate(column.tasks):
            if task.id == task_id:
                task_to_move = column.tasks.pop(i)
                break
        if task_to_move:
            break
    
    if not task_to_move:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Update task status
    task_to_move.status = column_id
    task_to_move.updated_at = datetime.now().isoformat()
    
    # Add to new column
    target_column = next(col for col in board.columns if col.id == column_id)
    target_column.tasks.append(task_to_move)
    
    save_kanban_data(board)
    return {"status": "success", "task": task_to_move}