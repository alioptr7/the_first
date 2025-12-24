import json
from datetime import datetime
from pathlib import Path
import hashlib
import uuid

from celery import shared_task
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.config import settings
from models.request import Request
from models.response import Response
from models.user import User # Register User model

# Setup sync database connection for Celery
sync_engine = create_engine(
    str(settings.DATABASE_URL).replace('postgresql+asyncpg', 'postgresql+psycopg'),
    pool_pre_ping=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

IMPORT_PATH = Path(settings.IMPORT_DIR) / "results"

@shared_task(bind=True, max_retries=3)
def import_results_from_response_network(self):
    """
    Import completed results from response-network.
    """
    try:
        IMPORT_PATH.mkdir(parents=True, exist_ok=True)
        
        # Get all JSONL files in import directory
        result_files = list(IMPORT_PATH.glob("results_*.jsonl"))
        
        if not result_files:
            return {
                "status": "no_files",
                "imported_at": datetime.utcnow().isoformat(),
                "count": 0
            }

        db = SessionLocal()
        total_imported = 0
        
        try:
            for result_file in result_files:
                with open(result_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                for line in lines:
                    if not line.strip():
                        continue
                    
                    try:
                        data = json.loads(line)
                        request_id = data.get("request_id")
                        
                        # Find original request
                        request = db.query(Request).filter(Request.id == request_id).first()
                        if not request:
                            continue # Request not found (maybe deleted?)

                        if request.status == "completed":
                            continue # Already processed

                        # Create Response
                        response = Response(
                            request_id=request.id,
                            result_data=data.get("result_data"),
                            execution_time_ms=data.get("execution_time_ms"),
                            received_at=datetime.utcnow(),
                            is_cached=False 
                        )
                        db.add(response)

                        # Update Request
                        request.status = "completed"
                        request.result_received_at = datetime.utcnow()
                        
                        total_imported += 1
                        
                    except Exception as e:
                        print(f"Error processing line: {e}")
                        continue
                
                db.commit()

                # Archive file
                archive_dir = IMPORT_PATH / "archive"
                archive_dir.mkdir(parents=True, exist_ok=True)
                result_file.rename(archive_dir / result_file.name)
                
            return {
                "status": "success",
                "imported_count": total_imported
            }
        finally:
            db.close()
            
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
