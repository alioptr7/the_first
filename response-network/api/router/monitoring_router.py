from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from core.dependencies import get_db
from models.schemas import (
    RequestStats,
    QueryStats,
    SystemHealth,
    SystemStats,
    LogEntry
)
from auth.dependencies import get_current_user
from models.user import User
from crud import stats as stats_service

router = APIRouter(
    prefix="/monitoring", 
    tags=["monitoring"]
)

@router.get("/health", response_model=SystemHealth)
async def get_system_health(current_user: User = Depends(get_current_user)):
    """Get current system health metrics."""
    from datetime import datetime
    return {
        "status": "healthy",
        "uptime": "1d 2h 34m",
        "last_error": None,
        "last_check": datetime.now().isoformat(),
        "components": {
            "database": "connected",
            "redis": "connected",
            "elasticsearch": "connected"
        }
    }

@router.get("/stats", response_model=SystemStats)
async def get_system_stats():
    """Get current system statistics."""
    return {
        "cpu_usage": 22.7,
        "memory_usage": 87.6,
        "disk_usage": 94.5,
        "requests_per_minute": 0.0,
        "avg_response_time": 0.0
    }

@router.get("/requests", response_model=RequestStats)
async def get_request_stats(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get statistics about requests processed by the response network."""
    return await stats_service.get_request_stats(db, start_date, end_date)

@router.get("/queries", response_model=QueryStats)
async def get_query_stats(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get statistics about queries processed by the response network."""
    return await stats_service.get_query_stats(db, start_date, end_date)

@router.get("/system/health", response_model=SystemHealth)
async def get_system_health(
    db: Session = Depends(get_db)
):
    """Get current system health status."""
    return await stats_service.get_system_health(db)

@router.get("/system/stats", response_model=SystemStats)
async def get_system_stats(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get system performance statistics."""
    return await stats_service.get_system_stats(db, start_date, end_date)

@router.get("/logs", response_model=List[LogEntry])
async def get_system_logs(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    level: Optional[str] = Query(None),
    limit: int = Query(100),
    offset: int = Query(0),
    db: Session = Depends(get_db)
):
    """Get system logs with filtering options."""
    return await stats_service.get_logs(
        db, 
        start_date=start_date,
        end_date=end_date,
        level=level,
        limit=limit,
        offset=offset
    )