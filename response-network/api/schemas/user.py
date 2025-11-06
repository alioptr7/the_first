from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr
import uuid


class UserBase(BaseModel):
    """Shared properties for a user."""
    email: EmailStr
    username: str
    daily_request_limit: int = 100
    monthly_request_limit: int = 2000
    max_results_per_request: int = 1000
    allowed_indices: list[str] = []


class UserRead(UserBase):
    """Properties to return to a client."""
    id: uuid.UUID
    profile_type: str
    is_active: bool
    daily_request_limit: int
    monthly_request_limit: int
    max_results_per_request: int
    allowed_indices: list[str]

    class Config:
        from_attributes = True


class UserCreate(UserBase):
    """Properties to receive via API on creation."""
    password: str
    profile_type: str = 'user'
    is_active: bool = True


class UserUpdate(BaseModel):
    """Properties that can be updated."""
    email: EmailStr | None = None
    username: str | None = None
    password: str | None = None


class UserStats(BaseModel):
    """User statistics."""
    total_requests: int
    completed_requests: int
    failed_requests: int
    avg_processing_time: float
    requests_today: int
    requests_this_month: int


class UserWithStats(UserRead):
    """User with statistics."""
    stats: UserStats

    class Config:
        from_attributes = True