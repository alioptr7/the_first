from datetime import datetime
from typing import List
from uuid import UUID

from sqlalchemy import String, Boolean, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from shared.database.base import BaseModel, UUIDMixin, TimestampMixin


class UserRequestAccess(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "user_request_access"
    __table_args__ = {'extend_existing': True}

    user_id: Mapped[UUID] = mapped_column(PGUUID, ForeignKey("users.id"), nullable=False)
    request_type_id: Mapped[UUID] = mapped_column(PGUUID, ForeignKey("request_types.id"), nullable=False)
    max_requests_per_hour: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="request_access")
    request_type: Mapped["RequestType"] = relationship("RequestType", back_populates="user_access")