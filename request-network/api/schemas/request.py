import uuid
from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, Field

from ..db.models.enums import RequestStatus
from .user import User


class RequestBase(BaseModel):
    """Shared properties for a request."""
    query_type: str = Field(..., max_length=50)
    query_params: Dict[str, Any]
    priority: int = Field(default=5, ge=1, le=10)


class RequestCreate(RequestBase):
    """Properties to receive via API on creation."""
    pass


class Request(RequestBase):
    """Properties to return to client."""
    id: uuid.UUID
    status: RequestStatus
    user: User
    created_at: datetime

    class Config:
        from_attributes = True