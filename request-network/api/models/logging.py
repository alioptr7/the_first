"""Models for logging functionality"""
from datetime import datetime
from typing import Dict, Optional
from sqlalchemy import Column, DateTime, String, Integer, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship

from api.db.base_class import Base


class LogEntry(Base):
    """Base model for all log entries"""
    __tablename__ = "log_entries"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    log_type = Column(String, nullable=False)
    service_name = Column(String, nullable=False)
    extra_data = Column(JSON, nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "log_entry",
        "polymorphic_on": log_type
    }


class ErrorLog(LogEntry):
    """Model for error logs"""
    __tablename__ = "error_logs"

    id = Column(Integer, ForeignKey("log_entries.id"), primary_key=True)
    error_type = Column(String, nullable=False)
    error_message = Column(String, nullable=False)
    stack_trace = Column(String, nullable=True)
    severity = Column(String, nullable=False)
    status = Column(String, nullable=False)
    resolution = Column(String, nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "error"
    }


class AuditLog(LogEntry):
    """Model for audit logs"""
    __tablename__ = "audit_logs"

    id = Column(Integer, ForeignKey("log_entries.id"), primary_key=True)
    user_id = Column(Integer, nullable=False)
    action = Column(String, nullable=False)
    resource_type = Column(String, nullable=False)
    resource_id = Column(String, nullable=False)
    status = Column(String, nullable=False)
    details = Column(JSON, nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "audit"
    }


class PerformanceLog(LogEntry):
    """Model for performance logs"""
    __tablename__ = "performance_logs"

    id = Column(Integer, ForeignKey("log_entries.id"), primary_key=True)
    endpoint = Column(String, nullable=False)
    method = Column(String, nullable=False)
    response_time_ms = Column(Integer, nullable=False)
    status_code = Column(Integer, nullable=False)
    request_size_bytes = Column(Integer, nullable=True)
    response_size_bytes = Column(Integer, nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "performance"
    }