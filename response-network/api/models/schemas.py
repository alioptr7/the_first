from pydantic import BaseModel, EmailStr, conint
from typing import Dict, List, Optional, Any
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    size: int

from schemas.user import UserBase, UserCreate, UserUpdate, UserStats, UserWithStats, UserRead as User

class RequestBase(BaseModel):
    content: Dict

class RequestCreate(RequestBase):
    pass

class RequestUpdate(BaseModel):
    status: Optional[str] = None
    result: Optional[Dict] = None
    error: Optional[str] = None
    progress: Optional[float] = None

class Request(RequestBase):
    id: int
    user_id: int
    status: str
    result: Optional[Dict] = None
    error: Optional[str] = None
    processing_time: Optional[float] = None
    progress: float
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class RequestStats(BaseModel):
    total: int
    pending: int
    processing: int
    completed: int
    failed: int
    avg_processing_time: float

class QueryStats(BaseModel):
    total_count: int
    successful_count: int
    failed_count: int
    average_processing_time: float

class SystemHealth(BaseModel):
    status: str
    components: Dict[str, str]
    last_check: datetime

class SystemStats(BaseModel):
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    requests_per_minute: float
    avg_response_time: float

class LogEntry(BaseModel):
    timestamp: datetime
    level: str
    message: str
    source: str
    metadata: Optional[Dict[str, str]] = None