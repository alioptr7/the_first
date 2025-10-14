import uuid
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from shared.database.base import BaseModel


class IncomingRequest(BaseModel):
    """
    Represents a request that has been imported into the Response Network for processing.
    This is a mirror of the original request from the Request Network, but is isolated.
    """
    __tablename__ = "incoming_requests"

    # The ID of the original request from the Request Network
    original_request_id = Column(UUID(as_uuid=True), nullable=False, unique=True, index=True)

    # The ID of the user who made the original request
    original_user_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    query_type = Column(String(100), nullable=False, index=True)
    query_params = Column(JSONB, nullable=False)
    priority = Column(Integer, nullable=False, default=5, index=True)

    # The timestamp from the original request creation
    original_timestamp = Column(DateTime(timezone=True), nullable=False)

    status = Column(String(50), nullable=False, default='pending', index=True)
    # Possible statuses: 'pending', 'processing', 'completed', 'failed'

    # Relationship to the result of this query
    query_result = relationship("QueryResult", back_populates="incoming_request", uselist=False)

    def __repr__(self):
        return f"<IncomingRequest(id={self.id}, original_request_id='{self.original_request_id}', status='{self.status}')>"