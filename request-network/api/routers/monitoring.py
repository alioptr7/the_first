"""روترهای مربوط به مانیتورینگ سیستم"""
from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth.dependencies import get_current_admin_user
from api.db.session import get_session
from api.models.monitoring import (
    SystemMetrics, ServiceHealth, ErrorLog,
    PerformanceMetrics, ResourceUsage
)
from api.schemas.monitoring import (
    SystemMetricsCreate, SystemMetricsRead,
    ServiceHealthCreate, ServiceHealthRead,
    ErrorLogCreate, ErrorLogRead,
    PerformanceMetricsCreate, PerformanceMetricsRead,
    ResourceUsageCreate, ResourceUsageRead,
    MetricsSummary, TimeRangeMetrics
)

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


@router.post("/metrics/system", response_model=SystemMetricsRead)
async def create_system_metrics(
    metrics: SystemMetricsCreate,
    current_user = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_session)
):
    """ثبت متریک‌های سیستمی جدید"""
    db_metrics = SystemMetrics(**metrics.model_dump())
    session.add(db_metrics)
    await session.commit()
    await session.refresh(db_metrics)
    return db_metrics


@router.get("/metrics/system", response_model=List[SystemMetricsRead])
async def list_system_metrics(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    metric_name: Optional[str] = None,
    metric_type: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    current_user = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_session)
):
    """دریافت لیست متریک‌های سیستمی با فیلترهای مختلف"""
    query = select(SystemMetrics)
    
    if metric_name:
        query = query.where(SystemMetrics.metric_name == metric_name)
    if metric_type:
        query = query.where(SystemMetrics.metric_type == metric_type)
    if start_time:
        query = query.where(SystemMetrics.timestamp >= start_time)
    if end_time:
        query = query.where(SystemMetrics.timestamp <= end_time)
    
    query = query.offset(skip).limit(limit)
    result = await session.execute(query)
    return result.scalars().all()


@router.post("/health", response_model=ServiceHealthRead)
async def update_service_health(
    health: ServiceHealthCreate,
    current_user = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_session)
):
    """به‌روزرسانی وضعیت سلامت یک سرویس"""
    db_health = ServiceHealth(**health.model_dump())
    session.add(db_health)
    await session.commit()
    await session.refresh(db_health)
    return db_health


@router.get("/health", response_model=List[ServiceHealthRead])
async def list_service_health(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service_name: Optional[str] = None,
    status: Optional[str] = None,
    current_user = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_session)
):
    """دریافت وضعیت سلامت سرویس‌ها"""
    query = select(ServiceHealth)
    
    if service_name:
        query = query.where(ServiceHealth.service_name == service_name)
    if status:
        query = query.where(ServiceHealth.status == status)
    
    query = query.offset(skip).limit(limit)
    result = await session.execute(query)
    return result.scalars().all()


@router.post("/errors", response_model=ErrorLogRead)
async def log_error(
    error: ErrorLogCreate,
    current_user = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_session)
):
    """ثبت یک خطای جدید"""
    db_error = ErrorLog(**error.model_dump())
    session.add(db_error)
    await session.commit()
    await session.refresh(db_error)
    return db_error


@router.get("/errors", response_model=List[ErrorLogRead])
async def list_errors(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    error_type: Optional[str] = None,
    service_name: Optional[str] = None,
    severity: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    current_user = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_session)
):
    """دریافت لیست خطاها با فیلترهای مختلف"""
    query = select(ErrorLog)
    
    if error_type:
        query = query.where(ErrorLog.error_type == error_type)
    if service_name:
        query = query.where(ErrorLog.service_name == service_name)
    if severity:
        query = query.where(ErrorLog.severity == severity)
    if start_time:
        query = query.where(ErrorLog.timestamp >= start_time)
    if end_time:
        query = query.where(ErrorLog.timestamp <= end_time)
    
    query = query.offset(skip).limit(limit)
    result = await session.execute(query)
    return result.scalars().all()


@router.get("/summary", response_model=MetricsSummary)
async def get_metrics_summary(
    current_user = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_session)
):
    """دریافت خلاصه متریک‌های سیستم"""
    # محاسبه تعداد کل درخواست‌ها
    total_requests_query = select(func.count(PerformanceMetrics.id))
    total_requests_result = await session.execute(total_requests_query)
    total_requests = total_requests_result.scalar()

    # محاسبه میانگین زمان پاسخ
    avg_response_time_query = select(func.avg(PerformanceMetrics.response_time_ms))
    avg_response_time_result = await session.execute(avg_response_time_query)
    average_response_time = avg_response_time_result.scalar() or 0.0

    # محاسبه نرخ خطا
    error_count_query = select(func.count(PerformanceMetrics.id)).where(
        PerformanceMetrics.status_code >= 400
    )
    error_count_result = await session.execute(error_count_query)
    error_count = error_count_result.scalar()
    error_rate = (error_count / total_requests * 100) if total_requests > 0 else 0.0
    success_rate = 100 - error_rate

    # دریافت آخرین وضعیت مصرف منابع
    resource_usage_query = select(ResourceUsage).order_by(
        ResourceUsage.timestamp.desc()
    ).limit(4)  # برای CPU, Memory, Disk, Network
    resource_usage_result = await session.execute(resource_usage_query)
    resource_usage = {
        ru.resource_type: ru.usage_value 
        for ru in resource_usage_result.scalars().all()
    }

    # دریافت وضعیت سلامت سرویس‌ها
    service_health_query = select(ServiceHealth).order_by(
        ServiceHealth.last_check.desc()
    )
    service_health_result = await session.execute(service_health_query)
    service_health = {
        sh.service_name: sh.status
        for sh in service_health_result.scalars().all()
    }

    return MetricsSummary(
        total_requests=total_requests,
        average_response_time=average_response_time,
        error_rate=error_rate,
        success_rate=success_rate,
        resource_usage=resource_usage,
        service_health=service_health,
        timestamp=datetime.utcnow()
    )


@router.get("/metrics/time-range", response_model=TimeRangeMetrics)
async def get_time_range_metrics(
    start_time: datetime,
    end_time: datetime,
    interval: str = Query(..., pattern="^(minute|hour|day|week|month)$"),
    metric_names: List[str] = Query(...),
    current_user = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_session)
):
    """دریافت متریک‌ها در یک بازه زمانی با فاصله زمانی مشخص"""
    if start_time >= end_time:
        raise HTTPException(status_code=400, detail="زمان شروع باید قبل از زمان پایان باشد")

    metrics = {}
    labels = {}

    for metric_name in metric_names:
        query = select(SystemMetrics).where(
            and_(
                SystemMetrics.metric_name == metric_name,
                SystemMetrics.timestamp.between(start_time, end_time)
            )
        ).order_by(SystemMetrics.timestamp)
        
        result = await session.execute(query)
        data = result.scalars().all()
        
        metrics[metric_name] = [m.metric_value for m in data]
        labels[metric_name] = [m.timestamp.isoformat() for m in data]

    return TimeRangeMetrics(
        start_time=start_time,
        end_time=end_time,
        interval=interval,
        metrics=metrics,
        labels=labels
    )