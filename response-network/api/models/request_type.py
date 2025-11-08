from datetime import datetime
from typing import List
from uuid import UUID

from sqlalchemy import String, Boolean, ForeignKey, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID, ARRAY

from shared.database.base import BaseModel


class RequestType(BaseModel):
    __tablename__ = "request_types"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_public: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    max_items_per_request: Mapped[int] = mapped_column(nullable=False)
    available_indices: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=False)

    created_by_id: Mapped[UUID] = mapped_column(PGUUID, ForeignKey("users.id"), nullable=False)
    created_by: Mapped["User"] = relationship("User", back_populates="created_request_types")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    parameters: Mapped[List["RequestTypeParameter"]] = relationship("RequestTypeParameter", back_populates="request_type", cascade="all, delete-orphan")
    access_rules: Mapped[List["UserRequestAccess"]] = relationship("UserRequestAccess", back_populates="request_type")