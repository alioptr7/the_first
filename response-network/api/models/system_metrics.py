from sqlalchemy import Column, String, DateTime, Float, Integer
from sqlalchemy.sql import func
from shared.database.base import Base


class SystemMetrics(Base):
    """System performance metrics table."""
    __tablename__ = "system_metrics"

    id = Column(String, primary_key=True, index=True)
    cpu_percent = Column(Float, nullable=False)
    memory_percent = Column(Float, nullable=False)
    disk_percent = Column(Float, nullable=False)
    requests_pending = Column(Integer, default=0)
    requests_completed = Column(Integer, default=0)
    requests_failed = Column(Integer, default=0)
    avg_processing_time = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
