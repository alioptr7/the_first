from datetime import datetime
from typing import List
from uuid import UUID

from sqlalchemy import String, Boolean, ForeignKey, DateTime, JSON, Enum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID, ARRAY

from shared.database.base import BaseModel, UUIDMixin, TimestampMixin
import enum


class AccessType(str, enum.Enum):
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"


class UserRequestAccess(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "user_request_access"
    __table_args__ = (
        UniqueConstraint('user_id', 'request_type_id', name='uix_user_request_type'),
    )

    user_id: Mapped[UUID] = mapped_column(PGUUID, ForeignKey("users.id"), nullable=False)
    request_type_id: Mapped[UUID] = mapped_column(PGUUID, ForeignKey("request_types.id"), nullable=False)
    access_type: Mapped[AccessType] = mapped_column(Enum(AccessType), nullable=False)
    allowed_indices: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="request_access")
    request_type: Mapped["RequestType"] = relationship("RequestType", back_populates="access_rules")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="request_access")
    request_type: Mapped["RequestType"] = relationship("RequestType", back_populates="access_rules")