from sqlalchemy import Boolean, Column, Integer, String, DateTime
import bcrypt
from sqlalchemy.dialects.postgresql import JSONB

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
    allowed_indices = Column(JSONB, nullable=False, server_default='["products"]')

    priority = Column(Integer, nullable=False, default=5)
    is_active = Column(Boolean, default=True, index=True)
    last_login = Column(DateTime(timezone=True), nullable=True)

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