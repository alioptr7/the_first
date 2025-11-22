"""
ProfileTypes export task - Export profile types and permissions to request-network
"""
from datetime import datetime
import json
from pathlib import Path

from celery import shared_task
from sqlalchemy.orm import Session

from core.config import settings
from core.dependencies import get_db_sync
from models.profile_type_config import ProfileTypeConfig

EXPORT_PATH = Path(settings.EXPORT_DIR) / "profile_types"


@shared_task(bind=True, max_retries=3)
def export_profile_types_to_request_network(self):
    """
    Export all profile types and their permissions to file for request-network.
    
    Exports:
    - name
    - display_name
    - description
    - allowed_request_types
    - blocked_request_types
    - daily_request_limit
    - monthly_request_limit
    - rate_limit_per_minute
    - rate_limit_per_hour
    """
    try:
        # Create export directory if it doesn't exist
        EXPORT_PATH.mkdir(parents=True, exist_ok=True)
        
        # Get current timestamp for filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        # Get synchronous session
        db = next(get_db_sync())
        
        try:
            # Get all active profile types
            all_profile_types = db.query(ProfileTypeConfig).filter(
                ProfileTypeConfig.is_active == True
            ).all()
            
            # Prepare export data
            profile_types_list = []
            for profile_type in all_profile_types:
                profile_types_list.append({
                    "name": profile_type.name,
                    "display_name": profile_type.display_name,
                    "description": profile_type.description,
                    "allowed_request_types": profile_type.get_allowed_request_types(),
                    "blocked_request_types": profile_type.get_blocked_request_types(),
                    "daily_request_limit": profile_type.daily_request_limit,
                    "monthly_request_limit": profile_type.monthly_request_limit,
                    "rate_limit_per_minute": profile_type.rate_limit_per_minute,
                    "rate_limit_per_hour": profile_type.rate_limit_per_hour,
                    "is_builtin": profile_type.is_builtin,
                    "updated_at": profile_type.updated_at.isoformat() if profile_type.updated_at else None
                })
            
            export_data = {
                "profile_types": profile_types_list,
                "exported_at": datetime.utcnow().isoformat(),
                "version": 1,
                "total_count": len(profile_types_list)
            }
            
            # Write to file
            export_file = EXPORT_PATH / f"profile_types_{timestamp}.json"
            with open(export_file, "w", encoding="utf-8") as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            # Write latest.json for easy access
            latest_file = EXPORT_PATH / "latest.json"
            with open(latest_file, "w", encoding="utf-8") as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            return {
                "status": "success",
                "export_file": str(export_file),
                "total_profile_types": len(profile_types_list),
                "exported_at": datetime.utcnow().isoformat()
            }
        finally:
            db.close()
            
    except Exception as exc:
        # Retry on error
        raise self.retry(exc=exc, countdown=60)
