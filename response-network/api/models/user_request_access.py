import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Boolean, Integer, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, Mapped, mapped_column

from ...shared.database.base import BaseModel


class UserRequestAccess(BaseModel):
    """مدل برای ذخیره‌سازی دسترسی‌های کاربران به انواع درخواست‌ها"""
    __tablename__ = "user_request_access"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    request_type_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("request_types.id", ondelete="CASCADE"), nullable=False)
    allowed_indices: Mapped[list] = mapped_column(JSONB, nullable=False, comment="لیست ایندکس‌هایی که کاربر به آنها دسترسی دارد")
    rate_limit: Mapped[int] = mapped_column(Integer, nullable=False, default=60)  # تعداد درخواست در دقیقه
    daily_limit: Mapped[int] = mapped_column(Integer, nullable=False, default=1000)  # تعداد درخواست در روز
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="request_access")
    request_type = relationship("RequestType", back_populates="user_access")