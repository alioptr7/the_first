"""Worker settings router module."""
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.session import get_db
from models.worker_settings import WorkerSettings
from schemas.worker_settings import (
    WorkerSettingsCreate,
    WorkerSettingsUpdate,
    WorkerSettingsResponse,
    StorageTestResponse
)
from services.worker_settings import WorkerSettingsService

router = APIRouter(prefix="/worker-settings", tags=["worker-settings"])

@router.get("/", response_model=list[WorkerSettingsResponse])
async def get_worker_settings(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> list[WorkerSettingsResponse]:
    """List all worker settings."""
    service = WorkerSettingsService(db)
    return await service.get_settings(skip=skip, limit=limit)

@router.post("/test-connection", response_model=StorageTestResponse)
async def test_connection(
    settings: Dict[str, Any],
    db: Session = Depends(get_db)
) -> StorageTestResponse:
    """Test connection to storage using provided settings."""
    # Create temporary settings object
    temp_settings = WorkerSettings(
        worker_type=settings["worker_type"],
        storage_type=settings["storage_type"],
        storage_settings=settings["storage_settings"]
    )
    
    service = WorkerSettingsService(db)
    is_connected = await service.test_connection(temp_settings)
    
    return StorageTestResponse(
        success=is_connected,
        message="Connection successful" if is_connected else "Connection failed"
    )

@router.get("/{settings_id}/test", response_model=StorageTestResponse)
async def test_existing_connection(
    settings_id: str,
    db: Session = Depends(get_db)
) -> StorageTestResponse:
    """Test connection to storage using existing settings."""
    settings = db.query(WorkerSettings).filter(WorkerSettings.id == settings_id).first()
    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found")
    
    service = WorkerSettingsService(db)
    is_connected = await service.test_connection(settings)
    
    return StorageTestResponse(
        success=is_connected,
        message="Connection successful" if is_connected else "Connection failed"
    )