import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from shared.file_format_handler import encrypt_file, calculate_checksum
from shared.schemas.transfer import ResponseBatch
from workers.celery_app import celery_app
from workers.redis_client import redis_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Directory configuration with environment variable support
EXPORT_DIR = Path(os.getenv("RESPONSE_EXPORT_DIR", "./export/responses"))
CONFIG_EXPORT_DIR = Path(os.getenv("CONFIG_EXPORT_DIR", "./export/config"))

# Ensure directories exist
for directory in [EXPORT_DIR, CONFIG_EXPORT_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

def export_config_file(source_path: Path, target_path: Path) -> bool:
    """
    Export configuration file with encryption
    Returns True if export was successful
    """
    try:
        logger.info(f"Exporting config file: {source_path}")
        
        # Read and encrypt config file
        with open(source_path, "rb") as f:
            content = f.read()
            
        encrypted_content = encrypt_file(content)
        checksum = calculate_checksum(encrypted_content)
        
        # Create metadata
        metadata = {
            "source_path": str(source_path),
            "target_path": str(target_path),
            "file_size": len(encrypted_content),
            "checksum": checksum,
            "encrypted": True,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Write encrypted file and metadata
        export_path = CONFIG_EXPORT_DIR / f"{source_path.stem}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.conf"
        with open(export_path, "wb") as f:
            f.write(encrypted_content)
            
        with open(export_path.with_suffix(".meta"), "w") as f:
            json.dump(metadata, f, indent=2)
            
        logger.info(f"Successfully exported config file to {export_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to export config file {source_path}: {e}", exc_info=True)
        return False

def process_responses_batch(responses: List[Dict[str, Any]]) -> bool:
    """
    Process a batch of responses and create export files
    Returns True if export was successful
    """
    try:
        if not responses:
            return True

        # Create JSONL content
        jsonl_content = "\n".join(json.dumps(resp) for resp in responses)
        content_bytes = jsonl_content.encode()
        
        # Calculate checksum
        checksum = calculate_checksum(content_bytes)
        
        # Create batch metadata
        batch_metadata = ResponseBatch(
            batch_id=f"batch_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            batch_type="responses",
            file_size=len(content_bytes),
            checksum=checksum,
            record_count=len(responses),
            source_network="response",
            created_at=datetime.utcnow().isoformat()
        )
        
        # Write response file and metadata
        filename = f"responses_{batch_metadata.batch_id}.jsonl"
        file_path = EXPORT_DIR / filename
        
        with open(file_path, "w") as f:
            f.write(jsonl_content)
            
        with open(file_path.with_suffix(".meta"), "w") as f:
            f.write(batch_metadata.json(indent=2))
            
        logger.info(f"Successfully exported {len(responses)} responses to {filename}")
        
        # Mark responses as exported in Redis
        for resp in responses:
            redis_client.lrem("responses_to_export", 0, json.dumps(resp))
            
        return True
        
    except Exception as e:
        logger.error(f"Failed to export responses batch: {e}", exc_info=True)
        return False

@celery_app.task(name="workers.tasks.export_responses.export_files")
def export_files():
    """Export responses and config files"""
    logger.info("Starting export_files task...")
    
    # Process config files first
    config_files = [
        (Path("/etc/response-network/config.yaml"), Path("/etc/request-network/config.yaml")),
        (Path("/etc/response-network/logging.yaml"), Path("/etc/request-network/logging.yaml")),
        # Add other config file pairs as needed
    ]
    
    configs_exported = 0
    for source_path, target_path in config_files:
        if source_path.exists() and export_config_file(source_path, target_path):
            configs_exported += 1
    
    # Process responses from Redis queue
    responses_exported = 0
    batch_size = 1000  # Adjust based on your needs
    
    while True:
        # Get responses batch from Redis
        responses = []
        for _ in range(batch_size):
            resp = redis_client.lpop("responses_to_export")
            if not resp:
                break
            try:
                responses.append(json.loads(resp))
            except json.JSONDecodeError:
                logger.error(f"Failed to parse response JSON: {resp}")
                continue
        
        if not responses:
            break
            
        if process_responses_batch(responses):
            responses_exported += len(responses)
    
    return f"Exported {responses_exported} responses and {configs_exported} config files."