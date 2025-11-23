"""
Import Requests Task - Import pending requests from request-network
"""
from datetime import datetime
import json
from pathlib import Path
import hashlib

from celery import shared_task
from sqlalchemy.orm import Session

from core.config import settings
from core.dependencies import get_db_sync
from models.request import Request as RequestModel

IMPORT_PATH = Path(settings.IMPORT_DIR) / "requests"


@shared_task(bind=True, max_retries=3)
def import_requests_from_request_network(self):
    """
    Import pending requests from request-network.
    
    Workflow:
    1. Poll /imports/requests/ for JSONL files
    2. Read each line as a request
    3. Check for duplicates by request ID
    4. Insert into incoming_requests table
    5. Archive processed file
    
    File format: requests_YYYYMMDD_HHMMSS.jsonl
    Each line: {"id": "uuid", "user_id": "uuid", "query_type": "...", "query_params": {...}, ...}
    """
    try:
        IMPORT_PATH.mkdir(parents=True, exist_ok=True)
        
        # Get all JSONL files in import directory
        request_files = list(IMPORT_PATH.glob("requests_*.jsonl"))
        
        if not request_files:
            return {
                "status": "no_files",
                "imported_at": datetime.utcnow().isoformat(),
                "total_requests": 0
            }

        db = next(get_db_sync())
        total_imported = 0
        total_duplicates = 0
        failed_files = []

        try:
            for request_file in request_files:
                try:
                    # Read JSONL file
                    with open(request_file, "r", encoding="utf-8") as f:
                        lines = f.readlines()

                    imported_count = 0
                    duplicate_count = 0

                    for line in lines:
                        if not line.strip():
                            continue

                        try:
                            req_data = json.loads(line)
                            request_id = req_data.get("id")
                            
                            # Check if request already exists (by id)
                            existing = db.query(RequestModel).filter(
                                RequestModel.id == request_id
                            ).first()

                            if not existing:
                                # Create new request
                                new_request = RequestModel(
                                    id=request_id,
                                    user_id=req_data.get("user_id"),
                                    query_type=req_data.get("query_type"),
                                    query_params=req_data.get("query_params", {}),
                                    priority=req_data.get("priority", 5),
                                    status="pending",
                                    created_at=datetime.fromisoformat(req_data.get("created_at")) if req_data.get("created_at") else datetime.utcnow()
                                )
                                db.add(new_request)
                                imported_count += 1
                            else:
                                duplicate_count += 1
                        except (json.JSONDecodeError, ValueError):
                            continue

                    db.commit()
                    total_imported += imported_count
                    total_duplicates += duplicate_count

                    # Move file to archive
                    archive_dir = IMPORT_PATH / "archive"
                    archive_dir.mkdir(parents=True, exist_ok=True)
                    request_file.rename(archive_dir / request_file.name)

                except Exception as e:
                    failed_files.append((request_file.name, str(e)))
                    db.rollback()
                    continue

            return {
                "status": "success" if not failed_files else "partial_success",
                "total_imported": total_imported,
                "total_duplicates": total_duplicates,
                "failed_files": failed_files,
                "imported_at": datetime.utcnow().isoformat()
            }
        finally:
            db.close()

    except Exception as exc:
        # Retry on error
        raise self.retry(exc=exc, countdown=60)


# Backwards-compatible task name if needed
@shared_task(name="workers.tasks.import_requests.import_request_files")
def import_request_files():
    """Compatibility wrapper that calls the new import task."""
    return import_requests_from_request_network()
