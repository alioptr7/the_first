from datetime import datetime
import typing
from typing import Optional, Dict, Any

from sqlalchemy import String, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column
from shared.database.base import BaseModel, UUIDMixin, TimestampMixin

if typing.TYPE_CHECKING:
    from models.user import User  # type: ignore


class Settings(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    value: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    def to_read(self):
        from schemas.settings import Settings as SettingsSchema

        return SettingsSchema(
            id=self.id,
            key=self.key,
            value=self.value,
            description=self.description,
            is_active=self.is_public,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


class UserSettings(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "user_settings"

    user_id: Mapped[str] = mapped_column(String(36), nullable=False)
    key: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)

    # Relationship to User is optional here for the replica
    # user: Mapped["User"] = relationship("User", back_populates="settings")
