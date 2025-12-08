from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, Integer, String, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from shared.database.base import BaseModel, UUIDMixin, TimestampMixin


class ProfileTypeRequestAccess(BaseModel, UUIDMixin, TimestampMixin):
    """
    Access rules for Profile Types to Request Types.
    Defines default limits that all users of a profile type inherit.
    """
    __tablename__ = "profile_type_request_access"
    __table_args__ = (
        UniqueConstraint('profile_type_id', 'request_type_id', name='uix_profile_request_type'),
    )

    profile_type_id: Mapped[str] = mapped_column(String(50), ForeignKey("profile_type_configs.name"), nullable=False)
    request_type_id: Mapped[UUID] = mapped_column(PGUUID, ForeignKey("request_types.id"), nullable=False)
    
    # Limits
    max_requests_per_day: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_requests_per_month: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Relationships
    profile_type: Mapped["ProfileTypeConfig"] = relationship("ProfileTypeConfig", back_populates="request_access")
    request_type: Mapped["RequestType"] = relationship("RequestType", back_populates="profile_access")
