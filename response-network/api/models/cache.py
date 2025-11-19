from sqlalchemy import Column, String, DateTime, JSON, Integer
from sqlalchemy.sql import func
from shared.database.base import Base


class Cache(Base):
    """Cache table for storing cached query results."""
    __tablename__ = "cache"

    id = Column(String, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    value = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
