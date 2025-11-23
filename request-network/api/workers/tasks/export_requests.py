"""
Export Requests Task - Export pending requests to response-network
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

EXPORT_PATH = Path(settings.EXPORT_DIR) / "requests"


@shared_task(bind=True, max_retries=3)
def export_pending_requests(self):
    """
    Export all pending requests to file for response-network.
    
    Exports to: /exports/requests/requests_YYYYMMDD_HHMMSS.jsonl
    
    Workflow:
    1. Query pending requests (status='pending')
    2. Sort by priority DESC, created_at ASC
    3. Generate JSONL file (JSON Lines format)
    4. Calculate SHA-256 checksum
    5. Write metadata file
    6. Update request status to 'exported'
    """
    try:
        # Create export directory if it doesn't exist
        EXPORT_PATH.mkdir(parents=True, exist_ok=True)

        # Get current timestamp for filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        batch_id = hashlib.sha256(timestamp.encode()).hexdigest()[:12]

        # Get synchronous session
        db = next(get_db_sync())

        try:
            # Query pending requests ordered by priority and creation time
            pending_requests = db.query(RequestModel).filter(
                RequestModel.status == "pending"
            ).order_by(
                RequestModel.priority.desc(),
                RequestModel.created_at.asc()
            ).limit(500).all()  # Batch size: max 500 per export

            # If nothing to export, return quickly
            if not pending_requests:
                return {
                    "status": "no_changes",
                    "exported_at": datetime.utcnow().isoformat(),
                    "total_requests": 0
                }

            # Prepare JSONL file content
            jsonl_lines = []
            for req in pending_requests:
                jsonl_lines.append(json.dumps({
                    "id": str(req.id),
                    "user_id": str(req.user_id),
                    "query_type": req.query_type,
                    "query_params": req.query_params or {},
                    "priority": req.priority,
                    "created_at": req.created_at.isoformat() if req.created_at else None,
                    "name": getattr(req, "name", None)
                }, ensure_ascii=False))

            # Write to JSONL file
            export_file = EXPORT_PATH / f"requests_{timestamp}.jsonl"
            with open(export_file, "w", encoding="utf-8") as f:
                f.write("\n".join(jsonl_lines))

            # Calculate checksum
            with open(export_file, "rb") as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()

            # Write metadata file
            metadata = {
                "batch_id": batch_id,
                "batch_type": "requests",
                "filename": export_file.name,
                "file_size": export_file.stat().st_size,
                "record_count": len(pending_requests),
                "checksum": file_hash,
                "exported_at": datetime.utcnow().isoformat(),
                "version": 1
            }
            
            meta_file = EXPORT_PATH / f"requests_{timestamp}.meta.json"
            with open(meta_file, "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)

            # Update request status to 'exported'
            for req in pending_requests:
                req.status = "exported"
                req.exported_at = datetime.utcnow()
            
            db.commit()

            return {
                "status": "success",
                "export_file": str(export_file),
                "metadata_file": str(meta_file),
                "total_requests": len(pending_requests),
                "batch_id": batch_id,
                "checksum": file_hash,
                "exported_at": metadata["exported_at"],
            }
        finally:
            db.close()
            
    except Exception as exc:
        # Retry on error
        raise self.retry(exc=exc, countdown=60)
