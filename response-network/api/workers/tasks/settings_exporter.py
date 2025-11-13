from datetime import datetime
import json
from pathlib import Path
import redis

from celery import shared_task
from sqlalchemy import select
from sqlalchemy.orm import Session

from core.config import settings
from core.dependencies import get_db_sync
from models.settings import Settings as SettingsModel

EXPORT_PATH = Path(settings.EXPORT_DIR) / "settings"

# Redis client for deduplication
redis_client = redis.from_url(settings.CELERY_BROKER_URL)

@shared_task(bind=True, max_retries=3)
def export_settings_to_request_network(self):
    """Export all public settings to file.
    
    Features:
    - Prevents duplicate execution if many queued (uses deduplication key)
    - Creates timestamped export files
    - Updates latest.json for easy access
    """
    try:
        # ⏱️ Deduplication: Check if there's a newer task in queue
        # This prevents executing old queued tasks when worker restarts
        dedup_key = "export_settings_dedup"
        current_task_id = self.request.id
        
        # Get the last task that was supposed to run
        last_task_id = redis_client.get(dedup_key)
        if last_task_id and last_task_id.decode() != current_task_id:
            # این task قدیمی است، skip کن
            return {
                "status": "skipped",
                "reason": "Newer task in queue",
                "current_task_id": current_task_id,
                "skipped_at": datetime.utcnow().isoformat()
            }
        
        # Set this task as the current one
        redis_client.set(dedup_key, current_task_id, ex=3600)  # 1 hour expiry
        
        # Create export directory if it doesn't exist
        EXPORT_PATH.mkdir(parents=True, exist_ok=True)
        
        # Get current timestamp for filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        # Get synchronous session
        db = next(get_db_sync())
        
        try:
            # Get all public settings
            all_settings = db.query(SettingsModel).filter(
                SettingsModel.is_public == True
            ).all()
            
            # Prepare export data
            settings_list = []
            for setting in all_settings:
                settings_list.append({
                    "key": setting.key,
                    "value": setting.value,
                    "description": setting.description,
                    "is_public": setting.is_public,
                    "created_at": setting.created_at.isoformat() if setting.created_at else None,
                    "updated_at": setting.updated_at.isoformat() if setting.updated_at else None
                })
            
            export_data = {
                "settings": settings_list,
                "exported_at": datetime.utcnow().isoformat(),
                "version": 1,
                "total_count": len(settings_list)
            }
            
            # Write to file
            export_file = EXPORT_PATH / f"settings_{timestamp}.json"
            with open(export_file, "w", encoding="utf-8") as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            # Write latest.json for easy access
            latest_file = EXPORT_PATH / "latest.json"
            with open(latest_file, "w", encoding="utf-8") as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            return {
                "status": "success",
                "export_file": str(export_file),
                "total_settings": len(settings_list),
                "exported_at": datetime.utcnow().isoformat()
            }
        finally:
            db.close()
            
    except Exception as exc:
        # Retry on error
        raise self.retry(exc=exc, countdown=60)