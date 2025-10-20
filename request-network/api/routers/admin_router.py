from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func, case, select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import require_admin
from db.session import get_db_session
from models.user import User
from models.request import Request
from models.batch import ExportBatch, ImportBatch
from schemas.admin import SystemStats

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(require_admin)] # این خط تمام اندپوینت‌های این روتر را محافظت می‌کند
)


@router.get("/stats", response_model=SystemStats)
async def get_system_stats(
    db: Annotated[AsyncSession, Depends(get_db_session)]
):
    """
    Retrieves overall statistics for the system.
    - User counts (total, active)
    - Request counts by status
    - Batch counts (import/export)
    """
    # 1. Get user stats
    user_stats_stmt = select(
        func.count(User.id).label("total_users"),
        func.count(case((User.is_active, 1))).label("active_users")
    )
    user_stats_result = (await db.execute(user_stats_stmt)).one()

    # 2. Get request stats
    request_stats_stmt = select(
        func.count(Request.id).label("total_requests"),
        func.count(case((Request.status == 'pending', 1))).label("pending_requests"),
        func.count(case((Request.status == 'completed', 1))).label("completed_requests"),
        func.count(case((Request.status == 'failed', 1))).label("failed_requests"),
    )
    request_stats_result = (await db.execute(request_stats_stmt)).one()

    # 3. Get batch stats
    export_batch_count = await db.scalar(select(func.count(ExportBatch.id)))
    import_batch_count = await db.scalar(select(func.count(ImportBatch.id)))

    return SystemStats(
        total_users=user_stats_result.total_users,
        active_users=user_stats_result.active_users,
        total_requests=request_stats_result.total_requests,
        pending_requests=request_stats_result.pending_requests,
        completed_requests=request_stats_result.completed_requests,
        failed_requests=request_stats_result.failed_requests,
        total_export_batches=export_batch_count or 0,
        total_import_batches=import_batch_count or 0,
    )