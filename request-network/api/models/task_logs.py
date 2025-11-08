"""Task logs model"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Integer, String, JSON
from sqlalchemy.orm import relationship

from api.db.base_class import Base, TimestampMixin


class TaskLog(Base, TimestampMixin):
    """Task log model"""
    __tablename__ = "task_logs"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, nullable=False)
    status = Column(String, nullable=False)
    result = Column(JSON, nullable=True)
    error = Column(String, nullable=True)
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<TaskLog(id={self.id}, task_id='{self.task_id}', status='{self.status}')>"