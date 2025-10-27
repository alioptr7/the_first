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

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    role: Optional[str] = "user"
    status: Optional[str] = "active"
    requests_per_minute: Optional[int] = 10
    requests_per_hour: Optional[int] = 100
    requests_per_day: Optional[int] = 1000
    total_requests_allocated: Optional[int] = 0

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None
    requests_per_minute: Optional[int] = None
    requests_per_hour: Optional[int] = None
    requests_per_day: Optional[int] = None
    total_requests_allocated: Optional[int] = None

class User(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    last_active: Optional[datetime] = None
    remaining_requests: int

    class Config:
        from_attributes = True

class UserStats(BaseModel):
    total_requests: int
    completed_requests: int
    failed_requests: int
    avg_processing_time: float
    requests_today: int
    requests_this_month: int

class UserWithStats(User):
    stats: UserStats

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
    network_latency: float

class LogEntry(BaseModel):
    timestamp: datetime
    level: str
    message: str
    source: str
    metadata: Optional[Dict[str, str]] = None