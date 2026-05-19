"""
GBrain → Kanban Sync Service
Automatically creates Kanban tasks from GBrain ideas
"""
import asyncio
from datetime import datetime
from typing import List, Optional
import json
import os

from .gbrain_service import GBrainService

class KanbanSyncService:
    def __init__(self):
        self.gbrain_service = GBrainService()
        self.sync_interval = 300  # 5 minutes
        self.is_running = False
        
    async def sync_ideas_to_kanban(self):
        """Sync GBrain ideas to Kanban board"""
        try:
            # Get all ideas from GBrain
            ideas = await self.gbrain_service.get_all_ideas()
            
            if not ideas:
                print("No ideas found in GBrain")
                return
            
            # Load current kanban data
            kanban_data = self._load_kanban_data()
            
            # Create tasks from ideas
            new_tasks_count = 0
            for idea in ideas:
                # Check if task already exists
                task_exists = self._task_exists(kanban_data, idea.get('slug'))
                
                if not task_exists:
                    # Map GBrain phase to Kanban column
                    column = self._map_phase_to_column(idea.get('phase', 'seed'))
                    
                    # Create task from idea
                    task = {
                        'id': f"gbrain-{idea.get('slug')}",
                        'title': idea.get('title') or idea.get('slug', 'Untitled'),
                        'description': idea.get('snippet', '')[:200],
                        'phase': idea.get('phase', 'seed'),
                        'tags': [idea.get('phase', 'seed'), 'gbrain'],
                        'status': column,
                        'created_at': datetime.now().isoformat(),
                        'updated_at': datetime.now().isoformat(),
                        'source': 'gbrain',
                        'source_id': idea.get('slug')
                    }
                    
                    # Add to appropriate column
                    kanban_column = next(col for col in kanban_data['columns'] if col['id'] == column)
                    kanban_column['tasks'].append(task)
                    new_tasks_count += 1
            
            # Save updated kanban data
            if new_tasks_count > 0:
                self._save_kanban_data(kanban_data)
                print(f"✅ Synced {new_tasks_count} new ideas to Kanban")
            else:
                print("ℹ️  No new ideas to sync")
                
        except Exception as e:
            print(f"❌ Error syncing ideas to Kanban: {e}")
    
    def _load_kanban_data(self) -> dict:
        """Load kanban data from file"""
        kanban_file = 'kanban_data.json'
        if os.path.exists(kanban_file):
            with open(kanban_file, 'r') as f:
                return json.load(f)
        
        # Default structure
        return {
            'columns': [
                {'id': 'backlog', 'title': '📋 Backlog', 'tasks': []},
                {'id': 'todo', 'title': '📝 To Do', 'tasks': []},
                {'id': 'in-progress', 'title': '🚀 In Progress', 'tasks': []},
                {'id': 'review', 'title': '👀 Review', 'tasks': []},
                {'id': 'done', 'title': '✅ Done', 'tasks': []},
            ]
        }
    
    def _save_kanban_data(self, data: dict):
        """Save kanban data to file"""
        with open('kanban_data.json', 'w') as f:
            json.dump(data, f, indent=2)
    
    def _task_exists(self, kanban_data: dict, idea_slug: str) -> bool:
        """Check if a task from this idea already exists"""
        task_id = f"gbrain-{idea_slug}"
        for column in kanban_data['columns']:
            for task in column['tasks']:
                if task['id'] == task_id:
                    return True
        return False
    
    def _map_phase_to_column(self, phase: str) -> str:
        """Map GBrain phase to Kanban column"""
        phase_mapping = {
            'seed': 'backlog',
            'sprout': 'todo',
            'growth': 'in-progress',
            'flower': 'review',
            'harvest': 'done'
        }
        return phase_mapping.get(phase.lower(), 'backlog')
    
    async def start_sync_loop(self):
        """Start automatic sync loop"""
        self.is_running = True
        print("🔄 Starting GBrain → Kanban sync loop...")
        
        while self.is_running:
            await self.sync_ideas_to_kanban()
            await asyncio.sleep(self.sync_interval)
    
    def stop_sync_loop(self):
        """Stop automatic sync loop"""
        self.is_running = False
        print("🛑 Stopped GBrain → Kanban sync loop")
    
    async def manual_sync(self):
        """Perform manual sync"""
        print("🔄 Performing manual GBrain → Kanban sync...")
        await self.sync_ideas_to_kanban()