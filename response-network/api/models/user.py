from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    TIMESTAMP,
    UUID,
)
from sqlalchemy.orm import relationship

from shared.database.base import Base
from response_network.api.core.hashing import verify_password

class User(Base):
    __tablename__ = "users"

    id = Column(UUID, primary_key=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    profile_type = Column(String(50), nullable=False, index=True)
    is_active = Column(Boolean, default=True, index=True)
    
    # Relationships
    requests = relationship("Request", back_populates="user", cascade="all, delete-orphan")

    def verify_password(self, password: str) -> bool:
        """Verifies the provided password against the stored hash."""
        return verify_password(password, self.hashed_password)