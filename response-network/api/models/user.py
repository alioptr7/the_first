from sqlalchemy import (
    Boolean,
    Column,
    String,
    UUID,
)
from sqlalchemy.orm import relationship

from shared.database.base import Base
from core.hashing import verify_password

class User(Base):
    __tablename__ = "users"

    id = Column(UUID, primary_key=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    
    # Relationships
    requests = relationship("Request", back_populates="user", cascade="all, delete-orphan")
    created_request_types = relationship("RequestType", back_populates="created_by")
    request_access = relationship("UserRequestAccess", back_populates="user", cascade="all, delete-orphan")
    settings = relationship("UserSettings", back_populates="user", cascade="all, delete-orphan")

    def verify_password(self, password: str) -> bool:
        """Verifies the provided password against the stored hash."""
        return verify_password(password, self.hashed_password)