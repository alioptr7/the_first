from pydantic import BaseModel


class SystemStats(BaseModel):
    """
    Schema for representing overall system statistics.
    """
    total_users: int
    active_users: int
    total_requests: int
    pending_requests: int
    completed_requests: int
    failed_requests: int
    total_export_batches: int
    total_import_batches: int

    class Config:
        from_attributes = True