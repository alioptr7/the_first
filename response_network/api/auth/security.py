from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Annotated

from fastapi import Depends, HTTPException, status, Cookie, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

security = HTTPBearer()
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import TokenData
from ..core.hashing import get_password_hash, verify_password # Import from the new module
from ..db.session import get_db_session
from ..models.user import User


from ..core.config import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Creates a new JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[TokenData]:
    """Decodes a JWT token and returns the payload as TokenData."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Try to get user_id from either "user_id" or "sub" field
        user_id = payload.get("user_id") or payload.get("sub")
        if user_id is None:
            return None
        token_data = TokenData(user_id=user_id, scopes=payload.get("scopes", []))
        return token_data
    except JWTError:
        return None


async def get_current_user(
    access_token: Annotated[Optional[str], Cookie()] = None,
    bearer_token: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)] = None,
    db: AsyncSession = Depends(get_db_session),
) -> User:
    """Get the current user from either cookie or bearer token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Try to get token from either cookie or bearer token
    token = None
    if access_token:
        token = access_token
    elif bearer_token:
        token = bearer_token.credentials

    if not token:
        raise credentials_exception

    token_data = decode_access_token(token)
    if not token_data:
        raise credentials_exception

    # Get user from database
    query = select(User).where(User.id == token_data.user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise credentials_exception

    return user
    """
    Decodes the JWT token from the cookie and returns the corresponding user.
    """
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    # Check if token starts with "bearer "
    if access_token.lower().startswith("bearer "):
        token = access_token.split(" ", 1)[1]
    else:
        token = access_token  # Use the whole token if no bearer prefix

    token_data = decode_access_token(token)
    if not token_data or not token_data.user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    # Use select query to be more explicit about the search
    query = select(User).where(User.id == token_data.user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user