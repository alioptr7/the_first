from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Annotated

from fastapi import Depends, HTTPException, status, Cookie
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import TokenData
from core.hashing import get_password_hash, verify_password # Import from the new module
from db.session import get_db_session
from models.user import User


# These should be in a config file and loaded securely
SECRET_KEY = "a_very_secret_key_for_response_network_admin" # TODO: Move to settings
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


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
        user_id = payload.get("user_id")
        if user_id is None:
            return None
        token_data = TokenData(user_id=user_id, scopes=payload.get("scopes", []))
        return token_data
    except JWTError:
        return None


async def get_current_user(
    access_token: Annotated[Optional[str], Cookie()] = None,
    db: AsyncSession = Depends(get_db_session),
) -> User:
    """
    Decodes the JWT token from the cookie and returns the corresponding user.
    """
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    # The cookie value is "bearer <token>", so we split it.
    token_type, _, token = access_token.partition(" ")
    if token_type.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token format"
        )

    token_data = decode_access_token(token)
    if not token_data or not token_data.user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    user = await db.get(User, token_data.user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user