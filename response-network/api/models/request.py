from sqlalchemy import Column, Integer, String, DateTime, UUID, Float, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from shared.database.base import Base

class Request(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status = Column(String, nullable=False)  # pending, processing, completed, failed
    content = Column(JSONB, nullable=False)  # Original request content
    result = Column(JSONB, nullable=True)  # Response data
    error = Column(String, nullable=True)  # Error message if failed
    processing_time = Column(Float, nullable=True)  # Time taken to process in seconds
    progress = Column(Float, server_default='0.0', nullable=False)  # Progress percentage (0-100)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="requests")