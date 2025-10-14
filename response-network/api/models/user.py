from sqlalchemy import Boolean, Column, Integer, String, DateTime

from shared.database.base import BaseModel


class User(BaseModel):
    """
    Represents a user in the system. This is the source of truth for user data.
    """
    __tablename__ = "users"

    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)

    profile_type = Column(String(50), nullable=False, default='basic', index=True)
    rate_limit_per_minute = Column(Integer, nullable=False, default=10)
    rate_limit_per_hour = Column(Integer, nullable=False, default=100)
    rate_limit_per_day = Column(Integer, nullable=False, default=500)

    priority = Column(Integer, nullable=False, default=5)
    is_active = Column(Boolean, default=True, index=True)
    last_login = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"

    # We will add password hashing and verification methods here later.