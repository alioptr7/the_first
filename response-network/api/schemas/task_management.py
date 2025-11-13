"""
Schemas for Celery task management
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime


class TaskInfo(BaseModel):
    """اطلاعات یک Task"""
    task_id: str
    name: str
    state: str  # PENDING, RECEIVED, STARTED, SUCCESS, FAILURE, RETRY, REVOKED
    args: Optional[List[Any]] = None
    kwargs: Optional[Dict[str, Any]] = None
    worker: Optional[str] = None
    timestamp: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class QueueStats(BaseModel):
    """آمار Queue"""
    total_queued: int
    total_active: int
    active_workers: int
    details: List[TaskInfo]


class TaskAction(BaseModel):
    """پاسخ برای اقدام روی Task"""
    task_id: str
    action: str  # skip, delete, retry
    status: str  # success, error
    message: str


class WorkerStats(BaseModel):
    """آمار Worker"""
    worker_name: str
    pool_type: str
    max_concurrency: int
    active_tasks: int
    processed_tasks: int
    offline: bool
