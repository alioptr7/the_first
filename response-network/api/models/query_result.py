from sqlalchemy import (
    Column,
    Integer,
    Boolean,
    ForeignKey,
    DateTime,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from shared.database.base import BaseModel


class QueryResult(BaseModel):
    """
    Stores the result of a processed IncomingRequest.
    """
    __tablename__ = "query_results"

    incoming_request_id = Column(UUID(as_uuid=True), ForeignKey("incoming_requests.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    original_request_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    result_data = Column(JSONB, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    cache_hit = Column(Boolean, default=False, nullable=False)
    exported_at = Column(DateTime(timezone=True), nullable=True)
    export_batch_id = Column(UUID(as_uuid=True), nullable=True, index=True)

    # Relationship back to the request
    incoming_request = relationship("IncomingRequest", back_populates="query_result")

    def __repr__(self):
        return f"<QueryResult(id={self.id}, request_id='{self.incoming_request_id}', cache_hit={self.cache_hit})>"