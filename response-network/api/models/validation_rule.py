from typing import Dict, Optional
from uuid import UUID
from sqlalchemy import String, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.database.base import BaseModel, UUIDMixin, TimestampMixin


class ValidationRule(BaseModel, UUIDMixin, TimestampMixin):
    """Validation rules that will be synced to request network."""
    __tablename__ = "validation_rules"

    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    rules: Mapped[Dict] = mapped_column(JSON, nullable=False)
    version: Mapped[int] = mapped_column(default=1, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    
    # Many-to-Many relationship with request types
    request_types: Mapped[list["RequestType"]] = relationship(
        "RequestType",
        secondary="request_type_validation_rules",
        back_populates="validation_rules"
    )