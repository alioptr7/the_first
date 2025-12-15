from pydantic import BaseModel, conint
from typing import Dict, List, Optional, Any
from datetime import datetime
from uuid import UUID

class Token(BaseModel):
    access_token: str
    token_type: str

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    size: int

class RequestPaginatedResponse(BaseModel):
    requests: List[Any]
    total: int
    page: int
    size: int

from schemas.user import UserBase, UserCreate, UserUpdate, UserStats, UserWithStats, UserRead as User

class RequestBase(BaseModel):
    content: Optional[Dict] = None

class RequestCreate(RequestBase):
    pass

class RequestUpdate(BaseModel):
    status: Optional[str] = None
    result: Optional[Dict] = None
    error: Optional[str] = None
    progress: Optional[float] = None

class Request(BaseModel):
    id: UUID | int | str
    original_request_id: Optional[UUID | str] = None
    user_id: UUID | int | str
    username: Optional[str] = None
    status: str
    query_type: Optional[str] = None
    query_params: Optional[Dict] = None
    query_params: Optional[Dict] = None
    content: Optional[Dict] = None
    result: Optional[Dict] = None
    error: Optional[str] = None
    error_message: Optional[str] = None

    processing_time: Optional[float] = None # IncomingRequest doesn't have it directly?
    progress: float = 0.0 # IncomingRequest doesn't have progress?
    created_at: datetime
    updated_at: datetime = datetime.utcnow()

    class Config:
        from_attributes = True
        orm_mode = True # For Pydantic v1
        arbitrary_types_allowed = True

class RequestStats(BaseModel):
    total: int
    pending: int
    processing: int
    completed: int
    failed: int
    avg_processing_time: float

class SystemHealth(BaseModel):
    status: str
    uptime: str
    last_error: Optional[str] = None
    last_check: str
    components: Dict[str, str]

class QueryStats(BaseModel):
    total_count: int
    successful_count: int
    failed_count: int
    average_processing_time: float

class SystemHealth(BaseModel):
    status: str
    components: Dict[str, str]
    components_stats: Optional[Dict[str, Dict[str, Any]]] = None
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