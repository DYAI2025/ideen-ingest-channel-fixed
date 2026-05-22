"""
Ingest API Router
Handles file upload and GBrain import operations
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
from typing import List, Optional
import aiofiles
from datetime import datetime

from ..services.gbrain_service import GBrainService
from ..core.config import settings

router = APIRouter()
gbrain_service = GBrainService()


@router.post("/upload")
async def upload_file(file: UploadFile = File(...), phase: str = "seed", auto_import: bool = True):
    """
    Upload a file to the ingest channel

    Args:
        file: File to upload
        phase: Phase to tag the idea with (seed, sprout, growth, flower, harvest)
        auto_import: Whether to automatically import to GBrain
    """
    try:
        # Validate file extension
        if file.filename:
            file_ext = Path(file.filename).suffix.lower()
            allowed_exts = [ext.strip() for ext in settings.allowed_extensions.split(',')]
            if file_ext not in allowed_exts:
                raise HTTPException(
                    status_code=400,
                    detail=f"File extension {file_ext} not allowed. Allowed: {settings.allowed_extensions}",
                )

        # Create upload directory if needed
        settings.upload_dir.expanduser().mkdir(parents=True, exist_ok=True)

        # Save file
        file_path = settings.upload_dir.expanduser() / file.filename
        async with aiofiles.open(file_path, "wb") as f:
            content = await file.read()
            await f.write(content)

        result = {
            "status": "uploaded",
            "filename": file.filename,
            "path": str(file_path),
            "phase": phase,
            "timestamp": datetime.now().isoformat(),
            "auto_import": auto_import,
        }

        # Auto-import to GBrain if requested
        if auto_import:
            import_result = await gbrain_service.import_file_to_gbrain(file_path, phase)
            result["import_result"] = import_result

        return JSONResponse(content=result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/import")
async def import_to_gbrain(file_path: str, phase: str = "seed"):
    """
    Manually trigger GBrain import for a file

    Args:
        file_path: Path to the file to import
        phase: Phase to tag the idea with
    """
    try:
        path = Path(file_path)
        if not path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        result = await gbrain_service.import_file_to_gbrain(path, phase)

        return JSONResponse(content=result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files")
async def list_uploaded_files():
    """
    List all files in the upload directory
    """
    try:
        files = []
        for file_path in settings.upload_dir.expanduser().iterdir():
            if file_path.is_file():
                stat = file_path.stat()
                files.append(
                    {
                        "filename": file_path.name,
                        "path": str(file_path),
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "extension": file_path.suffix,
                    }
                )

        return JSONResponse(
            content={"files": files, "count": len(files), "upload_dir": str(settings.upload_dir.expanduser())}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/files/{filename}")
async def delete_file(filename: str):
    """
    Delete a file from the upload directory
    """
    try:
        file_path = settings.upload_dir.expanduser() / filename
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        file_path.unlink()

        return JSONResponse(
            content={
                "status": "deleted",
                "filename": filename,
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
