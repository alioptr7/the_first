"""اسکیماهای مربوط به سیستم لاگینگ"""
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class LogEntryBase(BaseModel):
    """مدل پایه برای لاگ‌ها"""
    level: str = Field(..., description="سطح لاگ")
    message: str = Field(..., description="پیام لاگ")
    source: str = Field(..., description="منبع لاگ")
    trace_id: Optional[str] = Field(None, description="شناسه پیگیری")
    request_id: Optional[UUID] = Field(None, description="شناسه درخواست")
    user_id: Optional[UUID] = Field(None, description="شناسه کاربر")
    metadata: Optional[Dict] = Field(None, description="اطلاعات اضافی")


class LogEntryCreate(LogEntryBase):
    """مدل ایجاد لاگ"""
    pass


class LogEntryRead(LogEntryBase):
    """مدل خواندن لاگ"""
    id: UUID
    timestamp: datetime

    class Config:
        from_attributes = True


class ErrorLogBase(BaseModel):
    """مدل پایه برای لاگ خطاها"""
    error_type: str = Field(..., description="نوع خطا")
    error_message: str = Field(..., description="پیام خطا")
    stack_trace: Optional[str] = Field(None, description="جزئیات خطا")
    source: str = Field(..., description="منبع خطا")
    severity: str = Field(..., description="شدت خطا")
    status: str = Field(..., description="وضعیت خطا")
    resolution: Optional[str] = Field(None, description="راه‌حل خطا")
    request_id: Optional[UUID] = Field(None, description="شناسه درخواست")
    user_id: Optional[UUID] = Field(None, description="شناسه کاربر")
    metadata: Optional[Dict] = Field(None, description="اطلاعات اضافی")


class ErrorLogCreate(ErrorLogBase):
    """مدل ایجاد لاگ خطا"""
    pass


class ErrorLogUpdate(BaseModel):
    """مدل به‌روزرسانی لاگ خطا"""
    status: Optional[str] = Field(None, description="وضعیت جدید خطا")
    resolution: Optional[str] = Field(None, description="راه‌حل خطا")
    resolved_by: Optional[UUID] = Field(None, description="شناسه کاربر حل‌کننده")


class ErrorLogRead(ErrorLogBase):
    """مدل خواندن لاگ خطا"""
    id: UUID
    timestamp: datetime
    resolved_at: Optional[datetime]
    resolved_by: Optional[UUID]

    class Config:
        from_attributes = True


class AuditLogBase(BaseModel):
    """مدل پایه برای لاگ تغییرات"""
    action: str = Field(..., description="نوع عملیات")
    entity_type: str = Field(..., description="نوع موجودیت")
    entity_id: str = Field(..., description="شناسه موجودیت")
    user_id: Optional[UUID] = Field(None, description="شناسه کاربر")
    changes: Optional[Dict] = Field(None, description="تغییرات")
    metadata: Optional[Dict] = Field(None, description="اطلاعات اضافی")


class AuditLogCreate(AuditLogBase):
    """مدل ایجاد لاگ تغییرات"""
    pass


class AuditLogRead(AuditLogBase):
    """مدل خواندن لاگ تغییرات"""
    id: UUID
    timestamp: datetime

    class Config:
        from_attributes = True


class PerformanceLogBase(BaseModel):
    """مدل پایه برای لاگ عملکرد"""
    operation: str = Field(..., description="نوع عملیات")
    duration_ms: int = Field(..., description="مدت زمان اجرا")
    success: bool = Field(..., description="موفقیت عملیات")
    error_message: Optional[str] = Field(None, description="پیام خطا")
    request_id: Optional[UUID] = Field(None, description="شناسه درخواست")
    user_id: Optional[UUID] = Field(None, description="شناسه کاربر")
    metadata: Optional[Dict] = Field(None, description="اطلاعات اضافی")


class PerformanceLogCreate(PerformanceLogBase):
    """مدل ایجاد لاگ عملکرد"""
    pass


class PerformanceLogRead(PerformanceLogBase):
    """مدل خواندن لاگ عملکرد"""
    id: UUID
    timestamp: datetime

    class Config:
        from_attributes = True


class LogFilter(BaseModel):
    """مدل فیلتر لاگ‌ها"""
    start_time: Optional[datetime] = Field(None, description="زمان شروع")
    end_time: Optional[datetime] = Field(None, description="زمان پایان")
    level: Optional[str] = Field(None, description="سطح لاگ")
    source: Optional[str] = Field(None, description="منبع لاگ")
    user_id: Optional[UUID] = Field(None, description="شناسه کاربر")
    request_id: Optional[UUID] = Field(None, description="شناسه درخواست")


class LogSummary(BaseModel):
    """مدل خلاصه لاگ‌ها"""
    total_logs: int = Field(..., description="تعداد کل لاگ‌ها")
    error_count: int = Field(..., description="تعداد خطاها")
    warning_count: int = Field(..., description="تعداد هشدارها")
    info_count: int = Field(..., description="تعداد اطلاعات")
    debug_count: int = Field(..., description="تعداد لاگ‌های دیباگ")
    average_response_time: float = Field(..., description="میانگین زمان پاسخ")
    error_rate: float = Field(..., description="نرخ خطا")
    start_time: datetime = Field(..., description="زمان شروع")
    end_time: datetime = Field(..., description="زمان پایان")