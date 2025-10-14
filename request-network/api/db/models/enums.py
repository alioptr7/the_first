import enum


class RequestStatus(str, enum.Enum):
    """
    Represents the lifecycle status of a request.
    """
    PENDING = "pending"       # Request created, waiting for export
    EXPORTED = "exported"     # Request has been batched and exported
    COMPLETED = "completed"   # Response has been imported and is available
    FAILED = "failed"         # Processing failed at some stage
    CANCELLED = "cancelled"   # Request was cancelled by the user