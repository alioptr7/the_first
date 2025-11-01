from uuid import UUID
import asyncio

from .base_task import BaseTask


class SampleTask(BaseTask):
    """یک نمونه تسک برای نمایش نحوه استفاده از BaseTask"""

    def __init__(self, request_id: UUID):
        super().__init__(request_id, task_name="sample_task")
        
    async def run(self):
        """اجرای تسک نمونه"""
        # شبیه‌سازی یک عملیات زمان‌بر
        await asyncio.sleep(2)
        
        # می‌توانید اینجا هر عملیاتی که نیاز دارید انجام دهید
        result = {"message": "Task completed successfully"}
        
        return result


async def run_sample_task(request_id: UUID):
    """تابع کمکی برای اجرای تسک نمونه"""
    async with SampleTask(request_id) as task:
        result = await task.run()
    return result