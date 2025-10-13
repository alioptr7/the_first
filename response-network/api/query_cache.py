from sqlalchemy import String, Integer, Column
from sqlalchemy.dialects.postgresql import UUID, JSONB

from base import BaseModel


class QueryCache(BaseModel):
    __tablename__ = "query_cache"

    cache_key = Column(String(255), unique=True, nullable=False, index=True)
    query_hash = Column(String(64), nullable=False, index=True)
    query_params = Column(JSONB, nullable=False)
    result_data = Column(JSONB, nullable=True)
    result_count = Column(Integer, nullable=True)
    hit_count = Column(Integer, default=1)
    expires_at = Column(Integer, nullable=True)
    meta = Column(JSONB, nullable=True)