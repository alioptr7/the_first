"""
Results Importer Task - Import query results from response-network
"""
from datetime import datetime
import json
from pathlib import Path
import hashlib
import logging
import asyncio

from celery import shared_task
from sqlalchemy.orm import Session

from core.config import settings
from core.dependencies import get_db_sync
from models.request import Request as RequestModel

logger = logging.getLogger(__name__)
IMPORT_PATH = Path(settings.IMPORT_DIR) / "results"


@shared_task(bind=True, max_retries=3)
def import_results_from_response_network(self):
    """
    Import query results from response-network.
    
    Workflow:
    1. Poll /imports/results/ for result files
    2. Read JSONL format results
    3. Update corresponding requests with results
    4. Mark requests as completed
    5. Move file to archive/
    
    File format: results_YYYYMMDD_HHMMSS.jsonl
    Each line: {"request_id": "uuid", "result_data": {...}, "execution_time_ms": 123}
    """
    try:
        IMPORT_PATH.mkdir(parents=True, exist_ok=True)
        
        # Get all JSONL files in import directory
        result_files = list(IMPORT_PATH.glob("results_*.jsonl"))
        
        if not result_files:
            return {
                "status": "no_files",
                "imported_at": datetime.utcnow().isoformat(),
                "total_results": 0
            }

        db = next(get_db_sync())
        total_imported = 0
        failed_files = []

        try:
            for result_file in result_files:
                try:
                    # Read JSONL file
                    with open(result_file, "r", encoding="utf-8") as f:
                        lines = f.readlines()

                    imported_count = 0

                    for line in lines:
                        if not line.strip():
                            continue

                        try:
                            result_data = json.loads(line)
                            request_id = result_data.get("request_id")
                            
                            # Find request
                            request = db.query(RequestModel).filter(
                                RequestModel.id == request_id
                            ).first()

                            if request:
                                # Update request with result
                                request.status = "completed"
                                request.result_data = result_data.get("result_data")
                                request.result_received_at = datetime.utcnow()
                                
                                # Invalidate cache for this request (async)
                                try:
                                    from db.redis_client import RedisClient
                                    redis = RedisClient(settings.REDIS_URL)
                                    asyncio.run(redis.invalidate_response(str(request_id)))
                                    logger.info(f"✅ Invalidated cache for request {request_id}")
                                except Exception as e:
                                    logger.warning(f"Could not invalidate cache: {e}")
                                
                                imported_count += 1
                        except json.JSONDecodeError:
                            continue

                    db.commit()
                    total_imported += imported_count

                    # Move file to archive
                    archive_dir = IMPORT_PATH / "archive"
                    archive_dir.mkdir(parents=True, exist_ok=True)
                    result_file.rename(archive_dir / result_file.name)

                except Exception as e:
                    failed_files.append((result_file.name, str(e)))
                    continue

            return {
                "status": "success" if not failed_files else "partial_success",
                "total_imported": total_imported,
                "failed_files": failed_files,
                "imported_at": datetime.utcnow().isoformat()
            }
        finally:
            db.close()

    except Exception as exc:
        # Retry on error
        raise self.retry(exc=exc, countdown=60)
