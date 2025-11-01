from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID, uuid4

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID, JSONB

from api.db.base_class import Base


class TaskLogs(Base):
    """مدل برای ذخیره لاگ‌های تسک‌ها"""
    
    __tablename__ = "task_logs"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    request_id = Column(PostgresUUID(as_uuid=True), ForeignKey("requests.id", ondelete="CASCADE"), nullable=False, index=True)
    task_name = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False, index=True)  # running, completed, failed
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    error_details = Column(JSONB, nullable=True)