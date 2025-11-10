from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field
from datetime import datetime


class UserRequestAccessBase(BaseModel):
    max_requests_per_hour: int = Field(100, ge=1)
    is_active: bool = True


class UserRequestAccessCreate(UserRequestAccessBase):
    user_id: UUID
    request_type_id: UUID


class BulkUserRequestAccessCreate(BaseModel):
    user_ids: List[UUID]
    max_requests_per_hour: int = Field(100, ge=1)
    is_active: bool = True


class UserRequestAccessUpdate(BaseModel):
    max_requests_per_hour: Optional[int] = Field(None, ge=1)
    is_active: Optional[bool] = None


class UserRequestAccessRead(UserRequestAccessBase):
    id: UUID
    user_id: UUID
    request_type_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True