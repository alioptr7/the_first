from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

class ProfileTypeRequestAccessBase(BaseModel):
    max_requests_per_day: Optional[int] = Field(None, ge=1)
    max_requests_per_month: Optional[int] = Field(None, ge=1)
    is_active: bool = True

class ProfileTypeRequestAccessCreate(ProfileTypeRequestAccessBase):
    profile_type_ids: List[str]

class ProfileTypeRequestAccessUpdate(ProfileTypeRequestAccessBase):
    pass

class ProfileTypeRequestAccessRead(ProfileTypeRequestAccessBase):
    id: UUID
    profile_type_id: str
    request_type_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
