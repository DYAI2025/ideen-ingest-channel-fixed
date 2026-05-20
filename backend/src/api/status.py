"""
Status API Router
Health check and system status endpoints
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
import psutil
import platform
from datetime import datetime
from ..core.config import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Basic health check endpoint
    """
    return JSONResponse(
        content={
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "Ideen Ingest Channel",
        }
    )


@router.get("/system")
async def system_status():
    """
    Detailed system status
    """
    try:
        # System information
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        return JSONResponse(
            content={
                "timestamp": datetime.now().isoformat(),
                "system": {
                    "platform": platform.system(),
                    "platform_release": platform.release(),
                    "platform_version": platform.version(),
                    "architecture": platform.machine(),
                    "hostname": platform.node(),
                    "processor": platform.processor(),
                },
                "resources": {
                    "cpu_percent": cpu_percent,
                    "memory": {
                        "total": memory.total,
                        "available": memory.available,
                        "percent": memory.percent,
                        "used": memory.used,
                        "free": memory.free,
                    },
                    "disk": {
                        "total": disk.total,
                        "used": disk.used,
                        "free": disk.free,
                        "percent": disk.percent,
                    },
                },
                "config": {
                    "upload_dir": str(settings.upload_dir),
                    "gbrain_source": settings.gbrain_source,
                    "gbrain_path": settings.gbrain_path,
                    "allowed_extensions": settings.allowed_extensions,
                },
            }
        )

    except Exception as e:
        return JSONResponse(
            content={"status": "error", "error": str(e), "timestamp": datetime.now().isoformat()},
            status_code=500,
        )
