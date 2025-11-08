from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from typing import Optional, Annotated
from datetime import datetime
import json

from response_network.api.core.config import settings
from response_network.api.core.dependencies import get_db
from response_network.api.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """Get current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("user_id")  # Changed from "sub" to "user_id"
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Using async SQLAlchemy
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current authenticated user that is active."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def check_user_limits(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Check user request limits and return the user if within limits."""
    # Get current time for calculations
    now = datetime.utcnow()
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Count requests for today
    result = await db.execute(
        text("""
        SELECT COUNT(*) 
        FROM requests 
        WHERE user_id = :user_id 
        AND created_at >= :start_date
        """),
        {"user_id": str(current_user.id), "start_date": start_of_day}
    )
    daily_count = result.scalar()
    
    if daily_count >= current_user.daily_request_limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Daily request limit exceeded"
        )

    # Count requests for this month
    result = await db.execute(
        text("""
        SELECT COUNT(*) 
        FROM requests 
        WHERE user_id = :user_id 
        AND created_at >= :start_date
        """),
        {"user_id": str(current_user.id), "start_date": start_of_month}
    )
    monthly_count = result.scalar()
    
    if monthly_count >= current_user.monthly_request_limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Monthly request limit exceeded"
        )
    
    return current_user

def check_index_access(indices: list[str]):
    """Create a dependency that checks if user has access to requested indices."""
    async def index_access_checker(
        current_user: Annotated[User, Depends(get_current_user)]
    ):
        # Parse allowed indices from JSON string
        allowed_indices = json.loads(current_user.allowed_indices)
        
        # Check if user has access to all requested indices
        unauthorized_indices = [
            idx for idx in indices 
            if idx not in allowed_indices
        ]
        
        if unauthorized_indices:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied to indices: {', '.join(unauthorized_indices)}"
            )
        
        return current_user
    
    return index_access_checker

async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Get current authenticated user that is an admin."""
    if current_user.profile_type != "admin":
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user