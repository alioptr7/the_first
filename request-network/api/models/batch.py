import uuid
from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime, BigInteger, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

from shared.database.base import Base


class BaseBatch(Base):
    __abstract__ = True
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    batch_type = Column(String(50), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size_bytes = Column(BigInteger, nullable=True)
    record_count = Column(Integer, nullable=False, default=0)
    checksum = Column(String(64), nullable=True)
    status = Column(String(50), nullable=False, default='pending', index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    error_message = Column(Text, nullable=True)
    meta = Column(JSONB, nullable=True)


class ExportBatch(BaseBatch):
    """
    Represents a batch of records exported to a file.
    """
    __tablename__ = "export_batches"
    completed_at = Column(DateTime(timezone=True), nullable=True)


class ImportBatch(BaseBatch):
    """
    Represents a batch of records imported from a file.
    """
    __tablename__ = "import_batches"
    source_batch_id = Column(UUID(as_uuid=True), nullable=True)
    processed_at = Column(DateTime(timezone=True), nullable=True)