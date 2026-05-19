"""
File Watcher Service
Monitors upload directory for new files and triggers automatic GBrain import
"""
import asyncio
from pathlib import Path
from typing import Callable, Optional, Dict
import aiofiles
from datetime import datetime
from .gbrain_service import GBrainService
from ..core.config import settings

class FileWatcher:
    """Async file watcher for automatic GBrain import"""
    
    def __init__(self):
        self.upload_dir = settings.upload_dir
        self.gbrain_service = GBrainService()
        self.is_running = False
        self.processed_files = set()
        self.scan_interval = 5  # seconds
        self.phase = "seed"  # Default phase for new uploads
    
    async def watch_directory(self, directory: Optional[Path] = None):
        """
        Watch directory for new files and trigger GBrain import
        """
        watch_dir = directory or self.upload_dir
        self.is_running = True
        
        print(f"📁 Starting file watcher on: {watch_dir}")
        
        try:
            while self.is_running:
                await self._scan_directory(watch_dir)
                await asyncio.sleep(self.scan_interval)
        except asyncio.CancelledError:
            print("📁 File watcher stopped")
        except Exception as e:
            print(f"❌ File watcher error: {e}")
    
    async def _scan_directory(self, directory: Path):
        """
        Scan directory for new files
        """
        try:
            for file_path in directory.iterdir():
                if file_path.is_file() and self._should_import_file(file_path):
                    await self._import_file(file_path)
        except Exception as e:
            print(f"❌ Scan error: {e}")
    
    def _should_import_file(self, file_path: Path) -> bool:
        """
        Check if file should be imported
        """
        # Skip if already processed
        if str(file_path) in self.processed_files:
            return False
        
        # Skip if file is too new (might still be uploading)
        file_age = datetime.now().timestamp() - file_path.stat().st_mtime
        if file_age < 2:  # 2 seconds grace period
            return False
        
        # Check file extension
        if file_path.suffix.lower() not in settings.allowed_extensions:
            return False
        
        # Skip temporary files
        if file_path.name.startswith('.') or file_path.name.startswith('~'):
            return False
        
        return True
    
    async def _import_file(self, file_path: Path):
        """
        Import file to GBrain
        """
        try:
            print(f"📥 Importing file: {file_path.name}")
            
            result = await self.gbrain_service.import_file_to_gbrain(file_path, self.phase)
            
            if result["status"] == "success":
                print(f"✅ Successfully imported: {result['slug']} (phase: {result['phase']})")
                self.processed_files.add(str(file_path))
                
                # Emit event for frontend notification
                await self._emit_import_event(result)
            else:
                print(f"❌ Import failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Import error for {file_path.name}: {e}")
    
    async def _emit_import_event(self, import_result: Dict):
        """
        Emit import event for frontend notification
        """
        # This could be implemented with WebSocket or Server-Sent Events
        # For now, we'll just log it
        print(f"📡 Import event: {import_result['slug']} - {import_result['status']}")
    
    async def stop(self):
        """Stop the file watcher"""
        self.is_running = False