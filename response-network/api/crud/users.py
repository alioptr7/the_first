from sqlalchemy.orm import Session
from sqlalchemy import func, and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict
from datetime import datetime, timedelta

from response_network.api.models.user import User
from response_network.api.models.request import Request
from response_network.api.models.schemas import UserCreate, UserUpdate, UserStats
from response_network.api.core.security import get_password_hash

async def get_users_with_stats(
    db: AsyncSession,
    profile_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 20
) -> List[Dict]:
    """Get list of users with their request statistics."""
    
    # Base query for users
    query = select(User)
    if profile_type:
        query = query.where(User.profile_type == profile_type)
    if is_active is not None:  # Check for None specifically since is_active is a boolean
        query = query.where(User.is_active == is_active)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    users = result.scalars().all()
    result = []
    
    for user in users:
        stats = await get_user_stats(db, user.id)
        user_dict = {
            **user.__dict__,
            'stats': stats
        }
        result.append(user_dict)
    
    return result

async def get_user_with_stats(db: AsyncSession, user_id: str) -> Optional[Dict]:
    """Get detailed user information with statistics."""
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if not user:
        return None
    
    stats = await get_user_stats(db, user_id)
    return {
        **user.__dict__,
        'stats': stats
    }

async def get_user_stats(db: AsyncSession, user_id: str) -> UserStats:
    """Calculate statistics for a specific user."""
    
    # Get base query for user's requests
    base_query = select(func.count()).select_from(Request).where(Request.user_id == user_id)
    result = await db.execute(base_query)
    total_requests = result.scalar() or 0
    
    # Calculate completed requests
    completed_query = select(func.count()).select_from(Request).where(
        Request.user_id == user_id,
        Request.status == "completed"
    )
    result = await db.execute(completed_query)
    completed_requests = result.scalar() or 0
    
    # Calculate failed requests
    failed_query = select(func.count()).select_from(Request).where(
        Request.user_id == user_id,
        Request.status == "failed"
    )
    result = await db.execute(failed_query)
    failed_requests = result.scalar() or 0
    
    # Calculate average processing time
    avg_query = select(func.avg(Request.processing_time)).select_from(Request).where(
        Request.user_id == user_id,
        Request.status.in_(["completed", "failed"])
    )
    result = await db.execute(avg_query)
    avg_time = result.scalar() or 0.0
    
    # Get today's requests
    today = datetime.utcnow().date()
    today_query = select(func.count()).select_from(Request).where(
        Request.user_id == user_id,
        func.date(Request.created_at) == today
    )
    result = await db.execute(today_query)
    requests_today = result.scalar() or 0
    
    # Get this month's requests
    month_start = today.replace(day=1)
    month_query = select(func.count()).select_from(Request).where(
        Request.user_id == user_id,
        Request.created_at >= month_start
    )
    result = await db.execute(month_query)
    requests_this_month = result.scalar() or 0
    
    return UserStats(
        total_requests=total_requests,
        completed_requests=completed_requests,
        failed_requests=failed_requests,
        avg_processing_time=float(avg_time),
        requests_today=requests_today,
        requests_this_month=requests_this_month
    )

async def create_user(db: Session, user_in: UserCreate) -> User:
    """Create a new user."""
    db_user = User(
        email=user_in.email,
        username=user_in.username,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password),
        profile_type=user_in.profile_type,
        is_active=user_in.is_active,
        requests_per_minute=user_in.requests_per_minute,
        requests_per_hour=user_in.requests_per_hour,
        requests_per_day=user_in.requests_per_day,
        total_requests_allocated=user_in.total_requests_allocated,
        remaining_requests=user_in.total_requests_allocated
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

async def update_user(db: Session, user: User, user_in: UserUpdate) -> User:
    """Update user information."""
    update_data = user_in.dict(exclude_unset=True)
    
    if update_data.get("password"):
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

async def delete_user(db: Session, user_id: int) -> None:
    """Delete a user."""
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()

async def update_user_active_status(db: AsyncSession, user_id: str, is_active: bool) -> None:
    """Update user active status."""
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    if user:
        user.is_active = is_active
        await db.commit()
    db.commit()

async def get_user(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID."""
    return db.query(User).filter(User.id == user_id).first()

async def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email."""
    return db.query(User).filter(User.email == email).first()

async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """Get user by username."""
    result = await db.execute(select(User).filter(User.username == username))
    return result.scalar_one_or_none()

async def authenticate(db: AsyncSession, username: str, password: str) -> Optional[User]:
    """Authenticate user by username and password."""
    from core.security import verify_password
    
    user = await get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user