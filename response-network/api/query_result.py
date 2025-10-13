import uuid
from sqlalchemy import String, Integer, TIMESTAMP, Column, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from base import BaseModel


class QueryResult(BaseModel):
    __tablename__ = "query_results"

    request_id = Column(UUID(as_uuid=True), ForeignKey("incoming_requests.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    original_request_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    result_data = Column(JSONB, nullable=True)
    result_count = Column(Integer, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    elasticsearch_took_ms = Column(Integer, nullable=True)
    cache_hit = Column(Boolean, default=False)
    executed_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    exported_at = Column(TIMESTAMP(timezone=True), nullable=True)
    export_batch_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    meta = Column(JSONB, nullable=True)

    request = relationship("IncomingRequest", back_populates="result")