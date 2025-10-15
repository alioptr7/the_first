import uuid
from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from shared.database.base import Base


class Request(Base):
    """
    Represents a user's request submitted to the system.
    """
    __tablename__ = "requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    query_type = Column(String(50), nullable=False)
    query_params = Column(JSONB, nullable=False)
    elasticsearch_query = Column(JSONB, nullable=True)

    status = Column(String(50), nullable=False, default='pending', index=True)
    priority = Column(Integer, nullable=False, default=5)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    exported_at = Column(DateTime(timezone=True), nullable=True, index=True)
    export_batch_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    result_received_at = Column(DateTime(timezone=True), nullable=True)

    retry_count = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    meta = Column(JSONB, nullable=True)

    # Relationships
    user = relationship("User", back_populates="requests")
    response = relationship("Response", back_populates="request", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Request(id={self.id}, user_id={self.user_id}, status='{self.status}')>"