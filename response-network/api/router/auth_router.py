from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from auth import security
from core.config import settings
from db.session import get_db_session
from models.user import User
from schemas.user import UserRead

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", summary="Admin Login with Cookie")
async def login_for_access_token(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_db_session),
):
    """
    Authenticates an admin user and sets the JWT as an HttpOnly cookie.
    The username can be the user's username or email address.
    """
    # 1. Find the user by username or email
    query = select(User).where(
        (User.username == form_data.username) | (User.email == form_data.username)
    )
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    # 2. Check if user exists, is active, is an admin, and password is correct
    if (
        not user
        or not user.is_active
        or user.profile_type != "admin"
        or not security.verify_password(form_data.password, user.hashed_password)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password, or insufficient privileges",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Create the access token
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={
            "user_id": str(user.id),
            "scopes": ["admin"],  # Scope is hardcoded to admin for this panel
        },
        expires_delta=access_token_expires,
    )

    # 4. Set the token in an HttpOnly cookie
    response.set_cookie(
        key="access_token",
        value=f"bearer {access_token}",
        httponly=True,
        secure=not settings.DEV_MODE,  # True in production
        samesite="lax",
        max_age=int(access_token_expires.total_seconds()),
    )

    return {"message": "Login successful"}


@router.get("/me", response_model=UserRead, summary="Get Current User")
async def read_users_me(
    current_user: Annotated[User, Depends(security.get_current_user)],
):
    """Get the current logged-in user's details."""
    return current_user


@router.post("/logout", summary="Admin Logout")
<<<<<<< HEAD
async def logout(response: Response):
    """
    Logs out the admin user by clearing the access token cookie.
    """
    response.delete_cookie(key="access_token")
    return {"message": "Logout successful"}
=======
async def logout_user(response: Response):
    """
    Logs out the current user by deleting the HttpOnly access_token cookie.
    """
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=not settings.DEV_MODE,
        samesite="lax",
    )
    return {"message": "Logout successful"}
>>>>>>> 8872923d0365af6f7faa5534db6e2b10796f912d
