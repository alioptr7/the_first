"""User model"""
import uuid
from sqlalchemy import Boolean, String, Integer, JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column

from shared.database.base import BaseModel


class User(BaseModel):
    """User model"""
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    profile_type: Mapped[str] = mapped_column(String(50), nullable=False, default="basic")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    daily_request_limit: Mapped[int] = mapped_column(Integer, default=100)
    monthly_request_limit: Mapped[int] = mapped_column(Integer, default=2000)
    max_results_per_request: Mapped[int] = mapped_column(Integer, default=1000)
    allowed_indices: Mapped[list[str]] = mapped_column(JSON, server_default='[]')
    
    # Relationships
    requests = relationship("Request", back_populates="user", cascade="all, delete-orphan")
    created_request_types = relationship("RequestType", back_populates="created_by")
    request_access = relationship("UserRequestAccess", back_populates="user", cascade="all, delete-orphan")
    settings = relationship("UserSettings", back_populates="user", cascade="all, delete-orphan")