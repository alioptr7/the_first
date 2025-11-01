"""مدل‌های مربوط به لاگ اکشن‌های ادمین"""
from datetime import datetime
import uuid
from typing import List, Dict, Optional

from sqlalchemy import Column, String, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship

from api.db.base_class import Base


class AdminActionLog(Base):
    """مدل لاگ اکشن‌های ادمین"""
    __tablename__ = "admin_action_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    admin_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    action_type = Column(String(50), nullable=False)
    target_type = Column(String(50), nullable=False)
    target_ids = Column(ARRAY(UUID(as_uuid=True)), nullable=False)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # رابطه با جدول کاربران
    admin = relationship("User", back_populates="admin_actions")

    def __repr__(self):
        return f"<AdminActionLog(id={self.id}, admin_id={self.admin_id}, action_type={self.action_type})>"