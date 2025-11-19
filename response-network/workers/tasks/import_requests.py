import logging
import shutil
import os
from pathlib import Path

from pydantic import ValidationError

from api.models.batch import ImportBatch
from api.models.incoming_request import IncomingRequest
from shared.file_format_handler import JSONLHandler, calculate_checksum
from shared.schemas.transfer import RequestTransferSchema
from workers.celery_app import celery_app
from workers.database import db_session_scope
from workers.config import settings
from .query_executor import execute_query_task

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use settings from config to resolve import directory
IMPORT_DIR = Path(settings.IMPORT_DIR) / "requests" if hasattr(settings, 'IMPORT_DIR') else Path("./import/requests")
ARCHIVE_DIR = IMPORT_DIR / "archive"
FAILED_DIR = IMPORT_DIR / "failed"

# Ensure directories exist
IMPORT_DIR.mkdir(parents=True, exist_ok=True)
ARCHIVE_DIR.mkdir(exist_ok=True)
FAILED_DIR.mkdir(exist_ok=True)


@celery_app.task(name="workers.tasks.import_requests.import_request_files")
def import_request_files():
    """
    Scans the import directory for request files, processes them,
    creates IncomingRequest records, and triggers the query executor task.
    """
    logger.info("Starting import_request_files task...")
    processed_files = 0

    for file_path in IMPORT_DIR.glob("*.jsonl"):
        if not file_path.is_file():
            continue

        logger.info(f"Processing file: {file_path.name}")
        checksum = calculate_checksum(file_path)

        try:
            with db_session_scope() as db:
                # 1. Check for duplicates
                if db.query(ImportBatch).filter(ImportBatch.checksum == checksum).first():
                    logger.warning(f"Skipping duplicate file (checksum: {checksum}): {file_path.name}")
                    shutil.move(file_path, ARCHIVE_DIR / file_path.name)
                    continue

                # 2. Read and validate records
                try:
                    records = JSONLHandler.read_jsonl(file_path)
                    validated_requests = [RequestTransferSchema.parse_obj(rec) for rec in records]
                except (ValueError, ValidationError) as e:
                    logger.error(f"Failed to parse or validate file {file_path.name}: {e}")
                    shutil.move(file_path, FAILED_DIR / file_path.name)
                    continue

                if not validated_requests:
                    logger.warning(f"File {file_path.name} is empty or contains no valid records.")
                    shutil.move(file_path, ARCHIVE_DIR / file_path.name)
                    continue

                # 3. Create ImportBatch record
                import_batch = ImportBatch(
                    batch_type="requests",
                    filename=file_path.name,
                    file_path=str(file_path.absolute()),
                    record_count=len(validated_requests),
                    file_size_bytes=file_path.stat().st_size,
                    checksum=checksum,
                    status="processing",  # Changed from 'completed' to 'processing'
                )
                db.add(import_batch)
                db.flush()  # Flush to get the ID
                db.commit()  # Commit to ensure ID is available

                # 4. Create IncomingRequest for each record and dispatch task
                for req_data in validated_requests:
                    try:
                        new_request = IncomingRequest(
                            id=req_data.id,  # Use the original ID
                            original_request_id=req_data.id,
                            user_id=req_data.user_id,
                            query_type=req_data.query_type,
                            query_params=req_data.query_params,
                            priority=req_data.priority,
                            import_batch_id=import_batch.id,
                            status="pending",
                        )
                        db.add(new_request)
                        db.flush()  # Flush each request individually
                        
                        # Dispatch the executor task (sync call, no await needed)
                        logger.info(f"Dispatching query execution for request {new_request.id}")
                        execute_query_task.apply_async(
                            args=[str(new_request.id)],
                            priority=new_request.priority,
                            queue='default'
                        )
                    except Exception as req_error:
                        logger.error(f"Failed to process individual request: {req_error}", exc_info=True)
                        continue

                # Commit all requests
                db.commit()
                import_batch.status = "completed"
                db.commit()
                logger.info(f"Dispatched {len(validated_requests)} requests from batch {import_batch.id}.")

            # 5. Archive file after successful transaction
            shutil.move(file_path, ARCHIVE_DIR / file_path.name)
            processed_files += 1
        except Exception as e:
            logger.critical(f"Unhandled error processing file {file_path.name}: {e}", exc_info=True)
            try:
                shutil.move(file_path, FAILED_DIR / file_path.name)
            except Exception as move_error:
                logger.error(f"Failed to move file to failed directory: {move_error}")

    logger.info(f"import_request_files task completed. Processed {processed_files} files.")