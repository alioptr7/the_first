from datetime import datetime, timedelta
from typing import Dict, Optional
import uuid

from sqlalchemy import Column, DateTime, String, JSON, Boolean, Integer, Text, func
from sqlalchemy.dialects.postgresql import UUID

from db.base_class import Base

class WorkerSettings(Base):
    """Worker settings model - matches actual database schema."""
    __tablename__ = "worker_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    worker_type = Column(String(100), nullable=False, unique=True)
    # Storage settings
    storage_type = Column(String(50), nullable=False)
    storage_config = Column(JSON, nullable=False)
    # Status
    is_active = Column(Boolean, default=True)
    last_run = Column(DateTime(timezone=True), nullable=True)
    next_run = Column(DateTime(timezone=True), nullable=True)
    error_count = Column(Integer, default=0)
    # Metadata
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())