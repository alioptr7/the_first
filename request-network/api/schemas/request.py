import uuid
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

from .response import ResponsePublic


class RequestCreate(BaseModel):
    """
    Schema for creating a new request. This is the data a user sends.
    """
    query_type: str = Field(..., min_length=3, max_length=50, description="The type of query to be executed.")
    query_params: dict = Field(..., description="The parameters for the query in JSON format.")


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