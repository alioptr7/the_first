from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class SettingsBase(BaseModel):
    """Base settings schema."""
    key: str
    value: dict
    description: str | None = None
    is_active: bool = True
    

class SettingsCreate(SettingsBase):
    """Schema for creating settings."""
    pass


class SettingsUpdate(SettingsBase):
    """Schema for updating settings."""
    key: str | None = None
    value: dict | None = None
    description: str | None = None
    is_active: bool | None = None


class Settings(SettingsBase):
    """Schema for reading settings."""
    id: int
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class SettingsExport(BaseModel):
    """Schema for settings export file."""
    settings: List[Settings]
    exported_at: datetime = Field(description="UTC timestamp of export")
    version: int = Field(description="Export format version")


# User Settings
class UserSettingCreate(BaseModel):
    """Schema for creating user settings."""
    key: str
    value: dict


class UserSettingUpdate(BaseModel):
    """Schema for updating user settings."""
    value: dict


class UserSettingRead(BaseModel):
    """Schema for reading user settings."""
    key: str
    value: dict
    user_id: str

    class Config:
        from_attributes = True