import uuid
from sqlalchemy import String, Integer, TIMESTAMP, Column, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class Response(Base):
    __tablename__ = "responses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id = Column(UUID(as_uuid=True), ForeignKey("requests.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    result_data = Column(JSONB, nullable=True)
    result_count = Column(Integer, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    received_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    import_batch_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    is_cached = Column(Boolean, default=False)
    cache_key = Column(String(255), nullable=True, index=True)
    meta = Column(JSONB, nullable=True)

    request = relationship("Request", back_populates="response")