"""
ماژول مدل TaskLog برای ذخیره لاگ‌های تسک‌ها در دیتابیس
"""
import uuid
from datetime import datetime
from typing import Dict, Optional

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from api.db.base_class import Base


class TaskLog(Base):
    """مدل لاگ تسک‌ها"""
    
    __tablename__ = "task_logs"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    request_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    task_name: Mapped[str] = mapped_column(
        String,
        nullable=False,
        index=True
    )
    status: Mapped[str] = mapped_column(
        String,
        nullable=False,
        index=True
    )
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
    end_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    execution_time_ms: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )
    error_details: Mapped[Optional[Dict]] = mapped_column(
        JSON,
        nullable=True
    )

    def __repr__(self) -> str:
        """نمایش رشته‌ای مدل"""
        return (
            f"TaskLog(id={self.id}, request_id={self.request_id}, "
            f"task_name={self.task_name}, status={self.status})"
        )