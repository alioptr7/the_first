import logging
import uuid
from datetime import datetime
from pathlib import Path

from api.models.batch import ExportBatch
from api.models.result import QueryResult
from shared.file_format_handler import JSONLHandler, generate_filename, calculate_checksum
from shared.schemas.transfer import ResponseTransferSchema
from workers.celery_app import celery_app
from workers.database import db_session_scope

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

EXPORT_DIR = Path("./export/responses")
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

MAX_BATCH_SIZE = 500


@celery_app.task(name="workers.tasks.export_results.export_completed_results")
def export_completed_results():
    """
    Queries for completed query results that have not been exported,
    batches them, writes them to a JSONL file, and updates their status.
    """
    logger.info("Starting export_completed_results task...")

    with db_session_scope() as db:
        results_to_export = (
            db.query(QueryResult)
            .filter(QueryResult.exported_at.is_(None))
            .order_by(QueryResult.executed_at.asc())
            .limit(MAX_BATCH_SIZE)
            .all()
        )

        if not results_to_export:
            logger.info("No new results to export.")
            return "No new results to export."

        logger.info(f"Found {len(results_to_export)} results to export.")

        batch_id = uuid.uuid4()

        # Prepare data for export using the transfer schema
        records_to_export = [
            ResponseTransferSchema(
                request_id=res.original_request_id,
                result_data=res.result_data,
                execution_time_ms=res.execution_time_ms,
                timestamp=res.executed_at,
            ).dict()
            for res in results_to_export
        ]

        # Generate file
        filename = generate_filename("responses", batch_id)
        file_path = EXPORT_DIR / filename
        JSONLHandler.write_jsonl(records_to_export, file_path)

        # Create batch record
        checksum = calculate_checksum(file_path)
        export_batch = ExportBatch(
            id=batch_id,
            batch_type="responses",
            filename=filename,
            file_path=str(file_path.absolute()),
            record_count=len(results_to_export),
            file_size_bytes=file_path.stat().st_size,
            checksum=checksum,
            status="completed",
        )
        db.add(export_batch)

        # Update results
        for res in results_to_export:
            res.exported_at = datetime.utcnow()
            res.export_batch_id = batch_id

        logger.info(f"Successfully created export batch {batch_id} with {len(results_to_export)} results.")
        return f"Exported {len(results_to_export)} results to batch {batch_id}."