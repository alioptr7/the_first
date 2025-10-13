import uuid
from sqlalchemy import String, Integer, TIMESTAMP, Column, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from base import BaseModel


class IncomingRequest(BaseModel):
    __tablename__ = "incoming_requests"

    original_request_id = Column(UUID(as_uuid=True), nullable=False, index=True, unique=True) # The ID from the Request Network
    user_id = Column(UUID(as_uuid=True), nullable=False) # No foreign key, it's an isolated network
    query_type = Column(String(50), nullable=False)
    query_params = Column(JSONB, nullable=False)
    elasticsearch_query = Column(JSONB, nullable=True)
    priority = Column(Integer, nullable=False, default=5)
    imported_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    import_batch_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    status = Column(String(50), nullable=False, default='pending', index=True)
    assigned_worker = Column(String(100), nullable=True)
    started_at = Column(TIMESTAMP(timezone=True), nullable=True)
    completed_at = Column(TIMESTAMP(timezone=True), nullable=True)
    retry_count = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    meta = Column(JSONB, nullable=True)

    result = relationship("QueryResult", back_populates="request", uselist=False, cascade="all, delete-orphan")