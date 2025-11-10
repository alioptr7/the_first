from datetime import datetime
from enum import Enum
from typing import Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field

class StorageType(str, Enum):
    LOCAL = "local"
    FTP = "ftp"
    SFTP = "sftp"
    S3 = "s3"
    GCS = "gcs"
    AZURE = "azure"

class ScheduleType(str, Enum):
    CRONTAB = "crontab"
    INTERVAL = "interval"
    
class StorageConfigBase(BaseModel):
    """Base storage configuration."""
    path: str = Field(..., description="Base path for storage")

class LocalStorageConfig(StorageConfigBase):
    """Local storage configuration."""
    create_dirs: bool = Field(True, description="Create directories if they don't exist")

class FTPStorageConfig(StorageConfigBase):
    """FTP storage configuration."""
    host: str
    port: int = 21
    username: str
    password: str
    passive_mode: bool = True

class S3StorageConfig(StorageConfigBase):
    """S3 storage configuration."""
    bucket: str
    aws_access_key_id: str
    aws_secret_access_key: str
    region: str

class ScheduleConfigBase(BaseModel):
    """Base schedule configuration."""
    pass

class CrontabConfig(ScheduleConfigBase):
    """Crontab schedule configuration."""
    crontab: str = Field(..., description="Crontab expression")

class IntervalConfig(ScheduleConfigBase):
    """Interval schedule configuration."""
    days: int = Field(0, ge=0)
    hours: int = Field(0, ge=0)
    minutes: int = Field(0, ge=0)
    seconds: int = Field(0, ge=0)

class WorkerSettingsBase(BaseModel):
    """Base worker settings schema."""
    worker_name: str
    storage_type: StorageType
    storage_config: Dict
    schedule_type: ScheduleType
    schedule_config: Dict
    description: Optional[str] = None
    is_active: bool = True

class WorkerSettingsCreate(WorkerSettingsBase):
    """Schema for creating worker settings."""
    pass

class WorkerSettingsUpdate(BaseModel):
    """Schema for updating worker settings."""
    storage_type: Optional[StorageType] = None
    storage_config: Optional[Dict] = None
    schedule_type: Optional[ScheduleType] = None
    schedule_config: Optional[Dict] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class WorkerSettings(WorkerSettingsBase):
    """Schema for reading worker settings."""
    id: UUID
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    error_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True