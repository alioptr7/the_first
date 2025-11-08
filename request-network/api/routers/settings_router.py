"""Settings router"""
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.dependencies import get_current_admin_user
from ..db.session import get_db
from ..models.user import User

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/")
async def get_settings(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(get_current_admin_user)],
):
    """Get application settings"""
    return {
        "app_name": "Request Network",
        "version": "1.0.0",
        "environment": "development",
        "debug": True,
    }