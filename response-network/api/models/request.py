from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime

from db.base_class import Base

class Request(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String, index=True)  # pending, processing, completed, failed
    content = Column(JSON)  # Original request content
    result = Column(JSON, nullable=True)  # Response data
    error = Column(String, nullable=True)  # Error message if failed
    processing_time = Column(Float, nullable=True)  # Time taken to process in seconds
    progress = Column(Float, default=0.0)  # Progress percentage (0-100)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="requests")
    logs = relationship("RequestLog", back_populates="request", cascade="all, delete-orphan")