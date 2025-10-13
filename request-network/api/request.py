import uuid
from sqlalchemy import String, Integer, TIMESTAMP, Column, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class Request(Base):
    __tablename__ = "requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    query_type = Column(String(50), nullable=False)
    query_params = Column(JSONB, nullable=False)
    status = Column(String(50), nullable=False, default='pending', index=True)
    priority = Column(Integer, nullable=False, default=5)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), index=True)
    exported_at = Column(TIMESTAMP(timezone=True), nullable=True)
    export_batch_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    result_received_at = Column(TIMESTAMP(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    meta = Column(JSONB, nullable=True)

    user = relationship("User")