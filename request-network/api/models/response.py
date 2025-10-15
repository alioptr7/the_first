import uuid
from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from shared.database.base import Base


class Response(Base):
    """
    Represents the result of a processed request.
    """
    __tablename__ = "responses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id = Column(UUID(as_uuid=True), ForeignKey("requests.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)

    result_data = Column(JSONB, nullable=True)
    result_count = Column(Integer, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    received_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    import_batch_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    is_cached = Column(Boolean, default=False)
    cache_key = Column(String(255), nullable=True, index=True)
    meta = Column(JSONB, nullable=True)

    # Relationship back to the request
    request = relationship("Request", back_populates="response")