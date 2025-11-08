from datetime import datetime
from typing import List
from uuid import UUID

from sqlalchemy import String, Boolean, ForeignKey, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from shared.database.base import BaseModel


class RequestTypeParameter(BaseModel):
    __tablename__ = "request_type_parameters"

    request_type_id: Mapped[UUID] = mapped_column(PGUUID, ForeignKey("request_types.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    parameter_type: Mapped[str] = mapped_column(String(50), nullable=False)
    is_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    validation_rules: Mapped[dict] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    request_type: Mapped["RequestType"] = relationship("RequestType", back_populates="parameters")