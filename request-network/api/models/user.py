from datetime import datetime, timedelta
from typing import Optional
import jwt

from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from api.core.config import settings
from api.db.base_class import Base


class User(Base):
    """مدل کاربر در سیستم"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # روابط با سایر مدل‌ها
    requests = relationship("Request", back_populates="user")
    api_keys = relationship("APIKey", back_populates="user")

    def generate_token(self, expires_delta: Optional[timedelta] = None) -> str:
        """تولید توکن JWT برای کاربر"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode = {
            "exp": expire,
            "sub": str(self.id),
            "username": self.username,
            "email": self.email,
            "is_admin": self.is_admin
        }
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
        return encoded_jwt