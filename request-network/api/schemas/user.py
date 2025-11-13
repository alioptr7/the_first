from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None


class User(UserBase):
    id: UUID
    profile_type: str
    rate_limit_per_minute: int
    rate_limit_per_hour: int
    rate_limit_per_day: int
    priority: int
    is_active: bool
    allowed_indices: Optional[list[str]] = None
    
    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserBase):
    password: str


class ChangePasswordRequest(BaseModel):
    """User request to change own password"""
    current_password: str
    new_password: str


class PasswordChangeResponse(BaseModel):
    """Response after password change"""
    success: bool
    message: str
    username: str