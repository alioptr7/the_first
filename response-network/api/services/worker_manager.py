from fastapi import HTTPException, status
from typing import Dict

from schemas.worker_settings import StorageType, ScheduleType

class WorkerManager:
    """Service for managing worker settings and configurations."""
    
    @staticmethod
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
    
    @staticmethod
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
    
    @staticmethod
    def get_storage_handler(storage_type: StorageType, config: Dict):
        """Get appropriate storage handler based on type."""
        if storage_type == StorageType.LOCAL:
            return LocalStorageHandler(config)
        elif storage_type == StorageType.FTP:
            return FTPStorageHandler(config)
        elif storage_type == StorageType.S3:
            return S3StorageHandler(config)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported storage type: {storage_type}"
            )
    
    @staticmethod
    def get_schedule_handler(schedule_type: ScheduleType, config: Dict):
        """Get appropriate schedule handler based on type."""
        if schedule_type == ScheduleType.CRONTAB:
            return CrontabScheduleHandler(config)
        elif schedule_type == ScheduleType.INTERVAL:
            return IntervalScheduleHandler(config)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported schedule type: {schedule_type}"
            )