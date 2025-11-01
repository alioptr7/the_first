"""روترهای مربوط به پنل ادمین شبکه درخواست"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy import select, update, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth.dependencies import get_current_admin_user
from api.db.session import get_session
from api.models.request import Request
from api.models.request_type import RequestType
from api.models.user import User
from api.schemas.admin import (
    RequestStats, UserStats, SystemStats,
    RequestBatchAction, RequestFilter,
    AdminActionLog, AdminActionCreate
)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats/requests", response_model=RequestStats)
async def get_request_stats(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_session)
):
    """دریافت آمار درخواست‌ها"""
    query = select(Request)
    if start_date:
        query = query.where(Request.created_at >= start_date)
    if end_date:
        query = query.where(Request.created_at <= end_date)

    result = await session.execute(query)
    requests = result.scalars().all()

    total_requests = len(requests)
    pending_requests = sum(1 for r in requests if r.status == "pending")
    completed_requests = sum(1 for r in requests if r.status == "completed")
    failed_requests = sum(1 for r in requests if r.status == "failed")
    
    # محاسبه میانگین زمان پردازش
    processing_times = []
    for req in requests:
        if req.result_received_at and req.created_at:
            processing_time = (req.result_received_at - req.created_at).total_seconds()
            processing_times.append(processing_time)
    
    avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0

    return RequestStats(
        total_requests=total_requests,
        pending_requests=pending_requests,
        completed_requests=completed_requests,
        failed_requests=failed_requests,
        average_processing_time=avg_processing_time,
        start_date=start_date,
        end_date=end_date
    )


@router.get("/stats/users", response_model=UserStats)
async def get_user_stats(
    current_user = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_session)
):
    """دریافت آمار کاربران"""
    # تعداد کل کاربران
    total_users_query = select(func.count(User.id))
    total_users_result = await session.execute(total_users_query)
    total_users = total_users_result.scalar()

    # تعداد کاربران فعال (با حداقل یک درخواست در 30 روز گذشته)
    active_users_query = select(func.count(User.id)).where(
        User.last_login_at >= datetime.utcnow() - timedelta(days=30)
    )
    active_users_result = await session.execute(active_users_query)
    active_users = active_users_result.scalar()

    # کاربران با بیشترین درخواست
    top_users_query = select(
        User.id,
        User.username,
        func.count(Request.id).label("request_count")
    ).join(Request).group_by(User.id).order_by(
        func.count(Request.id).desc()
    ).limit(10)
    
    top_users_result = await session.execute(top_users_query)
    top_users = [{
        "user_id": row.id,
        "username": row.username,
        "request_count": row.request_count
    } for row in top_users_result]

    return UserStats(
        total_users=total_users,
        active_users=active_users,
        top_users=top_users
    )


@router.get("/stats/system", response_model=SystemStats)
async def get_system_stats(
    current_user = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_session)
):
    """دریافت آمار سیستمی"""
    # تعداد انواع درخواست
    request_types_query = select(func.count(RequestType.id))
    request_types_result = await session.execute(request_types_query)
    total_request_types = request_types_result.scalar()

    # میانگین زمان پاسخ کل سیستم
    avg_response_time_query = select(
        func.avg(Request.result_received_at - Request.created_at)
    ).where(
        Request.result_received_at.is_not(None)
    )
    avg_response_time_result = await session.execute(avg_response_time_query)
    avg_response_time = avg_response_time_result.scalar()

    # نرخ موفقیت سیستم
    success_rate_query = select(
        func.count(Request.id).filter(Request.status == "completed").label("completed"),
        func.count(Request.id).label("total")
    )
    success_rate_result = await session.execute(success_rate_query)
    completed, total = success_rate_result.first()
    success_rate = (completed / total * 100) if total > 0 else 0

    return SystemStats(
        total_request_types=total_request_types,
        average_response_time=float(avg_response_time.total_seconds()) if avg_response_time else 0,
        system_success_rate=success_rate,
        last_updated=datetime.utcnow()
    )


@router.post("/requests/batch", response_model=List[UUID])
async def batch_request_action(
    action: RequestBatchAction,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_session)
):
    """اجرای عملیات دسته‌ای روی درخواست‌ها"""
    if not action.request_ids and not action.filter:
        raise HTTPException(
            status_code=400,
            detail="باید حداقل یک شناسه درخواست یا فیلتر مشخص شود"
        )

    # ساخت کوئری بر اساس فیلترها یا شناسه‌های درخواست
    query = select(Request)
    if action.request_ids:
        query = query.where(Request.id.in_(action.request_ids))
    elif action.filter:
        if action.filter.status:
            query = query.where(Request.status == action.filter.status)
        if action.filter.priority:
            query = query.where(Request.priority == action.filter.priority)
        if action.filter.start_date:
            query = query.where(Request.created_at >= action.filter.start_date)
        if action.filter.end_date:
            query = query.where(Request.created_at <= action.filter.end_date)

    result = await session.execute(query)
    requests = result.scalars().all()
    
    if not requests:
        raise HTTPException(
            status_code=404,
            detail="هیچ درخواستی با معیارهای مشخص شده یافت نشد"
        )

    # اجرای عملیات مورد نظر
    update_data = {}
    if action.action == "retry":
        update_data = {
            "status": "pending",
            "retry_count": Request.retry_count + 1,
            "error_message": None
        }
    elif action.action == "cancel":
        update_data = {
            "status": "cancelled",
            "error_message": "لغو شده توسط ادمین"
        }
    elif action.action == "prioritize":
        update_data = {"priority": "high"}
    elif action.action == "archive":
        update_data = {"is_archived": True}

    # به‌روزرسانی درخواست‌ها
    request_ids = [r.id for r in requests]
    update_stmt = (
        update(Request)
        .where(Request.id.in_(request_ids))
        .values(**update_data)
    )
    await session.execute(update_stmt)
    
    # ثبت اکشن ادمین
    admin_action = AdminActionLog(
        admin_id=current_user.id,
        action_type=action.action,
        target_type="request",
        target_ids=request_ids,
        details=action.model_dump_json()
    )
    session.add(admin_action)
    
    await session.commit()
    
    # اگر عملیات retry است، تسک‌های پردازش مجدد را در پس‌زمینه اضافه می‌کنیم
    if action.action == "retry":
        for request_id in request_ids:
            background_tasks.add_task(reprocess_request, request_id)

    return request_ids


@router.post("/action-log", response_model=AdminActionLog)
async def log_admin_action(
    action: AdminActionCreate,
    current_user = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_session)
):
    """ثبت اکشن‌های ادمین"""
    db_action = AdminActionLog(
        admin_id=current_user.id,
        action_type=action.action_type,
        target_type=action.target_type,
        target_ids=action.target_ids,
        details=action.details
    )
    session.add(db_action)
    await session.commit()
    await session.refresh(db_action)
    return db_action


@router.get("/action-log", response_model=List[AdminActionLog])
async def get_admin_actions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    action_type: Optional[str] = None,
    target_type: Optional[str] = None,
    admin_id: Optional[UUID] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_session)
):
    """دریافت لاگ اکشن‌های ادمین"""
    query = select(AdminActionLog)
    
    if action_type:
        query = query.where(AdminActionLog.action_type == action_type)
    if target_type:
        query = query.where(AdminActionLog.target_type == target_type)
    if admin_id:
        query = query.where(AdminActionLog.admin_id == admin_id)
    if start_date:
        query = query.where(AdminActionLog.created_at >= start_date)
    if end_date:
        query = query.where(AdminActionLog.created_at <= end_date)
    
    query = query.order_by(AdminActionLog.created_at.desc()).offset(skip).limit(limit)
    result = await session.execute(query)
    return result.scalars().all()


async def reprocess_request(request_id: UUID):
    """پردازش مجدد یک درخواست در پس‌زمینه"""
    # TODO: پیاده‌سازی منطق پردازش مجدد درخواست
    pass