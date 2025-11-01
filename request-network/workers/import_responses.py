import json
import logging
import os
from datetime import datetime
from pathlib import Path

from shared.file_format_handler import decrypt_file, verify_checksum
from shared.schemas.transfer import ResponseBatch, ResponseTransferSchema
from workers.celery_app import celery_app
from workers.redis_client import redis_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Directory configuration with environment variable support
IMPORT_DIR = Path(os.getenv("REQUEST_IMPORT_DIR", "./import/responses"))
ARCHIVE_DIR = Path(os.getenv("REQUEST_ARCHIVE_DIR", "./import/responses/archive"))
FAILED_DIR = Path(os.getenv("REQUEST_FAILED_DIR", "./import/responses/failed"))
CONFIG_IMPORT_DIR = Path(os.getenv("CONFIG_IMPORT_DIR", "./import/config"))

# Ensure directories exist
for directory in [IMPORT_DIR, ARCHIVE_DIR, FAILED_DIR, CONFIG_IMPORT_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

def process_config_file(file_path: Path) -> bool:
    """
    Process configuration file from Response Network
    Returns True if processing was successful
    """
    try:
        logger.info(f"Processing config file: {file_path.name}")
        
        # Read and decrypt config file
        with open(file_path, "rb") as f:
            encrypted_content = f.read()
            
        # Read metadata
        meta_path = file_path.with_suffix(".meta")
        if not meta_path.exists():
            logger.error(f"Missing metadata file for config: {file_path.name}")
            return False
            
        with open(meta_path, "r") as f:
            metadata = json.loads(f.read())
            
        # Verify checksum
        if not verify_checksum(encrypted_content, metadata["checksum"]):
            logger.error(f"Checksum verification failed for config: {file_path.name}")
            return False
            
        # Decrypt and save config
        decrypted_content = decrypt_file(encrypted_content)
        target_path = Path(metadata["target_path"])
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(target_path, "wb") as f:
            f.write(decrypted_content)
            
        logger.info(f"Successfully applied config: {file_path.name} to {target_path}")
        
        # Archive files
        os.rename(file_path, ARCHIVE_DIR / file_path.name)
        os.rename(meta_path, ARCHIVE_DIR / meta_path.name)
        return True
        
    except Exception as e:
        logger.error(f"Failed to process config file {file_path.name}: {e}", exc_info=True)
        if file_path.exists():
            os.rename(file_path, FAILED_DIR / file_path.name)
        if meta_path.exists():
            os.rename(meta_path, FAILED_DIR / meta_path.name)
        return False

@celery_app.task(name="workers.tasks.import_responses.import_files")
def import_files():
    """Import responses and config files"""
    logger.info("Starting import_files task...")
    processed_files = {"responses": 0, "configs": 0}
    
    # Process config files first
    for file_path in CONFIG_IMPORT_DIR.glob("*.conf"):
        if process_config_file(file_path):
            processed_files["configs"] += 1
    
    # Process response files
    for file_path in IMPORT_DIR.glob("*.jsonl"):
        if not file_path.is_file():
            continue

        logger.info(f"Processing file: {file_path.name}")
        meta_path = file_path.with_suffix(".meta")

        try:
            # Read and validate metadata
            if not meta_path.exists():
                logger.error(f"Missing metadata file for: {file_path.name}")
                os.rename(file_path, FAILED_DIR / file_path.name)
                continue

            with open(meta_path, "r") as f:
                try:
                    metadata = ResponseBatch.parse_raw(f.read())
                except ValidationError as e:
                    logger.error(f"Invalid metadata format for {file_path.name}: {e}")
                    os.rename(file_path, FAILED_DIR / file_path.name)
                    os.rename(meta_path, FAILED_DIR / meta_path.name)
                    continue

            # Read file content
            with open(file_path, "r") as f:
                content = f.read()

            # Verify checksum
            if not verify_checksum(content.encode(), metadata.checksum):
                logger.error(f"Checksum verification failed for {file_path.name}")
                os.rename(file_path, FAILED_DIR / file_path.name)
                os.rename(meta_path, FAILED_DIR / meta_path.name)
                continue

            # Parse and validate records
            try:
                records = [json.loads(line) for line in content.splitlines()]
                validated_responses = [ResponseTransferSchema.parse_obj(rec) for rec in records]
            except (ValueError, ValidationError) as e:
                logger.error(f"Failed to parse or validate file {file_path.name}: {e}")
                os.rename(file_path, FAILED_DIR / file_path.name)
                os.rename(meta_path, FAILED_DIR / meta_path.name)
                continue

            if not validated_responses:
                logger.warning(f"File {file_path.name} is empty or contains no valid records.")
                os.rename(file_path, ARCHIVE_DIR / file_path.name)
                os.rename(meta_path, ARCHIVE_DIR / meta_path.name)
                continue

            # Push responses to Redis queue for processing
            for response in validated_responses:
                redis_client.rpush("responses_to_process", response.json())

            logger.info(f"Queued {len(validated_responses)} responses for processing")

            # Archive files after successful processing
            os.rename(file_path, ARCHIVE_DIR / file_path.name)
            os.rename(meta_path, ARCHIVE_DIR / meta_path.name)
            processed_files["responses"] += 1

        except Exception as e:
            logger.critical(f"Unhandled error processing file {file_path.name}: {e}", exc_info=True)
            if file_path.exists():
                os.rename(file_path, FAILED_DIR / file_path.name)
            if meta_path.exists():
                os.rename(meta_path, FAILED_DIR / meta_path.name)

    return f"Processed {processed_files['responses']} response files and {processed_files['configs']} config files."