import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from sqlalchemy.future import select

from models.settings import Settings, UserSettings
from shared.file_format_handler import encrypt_file, calculate_checksum
from workers.celery_app import celery_app
from workers.database import db_session_scope

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Directory configuration
EXPORT_DIR = Path(os.getenv("RESPONSE_EXPORT_DIR", "./export/settings"))
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

def export_setting_file(settings_data: List[Dict[str, Any]], target_path: str) -> bool:
    """
    Export settings to an encrypted file with metadata
    Returns True if export was successful
    """
    try:
        # Convert settings to JSON
        content = json.dumps(settings_data, indent=2).encode()
        
        # Encrypt content
        encrypted_content = encrypt_file(content)
        
        # Calculate checksum of encrypted content
        checksum = calculate_checksum(encrypted_content)
        
        # Create unique filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"settings_{timestamp}.conf"
        file_path = EXPORT_DIR / filename
        
        # Write encrypted file
        with open(file_path, "wb") as f:
            f.write(encrypted_content)
            
        # Create metadata file
        metadata = {
            "filename": filename,
            "target_path": target_path,
            "checksum": checksum,
            "encrypted": True,
            "created_at": datetime.utcnow().isoformat(),
            "record_count": len(settings_data)
        }
        
        with open(file_path.with_suffix(".meta"), "w") as f:
            json.dump(metadata, f, indent=2)
            
        logger.info(f"Successfully exported {len(settings_data)} settings to {filename}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to export settings: {e}", exc_info=True)
        return False

@celery_app.task(name="workers.tasks.export_settings.export_settings")
def export_settings():
    """Export settings that need to be synced to Request Network"""
    logger.info("Starting export_settings task...")
    exported_count = 0
    
    with db_session_scope() as db:
        # Get system settings that need sync
        system_settings = db.execute(
            select(Settings)
            .where(Settings.is_synced == False)
            .order_by(Settings.sync_priority.desc())
        ).scalars().all()
        
        if system_settings:
            settings_data = [
                {
                    "id": str(setting.id),
                    "key": setting.key,
                    "value": setting.value,
                    "is_user_specific": setting.is_user_specific
                }
                for setting in system_settings
            ]
            
            if export_setting_file(settings_data, "/config/system/"):
                # Update sync status
                for setting in system_settings:
                    setting.is_synced = True
                    setting.last_synced_at = datetime.utcnow()
                exported_count += len(system_settings)
        
        # Get user settings that need sync
        user_settings = db.execute(
            select(UserSettings)
            .where(UserSettings.is_synced == False)
            .join(Settings)
            .order_by(Settings.sync_priority.desc())
        ).scalars().all()
        
        if user_settings:
            settings_data = [
                {
                    "id": str(setting.id),
                    "user_id": str(setting.user_id),
                    "setting_id": str(setting.setting_id),
                    "value": setting.value
                }
                for setting in user_settings
            ]
            
            if export_setting_file(settings_data, "/config/users/"):
                # Update sync status
                for setting in user_settings:
                    setting.is_synced = True
                    setting.last_synced_at = datetime.utcnow()
                exported_count += len(user_settings)
        
        db.commit()
    
    return f"Exported {exported_count} settings"