import uuid
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, Mapped, mapped_column

from shared.database.base import BaseModel, UUIDMixin, TimestampMixin


class QueryResult(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "query_results"

    request_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("incoming_requests.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    original_request_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    result_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    result_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    execution_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    elasticsearch_took_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cache_hit: Mapped[bool] = mapped_column(Boolean, default=False)
    executed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    exported_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    export_batch_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    meta: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    request = relationship("IncomingRequest", back_populates="result")