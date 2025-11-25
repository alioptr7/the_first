import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ResponsePublic(BaseModel):
    """
    Schema for displaying a response's public details.
    The full result_data is omitted for brevity in list views,
    but could be included in a detailed view.
    """
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    request_id: uuid.UUID
    result_count: int | None = None
    execution_time_ms: int | None = None
    received_at: datetime
    is_cached: bool


class ResponseDetailed(ResponsePublic):
    """
    Schema for displaying full response details including result data.
    Used by GET /requests/{id}/response endpoint.
    """
    result_data: dict | None = None
    cache_key: str | None = None
    meta: dict | None = None