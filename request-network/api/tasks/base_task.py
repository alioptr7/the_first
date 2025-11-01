from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID

from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from api.db.session import async_session
from api.models.task_logs import TaskLogs


class BaseTask:
    """کلاس پایه برای همه تسک‌ها با قابلیت لاگ کردن"""

    def __init__(self, request_id: UUID, task_name: str):
        """
        Args:
            request_id: شناسه درخواست مرتبط با این تسک
            task_name: نام تسک
        """
        self.request_id = request_id
        self.task_name = task_name
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.error_details: Optional[Dict[str, Any]] = None
        self.db: Optional[AsyncSession] = None

    async def __aenter__(self):
        """شروع تسک و ثبت لاگ شروع"""
        self.start_time = datetime.now()
        self.db = async_session()
        await self._log_start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """پایان تسک و ثبت لاگ پایان"""
        self.end_time = datetime.now()
        if exc_type is not None:
            # اگر خطایی رخ داده باشد
            self.error_details = {
                "error_type": exc_type.__name__,
                "error_message": str(exc_val),
                "traceback": str(exc_tb)
            }
            await self._log_end("failed")
        else:
            await self._log_end("completed")
        
        if self.db:
            await self.db.close()

    async def _log_start(self):
        """ثبت لاگ شروع تسک"""
        query = insert(TaskLogs).values(
            request_id=self.request_id,
            task_name=self.task_name,
            status="running",
            start_time=self.start_time
        )
        await self.db.execute(query)
        await self.db.commit()

    async def _log_end(self, status: str):
        """ثبت لاگ پایان تسک
        
        Args:
            status: وضعیت نهایی تسک (completed یا failed)
        """
        execution_time = int((self.end_time - self.start_time).total_seconds() * 1000)
        query = insert(TaskLogs).values(
            request_id=self.request_id,
            task_name=self.task_name,
            status=status,
            start_time=self.start_time,
            end_time=self.end_time,
            execution_time_ms=execution_time,
            error_details=self.error_details
        )
        await self.db.execute(query)
        await self.db.commit()

    async def run(self):
        """
        متد اصلی که باید توسط کلاس‌های فرزند پیاده‌سازی شود
        """
        raise NotImplementedError("Subclasses must implement run()")