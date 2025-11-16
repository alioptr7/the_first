from datetime import timedelta
from typing import Annotated
import sys
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

# Ensure we're using local Request Network auth module
_api_dir = Path(__file__).parent.parent
if str(_api_dir) not in sys.path:
    sys.path.insert(0, str(_api_dir))

# Import directly from Request Network auth
from auth.security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from auth.schemas import Token
from db.session import get_db_session
from models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_db_session),
):
    """
    Authenticates a user and returns a JWT access token.
    """
    # 1. Find the user by username
    query = select(User).where(User.username == form_data.username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    # 2. Check if user exists and password is correct
    if not user or not user.verify_password(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Create the access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.username,
            "user_id": str(user.id),
            "scopes": form_data.scopes,
        },
        expires_delta=access_token_expires,
    )

    return {"access_token": access_token, "token_type": "bearer"}