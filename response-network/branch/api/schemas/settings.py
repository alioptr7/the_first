from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class SettingBase(BaseModel):
    """Base schema for system settings"""
    key: str = Field(..., description="Unique key for the setting")
    value: str = Field(..., description="Value of the setting")
    description: Optional[str] = Field(None, description="Description of what this setting does")
    is_user_specific: bool = Field(
        default=False,
        description="Whether this setting can be overridden per user"
    )
    sync_priority: int = Field(
        default=0,
        description="Priority for syncing (higher numbers sync first)",
        ge=0,
        le=100
    )


class SettingCreate(SettingBase):
    """Schema for creating a new system setting"""
    pass


class SettingUpdate(BaseModel):
    """Schema for updating a system setting"""
    value: Optional[str] = None
    description: Optional[str] = None
    sync_priority: Optional[int] = Field(None, ge=0, le=100)


class SettingRead(SettingBase):
    """Schema for reading a system setting"""
    id: UUID
    is_synced: bool
    last_synced_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserSettingBase(BaseModel):
    """Base schema for user-specific settings"""
    setting_id: UUID = Field(..., description="ID of the system setting being overridden")
    value: str = Field(..., description="User-specific value for the setting")


class UserSettingCreate(UserSettingBase):
    """Schema for creating a new user-specific setting"""
    pass


class UserSettingUpdate(BaseModel):
    """Schema for updating a user-specific setting"""
    value: str


class UserSettingRead(UserSettingBase):
    """Schema for reading a user-specific setting"""
    id: UUID
    user_id: UUID
    is_synced: bool
    last_synced_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True