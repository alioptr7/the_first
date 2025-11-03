"""مدل‌های مربوط به مانیتورینگ سیستم"""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, DateTime, ForeignKey, Float, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.db.base_class import Base


class SystemMetrics(Base):
    """مدل برای ذخیره متریک‌های سیستمی"""
    __tablename__ = "system_metrics"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False)
    metric_value: Mapped[float] = mapped_column(Float, nullable=False)
    metric_type: Mapped[str] = mapped_column(String(50), nullable=False)  # gauge, counter, histogram
    labels: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    def __repr__(self):
        return f"<SystemMetrics(metric_name={self.metric_name}, value={self.metric_value})>"


class ServiceHealth(Base):
    """مدل برای ذخیره وضعیت سلامت سرویس‌ها"""
    __tablename__ = "service_health"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service_name: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)  # up, down, degraded
    last_check: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    response_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_message: Mapped[str | None] = mapped_column(String, nullable=True)
    additional_info: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    def __repr__(self):
        return f"<ServiceHealth(service={self.service_name}, status={self.status})>"


class ErrorLog(Base):
    """مدل برای ذخیره لاگ خطاها"""
    __tablename__ = "error_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    error_type: Mapped[str] = mapped_column(String(100), nullable=False)
    error_message: Mapped[str] = mapped_column(String, nullable=False)
    stack_trace: Mapped[str | None] = mapped_column(String, nullable=True)
    service_name: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[str] = mapped_column(String(50), nullable=False)  # critical, error, warning
    context: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    def __repr__(self):
        return f"<ErrorLog(type={self.error_type}, service={self.service_name})>"


class PerformanceMetrics(Base):
    """مدل برای ذخیره متریک‌های عملکردی"""
    __tablename__ = "performance_metrics"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    endpoint: Mapped[str] = mapped_column(String(200), nullable=False)
    method: Mapped[str] = mapped_column(String(10), nullable=False)
    response_time_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    status_code: Mapped[int] = mapped_column(Integer, nullable=False)
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    request_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    additional_info: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    def __repr__(self):
        return f"<PerformanceMetrics(endpoint={self.endpoint}, response_time={self.response_time_ms}ms)>"


class ResourceUsage(Base):
    """مدل برای ذخیره اطلاعات مصرف منابع"""
    __tablename__ = "resource_usage"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False)  # cpu, memory, disk, network
    usage_value: Mapped[float] = mapped_column(Float, nullable=False)
    usage_unit: Mapped[str] = mapped_column(String(20), nullable=False)  # %, MB, GB, etc.
    host: Mapped[str] = mapped_column(String(100), nullable=False)
    service_name: Mapped[str] = mapped_column(String(100), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    def __repr__(self):
        return f"<ResourceUsage(type={self.resource_type}, value={self.usage_value}{self.usage_unit})>"