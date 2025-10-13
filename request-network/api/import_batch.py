import uuid
from sqlalchemy import String, Integer, TIMESTAMP, Column, BigInteger, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

from database import Base


class ImportBatch(Base):
    __tablename__ = "import_batches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    batch_type = Column(String(50), nullable=False, index=True)
    filename = Column(String(255), nullable=False, unique=True)
    file_path = Column(String(500), nullable=False)
    file_size_bytes = Column(BigInteger, nullable=True)
    record_count = Column(Integer, nullable=False, default=0)
    checksum = Column(String(64), nullable=True, index=True)
    source_batch_id = Column(UUID(as_uuid=True), nullable=True)
    status = Column(String(50), nullable=False, default='pending', index=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), index=True)
    processed_at = Column(TIMESTAMP(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    meta = Column(JSONB, nullable=True)