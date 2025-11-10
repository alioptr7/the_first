from datetime import datetime
from typing import Dict, Optional
from uuid import UUID

from sqlalchemy import Column, DateTime, String, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID

from db.base_class import Base

class WorkerSettings(Base):
    """Worker settings model."""
    __tablename__ = "worker_settings"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True)
    worker_name = Column(String, nullable=False, unique=True)
    # Storage settings
    storage_type = Column(String, nullable=False)  # local, ftp, s3, etc.
    storage_config = Column(JSON, nullable=False)  # connection details
    # Schedule settings
    schedule_type = Column(String, nullable=False)  # crontab, interval, etc.
    schedule_config = Column(JSON, nullable=False)  # crontab expression or interval
    # Status
    is_active = Column(Boolean, default=True)
    last_run = Column(DateTime, nullable=True)
    next_run = Column(DateTime, nullable=True)
    error_count = Column(Integer, default=0)
    # Metadata
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def update_next_run(self):
        """Update next_run based on schedule_config."""
        if self.schedule_type == "crontab":
            # Use croniter to calculate next run
            cron = croniter(self.schedule_config["crontab"], datetime.utcnow())
            self.next_run = cron.get_next(datetime)
        elif self.schedule_type == "interval":
            # Calculate next run based on interval
            seconds = self.schedule_config.get("seconds", 0)
            minutes = self.schedule_config.get("minutes", 0)
            hours = self.schedule_config.get("hours", 0)
            days = self.schedule_config.get("days", 0)
            
            self.next_run = datetime.utcnow() + timedelta(
                days=days,
                hours=hours,
                minutes=minutes,
                seconds=seconds
            )