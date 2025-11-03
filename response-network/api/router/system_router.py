from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime, timedelta

from db.session import get_db_session as get_db
from models.schemas import SystemStats, SystemHealth, LogEntry
from models.user import User
from auth.dependencies import get_current_user, get_current_admin_user
from crud import system as system_service

router = APIRouter(prefix="/api", tags=["system"])

@router.get("/stats", response_model=SystemStats)
async def get_system_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current system statistics including resource usage and performance metrics.
    """
    return await system_service.get_system_stats(db)

from datetime import datetime
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends
from core.elasticsearch_client import ElasticsearchClient
from db.session import get_db_session as get_db
from models.system import SystemHealth
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["system"])

@router.get("/health", response_model=SystemHealth, dependencies=[])  # Empty dependencies to override the global security
async def get_system_health(
    db: AsyncSession = Depends(get_db)
):
    """
    Get basic health status of the system. This endpoint is public and does not require authentication.
    Used by monitoring services and load balancers.
    """
    try:
        # بررسی اتصال به پایگاه داده
        await db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        db_status = "down"

    # بررسی اتصال به Elasticsearch
    es_client = ElasticsearchClient()
    try:
        if await es_client.check_health():
            es_status = "healthy"
        else:
            es_status = "down"
    except Exception as e:
        logger.error(f"Elasticsearch health check failed: {str(e)}")
        es_status = "down"
    finally:
        await es_client.close_connection()

    # تعیین وضعیت کلی سیستم
    overall_status = "down" if "down" in [db_status, es_status] else "healthy"

    return SystemHealth(
        status=overall_status,
        components={
            "database": db_status,
            "elasticsearch": es_status
        },
        components_stats={
            "database": {"status": db_status},
            "elasticsearch": {"status": es_status}
        },
        last_check=datetime.utcnow()
    )

@router.get("/system/health/detailed", response_model=SystemHealth)
async def get_detailed_system_health(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)  # Only admins can see detailed health
):
    """
    Get detailed health status of all system components including sensitive information.
    Requires authentication and admin privileges.
    """
    return await system_service.get_system_health(db, detailed=True)

@router.get("/system/logs", response_model=List[LogEntry])
async def get_system_logs(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    level: Optional[str] = Query(None, enum=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']),
    limit: int = Query(100, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get system logs with filtering options. Only accessible by admin users.
    """
    if not start_date:
        start_date = datetime.utcnow() - timedelta(hours=24)
    if not end_date:
        end_date = datetime.utcnow()

    return await system_service.get_logs(
        db,
        start_date=start_date,
        end_date=end_date,
        level=level,
        limit=limit
    )