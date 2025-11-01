"""اسکیماهای مربوط به پنل ادمین شبکه درخواست"""
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class RequestStats(BaseModel):
    """آمار درخواست‌ها"""
    total_requests: int = Field(..., description="تعداد کل درخواست‌ها")
    pending_requests: int = Field(..., description="تعداد درخواست‌های در انتظار")
    completed_requests: int = Field(..., description="تعداد درخواست‌های تکمیل شده")
    failed_requests: int = Field(..., description="تعداد درخواست‌های ناموفق")
    average_processing_time: float = Field(..., description="میانگین زمان پردازش (ثانیه)")
    start_date: Optional[datetime] = Field(None, description="تاریخ شروع بازه زمانی")
    end_date: Optional[datetime] = Field(None, description="تاریخ پایان بازه زمانی")


class TopUser(BaseModel):
    """اطلاعات کاربر پرکار"""
    user_id: UUID
    username: str
    request_count: int


class UserStats(BaseModel):
    """آمار کاربران"""
    total_users: int = Field(..., description="تعداد کل کاربران")
    active_users: int = Field(..., description="تعداد کاربران فعال")
    top_users: List[TopUser] = Field(..., description="کاربران با بیشترین درخواست")


class SystemStats(BaseModel):
    """آمار سیستمی"""
    total_request_types: int = Field(..., description="تعداد کل انواع درخواست")
    average_response_time: float = Field(..., description="میانگین زمان پاسخ (ثانیه)")
    system_success_rate: float = Field(..., description="نرخ موفقیت سیستم (درصد)")
    last_updated: datetime = Field(..., description="آخرین به‌روزرسانی")
    total_export_batches: int = Field(..., description="تعداد کل دسته‌های صادر شده")
    total_import_batches: int = Field(..., description="تعداد کل دسته‌های وارد شده")


class RequestFilter(BaseModel):
    """فیلتر درخواست‌ها"""
    status: Optional[str] = Field(None, description="وضعیت درخواست")
    priority: Optional[str] = Field(None, description="اولویت درخواست")
    start_date: Optional[datetime] = Field(None, description="تاریخ شروع")
    end_date: Optional[datetime] = Field(None, description="تاریخ پایان")


class RequestBatchAction(BaseModel):
    """عملیات دسته‌ای روی درخواست‌ها"""
    action: str = Field(..., description="نوع عملیات (retry, cancel, prioritize, archive)")
    request_ids: Optional[List[UUID]] = Field(None, description="لیست شناسه درخواست‌ها")
    filter: Optional[RequestFilter] = Field(None, description="فیلتر درخواست‌ها")
    reason: Optional[str] = Field(None, description="دلیل انجام عملیات")


class AdminActionCreate(BaseModel):
    """ایجاد لاگ اکشن ادمین"""
    action_type: str = Field(..., description="نوع عملیات")
    target_type: str = Field(..., description="نوع هدف (request, user, system)")
    target_ids: List[UUID] = Field(..., description="شناسه‌های هدف")
    details: Optional[Dict] = Field(None, description="جزئیات اضافی")


class AdminActionLog(BaseModel):
    """لاگ اکشن‌های ادمین"""
    id: UUID
    admin_id: UUID = Field(..., description="شناسه ادمین")
    action_type: str = Field(..., description="نوع عملیات")
    target_type: str = Field(..., description="نوع هدف")
    target_ids: List[UUID] = Field(..., description="شناسه‌های هدف")
    details: Optional[Dict] = Field(None, description="جزئیات اضافی")
    created_at: datetime = Field(..., description="تاریخ ایجاد")

    class Config:
        from_attributes = True