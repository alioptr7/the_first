from sqlalchemy import String, Column, Text, BigInteger
from sqlalchemy.dialects.postgresql import UUID, JSONB

from base import BaseModel


class SystemLog(BaseModel):
    __tablename__ = "system_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    level = Column(String(20), nullable=False, index=True)
    component = Column(String(100), nullable=False, index=True)
    message = Column(Text, nullable=False)
    error_trace = Column(Text, nullable=True)
    request_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    meta = Column(JSONB, nullable=True)