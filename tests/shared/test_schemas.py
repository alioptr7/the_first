import pytest
import uuid
from datetime import datetime, timezone
from pydantic import ValidationError

from shared.data_schemas import (
    RequestTransferSchema,
    ResponseTransferSchema,
    BatchMetadataSchema,
)


def test_request_transfer_schema_valid():
    """Tests successful validation of a request transfer schema."""
    request_id = uuid.uuid4()
    user_id = uuid.uuid4()
    now = datetime.now(timezone.utc)

    data = {
        "request_id": request_id,
        "user_id": user_id,
        "query_type": "match",
        "query_params": {"field": "content", "value": "hello"},
        "priority": 7,
        "timestamp_utc": now,
    }
    schema = RequestTransferSchema(**data)
    assert schema.request_id == request_id
    assert schema.priority == 7


def test_request_transfer_schema_invalid_priority():
    """Tests that validation fails for out-of-range priority."""
    with pytest.raises(ValidationError):
        RequestTransferSchema(
            request_id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            query_type="match",
            query_params={},
            priority=11,  # Invalid priority
            timestamp_utc=datetime.now(timezone.utc),
        )


def test_response_transfer_schema_valid_success():
    """Tests a valid successful response."""
    request_id = uuid.uuid4()
    now = datetime.now(timezone.utc)
    data = {
        "request_id": request_id,
        "result_data": [{"hit": 1}, {"hit": 2}],
        "execution_time_ms": 150,
        "timestamp_utc": now,
        "is_cached_result": True,
    }
    schema = ResponseTransferSchema(**data)
    assert schema.request_id == request_id
    assert schema.error_message is None
    assert schema.is_cached_result is True


def test_response_transfer_schema_valid_error():
    """Tests a valid error response."""
    request_id = uuid.uuid4()
    now = datetime.now(timezone.utc)
    data = {
        "request_id": request_id,
        "result_data": None,
        "execution_time_ms": 50,
        "error_message": "Query timed out",
        "timestamp_utc": now,
    }
    schema = ResponseTransferSchema(**data)
    assert schema.result_data is None
    assert schema.error_message == "Query timed out"


def test_batch_metadata_schema_invalid_checksum():
    """Tests that validation fails for a checksum with incorrect length."""
    with pytest.raises(ValidationError):
        BatchMetadataSchema(
            batch_id=uuid.uuid4(),
            batch_type="requests_export",
            record_count=100,
            file_size_bytes=1024,
            checksum_sha256="short_checksum",  # Invalid length
            created_at_utc=datetime.now(timezone.utc),
        )