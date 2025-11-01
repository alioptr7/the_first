import hashlib
from typing import Annotated
from datetime import datetime, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from db.session import get_db_session
from models.api_key import APIKey
from db.models.user import User

# تعریف هدر برای دریافت API Key
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key(
    key: Annotated[str | None, Depends(api_key_header)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> User:
    """
    Dependency to validate an API key and return the associated active user.
    Raises HTTPException for invalid, missing, or inactive keys/users.
    """
    if not key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key is missing.",
        )

    # کلیدها برای امنیت هش شده‌اند. ما کلید ورودی را هش کرده و با دیتابیس مقایسه می‌کنیم.
    hashed_key = hashlib.sha256(key.encode()).hexdigest()

    stmt = (
        select(APIKey)
        .join(User)
        .where(APIKey.key_hash == hashed_key)
    )
    result = await db.execute(stmt)
    api_key_obj = result.scalars().first()

    if not api_key_obj or not api_key_obj.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or inactive API Key.",
        )

    user = api_key_obj.user
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user associated with this API Key is inactive.",
        )

    # آپدیت زمان آخرین استفاده از کلید
    api_key_obj.last_used_at = datetime.now(timezone.utc)
    await db.commit()

    return user