from uuid import UUID
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, conint


class UserRequestAccessBase(BaseModel):
    request_type_id: UUID
    allowed_indices: List[str]
    rate_limit: conint(gt=0) = Field(60, description="تعداد درخواست مجاز در دقیقه")
    daily_limit: conint(gt=0) = Field(1000, description="تعداد درخواست مجاز در روز")
    is_active: bool = True


class UserRequestAccessCreate(UserRequestAccessBase):
    pass


class UserRequestAccessUpdate(BaseModel):
    allowed_indices: Optional[List[str]] = None
    rate_limit: Optional[conint(gt=0)] = None
    daily_limit: Optional[conint(gt=0)] = None
    is_active: Optional[bool] = None


class UserRequestAccessRead(UserRequestAccessBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True