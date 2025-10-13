from sqlalchemy import String, Integer, Column, BigInteger, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB

from base import BaseModel


class ImportBatch(BaseModel):
    __tablename__ = "import_batches"

    batch_type = Column(String(50), nullable=False, index=True)
    filename = Column(String(255), nullable=False, unique=True)
    file_path = Column(String(500), nullable=False)
    file_size_bytes = Column(BigInteger, nullable=True)
    record_count = Column(Integer, nullable=False, default=0)
    checksum = Column(String(64), nullable=True, index=True)
    status = Column(String(50), nullable=False, default='pending', index=True)
    processed_at = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    meta = Column(JSONB, nullable=True)
