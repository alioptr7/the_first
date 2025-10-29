import uuid
from datetime import datetime

from sqlalchemy import String, Integer, DateTime, BigInteger, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from shared.database.base import BaseModel


class BaseBatch(BaseModel):
    __abstract__ = True
    
    batch_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    record_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    checksum: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default='pending', index=True)


class ExportBatch(BaseBatch):
    __tablename__ = "response_export_batches"


class ImportBatch(BaseBatch):
    __tablename__ = "response_import_batches"
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    meta: Mapped[dict | None] = mapped_column(JSONB, nullable=True)


class ExportBatch(BaseBatch):
    __tablename__ = "export_batches"
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ImportBatch(BaseBatch):
    __tablename__ = "import_batches"
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)