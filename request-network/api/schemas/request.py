import uuid
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

from .response import ResponsePublic


from typing import Dict, Any

class RequestDetail(BaseModel):
    """
    Schema for service request details.
    """
    serviceName: str = Field(..., description="Name of the service to query")
    fieldRequest: Dict[str, Any] = Field(..., description="Specific fields for the request")

class RequestCreate(BaseModel):
    """
    Schema for creating a new request. This is the data a user sends.
    """
    reqState: str = Field(default="PENDING", description="Current state of the request")
    name: str = Field(..., description="Unique name/identifier for the request")
    request: RequestDetail = Field(..., description="Details of the request including service and fields")

class RequestStatus(BaseModel):
    """
    A lightweight schema for just the request status.
    """
    id: uuid.UUID
    status: str

class RequestPublic(BaseModel):
    """
    Schema for displaying a request's public details.
    """
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    query_type: str
    query_params: dict
    status: str
    priority: int
    created_at: datetime
    exported_at: datetime | None = None
    result_received_at: datetime | None = None
    error_message: str | None = None
    response: ResponsePublic | None = None