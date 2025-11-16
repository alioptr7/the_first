import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Annotated

# Add Response Network API directory to sys.path ONLY if needed
_response_api_dir = Path(__file__).resolve().parent.parent
if str(_response_api_dir) not in sys.path:
    sys.path.insert(0, str(_response_api_dir))

from fastapi import Depends, HTTPException, status, Cookie, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Use absolute imports relative to Response Network API
import importlib.util
_token_path = _response_api_dir / "schemas" / "token.py"
_spec = importlib.util.spec_from_file_location("token", _token_path)
_token_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_token_module)
TokenData = _token_module.TokenData

_hashing_path = _response_api_dir / "core" / "hashing.py"
_spec = importlib.util.spec_from_file_location("hashing", _hashing_path)
_hashing_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_hashing_module)
get_password_hash = _hashing_module.get_password_hash
verify_password = _hashing_module.verify_password

from db.session import get_db_session
from models.user import User
from core.config import settings

security = HTTPBearer()

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