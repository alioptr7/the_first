"""مدل برای ذخیره‌سازی انواع درخواست‌ها و الگوهای جستجوی آنها"""
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.database.base import BaseModel


class RequestTypeParameter(BaseModel):
    """مدل برای ذخیره‌سازی پارامترهای مورد نیاز هر نوع درخواست"""
    __tablename__ = "request_type_parameters"

    request_type_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("request_types.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    parameter_type: Mapped[str] = mapped_column(String(50), nullable=False)  # string, number, boolean, array, object
    required: Mapped[bool] = mapped_column(Boolean, default=True)
    validation_rules: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # min, max, pattern, enum, etc.
    default_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    example: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    request_type = relationship("RequestType", back_populates="parameters")


class RequestType(BaseModel):
    """مدل برای ذخیره‌سازی انواع درخواست‌ها و الگوهای جستجوی آنها"""
    __tablename__ = "request_types"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    query_type: Mapped[str] = mapped_column(String(50), nullable=False, comment="نوع جستجوی الستیک‌سرچ (match, term, etc.)")
    query_type_alias: Mapped[str] = mapped_column(String(50), nullable=False, comment="نام مستعار برای نوع جستجو که به کاربران نمایش داده می‌شود")
    query_template: Mapped[dict] = mapped_column(JSONB, nullable=False, comment="الگوی جستجوی الستیک‌سرچ با پارامترهای متغیر")
    available_indices: Mapped[list] = mapped_column(JSONB, nullable=False, comment="لیست ایندکس‌های قابل جستجو")
    max_results: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    requires_auth: Mapped[bool] = mapped_column(Boolean, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Response configuration
    response_template: Mapped[dict | None] = mapped_column(JSONB, nullable=True, comment="الگوی تبدیل پاسخ الستیک‌سرچ")
    error_templates: Mapped[dict | None] = mapped_column(JSONB, nullable=True, comment="الگوهای پاسخ برای خطاهای مختلف")

    # Relationships
    parameters = relationship("RequestTypeParameter", back_populates="request_type", cascade="all, delete-orphan")
    created_by = relationship("User", back_populates="created_request_types")
    requests = relationship("IncomingRequest", back_populates="request_type")
    user_access = relationship("UserRequestAccess", back_populates="request_type", cascade="all, delete-orphan")