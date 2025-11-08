import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from ..shared.file_format_handler import calculate_checksum
from ..shared.schemas.transfer import RequestBatch
from workers.celery_app import celery_app
from workers.redis_client import redis_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Directory configuration with environment variable support
EXPORT_DIR = Path(os.getenv("REQUEST_EXPORT_DIR", "./export/requests"))

# Ensure directories exist
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

def process_requests_batch(requests: List[Dict[str, Any]]) -> bool:
    """
    Process a batch of requests and create export files
    Returns True if export was successful
    """
    try:
        if not requests:
            return True

        # Create JSONL content
        jsonl_content = "\n".join(json.dumps(req) for req in requests)
        content_bytes = jsonl_content.encode()
        
        # Calculate checksum
        checksum = calculate_checksum(content_bytes)
        
        # Create batch metadata
        batch_metadata = RequestBatch(
            batch_id=f"batch_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            batch_type="requests",
            file_size=len(content_bytes),
            checksum=checksum,
            record_count=len(requests),
            source_network="request",
            created_at=datetime.utcnow().isoformat()
        )
        
        # Write request file and metadata
        filename = f"requests_{batch_metadata.batch_id}.jsonl"
        file_path = EXPORT_DIR / filename
        
        with open(file_path, "w") as f:
            f.write(jsonl_content)
            
        with open(file_path.with_suffix(".meta"), "w") as f:
            f.write(batch_metadata.json(indent=2))
            
        logger.info(f"Successfully exported {len(requests)} requests to {filename}")
        
        # Mark requests as exported in Redis
        for req in requests:
            redis_client.lrem("requests_to_export", 0, json.dumps(req))
            
        return True
        
    except Exception as e:
        logger.error(f"Failed to export requests batch: {e}", exc_info=True)
        return False

@celery_app.task(name="workers.tasks.export_requests.export_files")
def export_files():
    """Export requests"""
    logger.info("Starting export_files task...")
    
    # Process requests from Redis queue
    requests_exported = 0
    batch_size = 1000  # Adjust based on your needs
    
    while True:
        # Get requests batch from Redis
        requests = []
        for _ in range(batch_size):
            req = redis_client.lpop("requests_to_export")
            if not req:
                break
            try:
                requests.append(json.loads(req))
            except json.JSONDecodeError:
                logger.error(f"Failed to parse request JSON: {req}")
                continue
        
        if not requests:
            break
            
        if process_requests_batch(requests):
            requests_exported += len(requests)
    
    return f"Exported {requests_exported} requests."