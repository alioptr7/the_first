"""User model"""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, String, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column

from shared.database.base import BaseModel


class User(BaseModel):
    """User model"""
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    logs = relationship("LogEntry", back_populates="user")
    error_logs = relationship("ErrorLog", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")
    performance_logs = relationship("PerformanceLog", back_populates="user")
    requests = relationship("Request", back_populates="user")
    api_keys = relationship("ApiKey", back_populates="user")