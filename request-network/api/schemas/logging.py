"""Schemas for logging functionality"""
from datetime import datetime
from typing import Dict, Optional, List
from pydantic import BaseModel, ConfigDict


class LogEntryBase(BaseModel):
    """Base schema for all log entries"""
    service_name: str
    extra_data: Optional[Dict] = None


class LogEntryCreate(LogEntryBase):
    """Schema for creating a log entry"""
    pass


class LogEntry(LogEntryBase):
    """Schema for a log entry"""
    id: int
    timestamp: datetime
    log_type: str

    model_config = ConfigDict(from_attributes=True)


class ErrorLogBase(LogEntryBase):
    """Base schema for error logs"""
    error_type: str
    error_message: str
    stack_trace: Optional[str] = None
    severity: str
    status: str
    resolution: Optional[str] = None


class ErrorLogCreate(ErrorLogBase):
    """Schema for creating an error log"""
    pass


class ErrorLogUpdate(BaseModel):
    """Schema for updating an error log"""
    status: Optional[str] = None
    resolution: Optional[str] = None
    resolved_by: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class ErrorLog(ErrorLogBase):
    """Schema for an error log"""
    id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class AuditLogBase(LogEntryBase):
    """Base schema for audit logs"""
    user_id: int
    action: str
    resource_type: str
    resource_id: str
    status: str
    details: Optional[Dict] = None


class AuditLogCreate(AuditLogBase):
    """Schema for creating an audit log"""
    pass


class AuditLog(AuditLogBase):
    """Schema for an audit log"""
    id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class PerformanceLogBase(LogEntryBase):
    """Base schema for performance logs"""
    endpoint: str
    method: str
    response_time_ms: int
    status_code: int
    request_size_bytes: Optional[int] = None
    response_size_bytes: Optional[int] = None


class PerformanceLogCreate(PerformanceLogBase):
    """Schema for creating a performance log"""
    pass


class PerformanceLog(PerformanceLogBase):
    """Schema for a performance log"""
    id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


"""Logging schemas"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class LogFilter(BaseModel):
    """Log filter schema"""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    service_name: Optional[str] = None
    log_type: Optional[str] = None
    user_id: Optional[int] = None
    severity: Optional[str] = None
    status: Optional[str] = None


class LogResponse(BaseModel):
    """Log response schema"""
    id: int
    task_id: str
    status: str
    result: Optional[dict] = None
    error: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LogSummary(BaseModel):
    """Schema for log summary"""
    total_logs: int
    error_count: int
    warning_count: int
    average_response_time: float
    success_rate: float
    recent_errors: List[ErrorLog]

    model_config = ConfigDict(from_attributes=True)