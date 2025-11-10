import asyncio
from datetime import datetime, timedelta
import psutil

from celery import shared_task
from sqlalchemy import select, func

from core.config import settings
from core.dependencies import get_db, get_redis
from models.request import Request
from models.system_metrics import SystemMetrics

@shared_task
def collect_system_metrics():
    """Collect and store system performance metrics."""
    async def _collect():
        # Collect system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        async with get_db() as db:
            # Get request processing metrics
            last_hour = datetime.utcnow() - timedelta(hours=1)
            
            # Count requests by status in last hour
            result = await db.execute(
                select(
                    Request.status,
                    func.count(Request.id)
                )
                .where(Request.created_at >= last_hour)
                .group_by(Request.status)
            )
            request_metrics = dict(result.all())
            
            # Calculate average processing time
            result = await db.execute(
                select(func.avg(
                    Request.completed_at - Request.created_at
                ))
                .where(
                    Request.status == "completed",
                    Request.created_at >= last_hour
                )
            )
            avg_processing_time = result.scalar_one_or_none()
            
            # Store metrics
            metrics = SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_percent=disk.percent,
                requests_pending=request_metrics.get("pending", 0),
                requests_completed=request_metrics.get("completed", 0),
                requests_failed=request_metrics.get("failed", 0),
                avg_processing_time=avg_processing_time.total_seconds() if avg_processing_time else None
            )
            db.add(metrics)
            await db.commit()
            
            return "System metrics collected successfully"
    
    return asyncio.run(_collect())

@shared_task
def check_system_health():
    """Check system health and send alerts if needed."""
    async def _check():
        async with get_db() as db:
            # Get latest metrics
            result = await db.execute(
                select(SystemMetrics)
                .order_by(SystemMetrics.created_at.desc())
                .limit(1)
            )
            latest = result.scalar_one_or_none()
            
            if not latest:
                return "No metrics available"
            
            alerts = []
            
            # Check CPU usage
            if latest.cpu_percent > settings.ALERT_CPU_THRESHOLD:
                alerts.append(f"High CPU usage: {latest.cpu_percent}%")
            
            # Check memory usage
            if latest.memory_percent > settings.ALERT_MEMORY_THRESHOLD:
                alerts.append(f"High memory usage: {latest.memory_percent}%")
            
            # Check disk usage
            if latest.disk_percent > settings.ALERT_DISK_THRESHOLD:
                alerts.append(f"High disk usage: {latest.disk_percent}%")
            
            # Check request processing
            if latest.requests_failed > settings.ALERT_FAILED_REQUESTS_THRESHOLD:
                alerts.append(f"High number of failed requests: {latest.requests_failed}")
            
            if latest.avg_processing_time and latest.avg_processing_time > settings.ALERT_PROCESSING_TIME_THRESHOLD:
                alerts.append(f"Slow request processing: {latest.avg_processing_time:.2f}s average")
            
            if alerts:
                # TODO: Send alerts via configured channels (email, Slack, etc.)
                return f"Health check alerts: {'; '.join(alerts)}"
            
            return "System health check passed"
    
    return asyncio.run(_check())