from datetime import datetime
from typing import List
from uuid import UUID

from sqlalchemy import String, Boolean, Integer, ForeignKey, DateTime, JSON, Enum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID, ARRAY

from shared.database.base import BaseModel, UUIDMixin, TimestampMixin
import enum


class AccessType(str, enum.Enum):
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"


class UserRequestAccess(BaseModel, UUIDMixin, TimestampMixin):
    """
    User-specific access to Request Types.
    Can override profile type limits for individual users.
    """
    __tablename__ = "user_request_access"
    __table_args__ = (
        UniqueConstraint('user_id', 'request_type_id', name='uix_user_request_type'),
    )

    user_id: Mapped[UUID] = mapped_column(PGUUID, ForeignKey("users.id"), nullable=False)
    request_type_id: Mapped[UUID] = mapped_column(PGUUID, ForeignKey("request_types.id"), nullable=False)
    access_type: Mapped[AccessType] = mapped_column(Enum(AccessType), nullable=False)
    allowed_indices: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=False)
    
    # Override limits (nullable - if null, inherit from profile type)
    max_requests_per_day: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_requests_per_month: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="request_access")
    request_type: Mapped["RequestType"] = relationship("RequestType", back_populates="access_rules")

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="request_access")
    request_type: Mapped["RequestType"] = relationship("RequestType", back_populates="access_rules")