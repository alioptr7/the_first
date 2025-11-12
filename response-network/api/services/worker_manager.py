"""Worker manager service for configuration and validation."""
from fastapi import HTTPException, status
from typing import Dict

from schemas.worker_settings import StorageType, ScheduleType

def validate_storage_config(storage_type: StorageType, config: Dict) -> bool:
    """Validate storage configuration based on type."""
    try:
        if storage_type == StorageType.LOCAL:
            required = {"path"}
            optional = {"create_dirs"}
        elif storage_type == StorageType.FTP:
            required = {"path", "host", "username", "password"}
            optional = {"port", "passive_mode"}
        elif storage_type == StorageType.S3:
            required = {
                "path",
                "bucket",
                "aws_access_key_id",
                "aws_secret_access_key",
                "region"
            }
            optional = set()
        else:
            return False
        
        # Check required fields
        if not all(field in config for field in required):
            return False
        
        # Check only valid fields are present
        valid_fields = required | optional
        if not all(field in valid_fields for field in config):
            return False
        
        return True
        
    except Exception:
        return False

def validate_schedule_config(schedule_type: ScheduleType, config: Dict) -> bool:
    """Validate schedule configuration based on type."""
    try:
        if schedule_type == ScheduleType.CRONTAB:
            # Basic crontab validation
            if "crontab" not in config:
                return False
                
            parts = config["crontab"].split()
            return len(parts) == 5
            
        elif schedule_type == ScheduleType.INTERVAL:
            required = {"days", "hours", "minutes", "seconds"}
            
            # Check all fields are present
            if not all(field in config for field in required):
                return False
            
            # Check values are non-negative integers
            return all(
                isinstance(config[field], int) and config[field] >= 0
                for field in required
            )
        
        return False
        
    except Exception:
        return False

class WorkerManager:
    """Service for managing worker settings and configurations."""
    
    validate_storage_config = staticmethod(validate_storage_config)
    validate_schedule_config = staticmethod(validate_schedule_config)