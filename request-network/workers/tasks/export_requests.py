import logging
import uuid
from datetime import datetime
from pathlib import Path

from api.models.request import Request
from api.models.batch import ExportBatch
from shared.file_format_handler import JSONLHandler, generate_filename, calculate_checksum, BatchMetadata
from shared.schemas.transfer import RequestTransferSchema
from workers.celery_app import celery_app
from workers.database import db_session_scope

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

EXPORT_DIR = Path("./export/requests")
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

MAX_BATCH_SIZE = 500


@celery_app.task(name="workers.tasks.export_requests.export_pending_requests")
def export_pending_requests():
    """
    Queries for pending requests, batches them, writes them to a JSONL file,
    and updates their status in the database.
    """
    logger.info("Starting export_pending_requests task...")

    with db_session_scope() as db:
        pending_requests = (
            db.query(Request)
            .filter(Request.status == "pending")
            .order_by(Request.priority.desc(), Request.created_at.asc())
            .limit(MAX_BATCH_SIZE)
            .all()
        )

        if not pending_requests:
            logger.info("No pending requests to export.")
            return "No pending requests."

        logger.info(f"Found {len(pending_requests)} requests to export.")

        batch_id = uuid.uuid4()
        
        # Prepare data for export using the transfer schema
        records_to_export = [
            RequestTransferSchema.from_orm(req).dict() for req in pending_requests
        ]

        # Generate file
        filename = generate_filename("requests", batch_id)
        file_path = EXPORT_DIR / filename
        JSONLHandler.write_jsonl(records_to_export, file_path)

        # Create batch record
        checksum = calculate_checksum(file_path)
        export_batch = ExportBatch(
            id=batch_id,
            batch_type="requests",
            filename=filename,
            file_path=str(file_path.absolute()),
            record_count=len(pending_requests),
            file_size_bytes=file_path.stat().st_size,
            checksum=checksum,
            status="completed",
            completed_at=datetime.utcnow(),
        )
        db.add(export_batch)

        # Update requests
        for req in pending_requests:
            req.status = "exported"
            req.exported_at = datetime.utcnow()
            req.export_batch_id = batch_id

        logger.info(f"Successfully created export batch {batch_id} with {len(pending_requests)} records.")
        return f"Exported {len(pending_requests)} requests to batch {batch_id}."