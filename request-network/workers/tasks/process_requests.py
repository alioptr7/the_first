import json
import logging
from datetime import datetime

from sqlalchemy.future import select

from models.request import Request
from workers.celery_app import celery_app
from workers.database import db_session_scope
from workers.redis_client import redis_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@celery_app.task(name="workers.tasks.process_requests.process_redis_requests")
def process_redis_requests():
    """
    Process requests from Redis queue and store them in PostgreSQL
    """
    logger.info("Starting process_redis_requests task...")
    processed_count = 0
    
    while True:
        # Get request from Redis
        request_json = redis_client.lpop("requests_to_process")
        if not request_json:
            break
            
        try:
            request_data = json.loads(request_json)
            
            with db_session_scope() as db:
                # Check if request already exists
                existing_request = db.execute(
                    select(Request).where(Request.id == request_data["id"])
                ).scalar_one_or_none()
                
                if existing_request:
                    logger.warning(f"Request {request_data['id']} already exists, skipping")
                    continue
                    
                # Create new request
                new_request = Request(
                    id=request_data["id"],
                    user_id=request_data["user_id"],
                    name=request_data["name"],
                    query_type=request_data["query_type"],
                    query_params=request_data["query_params"],
                    status="pending",
                    priority=request_data.get("priority", 5),
                    created_at=datetime.fromisoformat(request_data["created_at"]),
                )
                
                db.add(new_request)
                processed_count += 1
                
        except Exception as e:
            logger.error(f"Failed to process request: {e}", exc_info=True)
            # Push back to queue for retry
            redis_client.rpush("requests_to_process", request_json)
            continue
    
    return f"Processed {processed_count} requests"