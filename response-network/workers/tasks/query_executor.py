import hashlib
import json
import logging
import time
from datetime import datetime

from api.models.request import IncomingRequest
from api.models.result import QueryResult
from workers.celery_app import celery_app
from workers.database import db_session_scope
from workers.elasticsearch_client import ElasticsearchClient
from workers.redis_client import get_redis_client
from workers.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_cache_key(index: str, query_body: dict, size: int, offset: int) -> str:
    """Generates a consistent cache key for a query."""
    # Use a stable json dump to ensure hash consistency
    query_str = json.dumps(query_body, sort_keys=True)
    query_hash = hashlib.sha256(query_str.encode()).hexdigest()
    return f"es_cache:{index}:{query_hash}:{size}:{offset}"


@celery_app.task(
    name="workers.tasks.query_executor.execute_query_task",
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 60},
    acks_late=True,
)
async def execute_query_task(self, incoming_request_id: str):
    """
    Executes a single query against Elasticsearch, with caching.
    """
    logger.info(f"Starting query execution for request_id: {incoming_request_id}")
    es_client = ElasticsearchClient()
    redis_client = get_redis_client()
    start_time = time.monotonic()

    try:
        with db_session_scope() as db:
            request = db.query(IncomingRequest).filter(IncomingRequest.id == incoming_request_id).first()
            if not request:
                logger.error(f"IncomingRequest with id {incoming_request_id} not found.")
                return

            # Avoid re-processing
            if request.status not in ["pending", "retry"]:
                logger.warning(f"Request {incoming_request_id} is already in status '{request.status}'. Skipping.")
                return

            request.status = "processing"
            request.assigned_worker = self.request.hostname
            request.started_at = datetime.utcnow()
            db.commit()

            query_body = es_client.build_es_query(request.query_type, request.query_params)
            size = request.query_params.get("size", 100)
            offset = request.query_params.get("from", 0)
            index = request.query_params.get("index")

            cache_key = generate_cache_key(index, query_body, size, offset)
            cached_result = redis_client.get(cache_key)
            cache_hit = False
            es_took_ms = None

            if cached_result:
                logger.info(f"Cache hit for request {incoming_request_id} with key {cache_key}")
                result_data = json.loads(cached_result)
                cache_hit = True
            else:
                logger.info(f"Cache miss for request {incoming_request_id}. Executing ES query.")
                es_response = await es_client.execute_query(
                    query_type=request.query_type,
                    query_params=request.query_params,
                    size=size,
                    offset=offset,
                )
                result_data = es_response
                es_took_ms = es_response.get("took")
                # Cache the result
                redis_client.set(cache_key, json.dumps(result_data), ex=settings.CACHE_MAINTENANCE_SCHEDULE_SECONDS)

            # Store result in the database
            new_result = QueryResult(
                request_id=request.id,
                original_request_id=request.original_request_id,
                result_data=result_data,
                result_count=len(result_data.get("hits", {}).get("hits", [])),
                execution_time_ms=int((time.monotonic() - start_time) * 1000),
                elasticsearch_took_ms=es_took_ms,
                cache_hit=cache_hit,
            )
            db.add(new_result)

            # Finalize request status
            request.status = "completed"
            request.completed_at = datetime.utcnow()
            logger.info(f"Successfully completed query for request {incoming_request_id}.")

    except Exception as e:
        logger.error(f"Query execution failed for request {incoming_request_id}: {e}", exc_info=True)
        with db_session_scope() as db:
            request = db.query(IncomingRequest).filter(IncomingRequest.id == incoming_request_id).first()
            if request:
                request.status = "failed"
                request.error_message = str(e)
        # Re-raise the exception to trigger Celery's retry mechanism
        raise
    finally:
        await es_client.close_connection()