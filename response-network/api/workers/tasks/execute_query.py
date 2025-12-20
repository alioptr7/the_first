import json
from datetime import datetime
import uuid
from time import sleep

from celery import shared_task
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.config import settings
from models.incoming_request import IncomingRequest
from models.request_type import RequestType
from models.query_result import QueryResult

# Setup sync database connection for Celery
sync_engine = create_engine(
    str(settings.DATABASE_URL).replace('postgresql+asyncpg', 'postgresql'),
    pool_pre_ping=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

@shared_task(bind=True, max_retries=3)
def execute_pending_queries(self):
    """
    Execute pending requests against Elasticsearch (mocked for now).
    """
    db = SessionLocal()
    try:
        # Get pending requests
        pending_requests = db.query(IncomingRequest).filter(
            IncomingRequest.status == "pending"
        ).limit(50).all()

        if not pending_requests:
            return {"status": "no_pending_requests"}

        processed_count = 0
        for req in pending_requests:
            try:
                # Update status to processing
                req.status = "processing"
                req.started_at = datetime.utcnow()
                req.assigned_worker = self.request.id
                db.commit()

                # Fetch Request Type
                stmt = db.query(RequestType).filter(RequestType.name == req.query_type)
                request_type = stmt.first()
                
                if not request_type:
                     raise ValueError(f"Request Type '{req.query_type}' not found or active")

                if not request_type.elasticsearch_query_template:
                     raise ValueError(f"No query template defined for '{req.query_type}'")

                # Parse and Render Query
                # Simple recursive replacement
                def render_template(template, params):
                    if isinstance(template, dict):
                        return {k: render_template(v, params) for k, v in template.items()}
                    elif isinstance(template, list):
                        return [render_template(v, params) for v in template]
                    elif isinstance(template, str):
                        for key, val in params.items():
                             # Handle simple string replacement
                             # Note: This doesn't handle type conversion automatically (e.g. number to int)
                             if f"{{{{{key}}}}}" in template:
                                  template = template.replace(f"{{{{{key}}}}}", str(val))
                        return template
                    else:
                        return template

                query_body = render_template(request_type.elasticsearch_query_template, req.query_params or {})
                
                # Execute Query
                index_name = request_type.available_indices[0] if request_type.available_indices else "default"
                base_url = str(settings.ELASTICSEARCH_URL).rstrip('/')
                es_url = f"{base_url}/{index_name}/_search"
                
                import requests
                response = requests.post(es_url, json=query_body, timeout=10)
                
                if response.status_code >= 400:
                     raise Exception(f"Elasticsearch Error ({response.status_code}): {response.text}")
                
                es_result = response.json()
                
                # Transform Result
                hits = es_result.get("hits", {}).get("hits", [])
                result_data = {
                    "count": es_result.get("hits", {}).get("total", {}).get("value", 0),
                    "results": [h["_source"] for h in hits], # Generic key for all request types
                    "provider": "Elasticsearch"
                }

                # Create QueryResult
                query_result = QueryResult(
                    id=uuid.uuid4(),
                    request_id=req.id,
                    original_request_id=req.original_request_id,
                    result_data=result_data,
                    result_count=result_data["count"],
                    execution_time_ms=es_result.get("took", 0), # Approximate
                    elasticsearch_took_ms=es_result.get("took", 0),
                    cache_hit=False,
                    executed_at=datetime.utcnow()
                )
                db.add(query_result)

                # Update Request Status
                req.status = "completed"
                req.completed_at = datetime.utcnow()
                req.progress = 100.0
                
                db.commit()
                processed_count += 1
                
            except Exception as e:
                db.rollback()
                req.status = "failed"
                req.error_message = str(e)
                req.retry_count += 1
                db.commit()
                # Continue to next request

        return {
            "status": "success",
            "processed_count": processed_count
        }
    finally:
        db.close()
