"""مدل‌های مشترک"""
from datetime import datetime
from typing import Optional
import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    """مدل کاربر"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_exported_at = Column(DateTime(timezone=True), nullable=True)
    settings_hash = Column(String(64), nullable=True)

    request_access = relationship("UserRequestAccess", back_populates="user")

class RequestType(Base):
    """مدل نوع درخواست"""
    __tablename__ = "request_types"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    user_access = relationship("UserRequestAccess", back_populates="request_type")

class UserRequestAccess(Base):
    """مدل دسترسی کاربر به نوع درخواست"""
    __tablename__ = "user_request_access"

    id = Column(Integer, primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    request_type_id = Column(Integer, ForeignKey("request_types.id"), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    allowed_indices = Column(JSON, nullable=True)
    rate_limit = Column(Integer, nullable=True)
    daily_limit = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="request_access")
    request_type = relationship("RequestType", back_populates="user_access")

class ExportableSettings(Base):
    """مدل تنظیمات قابل صادر کردن"""
    __tablename__ = "exportable_settings"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    settings = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)