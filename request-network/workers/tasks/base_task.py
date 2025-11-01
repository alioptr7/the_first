"""
ماژول کلاس پایه Task که قابلیت logging را فراهم می‌کند.
این کلاس به عنوان کلاس پایه برای تمام تسک‌های سیستم استفاده می‌شود.
"""
import logging
import time
import traceback
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from api.db.session import async_session
from api.models.request import Request
from api.models.task_log import TaskLog


class BaseTask(ABC):
    """کلاس پایه برای تمام تسک‌های سیستم با قابلیت logging"""

    def __init__(self, request_id: UUID, task_name: str):
        """
        مقداردهی اولیه تسک
        
        Args:
            request_id: شناسه درخواست مرتبط با تسک
            task_name: نام تسک برای لاگ کردن
        """
        self.request_id = request_id
        self.task_name = task_name
        self.logger = logging.getLogger(f"task.{task_name}")
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None

    async def __aenter__(self) -> 'BaseTask':
        """شروع context manager برای مدیریت session دیتابیس"""
        self.db_session = async_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """پایان context manager و بستن session دیتابیس"""
        await self.db_session.close()

    @abstractmethod
    async def execute(self, *args: Any, **kwargs: Any) -> Any:
        """
        متد اصلی اجرای تسک که باید در کلاس‌های فرزند پیاده‌سازی شود
        
        Args:
            *args: پارامترهای positional
            **kwargs: پارامترهای keyword
            
        Returns:
            نتیجه اجرای تسک
        """
        pass

    async def run(self, *args: Any, **kwargs: Any) -> Any:
        """
        اجرای تسک با logging
        
        Args:
            *args: پارامترهای positional برای متد execute
            **kwargs: پارامترهای keyword برای متد execute
            
        Returns:
            نتیجه اجرای تسک
        """
        self.start_time = time.time()
        
        try:
            # لاگ شروع تسک
            await self._log_task_start()
            
            # اجرای تسک
            result = await self.execute(*args, **kwargs)
            
            # لاگ پایان موفق تسک
            self.end_time = time.time()
            await self._log_task_end(success=True)
            
            return result
            
        except Exception as e:
            # لاگ خطا
            self.end_time = time.time()
            error_details = {
                'error_type': type(e).__name__,
                'error_message': str(e),
                'traceback': traceback.format_exc()
            }
            await self._log_task_end(success=False, error_details=error_details)
            
            # لاگ خطا در logger سیستم
            self.logger.error(
                f"Error in task {self.task_name} for request {self.request_id}: {str(e)}",
                exc_info=True
            )
            
            # انتشار مجدد خطا
            raise

    async def _log_task_start(self) -> None:
        """ثبت لاگ شروع تسک در دیتابیس"""
        async with self.db_session.begin():
            # بررسی وضعیت درخواست
            request = await self.db_session.get(Request, self.request_id)
            if not request:
                self.logger.warning(f"Request {self.request_id} not found for task {self.task_name}")
                return

            # ایجاد لاگ شروع تسک
            task_log = TaskLog(
                request_id=self.request_id,
                task_name=self.task_name,
                status='started',
                start_time=datetime.fromtimestamp(self.start_time, timezone.utc)
            )
            self.db_session.add(task_log)

    async def _log_task_end(self, success: bool, error_details: Optional[Dict] = None) -> None:
        """
        ثبت لاگ پایان تسک در دیتابیس
        
        Args:
            success: آیا تسک با موفقیت اجرا شده است
            error_details: جزئیات خطا در صورت وجود
        """
        async with self.db_session.begin():
            # بررسی وضعیت درخواست
            request = await self.db_session.get(Request, self.request_id)
            if not request:
                self.logger.warning(f"Request {self.request_id} not found for task {self.task_name}")
                return

            # محاسبه زمان اجرا
            execution_time = int((self.end_time - self.start_time) * 1000)  # تبدیل به میلی‌ثانیه

            # ایجاد لاگ پایان تسک
            task_log = TaskLog(
                request_id=self.request_id,
                task_name=self.task_name,
                status='completed' if success else 'failed',
                start_time=datetime.fromtimestamp(self.start_time, timezone.utc),
                end_time=datetime.fromtimestamp(self.end_time, timezone.utc),
                execution_time_ms=execution_time,
                error_details=error_details
            )
            self.db_session.add(task_log)

            # به‌روزرسانی وضعیت درخواست در صورت خطا
            if not success:
                request.status = 'failed'
                request.error_details = error_details