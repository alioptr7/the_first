"""User schemas"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    """Base user schema"""
    username: str
    email: EmailStr
    is_active: bool = True
    is_admin: bool = False


class UserCreate(UserBase):
    """User creation schema"""
    password: str


class UserUpdate(BaseModel):
    """User update schema"""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)


class UserResponse(UserBase):
    """User response schema"""
    id: int
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)