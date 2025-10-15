from datetime import datetime
from sqlalchemy import Boolean, Integer, String, DateTime
import bcrypt
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from shared.database.base import BaseModel


class User(BaseModel):
    """
    Represents a user in the system. This is the source of truth for user data.
    """
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    profile_type: Mapped[str] = mapped_column(String(50), nullable=False, default='basic', index=True)
    rate_limit_per_minute: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    rate_limit_per_hour: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    rate_limit_per_day: Mapped[int] = mapped_column(Integer, nullable=False, default=500)
    allowed_indices: Mapped[list] = mapped_column(JSONB, nullable=False, server_default='["products"]')
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"

    def set_password(self, password: str):
        """
        Hashes the provided password and sets it on the user model.
        """
        if not password:
            raise ValueError("Password cannot be empty.")
        
        pwd_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        self.hashed_password = bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')

    def verify_password(self, password: str) -> bool:
        """
        Verifies a given password against the stored hash.
        """
        if not password or not self.hashed_password:
            return False
            
        password_bytes = password.encode('utf-8')
        hashed_password_bytes = self.hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_password_bytes)