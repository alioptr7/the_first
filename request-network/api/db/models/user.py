import uuid
from typing import List
from sqlalchemy import String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base_class import Base, TimestampMixin


class User(Base, TimestampMixin):
    """
    Represents a user in the request network.
    This table is a read-only replica synced from the response network.
    """

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    role: Mapped[str] = mapped_column(String(50), default="user", nullable=False)

    # Relationships
    requests: Mapped[List["Request"]] = relationship(back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"