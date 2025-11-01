"""مدل‌های مربوط به سیستم لاگینگ"""
from datetime import datetime
import uuid
from typing import Dict, Optional

from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Integer, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from api.db.base_class import Base


class LogLevel(str, Enum):
    """سطوح مختلف لاگ"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class LogEntry(Base):
    """مدل ثبت لاگ‌ها"""
    __tablename__ = "log_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    level = Column(String(10), nullable=False)
    message = Column(String, nullable=False)
    source = Column(String(100), nullable=False)  # نام سرویس یا ماژول
    trace_id = Column(String(100), nullable=True)  # شناسه پیگیری
    request_id = Column(UUID(as_uuid=True), ForeignKey("requests.id"), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    metadata = Column(JSON, nullable=True)  # اطلاعات اضافی به صورت JSON

    # روابط
    request = relationship("Request", back_populates="logs")
    user = relationship("User", back_populates="logs")

    def __repr__(self):
        return f"<LogEntry(id={self.id}, level={self.level}, source={self.source})>"


class ErrorLog(Base):
    """مدل ثبت خطاها"""
    __tablename__ = "error_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    error_type = Column(String(100), nullable=False)
    error_message = Column(String, nullable=False)
    stack_trace = Column(String, nullable=True)
    source = Column(String(100), nullable=False)
    severity = Column(String(20), nullable=False)  # critical, high, medium, low
    status = Column(String(20), nullable=False, default="open")  # open, in_progress, resolved
    resolution = Column(String, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    request_id = Column(UUID(as_uuid=True), ForeignKey("requests.id"), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    metadata = Column(JSON, nullable=True)

    # روابط
    request = relationship("Request", back_populates="error_logs")
    user = relationship("User", back_populates="error_logs")
    resolver = relationship("User", foreign_keys=[resolved_by])

    def __repr__(self):
        return f"<ErrorLog(id={self.id}, error_type={self.error_type}, severity={self.severity})>"


class AuditLog(Base):
    """مدل ثبت تغییرات و رویدادهای مهم"""
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    action = Column(String(100), nullable=False)  # نوع عملیات (create, update, delete, etc.)
    entity_type = Column(String(100), nullable=False)  # نوع موجودیت (user, request, etc.)
    entity_id = Column(String, nullable=False)  # شناسه موجودیت
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    changes = Column(JSON, nullable=True)  # تغییرات به صورت JSON
    metadata = Column(JSON, nullable=True)

    # روابط
    user = relationship("User", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, entity_type={self.entity_type})>"


class PerformanceLog(Base):
    """مدل ثبت متریک‌های عملکردی"""
    __tablename__ = "performance_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    operation = Column(String(100), nullable=False)  # نوع عملیات
    duration_ms = Column(Integer, nullable=False)  # مدت زمان اجرا به میلی‌ثانیه
    success = Column(Boolean, nullable=False, default=True)
    error_message = Column(String, nullable=True)
    request_id = Column(UUID(as_uuid=True), ForeignKey("requests.id"), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    metadata = Column(JSON, nullable=True)

    # روابط
    request = relationship("Request", back_populates="performance_logs")
    user = relationship("User", back_populates="performance_logs")

    def __repr__(self):
        return f"<PerformanceLog(id={self.id}, operation={self.operation}, duration_ms={self.duration_ms})>"