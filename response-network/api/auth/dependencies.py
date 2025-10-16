from typing import Annotated, Optional

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from auth import security
from db.session import get_db_session
from models.user import User


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

    token_data = security.decode_access_token(token)
    if not token_data or not token_data.user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    user = await db.get(User, token_data.user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user