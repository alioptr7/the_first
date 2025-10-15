import logging
import shutil
from datetime import datetime
from pathlib import Path

from pydantic import ValidationError

from api.models.batch import ImportBatch
from api.models.request import Request
from api.models.response import Response
from shared.file_format_handler import JSONLHandler, calculate_checksum
from shared.schemas.transfer import ResponseTransferSchema
from workers.celery_app import celery_app
from workers.database import db_session_scope

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

IMPORT_DIR = Path("./import/responses")
ARCHIVE_DIR = IMPORT_DIR / "archive"
FAILED_DIR = IMPORT_DIR / "failed"

# Ensure directories exist
IMPORT_DIR.mkdir(parents=True, exist_ok=True)
ARCHIVE_DIR.mkdir(exist_ok=True)
FAILED_DIR.mkdir(exist_ok=True)


@celery_app.task(
    name="workers.tasks.import_results.import_response_files",
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 60},
)
def import_response_files():
    """
    Scans the import directory for response files, processes them,
    updates the database, and archives the files.
    """
    logger.info("Starting import_response_files task...")
    processed_files = 0
    
    # Look for .jsonl files (assuming .enc is handled before this stage)
    for file_path in IMPORT_DIR.glob("*.jsonl"):
        if not file_path.is_file():
            continue

        logger.info(f"Processing file: {file_path.name}")
        checksum = calculate_checksum(file_path)

        try:
            with db_session_scope() as db:
                # 1. Check for duplicates
                existing_batch = db.query(ImportBatch).filter(ImportBatch.checksum == checksum).first()
                if existing_batch:
                    logger.warning(f"Skipping duplicate file (checksum: {checksum}): {file_path.name}")
                    shutil.move(file_path, ARCHIVE_DIR / file_path.name)
                    continue

                # 2. Read and validate records
                try:
                    records = JSONLHandler.read_jsonl(file_path)
                    validated_responses = [ResponseTransferSchema.parse_obj(rec) for rec in records]
                except (ValueError, ValidationError) as e:
                    logger.error(f"Failed to parse or validate file {file_path.name}: {e}")
                    shutil.move(file_path, FAILED_DIR / file_path.name)
                    continue

                if not validated_responses:
                    logger.warning(f"File {file_path.name} is empty or contains no valid records.")
                    shutil.move(file_path, ARCHIVE_DIR / file_path.name)
                    continue

                # 3. Create ImportBatch record
                import_batch = ImportBatch(
                    batch_type="responses",
                    filename=file_path.name,
                    file_path=str(file_path.absolute()),
                    record_count=len(validated_responses),
                    file_size_bytes=file_path.stat().st_size,
                    checksum=checksum,
                    status="processing",
                )
                db.add(import_batch)
                db.flush() # To get the batch ID for FKs

                # 4. Process each response
                updated_count = 0
                for res_data in validated_responses:
                    request_to_update = db.query(Request).filter(Request.id == res_data.request_id).first()

                    if not request_to_update:
                        logger.warning(f"Request with ID {res_data.request_id} not found. Skipping response.")
                        continue

                    # Create Response record
                    new_response = Response(
                        request_id=res_data.request_id,
                        result_data=res_data.result_data,
                        execution_time_ms=res_data.execution_time_ms,
                        received_at=datetime.utcnow(),
                        import_batch_id=import_batch.id,
                    )
                    db.add(new_response)

                    # Update Request status
                    request_to_update.status = "completed"
                    request_to_update.result_received_at = datetime.utcnow()
                    updated_count += 1

                # 5. Finalize batch status
                import_batch.status = "completed"
                import_batch.processed_at = datetime.utcnow()
                
                logger.info(f"Successfully processed {updated_count}/{len(validated_responses)} records from {file_path.name}.")

            # 6. Archive file after successful transaction
            shutil.move(file_path, ARCHIVE_DIR / file_path.name)
            processed_files += 1

        except Exception as e:
            logger.critical(f"Unhandled error processing file {file_path.name}: {e}", exc_info=True)
            shutil.move(file_path, FAILED_DIR / file_path.name)
            # The task will be retried due to the decorator config
            raise

    if processed_files == 0:
        return "No new response files to import."
    
    return f"Successfully imported {processed_files} response files."