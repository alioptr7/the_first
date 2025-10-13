import uuid
from sqlalchemy import String, Integer, Boolean, TIMESTAMP, Column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=True)
    profile_type = Column(String(50), nullable=False, default="basic")
    rate_limit_per_minute = Column(Integer, nullable=False, default=10)
    rate_limit_per_hour = Column(Integer, nullable=False, default=100)
    rate_limit_per_day = Column(Integer, nullable=False, default=500)
    priority = Column(Integer, nullable=False, default=5)
    is_active = Column(Boolean, default=True)
    synced_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())