from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_

from api.auth.dependencies import get_current_user, require_admin
from api.db.session import get_db
from api.models.user import User
from api.models.user_request_access import UserRequestAccess
from api.models.request_type import RequestType
from api.schemas.user_request_access import (
    UserRequestAccessCreate,
    UserRequestAccessUpdate,
    UserRequestAccessRead
)

router = APIRouter(prefix="/user-request-access", tags=["user-request-access"])


@router.post("", response_model=UserRequestAccessRead)
async def create_user_request_access(
    user_id: UUID,
    access: UserRequestAccessCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """ایجاد دسترسی جدید برای کاربر به یک نوع درخواست"""
    # بررسی وجود کاربر
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="کاربر مورد نظر یافت نشد")

    # بررسی وجود نوع درخواست
    request_type = db.query(RequestType).filter(
        and_(
            RequestType.id == access.request_type_id,
            RequestType.is_active == True
        )
    ).first()
    if not request_type:
        raise HTTPException(status_code=404, detail="نوع درخواست مورد نظر یافت نشد")

    # بررسی معتبر بودن ایندکس‌ها
    invalid_indices = [idx for idx in access.allowed_indices if idx not in request_type.available_indices]
    if invalid_indices:
        raise HTTPException(
            status_code=400,
            detail=f"ایندکس‌های نامعتبر: {', '.join(invalid_indices)}"
        )

    # بررسی دسترسی‌های پایه کاربر
    unauthorized_indices = [idx for idx in access.allowed_indices if idx not in user.allowed_indices]
    if unauthorized_indices:
        raise HTTPException(
            status_code=400,
            detail=f"کاربر به این ایندکس‌ها دسترسی پایه ندارد: {', '.join(unauthorized_indices)}"
        )

    # بررسی عدم وجود دسترسی تکراری
    existing = db.query(UserRequestAccess).filter(
        and_(
            UserRequestAccess.user_id == user_id,
            UserRequestAccess.request_type_id == access.request_type_id
        )
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="این کاربر قبلاً به این نوع درخواست دسترسی دارد"
        )

    # ایجاد دسترسی جدید
    db_access = UserRequestAccess(
        user_id=user_id,
        **access.model_dump()
    )
    db.add(db_access)
    db.commit()
    db.refresh(db_access)
    return db_access


@router.get("/user/{user_id}", response_model=List[UserRequestAccessRead])
async def list_user_request_access(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """دریافت لیست دسترسی‌های یک کاربر"""
    # فقط ادمین یا خود کاربر می‌تواند دسترسی‌ها را ببیند
    if not current_user.is_admin and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="شما مجاز به دیدن دسترسی‌های این کاربر نیستید")

    return db.query(UserRequestAccess).filter(UserRequestAccess.user_id == user_id).all()


@router.put("/{access_id}", response_model=UserRequestAccessRead)
async def update_user_request_access(
    access_id: UUID,
    access_update: UserRequestAccessUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """به‌روزرسانی دسترسی کاربر"""
    db_access = db.query(UserRequestAccess).filter(UserRequestAccess.id == access_id).first()
    if not db_access:
        raise HTTPException(status_code=404, detail="دسترسی مورد نظر یافت نشد")

    # بررسی معتبر بودن ایندکس‌ها
    if access_update.allowed_indices is not None:
        # بررسی در برابر ایندکس‌های موجود در نوع درخواست
        request_type = db.query(RequestType).filter(RequestType.id == db_access.request_type_id).first()
        invalid_indices = [idx for idx in access_update.allowed_indices if idx not in request_type.available_indices]
        if invalid_indices:
            raise HTTPException(
                status_code=400,
                detail=f"ایندکس‌های نامعتبر: {', '.join(invalid_indices)}"
            )

        # بررسی در برابر دسترسی‌های پایه کاربر
        user = db.query(User).filter(User.id == db_access.user_id).first()
        unauthorized_indices = [idx for idx in access_update.allowed_indices if idx not in user.allowed_indices]
        if unauthorized_indices:
            raise HTTPException(
                status_code=400,
                detail=f"کاربر به این ایندکس‌ها دسترسی پایه ندارد: {', '.join(unauthorized_indices)}"
            )

    # به‌روزرسانی فیلدهای مجاز
    update_data = access_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_access, field, value)

    db.commit()
    db.refresh(db_access)
    return db_access


@router.delete("/{access_id}")
async def delete_user_request_access(
    access_id: UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """حذف دسترسی کاربر"""
    db_access = db.query(UserRequestAccess).filter(UserRequestAccess.id == access_id).first()
    if not db_access:
        raise HTTPException(status_code=404, detail="دسترسی مورد نظر یافت نشد")

    db.delete(db_access)
    db.commit()
    return {"message": "دسترسی با موفقیت حذف شد"}