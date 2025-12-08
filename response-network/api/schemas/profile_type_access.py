from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field
from datetime import datetime


class ProfileTypeAccessBase(BaseModel):
    """Base schema for Profile Type Request Access"""
    max_requests_per_day: Optional[int] = Field(None, ge=0, description="Maximum requests per day (null = unlimited)")
    max_requests_per_month: Optional[int] = Field(None, ge=0, description="Maximum requests per month (null = unlimited)")
    is_active: bool = Field(True, description="Whether this access rule is active")


class ProfileTypeAccessCreate(ProfileTypeAccessBase):
    """Schema for creating Profile Type Request Access"""
    profile_type_id: UUID
    request_type_id: UUID


class ProfileTypeAccessUpdate(BaseModel):
    """Schema for updating Profile Type Request Access"""
    max_requests_per_day: Optional[int] = Field(None, ge=0)
    max_requests_per_month: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class ProfileTypeAccessRead(ProfileTypeAccessBase):
    """Schema for reading Profile Type Request Access"""
    id: UUID
    profile_type_id: UUID
    request_type_id: UUID
    profile_type_name: Optional[str] = None  # Joined from profile_type
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BulkProfileTypeAccessCreate(BaseModel):
    """Schema for granting access to multiple profile types"""
    profile_type_ids: list[UUID]
    max_requests_per_day: Optional[int] = Field(None, ge=0)
    max_requests_per_month: Optional[int] = Field(None, ge=0)
    is_active: bool = True
