"""اسکیماهای مربوط به مانیتورینگ سیستم"""
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, constr


class SystemMetricsBase(BaseModel):
    metric_name: str = Field(..., min_length=1, max_length=100)
    metric_value: float
    metric_type: str = Field(..., pattern="^(gauge|counter|histogram)$")
    labels: Optional[Dict[str, Any]] = None


class SystemMetricsCreate(SystemMetricsBase):
    pass


class SystemMetricsRead(SystemMetricsBase):
    id: UUID
    timestamp: datetime

    class Config:
        from_attributes = True


class ServiceHealthBase(BaseModel):
    service_name: str = Field(..., min_length=1, max_length=100)
    status: str = Field(..., pattern="^(up|down|degraded)$")
    response_time_ms: Optional[int] = None
    error_message: Optional[str] = None
    additional_info: Optional[Dict[str, Any]] = None


class ServiceHealthCreate(ServiceHealthBase):
    pass


class ServiceHealthRead(ServiceHealthBase):
    id: UUID
    last_check: datetime

    class Config:
        from_attributes = True


class ErrorLogBase(BaseModel):
    error_type: str = Field(..., min_length=1, max_length=100)
    error_message: str
    stack_trace: Optional[str] = None
    service_name: str = Field(..., min_length=1, max_length=100)
    severity: str = Field(..., pattern="^(critical|error|warning)$")
    context: Optional[Dict[str, Any]] = None


class ErrorLogCreate(ErrorLogBase):
    pass


class ErrorLogRead(ErrorLogBase):
    id: UUID
    timestamp: datetime

    class Config:
        from_attributes = True


class PerformanceMetricsBase(BaseModel):
    endpoint: str = Field(..., min_length=1, max_length=200)
    method: str = Field(..., pattern="^(GET|POST|PUT|DELETE|PATCH)$")
    response_time_ms: int = Field(..., gt=0)
    status_code: int
    user_id: Optional[UUID] = None
    request_id: Optional[UUID] = None
    additional_info: Optional[Dict[str, Any]] = None


class PerformanceMetricsCreate(PerformanceMetricsBase):
    pass


class PerformanceMetricsRead(PerformanceMetricsBase):
    id: UUID
    timestamp: datetime

    class Config:
        from_attributes = True


class ResourceUsageBase(BaseModel):
    resource_type: str = Field(..., pattern="^(cpu|memory|disk|network)$")
    usage_value: float = Field(..., ge=0)
    usage_unit: str = Field(..., min_length=1, max_length=20)
    host: str = Field(..., min_length=1, max_length=100)
    service_name: str = Field(..., min_length=1, max_length=100)


class ResourceUsageCreate(ResourceUsageBase):
    pass


class ResourceUsageRead(ResourceUsageBase):
    id: UUID
    timestamp: datetime

    class Config:
        from_attributes = True


# اسکیماهای مربوط به گزارش‌گیری
class MetricsSummary(BaseModel):
    total_requests: int
    average_response_time: float
    error_rate: float
    success_rate: float
    resource_usage: Dict[str, float]
    service_health: Dict[str, str]
    timestamp: datetime


class TimeRangeMetrics(BaseModel):
    start_time: datetime
    end_time: datetime
    interval: str = Field(..., pattern="^(minute|hour|day|week|month)$")
    metrics: Dict[str, list[float]]
    labels: Dict[str, list[str]]