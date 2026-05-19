"""
Main FastAPI Application for Ideen Ingest Channel
SSH-zugänglicher Drag-and-Drop Eingangskanal für GBrain
"""
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import subprocess
import asyncio
from pathlib import Path
from typing import List, Optional
import json
from datetime import datetime

from src.api.ingest import router as ingest_router
from src.api.ideas import router as ideas_router
from src.api.status import router as status_router
from src.api.graph import router as graph_router
from src.services.gbrain_service import GBrainService
from src.services.file_watcher import FileWatcher
from src.core.config import settings

app = FastAPI(
    title="Ideen Ingest Channel",
    description="SSH-zugänglicher Drag-and-Drop Eingangskanal für GBrain Ideen-System",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Für SSH-Tunnel anpassen
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint for Railway
@app.get("/health")
async def health_check():
    """Health check endpoint for Railway deployment"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Include routers
app.include_router(ingest_router, prefix="/api/ingest", tags=["Ingest"])
app.include_router(ideas_router, prefix="/api/ideas", tags=["Ideas"])
app.include_router(status_router, prefix="/api/status", tags=["Status"])
app.include_router(graph_router, prefix="/api/graph", tags=["Graph"])

# Static files for frontend
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path)), name="frontend")
else:
    frontend_path.mkdir(parents=True, exist_ok=True)
    app.mount("/", StaticFiles(directory=str(frontend_path)), name="frontend")

# Services
gbrain_service = GBrainService()
file_watcher = FileWatcher()

@app.on_event("startup")
async def startup_event():
    """Start-up event handler"""
    print("🚀 Ideen Ingest Channel starting up...")
    print(f"📂 Upload directory: {settings.upload_dir}")
    print(f"🧠 GBrain source: {settings.gbrain_source}")
    
    # Ensure directories exist
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Start file watcher (commented out for now to prevent import loops)
    # asyncio.create_task(file_watcher.watch_directory(settings.upload_dir))
    
    print("✅ Startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    """Shut-down event handler"""
    print("🛑 Ideen Ingest Channel shutting down...")
    # await file_watcher.stop() # Commented out since file watcher is disabled
    print("✅ Shutdown complete")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )