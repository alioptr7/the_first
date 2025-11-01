import json
import logging
from datetime import datetime

from sqlalchemy.future import select

from models.request import Request
from models.response import Response
from workers.celery_app import celery_app
from workers.database import db_session_scope
from workers.redis_client import redis_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@celery_app.task(name="workers.tasks.process_responses.process_redis_responses")
def process_redis_responses():
    """
    Process responses from Redis queue and store them in PostgreSQL
    """
    logger.info("Starting process_redis_responses task...")
    processed_count = 0
    
    while True:
        # Get response from Redis
        response_json = redis_client.lpop("responses_to_process")
        if not response_json:
            break
            
        try:
            response_data = json.loads(response_json)
            
            with db_session_scope() as db:
                # Get associated request
                request = db.execute(
                    select(Request).where(Request.id == response_data["request_id"])
                ).scalar_one_or_none()
                
                if not request:
                    logger.error(f"Request {response_data['request_id']} not found for response")
                    continue
                
                # Check if response already exists
                existing_response = db.execute(
                    select(Response).where(Response.request_id == response_data["request_id"])
                ).scalar_one_or_none()
                
                if existing_response:
                    logger.warning(f"Response for request {response_data['request_id']} already exists, updating")
                    existing_response.result_data = response_data["result_data"]
                    existing_response.execution_time_ms = response_data.get("execution_time_ms")
                    existing_response.updated_at = datetime.utcnow()
                else:
                    # Create new response
                    new_response = Response(
                        request_id=response_data["request_id"],
                        result_data=response_data["result_data"],
                        execution_time_ms=response_data.get("execution_time_ms"),
                        received_at=datetime.utcnow()
                    )
                    db.add(new_response)
                
                # Update request status
                request.status = "completed"
                request.result_received_at = datetime.utcnow()
                processed_count += 1
                
        except Exception as e:
            logger.error(f"Failed to process response: {e}", exc_info=True)
            # Push back to queue for retry
            redis_client.rpush("responses_to_process", response_json)
            continue
    
    return f"Processed {processed_count} responses"