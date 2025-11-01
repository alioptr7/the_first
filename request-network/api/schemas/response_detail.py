import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ResponseDetail(BaseModel):
    """
    Schema for displaying complete response details including result data.
    """
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    request_id: uuid.UUID
    result_data: dict | list | None = None
    result_count: int | None = None
    execution_time_ms: int | None = None
    received_at: datetime
    is_cached: bool
    meta: dict | None = None