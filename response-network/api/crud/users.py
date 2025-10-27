from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional, Dict
from datetime import datetime, timedelta

from models.user import User
from models.request import Request
from models.schemas import UserCreate, UserUpdate, UserStats
from core.security import get_password_hash

async def get_users_with_stats(
    db: Session,
    role: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 20
) -> List[Dict]:
    """Get list of users with their request statistics."""
    
    # Base query for users
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    if status:
        query = query.filter(User.status == status)
    
    users = query.offset(skip).limit(limit).all()
    result = []
    
    for user in users:
        stats = await get_user_stats(db, user.id)
        user_dict = {
            **user.__dict__,
            'stats': stats
        }
        result.append(user_dict)
    
    return result

async def get_user_with_stats(db: Session, user_id: int) -> Optional[Dict]:
    """Get detailed user information with statistics."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    
    stats = await get_user_stats(db, user_id)
    return {
        **user.__dict__,
        'stats': stats
    }

async def get_user_stats(db: Session, user_id: int) -> UserStats:
    """Calculate statistics for a specific user."""
    
    # Get base query for user's requests
    base_query = db.query(Request).filter(Request.user_id == user_id)
    
    # Calculate total requests and their statuses
    total_requests = base_query.count()
    completed_requests = base_query.filter(Request.status == "completed").count()
    failed_requests = base_query.filter(Request.status == "failed").count()
    
    # Calculate average processing time
    avg_time = db.query(func.avg(Request.processing_time))\
        .filter(
            Request.user_id == user_id,
            Request.status.in_(["completed", "failed"])
        ).scalar() or 0.0
    
    # Get today's requests
    today = datetime.utcnow().date()
    requests_today = base_query.filter(
        func.date(Request.created_at) == today
    ).count()
    
    # Get this month's requests
    month_start = today.replace(day=1)
    requests_this_month = base_query.filter(
        Request.created_at >= month_start
    ).count()
    
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
        role=user_in.role,
        status=user_in.status,
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

async def update_user_status(db: Session, user_id: int, status: str) -> None:
    """Update user status."""
    db.query(User).filter(User.id == user_id).update({"status": status})
    db.commit()

async def get_user(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID."""
    return db.query(User).filter(User.id == user_id).first()

async def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email."""
    return db.query(User).filter(User.email == email).first()

async def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username."""
    return db.query(User).filter(User.username == username).first()

async def authenticate(db: Session, username: str, password: str) -> Optional[User]:
    """Authenticate user by username and password."""
    from core.security import verify_password
    
    user = await get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user