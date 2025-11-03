"""User model"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from api.db.base_class import Base, TimestampMixin


class User(Base, TimestampMixin):
    """User model"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    last_login = Column(DateTime, nullable=True)

    # Relationships
    logs = relationship("LogEntry", back_populates="user")
    error_logs = relationship("ErrorLog", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")
    performance_logs = relationship("PerformanceLog", back_populates="user")