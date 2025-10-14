import pytest
from pathlib import Path
import uuid
import re
import json

# برای اجرای این تست، پایتون باید ماژول shared را پیدا کند.
# این کار معمولاً با تنظیم PYTHONPATH انجام می‌شود.
# export PYTHONPATH=$PYTHONPATH:/home/s_analyst1991/projects/the_first
from shared.file_format_handler import (
    JSONLHandler,
    generate_filename,
    parse_filename,
    calculate_checksum,
    BatchMetadata,
)

# Sample data for testing
SAMPLE_DATA = [
    {"id": 1, "name": "test_1", "data": {"value": 10}},
    {"id": 2, "name": "test_2", "data": {"value": 20, "nested": [1, 2]}},
    {"id": 3, "name": "تست فارسی", "data": {}},
]


def test_write_and_read_jsonl(tmp_path: Path):
    """
    Tests the basic write and read functionality.
    """
    file_path = tmp_path / "test.jsonl"

    # Write data
    JSONLHandler.write_jsonl(SAMPLE_DATA, file_path)

    # Check if file exists
    assert file_path.exists()

    # Read data back
    read_data = JSONLHandler.read_jsonl(file_path)

    # Assert data is identical
    assert read_data == SAMPLE_DATA


def test_stream_read_jsonl(tmp_path: Path):
    """
    Tests the memory-efficient stream reading functionality.
    """
    file_path = tmp_path / "test.jsonl"
    JSONLHandler.write_jsonl(SAMPLE_DATA, file_path)

    # Read data using the generator
    read_data_generator = JSONLHandler.stream_read_jsonl(file_path)
    read_data = list(read_data_generator)

    assert read_data == SAMPLE_DATA


def test_read_empty_file(tmp_path: Path):
    """
    Tests reading from an empty file.
    """
    file_path = tmp_path / "empty.jsonl"
    file_path.touch()

    read_data = JSONLHandler.read_jsonl(file_path)
    assert read_data == []


def test_read_file_with_empty_lines(tmp_path: Path):
    """
    Tests if the reader correctly handles empty lines or lines with only whitespace.
    """
    file_path = tmp_path / "test_with_empty_lines.jsonl"
    content = (
        '{"id": 1, "name": "first"}\n'
        '\n'
        '{"id": 2, "name": "second"}\n'
        '   \n'
        '{"id": 3, "name": "third"}\n'
    )
    file_path.write_text(content, encoding='utf-8')

    read_data = JSONLHandler.read_jsonl(file_path)
    expected_data = [
        {"id": 1, "name": "first"},
        {"id": 2, "name": "second"},
        {"id": 3, "name": "third"},
    ]

    assert read_data == expected_data


def test_generate_and_parse_filename():
    """Tests the filename generation and parsing logic, including types with underscores."""
    batch_id = uuid.uuid4()
    batch_type = "requests_export"

    filename = generate_filename(batch_type, batch_id)

    # Test generation format
    assert filename.endswith(".jsonl")
    # Example: 20250115143000_requests_export_b1e3a5c8-f2d7-4c8e-b1a5-c8f2d74c8e0a.jsonl
    assert re.match(r"^\d{14}_", Path(filename).stem)  # Starts with YYYYMMDDHHMMSS_

    # Test parsing
    parsed_data = parse_filename(filename)
    assert parsed_data is not None
    assert parsed_data["batch_type"] == batch_type
    assert parsed_data["batch_id"] == str(batch_id)


def test_parse_invalid_filename():
    """Tests parsing of an invalid filename."""
    assert parse_filename("invalid_filename.jsonl") is None
    assert parse_filename("justtwo_parts.jsonl") is None
    assert parse_filename("no_extension") is None


def test_calculate_checksum(tmp_path: Path):
    """Tests the SHA-256 checksum calculation."""
    file_path = tmp_path / "checksum_test.txt"
    content = b"hello world"
    file_path.write_bytes(content)

    # Pre-calculated SHA-256 hash for "hello world"
    expected_checksum = "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"

    actual_checksum = calculate_checksum(file_path)

    assert actual_checksum == expected_checksum


def test_batch_metadata_creation_and_write(tmp_path: Path):
    """Tests the creation of a BatchMetadata object and writing it to a file."""
    data_file = tmp_path / "data.jsonl"
    data_file.write_text("some data")

    batch_id = uuid.uuid4()
    batch_type = "test_batch"
    record_count = 10
    checksum = "dummy_checksum"

    metadata = BatchMetadata(batch_id, batch_type, record_count, data_file, checksum)
    meta_file_path = metadata.write_metadata_file()

    assert meta_file_path.exists()
    assert meta_file_path.name == "data.meta"

    # Read and verify content
    with meta_file_path.open('r') as f:
        meta_data = json.load(f)

    assert meta_data["batch_id"] == str(batch_id)
    assert meta_data["record_count"] == record_count
    assert meta_data["checksum_sha256"] == checksum
    assert "created_at_utc" in meta_data