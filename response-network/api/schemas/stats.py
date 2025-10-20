from pydantic import BaseModel


class ResponseNetworkStats(BaseModel):
    """
    Schema for representing overall statistics for the Response Network.
    """
    total_users: int
    active_users: int
    total_incoming_requests: int
    processing_requests: int
    completed_requests: int
    failed_requests: int
    total_export_batches: int
    total_import_batches: int