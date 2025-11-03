import pytest
from uuid import uuid4
from datetime import datetime

from api.tasks.base_task import BaseTask
from api.models.task_logs import TaskLogs


class TestTask(BaseTask):
    """تسک نمونه برای تست"""
    
    def __init__(self, request_id, should_fail=False):
        super().__init__(request_id, task_name="test_task")
        self.should_fail = should_fail
        
    async def run(self):
        if self.should_fail:
            raise ValueError("Task failed intentionally")
        return {"status": "success"}


@pytest.mark.asyncio
async def test_successful_task(db_session: AsyncSession):
    """تست اجرای موفق تسک"""
    request_id = uuid4()
    
    async with TestTask(request_id) as task:
        result = await task.run()
        
    assert result == {"status": "success"}
    
    # بررسی لاگ‌های ثبت شده
    logs = await db_session.query(TaskLogs).filter_by(request_id=request_id).all()
    assert len(logs) == 2  # یک لاگ برای شروع و یک لاگ برای پایان
    
    start_log = next(log for log in logs if log.status == "running")
    end_log = next(log for log in logs if log.status == "completed")
    
    assert start_log.task_name == "test_task"
    assert start_log.start_time is not None
    assert start_log.end_time is None
    
    assert end_log.task_name == "test_task"
    assert end_log.start_time is not None
    assert end_log.end_time is not None
    assert end_log.execution_time_ms >= 0
    assert end_log.error_details is None


@pytest.mark.asyncio
async def test_failed_task(db_session):
    """تست اجرای ناموفق تسک"""
    request_id = uuid4()
    
    with pytest.raises(ValueError, match="Task failed intentionally"):
        async with TestTask(request_id, should_fail=True) as task:
            await task.run()
    
    # بررسی لاگ‌های ثبت شده
    logs = await db_session.query(TaskLogs).filter_by(request_id=request_id).all()
    assert len(logs) == 2  # یک لاگ برای شروع و یک لاگ برای پایان
    
    start_log = next(log for log in logs if log.status == "running")
    end_log = next(log for log in logs if log.status == "failed")
    
    assert start_log.task_name == "test_task"
    assert start_log.start_time is not None
    assert start_log.end_time is None
    
    assert end_log.task_name == "test_task"
    assert end_log.start_time is not None
    assert end_log.end_time is not None
    assert end_log.execution_time_ms >= 0
    assert end_log.error_details is not None
    assert end_log.error_details["error_type"] == "ValueError"
    assert end_log.error_details["error_message"] == "Task failed intentionally"