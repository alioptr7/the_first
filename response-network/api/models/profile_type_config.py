"""
Model for storing user profile types with their configurations
"""

import uuid
from typing import List
from sqlalchemy import String, Boolean, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID, ARRAY

from shared.database.base import Base, TimestampMixin


class ProfileTypeConfig(Base, TimestampMixin):
    """
    Configuration for user profile types.
    Allows admins to define and manage different user profiles.
    """
    __tablename__ = "profile_type_configs"

    # Basic info
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True, primary_key=True)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    
    # Permissions and limits
    permissions: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    daily_request_limit: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    monthly_request_limit: Mapped[int] = mapped_column(Integer, nullable=False, default=2000)
    max_results_per_request: Mapped[int] = mapped_column(Integer, nullable=False, default=1000)
    
    # Status and metadata
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    is_builtin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    config_metadata: Mapped[dict] = mapped_column(JSON, nullable=True)

    def __repr__(self):
        return f"<ProfileTypeConfig(name={self.name}, display_name={self.display_name})>"
