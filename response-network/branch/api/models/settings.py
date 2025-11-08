from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Boolean, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.database.base import BaseModel

class Settings(BaseModel):
    """
    Represents system and user settings in the Response Network.
    """
    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    value: Mapped[dict] = mapped_column(JSONB, nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    is_user_specific: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_synced: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sync_priority: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<Settings(key='{self.key}', is_user_specific={self.is_user_specific})>"

class UserSettings(BaseModel):
    """
    Represents user-specific settings overrides.
    """
    __tablename__ = "user_settings"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    setting_id: Mapped[UUID] = mapped_column(ForeignKey("settings.id", ondelete="CASCADE"), nullable=False)
    value: Mapped[dict] = mapped_column(JSONB, nullable=False)
    is_synced: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="settings")
    setting: Mapped[Settings] = relationship("Settings")

    def __repr__(self):
        return f"<UserSettings(user_id={self.user_id}, setting_id={self.setting_id})>"