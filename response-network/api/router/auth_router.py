from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from auth import security
from auth.dependencies import get_current_user
from db.session import get_db_session
from models.user import User
from schemas.user import UserRead

router = APIRouter(prefix="/auth", tags=["Admin Authentication"])


@router.post("/login", summary="Admin Login")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    response: Response,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Authenticates an admin user and returns a JWT access token for the admin panel.
    The username is the user's email address.
    """
    # 1. Find the user by email (which is used as username in the form)
    query = select(User).where(User.email == form_data.username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    # 2. Check if user exists, is an admin, and password is correct
    if not user or not user.verify_password(form_data.password) or user.profile_type != 'admin':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password, or not an admin user.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Create the access token
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"user_id": str(user.id), "scopes": ["admin"]},
        expires_delta=access_token_expires,
    )

    # Set the token in an HttpOnly cookie for security
    response.set_cookie(
        key="access_token",
        value=f"bearer {access_token}",
        httponly=True,
        max_age=security.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=access_token_expires,
        samesite="lax",
        secure=False,  # TODO: Set to True in production with HTTPS
    )

    return {"message": "Login successful"}


@router.get("/me", response_model=UserRead, summary="Get Current User")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Get the current logged-in user's details."""
    return current_user


@router.post("/logout", summary="Admin Logout")
async def logout(response: Response):
    """
    Logs out the admin user by clearing the access token cookie.
    """
    response.delete_cookie(key="access_token")
    return {"message": "Logout successful"}
