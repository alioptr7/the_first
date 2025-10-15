from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
import bcrypt

from shared.database.base import Base


class User(Base):
    """
    Represents a read-only replica of a user in the Request Network.
    This data is synced from the Response Network and is used primarily
    for rate limiting and associating requests with a user profile.
    The 'id' is not auto-generated but synced.
    """
    __tablename__ = "users"

    # The ID is the primary key but is not auto-generated like in BaseModel.
    # It's synced from the source of truth in the Response Network.
    id = Column(UUID(as_uuid=True), primary_key=True)

    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=False)

    profile_type = Column(String(50), nullable=False, default='basic', index=True)
    rate_limit_per_minute = Column(Integer, nullable=False, default=10)
    rate_limit_per_hour = Column(Integer, nullable=False, default=100)
    rate_limit_per_day = Column(Integer, nullable=False, default=500)
    allowed_indices = Column(JSONB, nullable=False, server_default='[]')

    priority = Column(Integer, nullable=False, default=5)
    is_active = Column(Boolean, default=True, index=True)
    synced_at = Column(DateTime(timezone=True), nullable=True)

    # Relationship to requests
    requests = relationship("Request", back_populates="user", cascade="all, delete-orphan")

    def verify_password(self, password: str) -> bool:
        """
        Verifies a given password against the stored hash.
        """
        if not password or not self.hashed_password:
            return False

        password_bytes = password.encode('utf-8')
        hashed_password_bytes = self.hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_password_bytes)

    def __repr__(self):
        return f"<UserReplica(id={self.id}, username='{self.username}')>"