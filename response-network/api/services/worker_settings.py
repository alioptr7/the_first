"""Worker settings service module."""
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from models.worker_settings import WorkerSettings
from storage import STORAGE_HANDLERS

class WorkerSettingsService:
    """Service for managing worker settings."""
    
    def __init__(self, db: Session):
        """Initialize worker settings service."""
        self.db = db
        self._handlers: Dict[str, Any] = {}
    
    async def get_settings(self, skip: int = 0, limit: int = 100) -> list[WorkerSettings]:
        """Get all worker settings."""
        return self.db.query(WorkerSettings).offset(skip).limit(limit).all()
    
    def _get_handler(self, settings: WorkerSettings):
        """Get or create storage handler for settings."""
        settings_id = str(settings.id)
        if settings_id not in self._handlers:
            handler_class = STORAGE_HANDLERS[settings.storage_type.value]
            self._handlers[settings_id] = handler_class(settings.storage_settings)
        return self._handlers[settings_id]
    
    async def test_connection(self, settings: WorkerSettings) -> bool:
        """Test connection to storage."""
        try:
            handler = self._get_handler(settings)
            return await handler.test_connection()
        except Exception:
            return False
    
    async def upload_file(self, settings: WorkerSettings, local_path: str, remote_path: str) -> bool:
        """Upload file to storage."""
        try:
            handler = self._get_handler(settings)
            return await handler.upload_file(local_path, remote_path)
        except Exception:
            return False
    
    async def download_file(self, settings: WorkerSettings, remote_path: str, local_path: str) -> bool:
        """Download file from storage."""
        try:
            handler = self._get_handler(settings)
            return await handler.download_file(remote_path, local_path)
        except Exception:
            return False
    
    async def list_files(self, settings: WorkerSettings, path: str) -> list[str]:
        """List files in storage path."""
        try:
            handler = self._get_handler(settings)
            return await handler.list_files(path)
        except Exception:
            return []
    
    async def delete_file(self, settings: WorkerSettings, path: str) -> bool:
        """Delete file from storage."""
        try:
            handler = self._get_handler(settings)
            return await handler.delete_file(path)
        except Exception:
            return False